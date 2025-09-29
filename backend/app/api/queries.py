from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from app.core.database import get_db
from app.core.exceptions import handle_query_processing_error, handle_data_analysis_error
from app.models.file import File as FileModel
from app.models.query import Query as QueryModel
from app.services.ai_service import AIService
from app.services.data_analysis_service import DataAnalysisService
from app.utils.excel_processor import ExcelProcessor
from app.utils.validators import validate_query_parameters, validate_data_for_analysis

logger = logging.getLogger(__name__)

router = APIRouter()
ai_service = AIService()
data_analysis_service = DataAnalysisService()
excel_processor = ExcelProcessor()


class QueryRequest(BaseModel):
    question: str
    file_id: int


class QueryResponse(BaseModel):
    id: int
    question: str
    response: Optional[str]
    query_type: Optional[str]
    data_result: Optional[Dict[str, Any]]
    chart_type: Optional[str]
    chart_config: Optional[Dict[str, Any]]
    status: str
    created_at: str


@router.post("/", response_model=QueryResponse)
async def process_query(
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process a natural language query about uploaded data."""
    
    # Validate query parameters
    try:
        validate_query_parameters(query_request.question, query_request.file_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Validate file exists and is processed
    file = db.query(FileModel).filter(FileModel.id == query_request.file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not file.is_processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not processed yet"
        )
    
    # Create query record
    db_query = QueryModel(
        file_id=query_request.file_id,
        question=query_request.question,
        status="processing"
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    
    try:
        # Process the query using AI service
        ai_response = await ai_service.process_query(
            question=query_request.question,
            file_schema=file.sheets_info or {},
            sample_data=None  # Could add sample data here for better context
        )
        
        # Execute the analysis
        file_data = excel_processor.process_file(file.file_path)
        validate_data_for_analysis(file_data)
        
        analysis_result = await data_analysis_service.execute_query(
            query_type=ai_response.get('query_type', 'general'),
            sql_query=ai_response.get('sql_query'),
            file_data=file_data['sheets_data'],
            question=query_request.question,
            chart_type=ai_response.get('chart_type', 'table')
        )
        
        # Update query record with results
        db_query.status = "completed"
        db_query.response = ai_response.get('explanation', 'Analysis completed')
        db_query.query_type = ai_response.get('query_type')
        db_query.sql_query = ai_response.get('sql_query')
        db_query.data_result = analysis_result
        db_query.chart_type = ai_response.get('chart_type')
        db_query.chart_config = ai_response.get('chart_config', {})
        db.commit()
        
        return QueryResponse(
            id=db_query.id,
            question=db_query.question,
            response=db_query.response,
            query_type=db_query.query_type,
            data_result=db_query.data_result,
            chart_type=db_query.chart_type,
            chart_config=db_query.chart_config,
            status=db_query.status,
            created_at=db_query.created_at.isoformat()
        )
        
    except Exception as e:
        # Update query record with error
        db_query.status = "failed"
        db_query.error_message = str(e)
        db.commit()
        
        logger.error(f"Error processing query '{query_request.question}': {str(e)}")
        raise handle_query_processing_error(e)


@router.get("/file/{file_id}")
async def get_file_queries(
    file_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all queries for a specific file."""
    
    # Validate file exists
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    queries = db.query(QueryModel).filter(
        QueryModel.file_id == file_id
    ).offset(skip).limit(limit).all()
    
    return {
        "queries": [
            {
                "id": query.id,
                "question": query.question,
                "response": query.response,
                "query_type": query.query_type,
                "chart_type": query.chart_type,
                "status": query.status,
                "created_at": query.created_at.isoformat(),
                "error_message": query.error_message
            }
            for query in queries
        ],
        "total": db.query(QueryModel).filter(QueryModel.file_id == file_id).count()
    }


@router.get("/{query_id}")
async def get_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific query and its results."""
    
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    return {
        "id": query.id,
        "question": query.question,
        "response": query.response,
        "query_type": query.query_type,
        "sql_query": query.sql_query,
        "data_result": query.data_result,
        "chart_type": query.chart_type,
        "chart_config": query.chart_config,
        "status": query.status,
        "error_message": query.error_message,
        "created_at": query.created_at.isoformat(),
        "completed_at": query.completed_at.isoformat() if query.completed_at else None
    }


@router.delete("/{query_id}")
async def delete_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """Delete a query."""
    
    query = db.query(QueryModel).filter(QueryModel.id == query_id).first()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    db.delete(query)
    db.commit()
    
    return {"message": "Query deleted successfully"}


@router.post("/suggest")
async def suggest_questions(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Get suggested questions for a file."""
    
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not file.is_processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not processed yet"
        )
    
    suggestions = ai_service.suggest_questions(file.sheets_info or {})
    
    return {
        "suggested_questions": suggestions,
        "file_id": file_id
    }
