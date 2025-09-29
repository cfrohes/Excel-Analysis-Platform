from openai import OpenAI
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
import re
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for processing natural language queries using OpenAI."""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        if not self.client:
            logger.warning("OpenAI API key not found. AI features will be limited.")
    
    async def process_query(
        self, 
        question: str, 
        file_schema: Dict[str, Any],
        sample_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language query and return structured response.
        
        Args:
            question: Natural language question about the data
            file_schema: Schema information about the uploaded file
            sample_data: Optional sample data for context
            
        Returns:
            Dictionary containing query analysis, SQL query, and visualization info
        """
        try:
            # Generate context from schema and sample data
            context = self._generate_context(file_schema, sample_data)
            
            # Process the query
            response = await self._analyze_query(question, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
    
    def _generate_context(self, file_schema: Dict[str, Any], sample_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate context string from file schema and sample data."""
        context_parts = []
        
        # Add schema information
        context_parts.append("FILE SCHEMA:")
        for sheet_name, sheet_info in file_schema.items():
            context_parts.append(f"\nSheet: {sheet_name}")
            context_parts.append(f"Rows: {sheet_info.get('row_count', 0)}")
            context_parts.append(f"Columns: {sheet_info.get('column_count', 0)}")
            
            context_parts.append("Columns:")
            for col_info in sheet_info.get('columns', []):
                col_desc = f"  - {col_info['name']} ({col_info['data_type']})"
                if col_info.get('null_count', 0) > 0:
                    col_desc += f" - {col_info['null_count']} null values"
                context_parts.append(col_desc)
                
                # Add sample values
                if col_info.get('sample_values'):
                    sample_str = ", ".join([str(v) for v in col_info['sample_values'][:3]])
                    context_parts.append(f"    Sample values: {sample_str}")
        
        # Add sample data if available
        if sample_data:
            context_parts.append("\nSAMPLE DATA:")
            for sheet_name, sheet_data in sample_data.items():
                context_parts.append(f"\n{sheet_name} (first 3 rows):")
                for i, row in enumerate(sheet_data[:3]):
                    context_parts.append(f"  Row {i+1}: {row}")
        
        return "\n".join(context_parts)
    
    async def _analyze_query(self, question: str, context: str) -> Dict[str, Any]:
        """Analyze the natural language query using OpenAI."""
        
        system_prompt = """You are an expert data analyst. Given a natural language question about data and the schema/sample data, you need to:

1. Analyze the question to understand what the user wants to know
2. Determine the query type (aggregation, filtering, comparison, etc.)
3. Generate appropriate SQL queries if needed
4. Suggest the best visualization type
5. Provide a clear, business-friendly response

Respond with a JSON object containing:
- "query_type": The type of analysis (e.g., "aggregation", "filtering", "comparison", "trend_analysis")
- "sql_query": SQL query if applicable (use table names like sheet_name for sheets)
- "chart_type": Suggested chart type ("bar", "line", "pie", "table", "scatter", "heatmap")
- "chart_config": Configuration for the chart (labels, colors, etc.)
- "explanation": Clear explanation of what the analysis shows
- "data_requirements": What specific data columns/fields are needed

If the question is too vague or unclear, ask for clarification."""

        user_prompt = f"""Context about the data:
{context}

User question: {question}

Please analyze this question and provide your response in the JSON format specified above."""

        try:
            if self.client:
                # OpenAI 1.x client
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

                content = response.choices[0].message.content or ""
                
                # Try to parse JSON response
                try:
                    result = json.loads(content)
                    return result
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a structured response
                    return self._create_fallback_response(question, content)
            else:
                # Fallback when no OpenAI API key
                return self._create_fallback_response(question, "AI service not available")
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return self._create_fallback_response(question, f"Error processing query: {str(e)}")
    
    def _create_fallback_response(self, question: str, content: str) -> Dict[str, Any]:
        """Create a fallback response when AI processing fails."""
        
        # Simple keyword-based analysis
        question_lower = question.lower()
        
        query_type = "general"
        chart_type = "table"
        
        if any(word in question_lower for word in ["sum", "total", "count", "average", "mean", "max", "min"]):
            query_type = "aggregation"
            chart_type = "bar"
        elif any(word in question_lower for word in ["compare", "comparison", "vs", "versus"]):
            query_type = "comparison"
            chart_type = "bar"
        elif any(word in question_lower for word in ["trend", "over time", "time series"]):
            query_type = "trend_analysis"
            chart_type = "line"
        elif any(word in question_lower for word in ["filter", "where", "show only"]):
            query_type = "filtering"
            chart_type = "table"
        elif any(word in question_lower for word in ["distribution", "percentage", "proportion"]):
            query_type = "distribution"
            chart_type = "pie"
        
        return {
            "query_type": query_type,
            "sql_query": None,
            "chart_type": chart_type,
            "chart_config": {},
            "explanation": content,
            "data_requirements": []
        }
    
    def extract_data_requirements(self, question: str, schema: Dict[str, Any]) -> List[str]:
        """Extract which data columns/fields are needed for the query."""
        requirements = []
        
        # Get all column names from schema
        all_columns = []
        for sheet_info in schema.values():
            for col_info in sheet_info.get('columns', []):
                all_columns.append(col_info['name'])
        
        question_lower = question.lower()
        
        # Simple keyword matching to find relevant columns
        for column in all_columns:
            column_lower = column.lower()
            if column_lower in question_lower or any(word in column_lower for word in question_lower.split()):
                requirements.append(column)
        
        return requirements[:10]  # Limit to 10 most relevant columns
    
    def suggest_questions(self, schema: Dict[str, Any]) -> List[str]:
        """Suggest sample questions based on the data schema."""
        suggestions = []
        
        # Analyze schema to generate relevant questions
        for sheet_name, sheet_info in schema.items():
            columns = [col['name'] for col in sheet_info.get('columns', [])]
            numeric_cols = [col['name'] for col in sheet_info.get('columns', []) 
                           if col['data_type'] in ['int64', 'float64']]
            
            if numeric_cols:
                suggestions.extend([
                    f"What is the total of {numeric_cols[0]}?",
                    f"What is the average {numeric_cols[0]}?",
                    f"Show me the top 10 records by {numeric_cols[0]}"
                ])
            
            if len(columns) > 1:
                suggestions.extend([
                    f"Show me all {sheet_name} data",
                    f"What are the unique values in {columns[0]}?",
                    f"How many records are in {sheet_name}?"
                ])
        
        return suggestions[:5]  # Return top 5 suggestions
