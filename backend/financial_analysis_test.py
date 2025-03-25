import concurrent.futures
import os
from typing import TypedDict, List, Dict, Any
import warnings

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
import numpy as np
import pandas as pd

import plotly.graph_objs as plt
import plotly.io as pio

# from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import yfinance as yf


load_dotenv()
warnings.filterwarnings("ignore")


# Configuration and Environment Setup
class FinancialAnalysisConfig:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = "gpt-4o-mini"
    ASSETS = ["AAPL", "GOOGL", "MSFT"]
    TIME_HORIZON = "6mo"


class FinancialAnalysisState(TypedDict):
    raw_data: List[Dict[str, Any]]
    processed_data: pd.DataFrame
    predictions: Dict[str, Any]
    analysis_report: str
    visualization_paths: List[str]
    analyst_feedback: str


llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


class FinancialDataIngestionNode:
    @staticmethod
    def fetch_financial_data(assets: List[str], time_horizon: str):
        """
        Fetch financial data for multiple assets using concurrent execution

        Args:
            assets (List[str]): List of stock ticker symbols
            time_horizon (str): Time period for data retrieval

        Returns:
            List of financial data dictionaries
        """

        def fetch_single_asset(asset):
            try:
                stock = yf.Ticker(asset)
                history = stock.history(period=time_horizon)
                return {"symbol": asset, "data": history, "info": stock.info}
            except Exception as e:
                print(f"Error fetching data for {asset}: {e}")
                return None

        # Use concurrent futures for parallel data fetching
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_single_asset, asset) for asset in assets]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        return [result for result in results if result is not None]


class DataPreprocessingNode:
    @staticmethod
    def preprocess_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Preprocess and consolidate financial data

        Args:
            raw_data (List[Dict]): Raw financial data from multiple assets

        Returns:
            Processed DataFrame
        """
        processed_frames = []
        for asset_data in raw_data:
            df = asset_data["data"]
            df["Symbol"] = asset_data["symbol"]
            processed_frames.append(df)

        combined_df = pd.concat(processed_frames)
        combined_df.reset_index(inplace=True)

        # Feature engineering
        combined_df["Returns"] = combined_df.groupby("Symbol")["Close"].pct_change()
        combined_df["RollingVolatility"] = (
            combined_df.groupby("Symbol")["Returns"]
            .rolling(window=5)
            .std()
            .reset_index(0, drop=True)
        )

        return combined_df


class PredictiveModelingNode:
    @staticmethod
    def determine_arima_order(data):
        """
        Determine appropriate ARIMA order using basic heuristics

        Args:
            data (pd.Series): Time series data

        Returns:
            Tuple of (p,d,q) ARIMA order
        """

        # Test for stationarity
        def adf_test(timeseries):
            dftest = adfuller(timeseries, autolag="AIC")
            return dftest[1] <= 0.05

        # Determine differencing
        d = 0
        series = data.copy()
        while not adf_test(series) and d < 2:
            d += 1
            series = np.diff(series)

        # Simple order selection (can be more sophisticated)
        return (1, d, 1)  # Basic (1,d,1) model

    @staticmethod
    def train_arima_model(data: pd.DataFrame, symbol: str):
        """
        Train ARIMA model for price prediction

        Args:
            data (pd.DataFrame): Processed financial data
            symbol (str): Stock symbol

        Returns:
            Prediction dictionary or None
        """
        # Filter data for specific symbol and use closing prices
        symbol_data = data[data["Symbol"] == symbol]["Close"].copy()

        # Ensure we have sufficient data
        if len(symbol_data) < 30:  # Minimum recommended for ARIMA
            print(f"Insufficient data for {symbol}. Require at least 30 data points.")
            return None

        try:
            # Remove any NaN values and reset index
            symbol_data = symbol_data.dropna().reset_index(drop=True)

            # Determine appropriate ARIMA order
            order = PredictiveModelingNode.determine_arima_order(symbol_data)

            # Fit ARIMA model
            model = ARIMA(symbol_data, order=order)
            model_fit = model.fit()

            # Forecast next week's prices
            forecast_steps = 5
            forecast = model_fit.forecast(steps=forecast_steps)

            # Calculate confidence intervals
            conf_int = model_fit.get_forecast(steps=forecast_steps).conf_int()

            # Create forecast DataFrame
            forecast_df = pd.DataFrame(
                {
                    "Forecast": forecast,
                    "LowerCI": conf_int.iloc[:, 0],
                    "UpperCI": conf_int.iloc[:, 1],
                }
            )

            return {
                "symbol": symbol,
                "forecast": forecast_df,
                "last_price": symbol_data.iloc[-1],
                "model_order": order,
            }

        except Exception as e:
            print(f"ARIMA modeling error for {symbol}: {e}")
            import traceback

            traceback.print_exc()
            return None


class ReportGenerationNode:
    @staticmethod
    def generate_market_report(predictions: List[Dict], llm):
        """
        Generate market analysis report using LLM

        Args:
            predictions (List[Dict]): Predictions for multiple assets
            llm: Language model for report generation

        Returns:
            Generated market analysis report
        """
        report_context = "\n".join(
            [
                f"Symbol: {pred['symbol']}\n"
                f"Last Price: ${pred['last_price']:.2f}\n"
                f"5-Day Forecast: {pred['forecast']['Forecast'].mean():.2f}\n"
                f"Forecast Confidence Interval: [{pred['forecast']['LowerCI'].mean():.2f}, {pred['forecast']['UpperCI'].mean():.2f}]"
                for pred in predictions
                if pred
            ]
        )

        prompt = f"""
        Analyze the following market predictions and provide a comprehensive investment insight:
        
        {report_context}
        
        Based on these predictions, provide:
        1. Overall market sentiment
        2. Potential investment strategies
        3. Risk assessment
        4. Short-term market outlook
        """

        return llm.invoke(prompt).content


class VisualizationNode:
    @staticmethod
    def create_forecast_visualization(predictions: List[Dict]):
        """
        Create interactive forecast visualizations

        Args:
            predictions (List[Dict]): Predictions for multiple assets

        Returns:
            List of visualization file paths
        """
        visualization_paths = []

        for pred in predictions:
            if pred:
                fig = plt.Figure()
                fig.add_trace(
                    plt.Scatter(
                        x=pred["forecast"].index,
                        y=pred["forecast"]["Forecast"],
                        mode="lines+markers",
                        name=f"{pred['symbol']} Forecast",
                    )
                )

                fig.add_trace(
                    plt.Scatter(
                        x=pred["forecast"].index,
                        y=pred["forecast"]["LowerCI"],
                        mode="lines",
                        line=dict(dash="dot"),
                        name="Lower Confidence Interval",
                    )
                )

                fig.add_trace(
                    plt.Scatter(
                        x=pred["forecast"].index,
                        y=pred["forecast"]["UpperCI"],
                        mode="lines",
                        line=dict(dash="dot"),
                        name="Upper Confidence Interval",
                    )
                )

                fig.update_layout(title=f'{pred["symbol"]} Price Forecast')

                # path = f'/tmp/{pred["symbol"]}_forecast.html'
                path = f'{pred["symbol"]}_forecast.html'
                pio.write_html(fig, file=path)
                visualization_paths.append(path)

        return visualization_paths


def build_financial_analysis_workflow():
    """
    Construct the LangGraph workflow for financial analysis
    """
    workflow = StateGraph(FinancialAnalysisState)

    # Define nodes
    workflow.add_node(
        "data_ingestion",
        lambda state: {
            **state,
            "raw_data": FinancialDataIngestionNode.fetch_financial_data(
                FinancialAnalysisConfig.ASSETS, FinancialAnalysisConfig.TIME_HORIZON
            ),
        },
    )

    workflow.add_node(
        "data_preprocessing",
        lambda state: {
            **state,
            "processed_data": DataPreprocessingNode.preprocess_data(state["raw_data"]),
        },
    )

    workflow.add_node(
        "predictive_modeling",
        lambda state: {
            **state,
            "predictions": [
                PredictiveModelingNode.train_arima_model(
                    state["processed_data"], symbol
                )
                for symbol in FinancialAnalysisConfig.ASSETS
            ],
        },
    )

    workflow.add_node(
        "report_generation",
        lambda state: {
            **state,
            "analysis_report": ReportGenerationNode.generate_market_report(
                state["predictions"], llm
            ),
        },
    )

    workflow.add_node(
        "visualization",
        lambda state: {
            **state,
            "visualization_paths": VisualizationNode.create_forecast_visualization(
                state["predictions"]
            ),
        },
    )

    # Define edges
    workflow.add_edge("data_ingestion", "data_preprocessing")
    workflow.add_edge("data_preprocessing", "predictive_modeling")
    workflow.add_edge("predictive_modeling", "report_generation")
    workflow.add_edge("report_generation", "visualization")
    workflow.add_edge("visualization", END)

    # Set starting point
    workflow.set_entry_point("data_ingestion")

    return workflow.compile()


# Execution
def run_financial_analysis():
    financial_workflow = build_financial_analysis_workflow()
    initial_state = {
        "raw_data": [],
        "processed_data": None,
        "predictions": [],
        "analysis_report": "",
        "visualization_paths": [],
        "analyst_feedback": "",
    }

    result = financial_workflow.invoke(initial_state)
    print("Financial Analysis Report:")
    print(result["analysis_report"])
    print("\nVisualization Paths:", result["visualization_paths"])


# Main execution
if __name__ == "__main__":
    run_financial_analysis()
