"""
Configuration settings for the financial analysis system.
"""

import os
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application information
    APP_NAME: str = "Financial Market Analysis and Reporting System"
    APP_DESCRIPTION: str = "A modular system for analyzing financial markets and generating reports"
    APP_VERSION: str = "1.0.0"
    
    # Market data settings
    ASSETS: List[str] = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    TIME_HORIZON: str = "6mo"
    FORECAST_DAYS: int = 5
    
    # LLM settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-8b-8192")
    LLM_TEMPERATURE: float = 0.5
    
    # Cache settings
    CACHE_EXPIRATION: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a settings instance
settings = Settings()