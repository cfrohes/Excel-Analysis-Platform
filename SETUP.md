# Excel Data Analysis Platform - Setup Guide

This guide will help you set up and run the Excel Data Analysis Platform on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd excel-analysis-platform
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy env.example .env
# On macOS/Linux:
cp env.example .env

# Edit .env file with your configuration
# At minimum, set your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# OpenAI API Configuration (Required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./excel_analysis.db

# Application Settings
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Settings
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=./uploads
```

### OpenAI API Key Setup

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Features Overview

### Core Features

1. **File Upload System**
   - Supports .xlsx, .xls, and .csv files
   - Handles files up to 50MB
   - Automatic data cleaning and processing

2. **Natural Language Queries**
   - Ask questions in plain English
   - AI-powered query understanding
   - Automatic chart type suggestions

3. **Data Visualization**
   - Interactive charts (bar, line, pie, scatter)
   - Data tables with pagination
   - Responsive design

4. **Robust Data Handling**
   - Handles inconsistent data formatting
   - Processes unnamed columns/sheets
   - Cleans dirty or incomplete data
   - Supports various Excel file structures

### Supported Query Types

- **Aggregation**: "What is the total sales?"
- **Comparison**: "Compare sales by region"
- **Filtering**: "Show me customers from New York"
- **Trend Analysis**: "Show sales trends over time"
- **Distribution**: "What percentage of sales comes from each product?"

## Usage Examples

### 1. Upload a File

1. Go to http://localhost:3000
2. Drag and drop an Excel file or click to select
3. Wait for processing to complete

### 2. Ask Questions

Try these example questions with your data:

- "What is the total revenue?"
- "Show me the top 10 customers by sales"
- "What is the average order value?"
- "Compare sales by month"
- "Which products are selling best?"
- "Show me sales trends over the last quarter"

### 3. View Results

- Results are displayed with appropriate charts
- Click on chart elements for more details
- Use the query history to revisit previous questions

## Troubleshooting

### Common Issues

**1. Backend won't start**
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify the virtual environment is activated

**2. Frontend won't start**
- Ensure Node.js 16+ is installed
- Install dependencies: `npm install`
- Check for port conflicts (default ports: 3000 for frontend, 8000 for backend)

**3. File upload fails**
- Check file size (max 50MB)
- Ensure file format is supported (.xlsx, .xls, .csv)
- Verify file is not corrupted

**4. AI queries don't work**
- Check OpenAI API key is set correctly in `.env`
- Verify API key has sufficient credits
- Check internet connection

**5. Database errors**
- Ensure the uploads directory exists and is writable
- Check database permissions
- Try deleting the database file to reset: `rm excel_analysis.db`

### Logs and Debugging

**Backend logs:**
- Check the terminal where you ran `uvicorn`
- Logs include file processing and query execution details

**Frontend logs:**
- Open browser Developer Tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API call failures

## Development

### Project Structure

```
excel-analysis-platform/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   └── package.json       # Node.js dependencies
└── README.md              # Project documentation
```

### Adding New Features

1. **Backend**: Add new endpoints in `backend/app/api/`
2. **Frontend**: Add new components in `frontend/src/components/`
3. **Database**: Modify models in `backend/app/models/`

### Testing

**Backend tests:**
```bash
cd backend
python -m pytest
```

**Frontend tests:**
```bash
cd frontend
npm test
```

## Deployment

### Production Considerations

1. **Security**:
   - Change default SECRET_KEY
   - Use environment variables for sensitive data
   - Enable HTTPS

2. **Database**:
   - Use PostgreSQL or MySQL for production
   - Set up database backups
   - Configure connection pooling

3. **File Storage**:
   - Use cloud storage (AWS S3, Google Cloud Storage)
   - Implement file cleanup policies
   - Add virus scanning

4. **Scaling**:
   - Use a reverse proxy (nginx)
   - Set up load balancing
   - Consider containerization (Docker)

### Docker Deployment

```dockerfile
# Example Dockerfile for backend
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are installed correctly
4. Verify your OpenAI API key is valid and has credits

For additional help, please refer to the project documentation or create an issue in the repository.
