import React, { useState } from 'react';
import { 
  TextField, 
  Select, 
  MenuItem, 
  Button, 
  Typography, 
  FormControl,
  InputLabel,
  Box,
  CircularProgress,
  Paper
} from '@mui/material';
import { analyzeMarket, submitFeedback } from '../../services/api';
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

const MarketAnalysis: React.FC = () => {
  const [stock, setStock] = useState('');
  const [timeframe, setTimeframe] = useState('1-week');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<any | null>(null);
  const [feedback, setFeedback] = useState('');

  const handleAnalysis = async () => {
    if (!stock) {
      setError('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await analyzeMarket(stock, timeframe);
      setPrediction(result);
    } catch (err) {
      setError('Failed to run analysis. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!feedback) {
      setError('Please provide your feedback.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await submitFeedback({ stock_symbol: stock, feedback });
      setFeedback('');
      alert('Feedback submitted successfully!');
    } catch (err) {
      setError('Failed to submit feedback. Please try again.');
      console.error('Feedback submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  const chartData: ChartData<'line'> = prediction ? {
    labels: Array.from({ length: prediction.forecast.length }, (_, i) => `Day ${i + 1}`),
    datasets: [
      {
        label: 'Predicted Price',
        data: prediction.forecast,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      },
      {
        label: 'Upper Confidence Interval',
        data: prediction.upper_ci,
        borderColor: 'rgba(75, 192, 192, 0.5)',
        borderDash: [5, 5],
        tension: 0.1
      },
      {
        label: 'Lower Confidence Interval',
        data: prediction.lower_ci,
        borderColor: 'rgba(75, 192, 192, 0.5)',
        borderDash: [5, 5],
        tension: 0.1
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
        text: 'Price Prediction and Confidence Intervals'
      }
    },
    scales: {
      y: {
        beginAtZero: false
      }
    }
  };

  return (
    <Box sx={{ p: 4, m: 2, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
      <Typography variant="h2">Market Analysis</Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, my: 2 }}>
        <TextField
          id="stock-selection"
          label="Select Stock"
          placeholder="e.g., AAPL, GOOGL, MSFT"
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          fullWidth
          error={!!error}
          helperText={error}
        />

        <FormControl fullWidth>
          <InputLabel id="timeframe-label">Select Timeframe</InputLabel>
          <Select
            labelId="timeframe-label"
            id="timeframe"
            value={timeframe}
            label="Select Timeframe"
            onChange={(e) => setTimeframe(e.target.value)}
          >
            <MenuItem value="1-week">1 Week</MenuItem>
            <MenuItem value="1-month">1 Month</MenuItem>
            <MenuItem value="3-months">3 Months</MenuItem>
          </Select>
        </FormControl>

        <Button 
          variant="contained" 
          onClick={handleAnalysis}
          sx={{ mt: 2 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Run Analysis'}
        </Button>

        {prediction && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h3" sx={{ mb: 2 }}>Results</Typography>
            
            <Typography variant="h6" sx={{ mb: 2 }}>
              Last Price: ${prediction.last_price.toFixed(2)}
            </Typography>

            <Box sx={{ height: 400, mb: 3 }}>
              <Line options={chartOptions} data={chartData} />
            </Box>

            <Typography variant="h6" sx={{ mb: 2 }}>AI Recommendation</Typography>
            <Typography paragraph>{prediction.ai_recommendation}</Typography>

            <Typography variant="h6" sx={{ mb: 2 }}>Your Feedback</Typography>
            <TextField
              id="feedback"
              label="Share your opinion"
              placeholder="What do you think about this prediction?"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              fullWidth
              multiline
              rows={4}
              sx={{ mb: 2 }}
            />

            <Button 
              variant="contained" 
              onClick={handleFeedbackSubmit}
              disabled={loading || !feedback}
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Feedback'}
            </Button>
          </Paper>
        )}
      </Box>
    </Box>
  );
};

export default MarketAnalysis; 