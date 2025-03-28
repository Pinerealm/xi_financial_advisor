"""
Market data retrieval module for financial analysis.
Provides functions to fetch and process financial market data from various sources.
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
import concurrent.futures
import yfinance as yf
import pandas as pd
from datetime import datetime

from core.config import settings
from core.models import StockData

# Configure logging
logger = logging.getLogger(__name__)

def fetch_stock_data(symbol: str, period: str = "6mo") -> Optional[StockData]:
    """
    Fetch stock data for a specific symbol and time period.
    
    Args:
        symbol: Stock ticker symbol
        period: Time period for data retrieval (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
    
    Returns:
        StockData object containing the fetched data, or None if fetching fails
    """
    try:
        logger.info(f"Fetching data for {symbol} with period {period}")
        
        # Create Ticker object
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist_data = ticker.history(period=period)
        
        # Get company info
        info = ticker.info
        
        # Create StockData object
        stock_data = StockData(
            symbol=symbol,
            data=hist_data,
            info=info
        )
        
        return stock_data
    
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def fetch_multiple_stocks(symbols: List[str], period: str = "6mo") -> List[StockData]:
    """
    Fetch stock data for multiple symbols.
    
    Args:
        symbols: List of stock ticker symbols
        period: Time period for data retrieval
    
    Returns:
        List of StockData objects for successfully fetched symbols
    """
    stock_data_list = []
    
    # Use concurrent execution for faster fetching
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_symbol = {
            executor.submit(fetch_stock_data, symbol, period): symbol
            for symbol in symbols
        }
        
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                stock_data = future.result()
                if stock_data:
                    stock_data_list.append(stock_data)
                else:
                    logger.warning(f"Failed to fetch data for {symbol}")
            except Exception as e:
                logger.error(f"Exception for {symbol}: {str(e)}")
    
    return stock_data_list

def prepare_stock_data_response(stock_data: StockData) -> Dict[str, Any]:
    """
    Convert StockData to a response format suitable for API endpoints.
    
    Args:
        stock_data: StockData object
    
    Returns:
        Dictionary with formatted stock data for API response
    """
    # Extract company name from info
    name = stock_data.info.get('shortName', stock_data.info.get('longName', stock_data.symbol))
    sector = stock_data.info.get('sector', 'Unknown')
    
    # Convert DataFrame to list of data points
    data_points = []
    for idx, row in stock_data.data.iterrows():
        data_point = {
            "date": idx.strftime('%Y-%m-%d'),
            "open": float(row["Open"]) if "Open" in row else 0.0,
            "high": float(row["High"]) if "High" in row else 0.0,
            "low": float(row["Low"]) if "Low" in row else 0.0,
            "close": float(row["Close"]) if "Close" in row else 0.0,
            "volume": int(row["Volume"]) if "Volume" in row else 0
        }
        data_points.append(data_point)
    
    return {
        "symbol": stock_data.symbol,
        "name": name,
        "sector": sector,
        "data_points": data_points
    }

def get_available_assets() -> List[str]:
    """
    Get the list of available assets for analysis.
    
    Returns:
        List of stock ticker symbols
    """
    return settings.ASSETS

def get_market_data(symbols: Optional[List[str]] = None, time_horizon: str = "6mo") -> List[Dict[str, Any]]:
    """
    Get market data for specified symbols.
    
    Args:
        symbols: List of stock ticker symbols (uses default from settings if None)
        time_horizon: Time period for data retrieval
    
    Returns:
        List of formatted stock data dictionaries
    """
    if symbols is None:
        symbols = settings.ASSETS
    
    # Fetch data for all requested symbols
    stock_data_list = fetch_multiple_stocks(symbols, time_horizon)
    
    # Convert to response format
    return [prepare_stock_data_response(stock_data) for stock_data in stock_data_list]