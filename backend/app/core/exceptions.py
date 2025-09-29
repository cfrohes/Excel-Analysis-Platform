from fastapi import HTTPException, status


class ExcelAnalysisException(Exception):
    """Base exception for Excel analysis platform."""
    pass


class FileProcessingError(ExcelAnalysisException):
    """Raised when file processing fails."""
    pass


class QueryProcessingError(ExcelAnalysisException):
    """Raised when query processing fails."""
    pass


class DataAnalysisError(ExcelAnalysisException):
    """Raised when data analysis fails."""
    pass


def handle_file_processing_error(error: Exception) -> HTTPException:
    """Convert file processing errors to HTTP exceptions."""
    if isinstance(error, FileProcessingError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File processing error: {str(error)}"
        )
    elif isinstance(error, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file format: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File processing failed: {str(error)}"
        )


def handle_query_processing_error(error: Exception) -> HTTPException:
    """Convert query processing errors to HTTP exceptions."""
    if isinstance(error, QueryProcessingError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query processing error: {str(error)}"
        )
    elif isinstance(error, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(error)}"
        )


def handle_data_analysis_error(error: Exception) -> HTTPException:
    """Convert data analysis errors to HTTP exceptions."""
    if isinstance(error, DataAnalysisError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data analysis error: {str(error)}"
        )
    elif isinstance(error, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid analysis parameters: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data analysis failed: {str(error)}"
        )
