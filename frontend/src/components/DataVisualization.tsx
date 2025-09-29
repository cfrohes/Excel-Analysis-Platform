import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { DataResult } from '../types';

interface DataVisualizationProps {
  data: DataResult;
  chartType?: string;
  title?: string;
}

const DataVisualization: React.FC<DataVisualizationProps> = ({
  data,
  chartType,
  title,
}) => {
  const { data: chartData, columns } = data;

  if (!chartData || chartData.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No data available for visualization
        </Typography>
      </Paper>
    );
  }

  const renderTable = () => (
    <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
      <Table stickyHeader>
        <TableHead>
          <TableRow>
            {columns.map((column, index) => (
              <TableCell key={index} sx={{ fontWeight: 'bold' }}>
                {column}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {chartData.slice(0, 100).map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {columns.map((column, colIndex) => (
                <TableCell key={colIndex}>
                  {typeof row[column] === 'number'
                    ? row[column].toLocaleString()
                    : String(row[column] || '')}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {chartData.length > 100 && (
        <Box sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Showing first 100 rows of {chartData.length} total rows
          </Typography>
        </Box>
      )}
    </TableContainer>
  );

  const renderBarChart = () => {
    // Find numeric columns for the chart
    const numericColumns = columns.filter(col => 
      chartData.some(row => typeof row[col] === 'number')
    );
    
    if (numericColumns.length === 0) {
      return renderTable();
    }

    const dataKey = numericColumns[0];
    const nameKey = columns.find(col => col !== dataKey && chartData.some(row => row[col])) || columns[0];

    return (
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData.slice(0, 20)}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey={nameKey} 
            angle={-45}
            textAnchor="end"
            height={100}
          />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={dataKey} fill="#1976d2" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const renderLineChart = () => {
    // Find numeric columns for the chart
    const numericColumns = columns.filter(col => 
      chartData.some(row => typeof row[col] === 'number')
    );
    
    if (numericColumns.length === 0) {
      return renderTable();
    }

    const dataKey = numericColumns[0];
    const nameKey = columns.find(col => col !== dataKey && chartData.some(row => row[col])) || columns[0];

    return (
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={nameKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke="#1976d2" 
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  const renderPieChart = () => {
    // Find the column with the most unique values for pie chart
    const countColumn = columns.find(col => 
      chartData.some(row => row[col] !== undefined && row[col] !== null)
    );

    if (!countColumn) {
      return renderTable();
    }

    // Count occurrences of each value
    const countMap = new Map();
    chartData.forEach(row => {
      const value = row[countColumn];
      if (value !== undefined && value !== null) {
        countMap.set(value, (countMap.get(value) || 0) + 1);
      }
    });

    const pieData = Array.from(countMap.entries()).map(([name, value]) => ({
      name: String(name),
      value: value,
    }));

    const COLORS = ['#1976d2', '#dc004e', '#2e7d32', '#f57c00', '#7b1fa2', '#d32f2f'];

    return (
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const renderChart = () => {
    const chartTypeToRender = chartType || data.chart_type || 'table';
    
    switch (chartTypeToRender) {
      case 'bar':
        return renderBarChart();
      case 'line':
        return renderLineChart();
      case 'pie':
        return renderPieChart();
      case 'table':
      default:
        return renderTable();
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      {title && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <Chip label={data.query_type} color="primary" size="small" />
            <Chip label={`${data.row_count} rows`} color="secondary" size="small" />
            {chartType && (
              <Chip label={`${chartType} chart`} color="default" size="small" />
            )}
          </Box>
        </Box>
      )}
      
      {renderChart()}
    </Paper>
  );
};

export default DataVisualization;
