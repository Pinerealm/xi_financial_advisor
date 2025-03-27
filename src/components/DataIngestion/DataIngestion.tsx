import React, { useState } from 'react';
import { 
  Button, 
  Typography, 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Box,
  CircularProgress,
  Alert,
  Paper
} from '@mui/material';
import { fetchFinancialData } from '../../services/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const DataIngestion: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [financialData, setFinancialData] = useState<any[]>([]);

  const handleFetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFinancialData();
      setFinancialData(data);
    } catch (err) {
      setError('Failed to fetch data. Please try again.');
      console.error('Data fetching error:', err);
    } finally {
      setLoading(false);
    }
  };

  const chartData: ChartData<'line'> = financialData.length > 0 ? {
    labels: financialData.map(d => d.date),
    datasets: [
      {
        label: 'Close Price',
        data: financialData.map(d => d.close),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      },
      {
        label: 'Volume',
        data: financialData.map(d => d.volume),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
        yAxisID: 'volume'
      }
    ]
  } : {
    labels: [],
    datasets: []
  };

  const chartOptions: ChartOptions<'line'> = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Financial Data Overview'
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Price ($)'
        }
      },
      volume: {
        beginAtZero: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Volume'
        }
      }
    }
  };

  return (
    <Box sx={{ p: 4, m: 2, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
      <Typography variant="h2">Data Ingestion</Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, my: 2 }}>
        <Button 
          variant="contained" 
          onClick={handleFetchData}
          sx={{ mt: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Fetch Data'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {financialData.length > 0 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h3" sx={{ mb: 2 }}>Data Preview</Typography>
            
            <Box sx={{ height: 400, mb: 3 }}>
              <Line options={chartOptions} data={chartData} />
            </Box>

            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Open</TableCell>
                  <TableCell>Close</TableCell>
                  <TableCell>Volume</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {financialData.map((data, index) => (
                  <TableRow key={index}>
                    <TableCell>{data.date}</TableCell>
                    <TableCell>${data.open.toFixed(2)}</TableCell>
                    <TableCell>${data.close.toFixed(2)}</TableCell>
                    <TableCell>{data.volume.toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default DataIngestion; 