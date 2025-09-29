import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from sqlalchemy import create_engine, text
from app.core.config import settings

logger = logging.getLogger(__name__)


class DataAnalysisService:
    """Service for executing data analysis queries on uploaded Excel data."""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
    
    async def execute_query(
        self, 
        query_type: str,
        sql_query: Optional[str],
        file_data: Dict[str, List[Dict[str, Any]]],
        question: str,
        chart_type: str = "table"
    ) -> Dict[str, Any]:
        """
        Execute a data analysis query and return results.
        
        Args:
            query_type: Type of analysis (aggregation, filtering, etc.)
            sql_query: SQL query if applicable
            file_data: The actual data from the Excel file
            question: Original user question
            chart_type: Suggested chart type
            
        Returns:
            Dictionary containing analysis results and visualization data
        """
        try:
            if sql_query and self._is_valid_sql(sql_query):
                return await self._execute_sql_query(sql_query, file_data)
            else:
                return await self._execute_pandas_analysis(
                    query_type, file_data, question, chart_type
                )
                
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise
    
    def _is_valid_sql(self, sql_query: str) -> bool:
        """Check if SQL query is valid and safe."""
        # Basic validation - only allow SELECT statements
        sql_upper = sql_query.upper().strip()
        return (
            sql_upper.startswith('SELECT') and
            not any(keyword in sql_upper for keyword in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER'])
        )
    
    async def _execute_sql_query(self, sql_query: str, file_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Execute SQL query on the data."""
        try:
            # Convert file_data to DataFrames and create temporary tables
            for sheet_name, sheet_data in file_data.items():
                df = pd.DataFrame(sheet_data)
                table_name = f"sheet_{sheet_name.lower().replace(' ', '_').replace('-', '_')}"
                
                # Create temporary table
                df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            
            # Execute the query
            with self.engine.connect() as connection:
                result = connection.execute(text(sql_query))
                rows = result.fetchall()
                columns = result.keys()
                
                # Convert to list of dictionaries
                data = [dict(zip(columns, row)) for row in rows]
                
                return {
                    'data': data,
                    'columns': list(columns),
                    'row_count': len(data),
                    'query_type': 'sql',
                    'sql_query': sql_query
                }
                
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            raise
    
    async def _execute_pandas_analysis(
        self, 
        query_type: str, 
        file_data: Dict[str, List[Dict[str, Any]]], 
        question: str,
        chart_type: str
    ) -> Dict[str, Any]:
        """Execute analysis using pandas operations."""
        
        # For now, work with the first sheet's data
        sheet_name = list(file_data.keys())[0]
        sheet_data = file_data[sheet_name]
        df = pd.DataFrame(sheet_data)
        
        # Clean the dataframe
        df = self._clean_dataframe(df)
        
        if query_type == "aggregation":
            return await self._perform_aggregation(df, question)
        elif query_type == "comparison":
            return await self._perform_comparison(df, question)
        elif query_type == "filtering":
            return await self._perform_filtering(df, question)
        elif query_type == "trend_analysis":
            return await self._perform_trend_analysis(df, question)
        elif query_type == "distribution":
            return await self._perform_distribution_analysis(df, question)
        else:
            return await self._perform_general_analysis(df, question)
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean dataframe for analysis."""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Convert numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if not numeric_series.isna().all():
                    df[col] = numeric_series
                # Try to convert to datetime
                elif self._is_date_column(df[col]):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if a column contains date-like data."""
        if series.isna().all():
            return False
        
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        date_count = 0
        for val in sample:
            if pd.to_datetime(val, errors='coerce') is not pd.NaT:
                date_count += 1
        
        return date_count > len(sample) / 2
    
    async def _perform_aggregation(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Perform aggregation analysis."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            return {
                'data': df.head(20).to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'query_type': 'aggregation',
                'message': 'No numeric columns found for aggregation'
            }
        
        # Perform basic aggregations
        aggregations = {}
        for col in numeric_cols:
            aggregations[col] = {
                'sum': float(df[col].sum()) if not df[col].isna().all() else 0,
                'mean': float(df[col].mean()) if not df[col].isna().all() else 0,
                'min': float(df[col].min()) if not df[col].isna().all() else 0,
                'max': float(df[col].max()) if not df[col].isna().all() else 0,
                'count': int(df[col].count())
            }
        
        return {
            'data': [aggregations],
            'columns': ['metric', 'value'],
            'row_count': 1,
            'query_type': 'aggregation',
            'aggregations': aggregations,
            'chart_type': 'bar'
        }
    
    async def _perform_comparison(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Perform comparison analysis."""
        # Group by categorical columns and compare numeric columns
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not categorical_cols or not numeric_cols:
            return {
                'data': df.head(20).to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'query_type': 'comparison',
                'message': 'Need both categorical and numeric columns for comparison'
            }
        
        # Group by first categorical column
        group_col = categorical_cols[0]
        agg_col = numeric_cols[0]
        
        comparison_data = df.groupby(group_col)[agg_col].agg(['sum', 'mean', 'count']).reset_index()
        comparison_data.columns = [group_col, f'{agg_col}_sum', f'{agg_col}_mean', 'count']
        
        return {
            'data': comparison_data.to_dict('records'),
            'columns': comparison_data.columns.tolist(),
            'row_count': len(comparison_data),
            'query_type': 'comparison',
            'chart_type': 'bar'
        }
    
    async def _perform_filtering(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Perform filtering analysis."""
        # Simple filtering - show top/bottom records
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            # Sort by first numeric column
            sorted_df = df.sort_values(by=numeric_cols[0], ascending=False)
            filtered_data = sorted_df.head(20)
        else:
            filtered_data = df.head(20)
        
        return {
            'data': filtered_data.to_dict('records'),
            'columns': filtered_data.columns.tolist(),
            'row_count': len(filtered_data),
            'query_type': 'filtering',
            'chart_type': 'table'
        }
    
    async def _perform_trend_analysis(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Perform trend analysis."""
        # Look for date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not date_cols or not numeric_cols:
            return {
                'data': df.head(20).to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'query_type': 'trend_analysis',
                'message': 'Need date and numeric columns for trend analysis'
            }
        
        # Group by date and aggregate numeric columns
        date_col = date_cols[0]
        numeric_col = numeric_cols[0]
        
        trend_data = df.groupby(df[date_col].dt.date)[numeric_col].sum().reset_index()
        trend_data.columns = ['date', numeric_col]
        
        return {
            'data': trend_data.to_dict('records'),
            'columns': trend_data.columns.tolist(),
            'row_count': len(trend_data),
            'query_type': 'trend_analysis',
            'chart_type': 'line'
        }
    
    async def _perform_distribution_analysis(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Perform distribution analysis."""
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if not categorical_cols:
            return {
                'data': df.head(20).to_dict('records'),
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'query_type': 'distribution',
                'message': 'Need categorical columns for distribution analysis'
            }
        
        # Count values in first categorical column
        distribution_data = df[categorical_cols[0]].value_counts().reset_index()
        distribution_data.columns = [categorical_cols[0], 'count']
        
        # Calculate percentages
        total = distribution_data['count'].sum()
        distribution_data['percentage'] = (distribution_data['count'] / total * 100).round(2)
        
        return {
            'data': distribution_data.to_dict('records'),
            'columns': distribution_data.columns.tolist(),
            'row_count': len(distribution_data),
            'query_type': 'distribution',
            'chart_type': 'pie'
        }
    
    async def _perform_general_analysis(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """Perform general analysis - just show the data."""
        return {
            'data': df.head(50).to_dict('records'),
            'columns': df.columns.tolist(),
            'row_count': len(df.head(50)),
            'query_type': 'general',
            'chart_type': 'table'
        }
