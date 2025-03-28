import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from core.analysis_workflow import run_financial_analysis, provide_analyst_feedback
from core.config import settings
from core.schemas import (
    AnalysisReport,
    AnalystFeedback,
    FinancialData,
    PredictionResult,
    StockSymbol,
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["financial"])


@router.get("/assets", response_model=List[StockSymbol])
async def get_available_assets():
    """
    Returns the list of available assets for analysis.
    """
    try:
        return [{"symbol": symbol} for symbol in settings.ASSETS]
    except Exception as e:
        logger.error(f"Error retrieving available assets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-data", response_model=List[FinancialData])
async def get_market_data(
    symbols: Optional[List[str]] = Query(None),
    time_horizon: Optional[str] = Query("6mo"),
):
    """
    Fetches market data for specified symbols.
    If no symbols are provided, uses the default assets from settings.
    
    - **symbols**: List of stock symbols to fetch (optional)
    - **time_horizon**: Time period for data retrieval (default: 6mo)
    """
    try:
        assets = symbols if symbols else settings.ASSETS
        result = run_financial_analysis(assets, time_horizon, step="data_ingestion")
        
        # Convert to FinancialData model
        financial_data = []
        for asset in result.get("raw_data", []):
            if asset:
                history_df = asset["data"]
                data_points = []
                for date, row in history_df.iterrows():
                    data_points.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "open": row["Open"],
                        "high": row["High"],
                        "low": row["Low"],
                        "close": row["Close"],
                        "volume": row["Volume"]
                    })
                
                financial_data.append({
                    "symbol": asset["symbol"],
                    "name": asset["info"].get("shortName", asset["symbol"]),
                    "sector": asset["info"].get("sector", "Unknown"),
                    "data_points": data_points
                })
                
        return financial_data
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions", response_model=List[PredictionResult])
async def get_predictions(
    symbols: Optional[List[str]] = Query(None),
    time_horizon: Optional[str] = Query("6mo"),
):
    """
    Runs the predictive modeling workflow and returns predictions.
    
    - **symbols**: List of stock symbols to fetch (optional)
    - **time_horizon**: Time period for data retrieval (default: 6mo)
    """
    try:
        assets = symbols if symbols else settings.ASSETS
        result = run_financial_analysis(assets, time_horizon, step="predictive_modeling")
        
        # Convert to PredictionResult model
        predictions = []
        for pred in result.get("predictions", []):
            if pred:
                forecast_data = []
                for idx, row in pred["forecast"].iterrows():
                    forecast_data.append({
                        "day": int(idx),
                        "forecast": float(row["Forecast"]),
                        "lower_ci": float(row["LowerCI"]),
                        "upper_ci": float(row["UpperCI"]),
                    })
                
                predictions.append({
                    "symbol": pred["symbol"],
                    "last_price": float(pred["last_price"]),
                    "forecast": forecast_data,
                    "model_info": {
                        "order": pred["model_order"]
                    }
                })
                
        return predictions
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis-report", response_model=AnalysisReport)
async def get_analysis_report(
    symbols: Optional[List[str]] = Query(None),
    time_horizon: Optional[str] = Query("6mo"),
):
    """
    Generates a comprehensive market analysis report.
    
    - **symbols**: List of stock symbols to fetch (optional)
    - **time_horizon**: Time period for data retrieval (default: 6mo)
    """
    try:
        assets = symbols if symbols else settings.ASSETS
        result = run_financial_analysis(assets, time_horizon, step="report_generation")
        
        # Extract visualization paths and report content
        visualization_paths = []
        if "visualization_paths" in result:
            visualization_paths = result["visualization_paths"]
        
        return {
            "report": result.get("analysis_report", "No report generated"),
            "timestamp": pd.Timestamp.now().isoformat(),
            "assets_analyzed": assets,
            "time_horizon": time_horizon,
            "visualization_paths": visualization_paths
        }
    except Exception as e:
        logger.error(f"Error generating analysis report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyst-feedback", response_model=AnalysisReport)
async def submit_analyst_feedback(feedback: AnalystFeedback):
    """
    Submits analyst feedback and regenerates the analysis report.
    
    - **feedback**: Feedback content from the analyst
    - **symbols**: List of stock symbols to fetch
    - **time_horizon**: Time period for data retrieval
    """
    try:
        assets = feedback.symbols if feedback.symbols else settings.ASSETS
        result = provide_analyst_feedback(
            assets, 
            feedback.time_horizon, 
            feedback.feedback_content
        )
        
        # Extract visualization paths and report content
        visualization_paths = []
        if "visualization_paths" in result:
            visualization_paths = result["visualization_paths"]
        
        return {
            "report": result.get("analysis_report", "No report generated"),
            "timestamp": pd.Timestamp.now().isoformat(),
            "assets_analyzed": assets,
            "time_horizon": feedback.time_horizon,
            "visualization_paths": visualization_paths
        }
    except Exception as e:
        logger.error(f"Error processing analyst feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualizations", response_model=List[str])
async def get_visualizations(
    symbols: Optional[List[str]] = Query(None),
    time_horizon: Optional[str] = Query("6mo"),
):
    """
    Generates and returns paths to interactive visualizations.
    
    - **symbols**: List of stock symbols to fetch (optional)
    - **time_horizon**: Time period for data retrieval (default: 6mo)
    """
    try:
        assets = symbols if symbols else settings.ASSETS
        result = run_financial_analysis(assets, time_horizon, step="visualization")
        
        return result.get("visualization_paths", [])
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
