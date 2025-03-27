import React, { useState } from 'react';
import { 
  Select, 
  MenuItem, 
  Button, 
  Typography, 
  FormControl,
  InputLabel,
  Box,
  Paper,
  CircularProgress,
  Alert
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { generateReport } from '../../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface Report {
  id: string;
  title: string;
  content: string;
  generated_at: string;
}

const Reports: React.FC = () => {
  const [reportTemplate, setReportTemplate] = useState('pdf');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<Report | null>(null);

  const handleGenerateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateReport('AAPL', reportTemplate);
      setReport(result);
    } catch (err) {
      setError('Failed to generate report. Please try again.');
      console.error('Report generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = () => {
    if (report?.content) {
      const blob = new Blob([report.content], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    }
  };

  const chartData = {
    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
    datasets: [
      {
        label: 'Price Forecast',
        data: [100, 102, 101, 103, 102],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      },
      {
        label: 'Upper CI',
        data: [105, 107, 106, 108, 107],
        borderColor: 'rgba(75, 192, 192, 0.5)',
        borderDash: [5, 5],
        tension: 0.1
      },
      {
        label: 'Lower CI',
        data: [95, 97, 96, 98, 97],
        borderColor: 'rgba(75, 192, 192, 0.5)',
        borderDash: [5, 5],
        tension: 0.1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Price Forecast with Confidence Intervals'
      }
    }
  };

  return (
    <Box sx={{ p: 4, m: 2, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
      <Typography variant="h2">Report Generation and Visualization</Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, my: 2 }}>
        <FormControl fullWidth>
          <InputLabel id="report-template-label">Select Report Template</InputLabel>
          <Select
            labelId="report-template-label"
            id="report-template"
            value={reportTemplate}
            label="Select Report Template"
            onChange={(e) => setReportTemplate(e.target.value)}
          >
            <MenuItem value="pdf">PDF</MenuItem>
            <MenuItem value="html">HTML</MenuItem>
          </Select>
        </FormControl>

        <Button 
          variant="contained" 
          onClick={handleGenerateReport}
          sx={{ mt: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Generate Report'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {report && (
          <>
            <Typography variant="h3" sx={{ mt: 4 }}>Analysis Report</Typography>
            <Paper sx={{ p: 2, mt: 2 }}>
              <Typography>{report.content}</Typography>
            </Paper>

            <Typography variant="h3" sx={{ mt: 4 }}>Visualizations</Typography>
            <Paper sx={{ p: 2, mt: 2 }}>
              <Line data={chartData} options={chartOptions} />
            </Paper>

            <Button 
              variant="contained" 
              onClick={handleDownloadReport}
              sx={{ mt: 2 }}
            >
              Download Report
            </Button>
          </>
        )}
      </Box>
    </Box>
  );
};

export default Reports; 