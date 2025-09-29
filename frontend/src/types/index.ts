export interface FileInfo {
  id: number;
  filename: string;
  file_size: number;
  file_type: string;
  is_processed: boolean;
  processing_status: string;
  created_at: string;
  sheets_count: number;
}

export interface FileDetails extends FileInfo {
  processing_error?: string;
  sheets_info?: Record<string, SheetInfo>;
  columns_info?: Record<string, ColumnInfo>;
  suggested_questions?: string[];
}

export interface SheetInfo {
  sheet_name: string;
  row_count: number;
  column_count: number;
  columns: ColumnInfo[];
}

export interface ColumnInfo {
  name: string;
  data_type: string;
  null_count: number;
  unique_count: number;
  sample_values: any[];
  min?: number;
  max?: number;
  mean?: number;
}

export interface QueryRequest {
  question: string;
  file_id: number;
}

export interface QueryResponse {
  id: number;
  question: string;
  response?: string;
  query_type?: string;
  data_result?: DataResult;
  chart_type?: string;
  chart_config?: Record<string, any>;
  status: string;
  created_at: string;
}

export interface DataResult {
  data: any[];
  columns: string[];
  row_count: number;
  query_type: string;
  chart_type?: string;
  message?: string;
  aggregations?: Record<string, any>;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface FileDataResponse {
  sheet_name: string;
  data: any[];
  total_rows: number;
  available_sheets?: string[];
}
