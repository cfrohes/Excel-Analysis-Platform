#!/usr/bin/env python3
"""
Run script for the Excel Data Analysis Platform backend.
"""

import uvicorn
import os
from app.core.config import settings

if __name__ == "__main__":
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
