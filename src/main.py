"""
Main entry point for the Flask application.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, send_from_directory
from src.routes.api import api_bp

# Create Flask app
app = Flask(__name__)

# Register blueprints
app.register_blueprint(api_bp)

# Ensure cache directory exists
cache_dir = os.path.join(app.static_folder, 'cache')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/fund-analysis')
def fund_analysis():
    """Render the fund analysis page."""
    return render_template('fund-analysis.html')

@app.route('/category-analysis')
def category_analysis():
    """Render the category analysis page."""
    return render_template('category-analysis.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
