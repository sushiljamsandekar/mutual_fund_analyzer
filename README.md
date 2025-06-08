# Indian Mutual Fund Analyzer

A web application for analyzing Indian mutual funds, comparing them with benchmark indices, and finding top performers in different categories.

## Features

- **Fund Analysis**: Compare specific mutual funds against the NIFTY 50 benchmark
- **Category Analysis**: Find top performing funds within each category based on 5-year returns
- **Interactive UI**: User-friendly interface with search, visualizations, and clear metrics
- **Caching System**: Server-side caching to improve performance

## Local Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

### Installation Steps

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - If dont work then run powershell in admin mode and use 
      ```bash
      Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
      or
      Set-ExecutionPolicy RemoteSigned
      ```
      to Disable it after the use 
      ```bash
      Set-ExecutionPolicy Restricted

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create cache directory**:
   ```bash
   mkdir -p src/static/cache
   ```

### Running the Application

1. **Start the Flask server**:
   ```bash
   python src/main.py
   ```

2. **Access the application**:
   Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage Guide

### Fund Analysis

1. Navigate to the "Fund Analysis" page
2. Enter a fund name in the search box (e.g., "Parag Parikh Flexi Cap Fund")
3. Select the specific fund from the search results
4. View the analysis results, including:
   - Performance comparison with NIFTY 50
   - Returns across different time periods (1Y, 3Y, 5Y, 10Y)
   - Visual charts and performance metrics

### Category Analysis

1. Navigate to the "Category Analysis" page
2. Browse or search for a specific fund category
3. Select a category to analyze
4. View the top 3 performing funds in that category based on 5-year returns

### Cache Management

1. Navigate to the "About" page
2. View the current cache status
3. Click "Refresh Cache" to update the data if needed

## Project Structure

```
mutual_fund_analyzer_web/
├── requirements.txt       # Python dependencies
├── src/
│   ├── analyzer/          # Core analysis logic
│   │   ├── __init__.py
│   │   ├── analyzer.py    # Main analyzer module
│   │   ├── calculator.py  # Return calculation functions
│   │   ├── category_analyzer.py # Category analysis functions
│   │   ├── data_fetcher.py # API data retrieval
│   │   ├── cache_manager.py # Caching functions
│   │   └── suggestion.py  # Suggestion generation
│   ├── models/            # Database models (not used in current version)
│   ├── routes/            # API routes
│   │   └── api.py         # API endpoints
│   ├── static/            # Static assets
│   │   ├── css/           # Stylesheets
│   │   ├── js/            # JavaScript files
│   │   └── cache/         # Cache storage directory
│   ├── templates/         # HTML templates
│   │   ├── base.html      # Base template
│   │   ├── index.html     # Home page
│   │   ├── fund-analysis.html # Fund analysis page
│   │   ├── category-analysis.html # Category analysis page
│   │   └── about.html     # About page
│   └── main.py            # Application entry point
└── venv/                  # Virtual environment (created during setup)
```

## Data Sources

- Mutual Fund Data: [mfapi.in](https://www.mfapi.in/)
- Benchmark Index: Yahoo Finance (NIFTY 50)

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**:
   - Ensure you've activated the virtual environment
   - Verify all dependencies are installed with `pip install -r requirements.txt`

2. **Cache directory errors**:
   - Make sure the `src/static/cache` directory exists
   - Check file permissions if you encounter write errors

3. **API connection issues**:
   - Verify your internet connection
   - The application requires access to external APIs (mfapi.in and Yahoo Finance)

### Yahoo Finance Data Access

The application uses a special module for accessing Yahoo Finance data. If you encounter issues with this functionality:

1. You may need to modify the `data_fetcher.py` file to use a different method for fetching index data
2. Consider using an alternative data source for benchmark index data

## License

This project is provided for educational and personal use.

## Acknowledgements

- Data provided by mfapi.in and Yahoo Finance
- Built with Flask, Bootstrap, and Chart.js
