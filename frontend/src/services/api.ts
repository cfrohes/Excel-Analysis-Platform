import axios from 'axios';
import {
  FileInfo,
  FileDetails,
  QueryRequest,
  QueryResponse,
  FileDataResponse,
  ApiResponse
} from '../types';

// In Vite, environment variables are available via import.meta.env
// If VITE_API_URL is not set, use a relative base so Vite's proxy forwards to the backend
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


// File API
export const fileApi = {
  uploadFile: async (file: File): Promise<ApiResponse<any>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await api.post('/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Upload failed');
    }
  },

  getFiles: async (skip = 0, limit = 100): Promise<{ files: FileInfo[]; total: number }> => {
    try {
      const response = await api.get(`/api/files?skip=${skip}&limit=${limit}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch files');
    }
  },

  getFile: async (fileId: number): Promise<FileDetails> => {
    try {
      const response = await api.get(`/api/files/${fileId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch file');
    }
  },

  getFileData: async (
    fileId: number,
    sheetName?: string,
    limit = 100
  ): Promise<FileDataResponse> => {
    try {
      const params = new URLSearchParams();
      if (sheetName) params.append('sheet_name', sheetName);
      params.append('limit', limit.toString());
      
      const response = await api.get(`/api/files/${fileId}/data?${params}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch file data');
    }
  },

  deleteFile: async (fileId: number): Promise<{ message: string }> => {
    try {
      const response = await api.delete(`/api/files/${fileId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete file');
    }
  },
};

// Query API
export const queryApi = {
  processQuery: async (request: QueryRequest): Promise<QueryResponse> => {
    try {
      const response = await api.post('/api/queries/', request);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Query processing failed');
    }
  },

  getFileQueries: async (fileId: number, skip = 0, limit = 50): Promise<{ queries: QueryResponse[]; total: number }> => {
    try {
      const response = await api.get(`/api/queries/file/${fileId}?skip=${skip}&limit=${limit}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch queries');
    }
  },

  getQuery: async (queryId: number): Promise<QueryResponse> => {
    try {
      const response = await api.get(`/api/queries/${queryId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch query');
    }
  },

  deleteQuery: async (queryId: number): Promise<{ message: string }> => {
    try {
      const response = await api.delete(`/api/queries/${queryId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete query');
    }
  },

  getSuggestedQuestions: async (fileId: number): Promise<{ suggested_questions: string[] }> => {
    try {
      const response = await api.post(`/api/queries/suggest`, { file_id: fileId });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to get suggested questions');
    }
  },
};

export default api;
