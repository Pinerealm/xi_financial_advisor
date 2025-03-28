"""
API schemas for request and response models.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class StockSymbol(BaseModel):
    """Stock symbol response model."""

    symbol: str


class DataPoint(BaseModel):
    """Financial data point."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class FinancialData(BaseModel):
    """Financial data response model."""

    symbol: str
    name: str
    sector: str = "Unknown"
    data_points: List[DataPoint]


class ForecastPoint(BaseModel):
    """Forecast data point."""

    day: int
    forecast: float
    lower_ci: float
    upper_ci: float


class PredictionResult(BaseModel):
    """Prediction result response model."""

    symbol: str
    last_price: float
    forecast: List[ForecastPoint]
    model_info: Dict[str, Any]


class AnalysisReport(BaseModel):
    """Analysis report response model."""

    report: str
    timestamp: str
    assets_analyzed: List[str]
    time_horizon: str
    visualization_paths: List[str] = []


class AnalystFeedback(BaseModel):
    """Analyst feedback request model."""

    feedback_content: str = Field(..., title="Analyst feedback content")
    symbols: Optional[List[str]] = Field(None, title="Stock symbols to analyze")
    time_horizon: str = Field("6mo", title="Time period for data retrieval")