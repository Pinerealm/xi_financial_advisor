from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from pydantic import BaseModel
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/v1/chat/completions"

class FinancialData(BaseModel):
    date: str
    open: float
    close: float
    volume: int

class PredictionResponse(BaseModel):
    last_price: float
    forecast: List[float]
    lower_ci: List[float]
    upper_ci: List[float]
    ai_recommendation: str

class FeedbackRequest(BaseModel):
    stock_symbol: str
    feedback: str

@app.get("/")
async def read_root():
    return {"message": "Financial Market Analysis API"}

@app.get("/api/financial-data", response_model=List[FinancialData])
async def get_financial_data():
    # Dummy data for the last 6 months
    data = [
        {"date": "2023-01-01", "open": 100.0, "close": 110.0, "volume": 1000},
        {"date": "2023-02-01", "open": 105.0, "close": 115.0, "volume": 1500},
        {"date": "2023-03-01", "open": 110.0, "close": 120.0, "volume": 2000},
        {"date": "2023-04-01", "open": 115.0, "close": 125.0, "volume": 2500},
        {"date": "2023-05-01", "open": 120.0, "close": 130.0, "volume": 3000},
        {"date": "2023-06-01", "open": 125.0, "close": 135.0, "volume": 3500},
    ]
    return data

@app.get("/api/market-analysis/{symbol}", response_model=PredictionResponse)
async def run_analysis(symbol: str, timeframe: str):
    # Dummy data for demonstration purposes
    # In a real application, you would fetch historical data for the stock symbol
    historical_data = np.random.rand(100) * 100  # Simulated historical prices
    model = ARIMA(historical_data, order=(5, 1, 0))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=5)
    last_price = historical_data[-1]
    lower_ci = forecast - 5  # Dummy confidence intervals
    upper_ci = forecast + 5

    # Generate AI recommendation using Groq
    prompt = f"Based on the following stock data for {symbol}: Last price: ${last_price:.2f}, Forecast: {[f'${x:.2f}' for x in forecast]}, provide a brief investment recommendation."
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        ai_recommendation = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        ai_recommendation = "Unable to generate AI recommendation at this time."

    return {
        "last_price": last_price,
        "forecast": forecast.tolist(),
        "lower_ci": lower_ci.tolist(),
        "upper_ci": upper_ci.tolist(),
        "ai_recommendation": ai_recommendation
    }

@app.post("/api/feedback")
async def submit_feedback(feedback_request: FeedbackRequest):
    # Send feedback to Groq for analysis
    prompt = f"Analyze the following feedback for {feedback_request.stock_symbol}: {feedback_request.feedback}"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        analysis = response.json()["choices"][0]["message"]["content"]
        print(f"Feedback analysis for {feedback_request.stock_symbol}: {analysis}")
    except Exception as e:
        print(f"Error analyzing feedback: {str(e)}")
    
    return {"message": "Feedback submitted successfully"} 