import logging
import os
from typing import Dict

from flask import Flask, render_template, request, jsonify, Blueprint
from flask_cors import CORS

from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    static_folder="static", 
    template_folder="templates"
)

# Configure CORS
CORS(app)

# Create a blueprint for our API routes
financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/available-assets', methods=['GET'])
def get_available_assets():
    """Returns the list of available assets for analysis."""
    from core.market_data import get_available_assets
    return jsonify(get_available_assets())

@financial_bp.route('/market-data', methods=['GET'])
def get_market_data():
    """Fetches market data for specified symbols."""
    # Get query parameters
    symbols = request.args.getlist('symbols') or settings.ASSETS
    time_horizon = request.args.get('time_horizon', "6mo")
    
    # Import here to avoid circular imports
    from core.market_data import get_market_data
    
    try:
        # Fetch market data
        data = get_market_data(symbols, time_horizon)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@financial_bp.route('/predictions', methods=['GET'])
def get_predictions():
    """Runs the predictive modeling workflow and returns predictions."""
    # Get query parameters
    symbols = request.args.getlist('symbols') or settings.ASSETS
    time_horizon = request.args.get('time_horizon', "6mo")
    
    try:
        # Import here to avoid circular imports
        from core.market_data import fetch_multiple_stocks
        from core.predictive_modeling import get_predictions
        
        # Fetch the raw stock data first
        stock_data_list = fetch_multiple_stocks(symbols, time_horizon)
        
        if not stock_data_list:
            return jsonify({
                "status": "error",
                "message": "No data available for the requested symbols"
            }), 404
            
        # Generate predictions
        predictions = get_predictions(stock_data_list)
        
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@financial_bp.route('/analysis-report', methods=['GET'])
def get_analysis_report():
    """Generates a comprehensive market analysis report."""
    # Get query parameters
    symbols = request.args.getlist('symbols') or settings.ASSETS
    time_horizon = request.args.get('time_horizon', "6mo")
    
    try:
        # Import here to avoid circular imports
        from core.market_data import fetch_multiple_stocks
        from core.predictive_modeling import get_predictions
        from core.analysis_report import generate_analysis_report
        
        # Fetch the raw stock data first
        stock_data_list = fetch_multiple_stocks(symbols, time_horizon)
        
        if not stock_data_list:
            return jsonify({
                "status": "error",
                "message": "No data available for the requested symbols"
            }), 404
            
        # Generate predictions
        predictions_data = get_predictions(stock_data_list)
        
        # Generate analysis report
        report = generate_analysis_report(stock_data_list, predictions_data)
        
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error generating analysis report: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@financial_bp.route('/visualizations', methods=['GET'])
def get_visualizations():
    """Generates and returns paths to interactive visualizations."""
    # Get query parameters
    symbols = request.args.getlist('symbols') or settings.ASSETS
    time_horizon = request.args.get('time_horizon', "6mo")
    
    try:
        # Import here to avoid circular imports
        from core.market_data import fetch_multiple_stocks
        from core.predictive_modeling import get_predictions
        from core.visualizations import generate_visualizations
        
        # Fetch the raw stock data first
        stock_data_list = fetch_multiple_stocks(symbols, time_horizon)
        
        if not stock_data_list:
            return jsonify({
                "status": "error",
                "message": "No data available for the requested symbols"
            }), 404
            
        # Generate predictions
        predictions_data = get_predictions(stock_data_list)
        
        # Generate visualizations
        visualization_paths = generate_visualizations(stock_data_list, predictions_data)
        
        return jsonify(visualization_paths)
    except Exception as e:
        logger.error(f"Error generating visualizations: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@financial_bp.route('/analyst-feedback', methods=['POST'])
def submit_analyst_feedback():
    """Submits analyst feedback and regenerates the analysis report."""
    try:
        # Get request data
        data = request.json
        feedback_content = data.get('feedback_content', '')
        symbols = data.get('symbols', settings.ASSETS)
        time_horizon = data.get('time_horizon', "6mo")
        
        if not feedback_content:
            return jsonify({
                "status": "error",
                "message": "Feedback content is required"
            }), 400
        
        # Import here to avoid circular imports
        from core.market_data import fetch_multiple_stocks
        from core.predictive_modeling import get_predictions
        from core.analysis_report import generate_analysis_report_with_feedback
        
        # Fetch the raw stock data
        stock_data_list = fetch_multiple_stocks(symbols, time_horizon)
        
        if not stock_data_list:
            return jsonify({
                "status": "error",
                "message": "No data available for the requested symbols"
            }), 404
            
        # Generate predictions
        predictions_data = get_predictions(stock_data_list)
        
        # Generate analysis report with feedback
        report = generate_analysis_report_with_feedback(
            stock_data_list, 
            predictions_data,
            feedback_content
        )
        
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error processing analyst feedback: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Register the api blueprint
app.register_blueprint(financial_bp, url_prefix='/api')


@app.route("/")
def index():
    """Render the index/home page."""
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """Render the dashboard page."""
    return render_template("dashboard.html")


@app.route("/reports")
def reports():
    """Render the analysis reports page."""
    return render_template("analysis_reports.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)
