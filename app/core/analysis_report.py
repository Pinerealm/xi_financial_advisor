"""
Analysis report generation module for financial market analysis.
Utilizes GROQ LLM API to generate comprehensive market analysis reports.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import settings
from core.models import StockData

# Configure logging
logger = logging.getLogger(__name__)

def get_llm():
    """
    Initialize and return the GROQ LLM client.
    
    Returns:
        ChatGroq: GROQ LLM client
    """
    if not settings.GROQ_API_KEY:
        logger.error("GROQ API key is not set. Please set GROQ_API_KEY in the environment.")
        raise ValueError("GROQ API key is not configured. Please set GROQ_API_KEY in the environment.")
    
    # Initialize GROQ LLM client
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE
    )
    
    return llm

def prepare_market_data_prompt(stock_data_list: List[StockData], predictions_data: List[Dict[str, Any]]) -> str:
    """
    Prepare market data for the analysis prompt.
    
    Args:
        stock_data_list: List of StockData objects
        predictions_data: List of prediction data dictionaries
    
    Returns:
        Formatted market data string for the prompt
    """
    market_data = []
    
    for stock_data in stock_data_list:
        # Find corresponding prediction data
        prediction = next((p for p in predictions_data if p["symbol"] == stock_data.symbol), None)
        
        if not prediction:
            continue
        
        # Extract key financial metrics
        last_price = prediction["last_price"]
        
        # Calculate price changes
        price_data = stock_data.data["Close"]
        if len(price_data) >= 2:
            daily_change = (price_data.iloc[-1] - price_data.iloc[-2]) / price_data.iloc[-2] * 100
        else:
            daily_change = 0
            
        if len(price_data) >= 30:
            monthly_change = (price_data.iloc[-1] - price_data.iloc[-30]) / price_data.iloc[-30] * 100
        else:
            monthly_change = (price_data.iloc[-1] - price_data.iloc[0]) / price_data.iloc[0] * 100
        
        # Get company info
        name = stock_data.info.get("shortName", stock_data.info.get("longName", stock_data.symbol))
        sector = stock_data.info.get("sector", "Unknown")
        industry = stock_data.info.get("industry", "Unknown")
        
        # Get prediction data
        forecast_points = prediction.get("forecast", [])
        avg_forecast = sum(p.get("forecast", 0) for p in forecast_points) / len(forecast_points) if forecast_points else last_price
        forecast_change = (avg_forecast - last_price) / last_price * 100 if last_price else 0
        
        # Format the data
        stock_summary = {
            "symbol": stock_data.symbol,
            "name": name,
            "sector": sector,
            "industry": industry,
            "current_price": round(last_price, 2),
            "daily_change_pct": round(daily_change, 2),
            "monthly_change_pct": round(monthly_change, 2),
            "predicted_avg_price": round(avg_forecast, 2),
            "predicted_change_pct": round(forecast_change, 2),
            "trading_volume": int(stock_data.data["Volume"].mean()) if "Volume" in stock_data.data else 0,
            "forecast_details": [{
                "day": point.get("day", 0) + 1,
                "price": round(point.get("forecast", 0), 2),
                "lower_ci": round(point.get("lower_ci", 0), 2),
                "upper_ci": round(point.get("upper_ci", 0), 2)
            } for point in forecast_points]
        }
        
        market_data.append(stock_summary)
    
    return json.dumps(market_data, indent=2)

def generate_analysis_report(stock_data_list: List[StockData], predictions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a market analysis report using GROQ LLM.
    
    Args:
        stock_data_list: List of StockData objects
        predictions_data: List of prediction data dictionaries
    
    Returns:
        Dictionary with analysis report
    """
    try:
        # Get GROQ LLM client
        llm = get_llm()
        
        # Prepare market data for prompt
        market_data_str = prepare_market_data_prompt(stock_data_list, predictions_data)
        
        # Define the system prompt
        system_prompt = """
        You are FinanceGPT, an expert financial analyst specializing in stock market analysis and forecasting.
        Your task is to generate a comprehensive market analysis report based on the provided financial data and ARIMA model predictions.
        
        The report should include:
        
        1. Market Overview: Summarize the overall market trends and patterns observed in the provided stocks.
        2. Individual Stock Analysis: For each stock, provide detailed analysis including:
           - Current performance evaluation
           - Technical indicators and patterns
           - Analysis of the ARIMA model predictions
           - Potential risks and opportunities
        3. Sector Comparison: Compare performance across different sectors if applicable.
        4. Investment Recommendations: Provide strategic recommendations based on the analysis (bullish/bearish outlook).
        5. Key Metrics to Watch: Highlight important metrics investors should monitor.
        
        Use specific numbers and percentages from the data provided. The report should be well-structured, professional, 
        and provide actionable insights. Aim for approximately 500-700 words.
        
        IMPORTANT: Format your response using Markdown syntax:
        - Use # for main headings, ## for section headings, and ### for subsections
        - Use **bold** for important numbers, metrics, and trends
        - Use bullet points (- item) for lists of observations
        - Use `backticks` for specific metrics or technical terms
        - Format any tables using proper Markdown table syntax
        - Use > for insightful quotes or important takeaways
        
        This markdown formatting will be rendered on the front-end, so proper syntax is essential.
        """
        
        # Define the human prompt
        human_prompt = f"""
        Please generate a comprehensive market analysis report based on the following stock data and ARIMA model predictions.
        
        FINANCIAL DATA:
        {market_data_str}
        
        Focus on identifying key trends, technical patterns, and providing actionable investment recommendations.
        """
        
        # Generate the report
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Create report object
        report = {
            "report": response.content,
            "timestamp": datetime.now().isoformat(),
            "assets_analyzed": [stock.symbol for stock in stock_data_list],
            "time_horizon": "5-day forecast",
            "visualization_paths": []  # This would be populated if visualizations are generated
        }
        
        return report
    
    except Exception as e:
        logger.error(f"Error generating analysis report: {str(e)}")
        # Return a basic report with the error
        return {
            "report": f"Unable to generate analysis report due to an error: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "assets_analyzed": [stock.symbol for stock in stock_data_list],
            "time_horizon": "5-day forecast",
            "visualization_paths": []
        }

def generate_analysis_report_with_feedback(
    stock_data_list: List[StockData], 
    predictions_data: List[Dict[str, Any]],
    feedback: str
) -> Dict[str, Any]:
    """
    Generate a market analysis report using GROQ LLM, incorporating analyst feedback.
    
    Args:
        stock_data_list: List of StockData objects
        predictions_data: List of prediction data dictionaries
        feedback: Analyst feedback to incorporate
    
    Returns:
        Dictionary with enhanced analysis report
    """
    try:
        # Get GROQ LLM client
        llm = get_llm()
        
        # Prepare market data for prompt
        market_data_str = prepare_market_data_prompt(stock_data_list, predictions_data)
        
        # Define the system prompt
        system_prompt = """
        You are FinanceGPT, an expert financial analyst specializing in stock market analysis and forecasting.
        Your task is to generate a comprehensive market analysis report based on the provided financial data, 
        ARIMA model predictions, and expert analyst feedback.
        
        The report should include:
        
        1. Market Overview: Summarize the overall market trends and patterns observed in the provided stocks.
        2. Individual Stock Analysis: For each stock, provide detailed analysis including:
           - Current performance evaluation
           - Technical indicators and patterns
           - Analysis of the ARIMA model predictions
           - Incorporation of analyst feedback
           - Potential risks and opportunities
        3. Sector Comparison: Compare performance across different sectors if applicable.
        4. Investment Recommendations: Provide strategic recommendations based on the analysis and feedback.
        5. Key Metrics to Watch: Highlight important metrics investors should monitor.
        
        Use specific numbers and percentages from the data provided. The report should be well-structured, professional, 
        incorporate the analyst's insights thoughtfully, and provide actionable recommendations. 
        Aim for approximately 600-800 words.
        
        IMPORTANT: Format your response using Markdown syntax:
        - Use # for main headings, ## for section headings, and ### for subsections
        - Use **bold** for important numbers, metrics, and trends
        - Use bullet points (- item) for lists of observations
        - Use `backticks` for specific metrics or technical terms
        - Format any tables using proper Markdown table syntax
        - Use > for insightful quotes or important takeaways
        
        This markdown formatting will be rendered on the front-end, so proper syntax is essential.
        """
        
        # Define the human prompt
        human_prompt = f"""
        Please generate a comprehensive market analysis report based on the following stock data, ARIMA model predictions,
        and expert analyst feedback.
        
        FINANCIAL DATA:
        {market_data_str}
        
        ANALYST FEEDBACK:
        {feedback}
        
        Focus on identifying key trends, technical patterns, incorporating the analyst's insights, 
        and providing actionable investment recommendations.
        """
        
        # Generate the report
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        response = llm.invoke(messages)
        
        # Create report object
        report = {
            "report": response.content,
            "timestamp": datetime.now().isoformat(),
            "assets_analyzed": [stock.symbol for stock in stock_data_list],
            "time_horizon": "5-day forecast",
            "visualization_paths": []  # This would be populated if visualizations are generated
        }
        
        return report
    
    except Exception as e:
        logger.error(f"Error generating analysis report with feedback: {str(e)}")
        # Return a basic report with the error
        return {
            "report": f"Unable to generate analysis report due to an error: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "assets_analyzed": [stock.symbol for stock in stock_data_list],
            "time_horizon": "5-day forecast",
            "visualization_paths": []
        }