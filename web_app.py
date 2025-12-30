"""
Flask Web Application for InvestIQ - Multi-Agent Investment Analysis System.
"""

import sys
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd
import numpy as np

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from decision_engine import DecisionEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


def make_json_serializable(obj):
    """Convert non-JSON serializable objects (pandas Series, numpy types, etc.) to JSON-serializable formats."""
    # Handle None first
    if obj is None:
        return None
    
    # Handle pandas objects
    if isinstance(obj, pd.Series):
        # Convert Series to list, handling NaN values
        return obj.where(pd.notna(obj), None).tolist()
    elif isinstance(obj, pd.DataFrame):
        # Convert DataFrame to dict, handling NaN values
        return obj.where(pd.notna(obj), None).to_dict('records')
    
    # Handle numpy types
    elif isinstance(obj, (np.integer, np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    
    # Handle collections (check dict before iterating, as dicts are iterable)
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    
    # Handle NaN/None values
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass  # Object doesn't support pd.isna, continue
    
    # Return as-is if already JSON-serializable
    return obj


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a stock symbol and return results."""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        # Initialize decision engine
        engine = DecisionEngine()
        
        # Run analysis
        decision = engine.analyze(symbol)
        
        # Convert pandas Series and other non-serializable objects to JSON-serializable formats
        decision_serialized = make_json_serializable(decision)
        
        # Return decision as JSON
        return jsonify({
            'success': True,
            'decision': decision_serialized,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'InvestIQ Flask API'}), 200


if __name__ == '__main__':
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)

