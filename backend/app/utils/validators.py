import os
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings
from app.core.exceptions import FileProcessingError


def validate_file_upload(file_path: str, file_size: int, file_type: str) -> None:
    """
    Validate uploaded file for security and format requirements.
    
    Args:
        file_path: Path to the uploaded file
        file_size: Size of the file in bytes
        file_type: File extension
        
    Raises:
        FileProcessingError: If validation fails
    """
    # Check file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise FileProcessingError(f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)")
    
    # Check file extension
    if file_type not in settings.ALLOWED_EXTENSIONS:
        raise FileProcessingError(f"File type '{file_type}' not supported. Allowed types: {settings.ALLOWED_EXTENSIONS}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileProcessingError(f"File not found: {file_path}")
    
    # Check file permissions
    if not os.access(file_path, os.R_OK):
        raise FileProcessingError(f"Cannot read file: {file_path}")


def validate_excel_structure(sheets_info: Dict[str, Any]) -> None:
    """
    Validate Excel file structure for processing.
    
    Args:
        sheets_info: Information about sheets in the Excel file
        
    Raises:
        FileProcessingError: If structure is invalid
    """
    if not sheets_info:
        raise FileProcessingError("No sheets found in the Excel file")
    
    for sheet_name, sheet_info in sheets_info.items():
        if not isinstance(sheet_info, dict):
            raise FileProcessingError(f"Invalid sheet info for '{sheet_name}'")
        
        if 'columns' not in sheet_info:
            raise FileProcessingError(f"No columns found in sheet '{sheet_name}'")
        
        if len(sheet_info['columns']) == 0:
            raise FileProcessingError(f"Sheet '{sheet_name}' has no columns")
        
        # Check for reasonable column count
        if len(sheet_info['columns']) > 1000:
            raise FileProcessingError(f"Sheet '{sheet_name}' has too many columns ({len(sheet_info['columns'])})")


def validate_query_parameters(question: str, file_id: int) -> None:
    """
    Validate query parameters.
    
    Args:
        question: Natural language question
        file_id: ID of the file to query
        
    Raises:
        ValueError: If parameters are invalid
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if len(question.strip()) < 3:
        raise ValueError("Question must be at least 3 characters long")
    
    if len(question) > 1000:
        raise ValueError("Question is too long (maximum 1000 characters)")
    
    if not isinstance(file_id, int) or file_id <= 0:
        raise ValueError("Invalid file ID")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:250] + ext
    
    return sanitized


def validate_data_for_analysis(data: Dict[str, Any]) -> None:
    """
    Validate data before analysis.
    
    Args:
        data: Data to be analyzed
        
    Raises:
        ValueError: If data is invalid
    """
    if not data:
        raise ValueError("No data provided for analysis")
    
    if 'sheets_data' not in data:
        raise ValueError("No sheets data found")
    
    sheets_data = data['sheets_data']
    if not isinstance(sheets_data, dict):
        raise ValueError("Invalid sheets data format")
    
    if len(sheets_data) == 0:
        raise ValueError("No sheets found in data")
    
    # Check each sheet
    for sheet_name, sheet_data in sheets_data.items():
        if not isinstance(sheet_data, list):
            raise ValueError(f"Invalid data format for sheet '{sheet_name}'")
        
        if len(sheet_data) == 0:
            raise ValueError(f"Sheet '{sheet_name}' contains no data")
        
        # Check for reasonable row count
        if len(sheet_data) > 100000:
            raise ValueError(f"Sheet '{sheet_name}' has too many rows ({len(sheet_data)})")


def validate_chart_config(chart_type: str, data_columns: List[str]) -> None:
    """
    Validate chart configuration against available data.
    
    Args:
        chart_type: Type of chart to create
        data_columns: Available columns in the data
        
    Raises:
        ValueError: If chart configuration is invalid
    """
    if not chart_type:
        raise ValueError("Chart type is required")
    
    valid_chart_types = ['bar', 'line', 'pie', 'scatter', 'table']
    if chart_type not in valid_chart_types:
        raise ValueError(f"Invalid chart type '{chart_type}'. Valid types: {valid_chart_types}")
    
    if not data_columns:
        raise ValueError("No data columns available for chart")
    
    # Check minimum requirements for different chart types
    if chart_type in ['bar', 'line', 'scatter'] and len(data_columns) < 2:
        raise ValueError(f"Chart type '{chart_type}' requires at least 2 data columns")
    
    if chart_type == 'pie' and len(data_columns) < 1:
        raise ValueError("Pie chart requires at least 1 data column")
