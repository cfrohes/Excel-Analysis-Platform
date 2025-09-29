import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Grid,
  Card,
  CardContent,
  IconButton,
} from '@mui/material';
import {
  Send as SendIcon,
  Refresh as RefreshIcon,
  ArrowBack as ArrowBackIcon,
  Lightbulb as LightbulbIcon,
} from '@mui/icons-material';
import { fileApi, queryApi } from '../services/api';
import { FileDetails, QueryResponse, DataResult } from '../types';
import DataVisualization from './DataVisualization';
import QueryHistory from './QueryHistory';

interface FileAnalysisProps {
  selectedFile: FileDetails | null;
  onFileSelect: (file: FileDetails) => void;
}

const FileAnalysis: React.FC<FileAnalysisProps> = ({ selectedFile, onFileSelect }) => {
  const { fileId } = useParams<{ fileId: string }>();
  const navigate = useNavigate();
  
  const [file, setFile] = useState<FileDetails | null>(selectedFile);
  const [loading, setLoading] = useState(!selectedFile);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [processingQuery, setProcessingQuery] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  useEffect(() => {
    if (fileId && !selectedFile) {
      loadFile();
    }
    if (selectedFile) {
      setFile(selectedFile);
      setLoading(false);
    }
  }, [fileId, selectedFile]);

  useEffect(() => {
    if (file) {
      loadSuggestedQuestions();
    }
  }, [file]);

  const loadFile = async () => {
    if (!fileId) return;
    
    try {
      setLoading(true);
      setError(null);
      const fileData = await fileApi.getFile(parseInt(fileId));
      setFile(fileData);
      if (onFileSelect) {
        onFileSelect(fileData);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load file');
    } finally {
      setLoading(false);
    }
  };

  const loadSuggestedQuestions = async () => {
    if (!file?.id) return;
    
    try {
      setLoadingSuggestions(true);
      const response = await queryApi.getSuggestedQuestions(file.id);
      setSuggestedQuestions(response.suggested_questions);
    } catch (err: any) {
      console.error('Failed to load suggested questions:', err);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleSubmitQuery = async () => {
    if (!query.trim() || !file?.id) return;

    try {
      setProcessingQuery(true);
      setError(null);
      
      const response = await queryApi.processQuery({
        question: query,
        file_id: file.id,
      });
      
      setQueryResult(response);
      setQuery('');
    } catch (err: any) {
      setError(err.message || 'Failed to process query');
    } finally {
      setProcessingQuery(false);
    }
  };

  const handleSuggestedQuestionClick = (question: string) => {
    setQuery(question);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmitQuery();
    }
  };

  const handleBackClick = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !file) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'File not found'}
        </Alert>
        <Button onClick={handleBackClick} startIcon={<ArrowBackIcon />}>
          Back to Home
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <IconButton onClick={handleBackClick} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4" component="h1">
            {file.filename}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Chip 
            label={file.processing_status} 
            color={file.is_processed ? 'success' : 'warning'} 
            size="small" 
          />
          <Chip label={`${file.sheets_count} sheets`} color="primary" size="small" />
          <Chip label={file.file_type} color="default" size="small" />
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Left Column - Query Interface */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Ask Questions About Your Data
            </Typography>
            
            <TextField
              fullWidth
              multiline
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask any question about your data... (e.g., 'What is the total sales?' or 'Show me the top 10 customers')"
              sx={{ mb: 2 }}
            />
            
            <Button
              variant="contained"
              onClick={handleSubmitQuery}
              disabled={!query.trim() || processingQuery}
              startIcon={processingQuery ? <CircularProgress size={20} /> : <SendIcon />}
              fullWidth
            >
              {processingQuery ? 'Processing...' : 'Ask Question'}
            </Button>
          </Paper>

          {/* Suggested Questions */}
          {suggestedQuestions.length > 0 && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <LightbulbIcon sx={{ mr: 1 }} />
                Suggested Questions
              </Typography>
              
              {loadingSuggestions ? (
                <CircularProgress size={24} />
              ) : (
                <List dense>
                  {suggestedQuestions.map((question, index) => (
                    <ListItem key={index} disablePadding>
                      <ListItemButton onClick={() => handleSuggestedQuestionClick(question)}>
                        <ListItemText 
                          primary={question}
                          sx={{ '& .MuiListItemText-primary': { fontSize: '0.9rem' } }}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              )}
            </Paper>
          )}

          {/* Query History */}
          <QueryHistory fileId={file.id} />
        </Grid>

        {/* Right Column - Results */}
        <Grid item xs={12} md={6}>
          {queryResult ? (
            <Box>
              {/* Query Response */}
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Result
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {queryResult.response}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip label={queryResult.query_type} color="primary" size="small" />
                    <Chip label={queryResult.chart_type} color="secondary" size="small" />
                    <Chip label={`${queryResult.data_result?.row_count || 0} rows`} color="default" size="small" />
                  </Box>
                </CardContent>
              </Card>

              {/* Data Visualization */}
              {queryResult.data_result && (
                <DataVisualization
                  data={queryResult.data_result}
                  chartType={queryResult.chart_type}
                  title="Data Visualization"
                />
              )}
            </Box>
          ) : (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                Ask a question about your data to see analysis results and visualizations here.
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default FileAnalysis;
