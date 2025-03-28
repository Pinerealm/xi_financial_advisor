"""
Predictive modeling module for financial market analysis.
Provides functionality for time series forecasting using ARIMA models.
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

from core.config import settings
from core.models import StockData, ForecastData, PredictionData

# Configure logging
logger = logging.getLogger(__name__)

def determine_arima_order(data: pd.Series) -> Tuple[int, int, int]:
    """
    Determine appropriate ARIMA order using basic heuristics.
    
    Args:
        data: Time series data
        
    Returns:
        Tuple of (p,d,q) ARIMA order
    """
    # Check stationarity using ADF test
    adf_result = adf_test(data)
    
    # Determine differencing order (d)
    if adf_result['is_stationary']:
        d = 0
    else:
        # Try first differencing
        diff1 = data.diff().dropna()
        adf_result_diff1 = adf_test(diff1)
        
        if adf_result_diff1['is_stationary']:
            d = 1
        else:
            # Try second differencing
            diff2 = diff1.diff().dropna()
            d = 2
    
    # Set basic AR and MA terms
    # For financial data, starting with (1,d,1) is often reasonable
    p, q = 1, 1
    
    return (p, d, q)

def adf_test(timeseries: pd.Series) -> Dict[str, Any]:
    """
    Augmented Dickey-Fuller test for stationarity.
    
    Args:
        timeseries: Time series data
        
    Returns:
        Dictionary with test results
    """
    try:
        result = adfuller(timeseries.dropna())
        adf_stat = result[0]
        p_value = result[1]
        critical_values = result[4]
        
        is_stationary = p_value < 0.05
        
        return {
            'adf_statistic': adf_stat,
            'p_value': p_value,
            'critical_values': critical_values,
            'is_stationary': is_stationary
        }
    except Exception as e:
        logger.error(f"Error in ADF test: {str(e)}")
        # Default to non-stationary if test fails
        return {
            'is_stationary': False,
            'error': str(e)
        }

def train_arima_model(stock_data: StockData) -> Optional[PredictionData]:
    """
    Train ARIMA model and generate price forecast.
    
    Args:
        stock_data: StockData object containing historical price data
        
    Returns:
        PredictionData object with forecast results or None if model fails
    """
    try:
        # Extract the close price series
        if 'Close' not in stock_data.data.columns:
            logger.error(f"Close column not found in data for {stock_data.symbol}")
            return None
            
        ts_data = stock_data.data['Close']
        
        # Determine ARIMA order
        order = determine_arima_order(ts_data)
        logger.info(f"Determined ARIMA order for {stock_data.symbol}: {order}")
        
        # Train ARIMA model
        model = ARIMA(ts_data, order=order)
        model_fit = model.fit()
        
        # Forecast next 5 days (or as configured)
        forecast_steps = settings.FORECAST_DAYS
        forecast = model_fit.forecast(steps=forecast_steps)
        
        # Generate confidence intervals
        forecast_index = pd.date_range(
            start=ts_data.index[-1] + pd.Timedelta(days=1),
            periods=forecast_steps
        )
        
        pred_obj = model_fit.get_prediction(
            start=len(ts_data),
            end=len(ts_data) + forecast_steps - 1
        )
        
        # Get confidence intervals
        conf_int = pred_obj.conf_int(alpha=0.05)  # 95% confidence interval
        
        # Create results DataFrame
        forecast_df = pd.DataFrame({
            'forecast': forecast,
            'lower_ci': conf_int.iloc[:, 0],
            'upper_ci': conf_int.iloc[:, 1]
        }, index=forecast_index)
        
        # Replace NaN values with interpolated values
        forecast_df = forecast_df.interpolate(method='linear')
        forecast_df = forecast_df.bfill().ffill()
        
        last_price = ts_data.iloc[-1]
        
        # Return prediction data
        return PredictionData(
            symbol=stock_data.symbol,
            forecast=forecast_df,
            last_price=last_price,
            model_order=order
        )
    
    except Exception as e:
        logger.error(f"Error in ARIMA modeling for {stock_data.symbol}: {str(e)}")
        return None

def generate_predictions(stock_data_list: List[StockData]) -> List[PredictionData]:
    """
    Generate predictions for multiple stocks.
    
    Args:
        stock_data_list: List of StockData objects
        
    Returns:
        List of PredictionData objects
    """
    predictions = []
    
    for stock_data in stock_data_list:
        prediction = train_arima_model(stock_data)
        if prediction:
            predictions.append(prediction)
    
    return predictions

def prepare_prediction_response(prediction: PredictionData) -> Dict[str, Any]:
    """
    Convert PredictionData to a response format suitable for API endpoints.
    
    Args:
        prediction: PredictionData object
        
    Returns:
        Dictionary with formatted prediction data for API response
    """
    import math
    forecast_points = []
    
    for day, (idx, row) in enumerate(prediction.forecast.iterrows()):
        # Handle NaN values by replacing them with default values
        forecast = float(row["forecast"]) if not math.isnan(row["forecast"]) else 0.0
        lower_ci = float(row["lower_ci"]) if not math.isnan(row["lower_ci"]) else forecast * 0.9
        upper_ci = float(row["upper_ci"]) if not math.isnan(row["upper_ci"]) else forecast * 1.1
        
        forecast_point = {
            "day": day,
            "forecast": forecast,
            "lower_ci": lower_ci,
            "upper_ci": upper_ci
        }
        forecast_points.append(forecast_point)
    
    return {
        "symbol": prediction.symbol,
        "last_price": float(prediction.last_price),
        "forecast": forecast_points,
        "model_info": {
            "order": list(prediction.model_order)
        }
    }

def get_predictions(stock_data_list: List[StockData]) -> List[Dict[str, Any]]:
    """
    Get predictions for specified stock data.
    
    Args:
        stock_data_list: List of StockData objects
        
    Returns:
        List of formatted prediction dictionaries
    """
    # Generate predictions for all requested symbols
    predictions = generate_predictions(stock_data_list)
    
    # Convert to response format
    return [prepare_prediction_response(prediction) for prediction in predictions]