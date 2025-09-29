from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
import aiofiles
import logging

from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import handle_file_processing_error, FileProcessingError
from app.models.file import File as FileModel
from app.models.query import Query as QueryModel
from app.utils.excel_processor import ExcelProcessor
from app.utils.validators import validate_file_upload, validate_excel_structure, sanitize_filename
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter()
excel_processor = ExcelProcessor()
ai_service = AIService()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an Excel file for analysis."""
    
    # Validate file type
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )
    
    # Initialize for cleanup in exception handler
    file_path = ""
    
    try:
        # Create unique filename and ensure upload directory exists
        sanitized_filename = sanitize_filename(file.filename)
        unique_filename = f"{sanitized_filename}_{file_size}_{hash(content)}"
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Validate the saved file
        validate_file_upload(file_path, file_size, file_extension)
        
        # Create database record
        db_file = FileModel(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_extension,
            processing_status="pending"
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Process file asynchronously
        await process_file_async(db_file.id, file_path, db)
        
        return {
            "message": "File uploaded successfully",
            "file_id": db_file.id,
            "filename": file.filename,
            "file_size": file_size,
            "processing_status": "processing"
        }
        
    except Exception as e:
        # Clean up file if processing fails
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        raise handle_file_processing_error(e)


async def process_file_async(file_id: int, file_path: str, db: Session):
    """Process uploaded file asynchronously."""
    try:
        # Update status to processing
        db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if db_file:
            db_file.processing_status = "processing"
            db.commit()
        
        # Process the Excel file
        processed_data = excel_processor.process_file(file_path)
        
        # Validate processed data structure
        validate_excel_structure(processed_data.get('sheets_info', {}))
        
        # Update database with processed data
        if db_file:
            db_file.is_processed = True
            db_file.processing_status = "completed"
            db_file.sheets_info = processed_data.get('sheets_info', {})
            db_file.columns_info = processed_data.get('columns_info', {})
            db.commit()
        
    except Exception as e:
        # Update status to failed
        db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if db_file:
            db_file.processing_status = "failed"
            db_file.processing_error = str(e)
            db.commit()
        
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/")
async def list_files(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all uploaded files."""
    files = db.query(FileModel).offset(skip).limit(limit).all()
    
    return {
        "files": [
            {
                "id": file.id,
                "filename": file.original_filename,
                "file_size": file.file_size,
                "file_type": file.file_type,
                "is_processed": file.is_processed,
                "processing_status": file.processing_status,
                "created_at": file.created_at,
                "sheets_count": len(file.sheets_info) if file.sheets_info else 0
            }
            for file in files
        ],
        "total": db.query(FileModel).count()
    }


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Get file details and schema information."""
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
        "id": file.id,
        "filename": file.original_filename,
        "file_size": file.file_size,
        "file_type": file.file_type,
        "is_processed": file.is_processed,
        "processing_status": file.processing_status,
        "processing_error": file.processing_error,
        "created_at": file.created_at,
        "sheets_info": file.sheets_info,
        "columns_info": file.columns_info,
        "suggested_questions": ai_service.suggest_questions(file.sheets_info or {}) if file.sheets_info else []
    }


@router.get("/{file_id}/data")
async def get_file_data(
    file_id: int,
    sheet_name: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get actual data from a file."""
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
    
    try:
        # Load the processed data
        processed_data = excel_processor.process_file(file.file_path)
        
        if sheet_name:
            if sheet_name in processed_data['sheets_data']:
                data = processed_data['sheets_data'][sheet_name][:limit]
                return {
                    "sheet_name": sheet_name,
                    "data": data,
                    "total_rows": len(processed_data['sheets_data'][sheet_name])
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sheet '{sheet_name}' not found"
                )
        else:
            # Return first sheet data
            first_sheet = list(processed_data['sheets_data'].keys())[0]
            data = processed_data['sheets_data'][first_sheet][:limit]
            return {
                "sheet_name": first_sheet,
                "data": data,
                "total_rows": len(processed_data['sheets_data'][first_sheet]),
                "available_sheets": list(processed_data['sheets_data'].keys())
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading file data: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Delete a file and its associated data."""
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete associated queries
        db.query(QueryModel).filter(QueryModel.file_id == file_id).delete()
        
        # Delete file record
        db.delete(file)
        db.commit()
        
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
