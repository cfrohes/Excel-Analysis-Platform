# Excel Data Analysis Platform

A conversational interface platform where users can upload Excel files and ask complex business questions about their data in natural language.

## Features

- **File Upload System**: Accepts any Excel file format and structure
- **Data Processing**: Handles bad/inconsistent data formatting, unnamed columns/sheets, dirty or incomplete data
- **Natural Language Queries**: AI-powered understanding of user questions about uploaded data
- **Data Visualization**: Interactive charts and tables for data insights
- **Robust Data Handling**: Processes various Excel file formats and structures

## Tech Stack

- **Frontend**: React with TypeScript
- **Backend**: Python with FastAPI
- **Database**: SQLite (can be upgraded to PostgreSQL/MySQL)
- **AI Processing**: OpenAI GPT or local LLM for natural language understanding
- **Data Processing**: Pandas, NumPy for Excel file handling
- **Visualization**: Chart.js/Recharts for frontend charts

## Project Structure

```
excel-analysis-platform/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── ...
├── backend/                  # Python backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── requirements.txt
│   └── ...
├── database/                 # Database files and migrations
└── README.md
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

### Installation

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Run the application:
   - Backend: `python -m uvicorn app.main:app --reload`
   - Frontend: `npm start`

## Usage

1. Upload an Excel file through the web interface
2. Wait for data processing to complete
3. Ask questions about your data in natural language
4. View results with interactive charts and tables

## API Documentation

The backend provides a REST API for:
- File upload and processing
- Natural language query processing
- Data retrieval and visualization
- File management

API documentation is available at `/docs` when the backend is running.
