from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    
    # Query processing information
    query_type = Column(String(100), nullable=True)  # e.g., "aggregation", "filtering", "comparison"
    sql_query = Column(Text, nullable=True)  # Generated SQL query if applicable
    data_result = Column(JSON, nullable=True)  # Structured data result
    
    # Visualization information
    chart_type = Column(String(50), nullable=True)  # e.g., "bar", "line", "pie", "table"
    chart_config = Column(JSON, nullable=True)  # Chart configuration
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    file = relationship("File", back_populates="queries")
