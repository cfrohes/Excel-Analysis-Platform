import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert, Paper, TextField, Button, Stack } from '@mui/material';
import { fileApi } from '../services/api';
import { queryApi } from '../services/api';
import QueryHistory from './QueryHistory';

const FilePage: React.FC = () => {
  const { id } = useParams();
  const fileId = Number(id);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [asking, setAsking] = useState<boolean>(false);

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const details = await fileApi.getFile(fileId);
        setFileName(details.filename);
      } catch (e: any) {
        setError(e.message || 'Failed to load file');
      } finally {
        setLoading(false);
      }
    };
    if (!isNaN(fileId)) load();
  }, [fileId]);

  if (isNaN(fileId)) {
    return <Alert severity="error">Invalid file id.</Alert>;
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 2 }}>{fileName}</Typography>
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
          <TextField
            fullWidth
            label="Ask a question about this file"
            placeholder="e.g., Total sales by month in 2024"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <Button
            variant="contained"
            disabled={!question.trim() || asking}
            onClick={async () => {
              try {
                setAsking(true);
                setError(null);
                await queryApi.processQuery({ question: question.trim(), file_id: fileId });
                setQuestion('');
              } catch (e: any) {
                setError(e.message || 'Failed to run query');
              } finally {
                setAsking(false);
              }
            }}
          >
            {asking ? 'Asking…' : 'Ask'}
          </Button>
        </Stack>
      </Paper>
      <QueryHistory fileId={fileId} />
    </Box>
  );
};

export default FilePage;


