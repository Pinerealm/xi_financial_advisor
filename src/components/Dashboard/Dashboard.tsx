import React, { useState } from 'react';
import { Button, Typography, List, ListItem, Box, CircularProgress, Alert } from '@mui/material';
import { fetchFinancialData, generateReport } from '../../services/api';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentActivity, setRecentActivity] = useState<string[]>([]);

  const handleFetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFinancialData();
      setRecentActivity([
        `Latest data fetched for ${data.length} records`,
        `Market analysis completed for ${data[0]?.date || 'N/A'}`
      ]);
    } catch (err) {
      setError('Failed to fetch latest data. Please try again.');
      console.error('Data fetching error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const report = await generateReport('AAPL', 'pdf');
      setRecentActivity(prev => [
        `New report generated: ${report.title}`,
        ...prev
      ]);
    } catch (err) {
      setError('Failed to generate report. Please try again.');
      console.error('Report generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, m: 2, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
      <Typography variant="h2">Home Dashboard</Typography>
      <Typography paragraph>
        Welcome to the system! Here you can manage your financial data and analysis.
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <Button 
          variant="contained" 
          onClick={handleFetchData}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Fetch Latest Data'}
        </Button>
        <Button 
          variant="contained" 
          onClick={handleGenerateReport}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Generate New Report'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Typography variant="h3">Recent Activity</Typography>
      <List>
        {recentActivity.map((activity, index) => (
          <ListItem key={index}>{activity}</ListItem>
        ))}
        {recentActivity.length === 0 && (
          <ListItem>No recent activity</ListItem>
        )}
      </List>
    </Box>
  );
};

export default Dashboard; 