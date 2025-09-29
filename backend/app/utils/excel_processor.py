import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Handles Excel file processing, data cleaning, and schema extraction."""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.xls', '.csv']
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process an Excel file and return structured data and metadata.
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dictionary containing processed data and metadata
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.csv':
                return self._process_csv(file_path)
            else:
                return self._process_excel(file_path)
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise
    
    def _process_excel(self, file_path: str) -> Dict[str, Any]:
        """Process Excel files (.xlsx, .xls)."""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheets_data = {}
            sheets_info = {}
            
            for sheet_name in excel_file.sheet_names:
                try:
                    # Read sheet with flexible parameters
                    df = pd.read_excel(
                        file_path,
                        sheet_name=sheet_name,
                        header=None,  # Start without assuming headers
                        na_values=['', 'N/A', 'n/a', 'NULL', 'null', '#N/A', '#DIV/0!']
                    )
                    
                    # Clean and process the dataframe
                    cleaned_df = self._clean_dataframe(df, sheet_name)
                    
                    # Extract schema information
                    schema_info = self._extract_schema_info(cleaned_df, sheet_name)
                    
                    sheets_data[sheet_name] = cleaned_df.to_dict('records')
                    sheets_info[sheet_name] = schema_info
                    
                except Exception as e:
                    logger.warning(f"Error processing sheet {sheet_name}: {str(e)}")
                    continue
            
            return {
                'sheets_data': sheets_data,
                'sheets_info': sheets_info,
                'file_type': 'excel',
                'total_sheets': len(sheets_data)
            }
            
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            raise
    
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process CSV files."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        header=None,
                        na_values=['', 'N/A', 'n/a', 'NULL', 'null']
                    )
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file with any supported encoding")
            
            # Clean and process the dataframe
            cleaned_df = self._clean_dataframe(df, "Sheet1")
            
            # Extract schema information
            schema_info = self._extract_schema_info(cleaned_df, "Sheet1")
            
            return {
                'sheets_data': {"Sheet1": cleaned_df.to_dict('records')},
                'sheets_info': {"Sheet1": schema_info},
                'file_type': 'csv',
                'total_sheets': 1
            }
            
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {str(e)}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
        """Clean and standardize a dataframe."""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Handle unnamed columns
        df.columns = self._standardize_column_names(df.columns)
        
        # Try to detect header row
        df = self._detect_and_set_headers(df)
        
        # Clean data types
        df = self._clean_data_types(df)
        
        return df
    
    def _standardize_column_names(self, columns: pd.Index) -> List[str]:
        """Standardize column names."""
        new_columns = []
        unnamed_count = 1
        
        for col in columns:
            if pd.isna(col) or str(col).strip() == '' or 'Unnamed' in str(col):
                new_columns.append(f'Column_{unnamed_count}')
                unnamed_count += 1
            else:
                # Clean column name
                clean_name = str(col).strip().replace('\n', ' ').replace('\r', ' ')
                new_columns.append(clean_name)
        
        return new_columns
    
    def _detect_and_set_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect if first row contains headers and set them appropriately."""
        if len(df) == 0:
            return df
        
        # Check if first row looks like headers (mostly strings, few numeric values)
        first_row = df.iloc[0]
        string_count = sum(1 for val in first_row if isinstance(val, str))
        
        # If more than half of first row values are strings, treat as headers
        if string_count > len(first_row) / 2:
            # Set first row as headers and remove it from data
            new_columns = [str(val) if pd.notna(val) else f'Column_{i+1}' 
                          for i, val in enumerate(first_row)]
            df.columns = new_columns
            df = df.iloc[1:].reset_index(drop=True)
        
        return df
    
    def _clean_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and optimize data types."""
        for col in df.columns:
            # Try to convert to numeric
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
        
        # Sample some non-null values to check
        sample = series.dropna().head(10)
        if len(sample) == 0:
            return False
        
        date_count = 0
        for val in sample:
            if pd.to_datetime(val, errors='coerce') is not pd.NaT:
                date_count += 1
        
        return date_count > len(sample) / 2
    
    def _extract_schema_info(self, df: pd.DataFrame, sheet_name: str) -> Dict[str, Any]:
        """Extract schema information from a dataframe."""
        schema_info = {
            'sheet_name': sheet_name,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': []
        }
        
        for col in df.columns:
            col_info = {
                'name': str(col),
                'data_type': str(df[col].dtype),
                'null_count': int(df[col].isna().sum()),
                'unique_count': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(5).tolist()
            }
            
            # Add statistical info for numeric columns
            if df[col].dtype in ['int64', 'float64']:
                col_info.update({
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None
                })
            
            schema_info['columns'].append(col_info)
        
        return schema_info
    
    def generate_sql_schema(self, sheets_info: Dict[str, Any]) -> str:
        """Generate SQL schema from sheets information."""
        schema_statements = []
        
        for sheet_name, sheet_info in sheets_info.items():
            table_name = f"sheet_{sheet_name.lower().replace(' ', '_').replace('-', '_')}"
            
            columns = []
            for col_info in sheet_info['columns']:
                col_name = col_info['name'].lower().replace(' ', '_').replace('-', '_')
                data_type = self._pandas_to_sql_type(col_info['data_type'])
                columns.append(f"    {col_name} {data_type}")
            
            create_table = f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n);"
            schema_statements.append(create_table)
        
        return "\n\n".join(schema_statements)
    
    def _pandas_to_sql_type(self, pandas_type: str) -> str:
        """Convert pandas data type to SQL type."""
        type_mapping = {
            'int64': 'INTEGER',
            'float64': 'REAL',
            'bool': 'BOOLEAN',
            'datetime64[ns]': 'TIMESTAMP',
            'object': 'TEXT'
        }
        return type_mapping.get(pandas_type, 'TEXT')
