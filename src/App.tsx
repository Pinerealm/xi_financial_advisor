import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme.ts';
import Layout from './components/Layout/Layout.tsx';
import Dashboard from './components/Dashboard/Dashboard.tsx';
import DataIngestion from './components/DataIngestion/DataIngestion.tsx';
import MarketAnalysis from './components/MarketAnalysis/MarketAnalysis.tsx';
import Reports from './components/Reports/Reports.tsx';

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/data-ingestion" element={<DataIngestion />} />
              <Route path="/market-analysis" element={<MarketAnalysis />} />
              <Route path="/reports" element={<Reports />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App; 