from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.api import files, queries
from app.core.config import settings
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    yield
    
    # Cleanup code here if needed


app = FastAPI(
    title="Excel Data Analysis Platform",
    description="A platform for analyzing Excel files with natural language queries",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API routers
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(queries.router, prefix="/api/queries", tags=["queries"])


@app.get("/")
async def root():
    return {"message": "Excel Data Analysis Platform API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
