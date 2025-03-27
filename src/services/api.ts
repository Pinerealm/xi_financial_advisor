import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FinancialData {
  date: string;
  open: number;
  close: number;
  volume: number;
}

export interface MarketAnalysis {
  trend: string;
  support: number;
  resistance: number;
  indicators: {
    rsi: number;
    macd: number;
    moving_average: number;
  };
}

export interface Report {
  id: string;
  title: string;
  content: string;
  generated_at: string;
}

export interface Prediction {
  last_price: number;
  forecast: number[];
  lower_ci: number[];
  upper_ci: number[];
  ai_recommendation: string;
}

export const fetchFinancialData = async (): Promise<FinancialData[]> => {
  const response = await api.get('/api/financial-data');
  return response.data;
};

export const analyzeMarket = async (symbol: string, timeframe: string): Promise<Prediction> => {
  const response = await api.get(`/api/market-analysis/${symbol}`, {
    params: { timeframe }
  });
  return response.data;
};

export const submitFeedback = async (feedback: { stock_symbol: string; feedback: string }) => {
  await api.post('/api/feedback', feedback);
};

export const generateReport = async (symbol: string, reportType: string): Promise<Report> => {
  const response = await api.post('/api/reports', {
    symbol,
    report_type: reportType,
  });
  return response.data;
};

export const getReports = async (): Promise<Report[]> => {
  const response = await api.get('/api/reports');
  return response.data;
};

export default api; 