import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  History as HistoryIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { queryApi } from '../services/api';
import { QueryResponse } from '../types';

interface QueryHistoryProps {
  fileId: number;
  onQuerySelect?: (query: QueryResponse) => void;
}

const QueryHistory: React.FC<QueryHistoryProps> = ({ fileId, onQuerySelect }) => {
  const [queries, setQueries] = useState<QueryResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [queryToDelete, setQueryToDelete] = useState<QueryResponse | null>(null);

  const fetchQueries = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await queryApi.getFileQueries(fileId, 0, 20);
      setQueries(response.queries);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch query history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueries();
  }, [fileId]);

  const handleDeleteClick = (query: QueryResponse) => {
    setQueryToDelete(query);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!queryToDelete) return;

    try {
      await queryApi.deleteQuery(queryToDelete.id);
      setQueries(queries.filter(q => q.id !== queryToDelete.id));
      setDeleteDialogOpen(false);
      setQueryToDelete(null);
    } catch (err: any) {
      setError(err.message || 'Failed to delete query');
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setQueryToDelete(null);
  };

  const handleQueryClick = (query: QueryResponse) => {
    if (onQuerySelect) {
      onQuerySelect(query);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography component="div" variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
          <HistoryIcon sx={{ mr: 1 }} />
          Query History
        </Typography>
        <Button
          size="small"
          startIcon={<RefreshIcon />}
          onClick={fetchQueries}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      ) : queries.length === 0 ? (
        <Typography component="div" variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
          No queries yet. Ask your first question to see the history here.
        </Typography>
      ) : (
        <List dense>
          {queries.map((query) => (
            <ListItem
              key={query.id}
              divider
              sx={{
                cursor: onQuerySelect ? 'pointer' : 'default',
                '&:hover': onQuerySelect ? { backgroundColor: 'action.hover' } : {},
              }}
              onClick={() => handleQueryClick(query)}
            >
              <ListItemText
                primaryTypographyProps={{ component: 'div' }}
                secondaryTypographyProps={{ component: 'div' }}
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography component="span" variant="subtitle2" sx={{ flexGrow: 1 }}>
                      {truncateText(query.question)}
                    </Typography>
                    <Chip
                      label={query.status}
                      color={getStatusColor(query.status) as any}
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography component="span" variant="body2" color="text.secondary">
                      {formatDate(query.created_at)}
                      {query.query_type && ` • ${query.query_type}`}
                      {query.chart_type && ` • ${query.chart_type} chart`}
                    </Typography>
                    {query.response && (
                      <Typography component="div" variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {truncateText(query.response, 80)}
                      </Typography>
                    )}
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteClick(query);
                  }}
                  size="small"
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      )}

      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">
          Delete Query
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete this query? This action cannot be undone.
          </DialogContentText>
          {queryToDelete && (
            <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
              "{queryToDelete.question}"
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default QueryHistory;
