"""
Data models for the financial analysis system.
"""

from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
from pydantic import BaseModel, Field


class StockData(BaseModel):
    """Stock market data for a specific symbol."""
    
    symbol: str
    data: pd.DataFrame
    info: Dict
    
    class Config:
        arbitrary_types_allowed = True


class ForecastData(BaseModel):
    """Forecast data with confidence intervals."""
    
    forecast: pd.DataFrame
    model_order: Tuple[int, int, int]
    
    class Config:
        arbitrary_types_allowed = True


class PredictionData(BaseModel):
    """Prediction data for a specific symbol."""
    
    symbol: str
    forecast: pd.DataFrame
    last_price: float
    model_order: Tuple[int, int, int]
    
    class Config:
        arbitrary_types_allowed = True


class AnalysisData(BaseModel):
    """Complete analysis data including raw data, processed data, predictions, and reports."""
    
    raw_data: List[StockData]
    processed_data: Optional[pd.DataFrame] = None
    predictions: Optional[List[PredictionData]] = None
    analysis_report: Optional[str] = None
    visualization_paths: Optional[List[str]] = None
    analyst_feedback: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True