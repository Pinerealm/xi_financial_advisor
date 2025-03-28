"""
Visualization module for financial market analysis.
Provides functionality to generate interactive visualizations of market data and predictions.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import math
import numpy as np
import pandas as pd

import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from core.models import StockData

# Configure logging
logger = logging.getLogger(__name__)

# Configure the static directory for visualizations
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
VIZ_DIR = os.path.join(STATIC_DIR, 'visualizations')

# Ensure the visualizations directory exists
os.makedirs(VIZ_DIR, exist_ok=True)

# Color palette for consistent styling
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#1E88E5',
    'success': '#26A69A',
    'warning': '#FFC107',
    'danger': '#EF5350',
    'info': '#42A5F5',
    'background': '#121212',
    'text': '#FFFFFF',
    'grid': '#333333',
    'positive': '#4CAF50',
    'negative': '#F44336',
    'neutral': '#9E9E9E',
}

# Custom theme for all visualizations
PLOTLY_TEMPLATE = go.layout.Template(
    layout=dict(
        font=dict(family="Arial, sans-serif", size=12, color=COLORS['text']),
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        colorway=[COLORS['info'], COLORS['success'], COLORS['warning'], 
                  COLORS['danger'], COLORS['secondary'], COLORS['primary']],
        xaxis=dict(
            gridcolor=COLORS['grid'],
            linecolor=COLORS['grid'],
            showline=True,
            showgrid=True,
            zeroline=False,
            title=dict(font=dict(size=14))
        ),
        yaxis=dict(
            gridcolor=COLORS['grid'],
            linecolor=COLORS['grid'],
            showline=True,
            showgrid=True,
            zeroline=False,
            title=dict(font=dict(size=14))
        ),
        legend=dict(
            font=dict(size=12, color=COLORS['text']),
            bordercolor=COLORS['grid'],
            borderwidth=1
        ),
        title=dict(
            font=dict(size=18, color=COLORS['text'])
        ),
        margin=dict(l=60, r=40, b=50, t=80),
        hoverlabel=dict(
            font=dict(family="Arial, sans-serif", size=12, color=COLORS['text']),
            bordercolor=COLORS['grid']
        ),
        annotations=[
            dict(
                text="Financial Market Analysis System",
                showarrow=False,
                xref="paper", 
                yref="paper",
                x=0.01, 
                y=0.01,
                font=dict(size=10, color=COLORS['grid'])
            )
        ]
    )
)

# Set default template
pio.templates["custom_dark"] = PLOTLY_TEMPLATE
pio.templates.default = "custom_dark"

def create_historical_price_chart(stock_data: StockData) -> str:
    """
    Create an interactive chart of historical stock prices with advanced indicators.
    
    Args:
        stock_data: StockData object
        
    Returns:
        Path to the generated visualization file
    """
    try:
        # Create figure with subplots
        fig = make_subplots(
            rows=3, 
            cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(
                "Price & Moving Averages", 
                "Volume", 
                "Relative Strength Index"
            )
        )
        
        # Calculate moving averages
        data = stock_data.data.copy()
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        
        # Calculate RSI
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # Add price candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="OHLC",
                increasing_line=dict(color=COLORS['positive']),
                decreasing_line=dict(color=COLORS['negative'])
            ),
            row=1, col=1
        )
        
        # Add moving average lines
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA20'],
                name="20-Day MA",
                line=dict(color=COLORS['info'], width=1.5)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA50'],
                name="50-Day MA",
                line=dict(color=COLORS['warning'], width=1.5)
            ),
            row=1, col=1
        )
        
        # Add volume chart
        colors = [COLORS['positive'] if data['Close'].iloc[i] > data['Close'].iloc[i-1] 
                  else COLORS['negative'] for i in range(1, len(data))]
        colors.insert(0, COLORS['neutral'])  # For the first bar
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name="Volume",
                marker=dict(color=colors, opacity=0.7),
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Add RSI
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI'],
                name="RSI (14)",
                line=dict(color=COLORS['secondary'], width=1.5)
            ),
            row=3, col=1
        )
        
        # Add RSI reference lines (30 and 70)
        fig.add_trace(
            go.Scatter(
                x=[data.index[0], data.index[-1]],
                y=[30, 30],
                mode="lines",
                line=dict(color=COLORS['grid'], width=1, dash="dash"),
                showlegend=False
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=[data.index[0], data.index[-1]],
                y=[70, 70],
                mode="lines",
                line=dict(color=COLORS['grid'], width=1, dash="dash"),
                showlegend=False
            ),
            row=3, col=1
        )
        
        # Update layout
        name = stock_data.info.get('shortName', stock_data.info.get('longName', stock_data.symbol))
        
        # Add range slider
        fig.update_layout(
            title=f'{name} ({stock_data.symbol}) Technical Analysis',
            height=800,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis_rangeslider_visible=False,
            yaxis=dict(title='Price ($)'),
            yaxis2=dict(title='Volume'),
            yaxis3=dict(title='RSI', range=[0, 100])
        )
        
        # Add buttons for time range selection
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    buttons=[
                        dict(
                            label="All Data",
                            method="relayout",
                            args=[{"xaxis.range": [data.index[0], data.index[-1]]}]
                        ),
                        dict(
                            label="YTD",
                            method="relayout",
                            args=[{"xaxis.range": [datetime(data.index[-1].year, 1, 1), data.index[-1]]}]
                        ),
                        dict(
                            label="6 Months",
                            method="relayout",
                            args=[{"xaxis.range": [data.index[-1] - timedelta(days=180), data.index[-1]]}]
                        ),
                        dict(
                            label="3 Months",
                            method="relayout",
                            args=[{"xaxis.range": [data.index[-1] - timedelta(days=90), data.index[-1]]}]
                        ),
                        dict(
                            label="1 Month",
                            method="relayout",
                            args=[{"xaxis.range": [data.index[-1] - timedelta(days=30), data.index[-1]]}]
                        ),
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.05,
                    xanchor="left",
                    y=1.15,
                    yanchor="top"
                )
            ]
        )
        
        # Add annotations for current price and change
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2]
        price_change = current_price - previous_price
        price_change_pct = (price_change / previous_price) * 100
        
        fig.add_annotation(
            x=0.01,
            y=0.97,
            xref="paper",
            yref="paper",
            text=f"Current Price: ${current_price:.2f}",
            showarrow=False,
            font=dict(size=16, color=COLORS['text']),
            align="left",
            bgcolor=COLORS['primary'],
            bordercolor=COLORS['grid'],
            borderwidth=1,
            borderpad=4
        )
        
        change_color = COLORS['positive'] if price_change >= 0 else COLORS['negative']
        change_symbol = "▲" if price_change >= 0 else "▼"
        
        fig.add_annotation(
            x=0.01,
            y=0.92,
            xref="paper",
            yref="paper",
            text=f"Change: {change_symbol} ${abs(price_change):.2f} ({abs(price_change_pct):.2f}%)",
            showarrow=False,
            font=dict(size=14, color=change_color),
            align="left",
            bgcolor=COLORS['primary'],
            bordercolor=COLORS['grid'],
            borderwidth=1,
            borderpad=4
        )
        
        # Save the figure
        filename = f"{stock_data.symbol}_historical_price.html"
        filepath = os.path.join(VIZ_DIR, filename)
        pio.write_html(fig, file=filepath, auto_open=False)
        
        # Return the relative path from static directory
        return f"visualizations/{filename}"
    
    except Exception as e:
        logger.error(f"Error creating historical price chart for {stock_data.symbol}: {str(e)}")
        return ""

def create_forecast_chart(stock_data: StockData, prediction: Dict[str, Any]) -> str:
    """
    Create an interactive chart of price forecast with confidence intervals and prediction insights.
    
    Args:
        stock_data: StockData object
        prediction: Prediction data dictionary
        
    Returns:
        Path to the generated visualization file
    """
    try:
        # Create figure with subplots
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=(
                "Price Forecast with Confidence Intervals", 
                "Prediction Performance Metrics"
            )
        )
        
        # Prepare forecast data
        forecast_points = prediction.get('forecast', [])
        if not forecast_points:
            logger.warning(f"No forecast points available for {stock_data.symbol}")
            return ""
        
        # Create dates for forecast
        last_date = stock_data.data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(len(forecast_points))]
        
        # Add historical price - last 30 days
        historical_x = stock_data.data.index[-30:]
        historical_y = stock_data.data['Close'][-30:]
        
        fig.add_trace(
            go.Scatter(
                x=historical_x,
                y=historical_y,
                mode='lines',
                name='Historical Price',
                line=dict(color=COLORS['info'], width=2)
            ),
            row=1, col=1
        )
        
        # Add forecast line
        forecast_values = [point.get('forecast', 0) for point in forecast_points]
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                mode='lines+markers',
                name='ARIMA Forecast',
                line=dict(color=COLORS['success'], width=2)
            ),
            row=1, col=1
        )
        
        # Add confidence intervals
        lower_ci = [point.get('lower_ci', 0) for point in forecast_points]
        upper_ci = [point.get('upper_ci', 0) for point in forecast_points]
        
        # Handle NaN values
        for i in range(len(lower_ci)):
            if np.isnan(lower_ci[i]) or lower_ci[i] == 0:
                if not np.isnan(forecast_values[i]) and forecast_values[i] != 0:
                    lower_ci[i] = forecast_values[i] * 0.95
                else:
                    lower_ci[i] = historical_y.iloc[-1] * 0.95
                    
        for i in range(len(upper_ci)):
            if np.isnan(upper_ci[i]) or upper_ci[i] == 0:
                if not np.isnan(forecast_values[i]) and forecast_values[i] != 0:
                    upper_ci[i] = forecast_values[i] * 1.05
                else:
                    upper_ci[i] = historical_y.iloc[-1] * 1.05
                    
        # Add confidence interval as a filled area
        fig.add_trace(
            go.Scatter(
                x=forecast_dates + forecast_dates[::-1],
                y=upper_ci + lower_ci[::-1],
                fill='toself',
                fillcolor=f'rgba({",".join(str(int(c)) for c in px.colors.hex_to_rgb(COLORS["success"]))},0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                name='95% Confidence Interval',
                showlegend=True
            ),
            row=1, col=1
        )
        
        # Calculate forecast metrics
        current_price = historical_y.iloc[-1]
        avg_forecast = sum(forecast_values) / len(forecast_values)
        forecast_change = (avg_forecast - current_price) / current_price * 100
        min_forecast = min(lower_ci)
        max_forecast = max(upper_ci)
        forecast_range = max_forecast - min_forecast
        forecast_volatility = forecast_range / current_price * 100
        
        # Create a bar chart for the forecast metrics in the bottom subplot
        metrics = ['Current Price', 'Avg Forecast', 'Min Forecast', 'Max Forecast']
        values = [current_price, avg_forecast, min_forecast, max_forecast]
        colors = [COLORS['neutral'], 
                 COLORS['positive'] if avg_forecast >= current_price else COLORS['negative'],
                 COLORS['negative'], 
                 COLORS['positive']]
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=values,
                marker_color=colors,
                text=[f"${v:.2f}" for v in values],
                textposition='outside',
                name='Price Metrics'
            ),
            row=2, col=1
        )
        
        # Update layout
        name = stock_data.info.get('shortName', stock_data.info.get('longName', stock_data.symbol))
        model_info = prediction.get('model_info', {})
        arima_order = model_info.get('order', (0, 0, 0))
        
        fig.update_layout(
            title=f'{name} ({stock_data.symbol}) 5-Day Price Forecast',
            height=700,
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        fig.update_xaxes(title_text='Date', row=1, col=1)
        fig.update_yaxes(title_text='Price ($)', row=1, col=1)
        fig.update_xaxes(title_text='Metric', row=2, col=1)
        fig.update_yaxes(title_text='Value ($)', row=2, col=1)
        
        # Add a vertical line to separate historical from forecast
        fig.add_shape(
            type="line",
            x0=last_date,
            y0=min(min(historical_y), min(lower_ci)) * 0.95,
            x1=last_date,
            y1=max(max(historical_y), max(upper_ci)) * 1.05,
            line=dict(color=COLORS['warning'], width=2, dash="dash"),
            row=1, col=1
        )
        
        # Add model info annotation
        fig.add_annotation(
            x=0.01,
            y=0.97,
            xref="paper",
            yref="paper",
            text=f"ARIMA Model: {arima_order}",
            showarrow=False,
            font=dict(size=12, color=COLORS['text']),
            bgcolor=COLORS['primary'],
            bordercolor=COLORS['grid'],
            borderwidth=1,
            borderpad=4,
            align="left"
        )
        
        # Add forecast prediction annotation
        change_color = COLORS['positive'] if forecast_change >= 0 else COLORS['negative']
        change_symbol = "▲" if forecast_change >= 0 else "▼"
        prediction_text = f"5-Day Outlook: {change_symbol} {abs(forecast_change):.2f}%"
        
        fig.add_annotation(
            x=0.01,
            y=0.92,
            xref="paper",
            yref="paper",
            text=prediction_text,
            showarrow=False,
            font=dict(size=14, color=change_color),
            bgcolor=COLORS['primary'],
            bordercolor=COLORS['grid'],
            borderwidth=1,
            borderpad=4,
            align="left"
        )
        
        # Add volatility annotation
        fig.add_annotation(
            x=0.01,
            y=0.87,
            xref="paper",
            yref="paper",
            text=f"Forecast Volatility: {forecast_volatility:.2f}%",
            showarrow=False,
            font=dict(size=12, color=COLORS['warning']),
            bgcolor=COLORS['primary'],
            bordercolor=COLORS['grid'],
            borderwidth=1,
            borderpad=4,
            align="left"
        )
        
        # Save the figure
        filename = f"{stock_data.symbol}_forecast.html"
        filepath = os.path.join(VIZ_DIR, filename)
        pio.write_html(fig, file=filepath, 
                      config={'displayModeBar': True, 'scrollZoom': True},
                      auto_open=False,
                      include_plotlyjs='cdn',
                      full_html=True)
        
        # Return the relative path from static directory
        return f"visualizations/{filename}"
    
    except Exception as e:
        logger.error(f"Error creating forecast chart for {stock_data.symbol}: {str(e)}")
        return ""

def create_comparative_chart(stock_data_list: List[StockData]) -> str:
    """
    Create an advanced comparative chart of multiple stocks with metrics.
    
    Args:
        stock_data_list: List of StockData objects
        
    Returns:
        Path to the generated visualization file
    """
    try:
        if not stock_data_list:
            logger.warning("No stock data provided for comparative chart")
            return ""
        
        # Create figure with subplots
        fig = make_subplots(
            rows=2, 
            cols=2,
            subplot_titles=(
                "Normalized Price Performance", 
                "Relative Volume",
                "Volatility Comparison",
                "Correlation Matrix"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "heatmap"}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.08
        )
        
        # Prepare data for correlation matrix
        correlation_data = {}
        stock_names = []
        closing_prices = []
        volatilities = []
        
        # Normalize all prices to percentage change from first day
        for stock_data in stock_data_list:
            if len(stock_data.data) == 0:
                continue
                
            # Get stock name    
            name = stock_data.info.get('shortName', stock_data.info.get('longName', stock_data.symbol))
            stock_names.append(name)
            
            # Calculate normalized prices (percentage change from first day)
            first_price = stock_data.data['Close'].iloc[0]
            normalized_prices = (stock_data.data['Close'] - first_price) / first_price * 100
            
            # Add normalized price trace
            fig.add_trace(
                go.Scatter(
                    x=stock_data.data.index,
                    y=normalized_prices,
                    mode='lines',
                    name=f'{name} ({stock_data.symbol})',
                    hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Calculate average volume and relative volume
            avg_vol = stock_data.data['Volume'].mean()
            last_vol = stock_data.data['Volume'].iloc[-1]
            rel_vol = last_vol / avg_vol
            
            # Add relative volume bar
            fig.add_trace(
                go.Bar(
                    x=[name],
                    y=[rel_vol],
                    text=[f"{rel_vol:.2f}x"],
                    textposition='outside',
                    name=f'{name} Rel. Vol.',
                    marker_color=COLORS['info'] if rel_vol > 1 else COLORS['warning'],
                    hovertemplate='%{x}<br>Relative Volume: %{y:.2f}x<extra></extra>'
                ),
                row=1, col=2
            )
            
            # Calculate volatility (standard deviation of daily returns)
            daily_returns = stock_data.data['Close'].pct_change().dropna()
            volatility = daily_returns.std() * 100  # Convert to percentage
            volatilities.append((stock_data.symbol, volatility))
            
            # Store closing prices for correlation
            correlation_data[stock_data.symbol] = stock_data.data['Close']
            closing_prices.append(stock_data.data['Close'])
        
        # Add volatility comparison
        vol_symbols = [v[0] for v in volatilities]
        vol_values = [v[1] for v in volatilities]
        
        fig.add_trace(
            go.Scatter(
                x=vol_symbols,
                y=vol_values,
                mode='markers+text',
                marker=dict(
                    size=vol_values,
                    sizemode='area',
                    sizeref=2.*max(vol_values)/(40.**2),
                    sizemin=4,
                    color=vol_values,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(
                        title="Volatility (%)",
                        thickness=15,
                        len=0.5,
                        y=0.25
                    )
                ),
                text=vol_symbols,
                textposition='top center',
                name='Volatility',
                hovertemplate='%{x}<br>Volatility: %{y:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Create correlation matrix
        if len(closing_prices) > 1:
            # Align all closing price series to handle different dates
            df_combined = pd.concat(correlation_data, axis=1).dropna()
            
            if not df_combined.empty:
                # Calculate correlation matrix
                corr_matrix = df_combined.corr().round(2)
                
                # Add correlation heatmap
                fig.add_trace(
                    go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu_r',
                        zmid=0,
                        text=corr_matrix.values,
                        texttemplate='%{text:.2f}',
                        hovertemplate='%{x} vs %{y}<br>Correlation: %{z:.2f}<extra></extra>'
                    ),
                    row=2, col=2
                )
        
        # Update layout
        symbols = ', '.join([stock.symbol for stock in stock_data_list])
        
        fig.update_layout(
            title=f'Comparative Market Analysis: {symbols}',
            height=800,
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            hovermode='closest'
        )
        
        # Update axes titles
        fig.update_xaxes(title_text='Date', row=1, col=1)
        fig.update_yaxes(title_text='Price Change (%)', row=1, col=1)
        
        fig.update_xaxes(title_text='Stock', row=1, col=2)
        fig.update_yaxes(title_text='Relative Volume (Current/Avg)', row=1, col=2)
        
        fig.update_xaxes(title_text='Stock Symbol', row=2, col=1)
        fig.update_yaxes(title_text='Volatility (%)', row=2, col=1)
        
        # Add time range selector
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]),
                    bgcolor=COLORS['primary'],
                    activecolor=COLORS['info']
                ),
                type="date"
            )
        )
        
        # Add performance summary annotation
        latest_dates = [stock.data.index[-1] for stock in stock_data_list if len(stock.data) > 0]
        if latest_dates:
            latest_date = max(latest_dates)
            
            # Calculate 1-month performance for each stock
            one_month_ago = latest_date - timedelta(days=30)
            performances = []
            
            for stock in stock_data_list:
                if len(stock.data) == 0:
                    continue
                
                latest_price = stock.data['Close'].iloc[-1]
                
                # Find closest date to one month ago
                past_prices = stock.data[stock.data.index <= one_month_ago]['Close']
                if not past_prices.empty:
                    past_price = past_prices.iloc[-1]
                    perf = ((latest_price - past_price) / past_price) * 100
                    performances.append((stock.symbol, perf))
            
            if performances:
                # Sort by performance
                performances.sort(key=lambda x: x[1], reverse=True)
                
                # Create summary text
                summary_text = "30-Day Performance:<br>"
                for symbol, perf in performances:
                    arrow = "▲" if perf >= 0 else "▼"
                    color = COLORS['positive'] if perf >= 0 else COLORS['negative']
                    summary_text += f"<span style='color:{color}'>{symbol}: {arrow} {abs(perf):.2f}%</span><br>"
                
                fig.add_annotation(
                    x=0.02,
                    y=0.98,
                    xref="paper",
                    yref="paper",
                    text=summary_text,
                    showarrow=False,
                    font=dict(size=12),
                    bgcolor=COLORS['primary'],
                    bordercolor=COLORS['grid'],
                    borderwidth=1,
                    borderpad=4,
                    align="left",
                    xanchor="left",
                    yanchor="top"
                )
        
        # Save the figure
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"comparative_chart_{timestamp}.html"
        filepath = os.path.join(VIZ_DIR, filename)
        pio.write_html(fig, file=filepath, 
                      config={'displayModeBar': True, 'scrollZoom': True},
                      auto_open=False,
                      include_plotlyjs='cdn',
                      full_html=True)
        
        # Return the relative path from static directory
        return f"visualizations/{filename}"
    
    except Exception as e:
        logger.error(f"Error creating comparative chart: {str(e)}")
        return ""

def create_market_dashboard(stock_data_list: List[StockData], predictions_data: List[Dict[str, Any]]) -> str:
    """
    Create a comprehensive market dashboard with all selected assets.
    
    Args:
        stock_data_list: List of StockData objects
        predictions_data: List of prediction data dictionaries
        
    Returns:
        Path to the generated visualization file
    """
    try:
        if not stock_data_list:
            logger.warning("No stock data provided for market dashboard")
            return ""
        
        # Determine grid layout based on number of stocks
        num_stocks = len(stock_data_list)
        
        # Create figure with subplots - one row per stock, 3 columns (price, volume, forecast)
        fig = make_subplots(
            rows=num_stocks,
            cols=3,
            subplot_titles=[f"{stock.symbol} Price" for stock in stock_data_list] +
                          [f"{stock.symbol} Volume" for stock in stock_data_list] +
                          [f"{stock.symbol} Forecast" for stock in stock_data_list],
            specs=[[{"type": "scatter"}, {"type": "bar"}, {"type": "scatter"}] for _ in range(num_stocks)],
            vertical_spacing=0.05,
            horizontal_spacing=0.05
        )
        
        # Add data for each stock
        for i, stock_data in enumerate(stock_data_list):
            row = i + 1
            
            # Add price chart
            fig.add_trace(
                go.Scatter(
                    x=stock_data.data.index[-90:],  # Last 90 days
                    y=stock_data.data['Close'][-90:],
                    name=f"{stock_data.symbol} Price",
                    line=dict(color=COLORS['info'], width=1.5)
                ),
                row=row, col=1
            )
            
            # Add 20-day moving average
            ma20 = stock_data.data['Close'].rolling(window=20).mean()
            fig.add_trace(
                go.Scatter(
                    x=stock_data.data.index[-90:],
                    y=ma20[-90:],
                    name=f"{stock_data.symbol} 20-day MA",
                    line=dict(color=COLORS['success'], width=1, dash='dash'),
                    showlegend=False
                ),
                row=row, col=1
            )
            
            # Add volume chart
            colors = [COLORS['positive'] if stock_data.data['Close'].iloc[i] > stock_data.data['Close'].iloc[i-1] 
                     else COLORS['negative'] for i in range(1, len(stock_data.data))]
            colors.insert(0, COLORS['neutral'])  # For the first bar
            
            fig.add_trace(
                go.Bar(
                    x=stock_data.data.index[-30:],  # Last 30 days
                    y=stock_data.data['Volume'][-30:],
                    name=f"{stock_data.symbol} Volume",
                    marker=dict(color=colors[-30:], opacity=0.7),
                    showlegend=False
                ),
                row=row, col=2
            )
            
            # Add forecast chart if available
            prediction = next((p for p in predictions_data if p["symbol"] == stock_data.symbol), None)
            if prediction:
                forecast_points = prediction.get('forecast', [])
                if forecast_points:
                    # Create dates for forecast
                    last_date = stock_data.data.index[-1]
                    forecast_dates = [last_date + timedelta(days=i+1) for i in range(len(forecast_points))]
                    
                    # Add forecast line
                    forecast_values = [point.get('forecast', 0) for point in forecast_points]
                    
                    # Handle NaN values
                    forecast_values = [0 if np.isnan(x) else x for x in forecast_values]
                    
                    # Add historical price for context - last 15 days
                    fig.add_trace(
                        go.Scatter(
                            x=stock_data.data.index[-15:],
                            y=stock_data.data['Close'][-15:],
                            name=f"{stock_data.symbol} Price",
                            line=dict(color=COLORS['info'], width=1),
                            showlegend=False
                        ),
                        row=row, col=3
                    )
                    
                    # Add forecast
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_dates,
                            y=forecast_values,
                            name=f"{stock_data.symbol} Forecast",
                            line=dict(color=COLORS['warning'], width=2, dash='dash'),
                            mode='lines+markers',
                            showlegend=False
                        ),
                        row=row, col=3
                    )
                    
                    # Get confidence intervals
                    lower_ci = [point.get('lower_ci', 0) for point in forecast_points]
                    upper_ci = [point.get('upper_ci', 0) for point in forecast_points]
                    
                    # Handle NaN values
                    lower_ci = [0 if np.isnan(x) else x for x in lower_ci]
                    upper_ci = [0 if np.isnan(x) else x for x in upper_ci]
                    
                    # Add confidence interval
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_dates + forecast_dates[::-1],
                            y=upper_ci + lower_ci[::-1],
                            fill='toself',
                            fillcolor=f'rgba({",".join(str(int(c)) for c in px.colors.hex_to_rgb(COLORS["success"]))},0.2)',
                            line=dict(color='rgba(0,0,0,0)'),
                            showlegend=False
                        ),
                        row=row, col=3
                    )
                    
                    # Add line for current date
                    fig.add_shape(
                        type="line",
                        x0=last_date,
                        y0=min(stock_data.data['Close'][-15:].min(), min(lower_ci)),
                        x1=last_date,
                        y1=max(stock_data.data['Close'][-15:].max(), max(upper_ci)),
                        line=dict(color=COLORS['grid'], width=1, dash="dot"),
                        row=row, col=3
                    )
            
            # Add current price and change annotation
            current_price = stock_data.data['Close'].iloc[-1]
            previous_price = stock_data.data['Close'].iloc[-2]
            price_change = current_price - previous_price
            price_change_pct = (price_change / previous_price) * 100
            
            change_color = COLORS['positive'] if price_change >= 0 else COLORS['negative']
            change_symbol = "▲" if price_change >= 0 else "▼"
            
            fig.add_annotation(
                x=stock_data.data.index[-1],
                y=current_price,
                text=f"${current_price:.2f} ({change_symbol}{abs(price_change_pct):.2f}%)",
                showarrow=True,
                arrowhead=1,
                arrowcolor=change_color,
                arrowwidth=1,
                arrowsize=0.8,
                font=dict(size=10, color=change_color),
                row=row, col=1
            )
            
            # Add company name annotation
            company_name = stock_data.info.get('shortName', stock_data.info.get('longName', stock_data.symbol))
            sector = stock_data.info.get('sector', 'Unknown')
            
            fig.add_annotation(
                x=0.02,
                y=0.9,
                xref=f"x{row * 3 - 2} domain",
                yref=f"y{row * 3 - 2} domain",
                text=f"{company_name}<br><span style='font-size:0.8em;color:{COLORS['grid']}'>{sector}</span>",
                showarrow=False,
                font=dict(size=10, color=COLORS['text']),
                align="left",
                xanchor="left"
            )
        
        # Update layout
        height = max(600, 250 * num_stocks)  # Adjust height based on number of stocks
        
        fig.update_layout(
            title="Market Dashboard - Selected Assets",
            height=height,
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        # Update axes formatting
        for i in range(1, num_stocks + 1):
            fig.update_yaxes(title_text="Price ($)", row=i, col=1)
            fig.update_yaxes(title_text="Volume", row=i, col=2)
            fig.update_yaxes(title_text="Price ($)", row=i, col=3)
            
            # Only show x-axis title on bottom row
            if i == num_stocks:
                fig.update_xaxes(title_text="Date", row=i, col=1)
                fig.update_xaxes(title_text="Date", row=i, col=2)
                fig.update_xaxes(title_text="Date", row=i, col=3)
        
        # Save the figure
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"market_dashboard_{timestamp}.html"
        filepath = os.path.join(VIZ_DIR, filename)
        pio.write_html(fig, file=filepath, 
                      config={'displayModeBar': True, 'scrollZoom': True},
                      auto_open=False,
                      include_plotlyjs='cdn',
                      full_html=True)
        
        # Return the relative path from static directory
        return f"visualizations/{filename}"
    
    except Exception as e:
        logger.error(f"Error creating market dashboard: {str(e)}")
        return ""

def generate_visualizations(stock_data_list: List[StockData], predictions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate visualizations for the given stock data and predictions.
    
    Args:
        stock_data_list: List of StockData objects
        predictions_data: List of prediction data dictionaries
        
    Returns:
        List of visualization info dictionaries
    """
    visualizations = []
    
    try:
        # Create historical price charts for each stock
        for stock_data in stock_data_list:
            historical_path = create_historical_price_chart(stock_data)
            if historical_path:
                visualizations.append({
                    "type": "historical_price",
                    "symbol": stock_data.symbol,
                    "path": historical_path,
                    "title": f"{stock_data.symbol} Technical Analysis"
                })
        
        # Create forecast charts for each stock
        for stock_data in stock_data_list:
            # Find corresponding prediction
            prediction = next((p for p in predictions_data if p["symbol"] == stock_data.symbol), None)
            if prediction:
                forecast_path = create_forecast_chart(stock_data, prediction)
                if forecast_path:
                    visualizations.append({
                        "type": "forecast",
                        "symbol": stock_data.symbol,
                        "path": forecast_path,
                        "title": f"{stock_data.symbol} 5-Day Forecast"
                    })
        
        # Create comparative chart if multiple stocks
        if len(stock_data_list) > 1:
            comparative_path = create_comparative_chart(stock_data_list)
            if comparative_path:
                symbols = [stock.symbol for stock in stock_data_list]
                visualizations.append({
                    "type": "comparative",
                    "symbols": symbols,
                    "path": comparative_path,
                    "title": "Comparative Market Analysis"
                })
            
            # Create market dashboard
            dashboard_path = create_market_dashboard(stock_data_list, predictions_data)
            if dashboard_path:
                symbols = [stock.symbol for stock in stock_data_list]
                visualizations.append({
                    "type": "dashboard",
                    "symbols": symbols,
                    "path": dashboard_path,
                    "title": "Market Dashboard"
                })
        
        return visualizations
    
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        return visualizations