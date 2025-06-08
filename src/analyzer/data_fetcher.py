"""
Data fetching module for mutual fund analyzer.
Handles retrieving data from external APIs.
"""

import requests
import json
import time
from datetime import datetime, timedelta, timezone
import os
import sys
import yfinance as yf


# Add path for data_api module
sys.path.append("/opt/.manus/.sandbox-runtime")
try:
    from data_api import ApiClient
    api_client = ApiClient()
except ImportError:
    print("Warning: Could not import ApiClient. Yahoo Finance data will be unavailable.")
    api_client = None

# Constants
MFAPI_BASE_URL = "https://api.mfapi.in/mf"
REQUEST_TIMEOUT = 30
API_DELAY = 0.05  # Small delay between API calls

def get_all_funds_live():
    """Fetches the list of all available funds directly from mfapi.in."""
    try:
        response = requests.get(MFAPI_BASE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        funds = response.json()
        if isinstance(funds, list) and len(funds) > 0:
            return funds
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fund list from {MFAPI_BASE_URL}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response from MF API: {e}")
        return None

def get_fund_data(scheme_code):
    """Fetches metadata and historical NAV for a specific fund."""
    if not scheme_code:
        return None
    fund_url = f"{MFAPI_BASE_URL}/{scheme_code}"
    try:
        time.sleep(API_DELAY)  # Add delay to avoid rate limiting
        response = requests.get(fund_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        fund_data = response.json()
        if isinstance(fund_data, dict) and 'meta' in fund_data and 'data' in fund_data:
            return fund_data
        else:
            return None
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def find_fund_code(fund_name, all_funds):
    """Searches the list of funds to find the scheme code(s) for a given name."""
    if not all_funds:
        return []
    matches = []
    fund_name_lower_trimmed = fund_name.lower().strip()
    if not fund_name_lower_trimmed:
        return []
    
    for fund in all_funds:
        scheme_name = fund.get("schemeName", "")
        # Use exact match for schemeName first, then fallback to contains
        if fund_name_lower_trimmed == scheme_name.lower().strip():
             matches.insert(0, {"schemeCode": fund.get("schemeCode"), "schemeName": scheme_name})
        elif fund_name_lower_trimmed in scheme_name.lower().strip():
            matches.append({
                "schemeCode": fund.get("schemeCode"),
                "schemeName": scheme_name
            })
    
    # Remove duplicates if exact match was also found by 'in'
    unique_matches = []
    seen_codes = set()
    for match in matches:
        code = match.get("schemeCode")
        if code not in seen_codes:
            unique_matches.append(match)
            seen_codes.add(code)
    
    return unique_matches

def get_index_data_manus(index_symbol, range_years=10):
    """Fetches historical data for a benchmark index using Yahoo Finance API."""
    if not api_client:
        return None
    
    # Determine range string based on max years needed
    if range_years <= 1: range_str = "1y"
    elif range_years <= 2: range_str = "2y"
    elif range_years <= 5: range_str = "5y"
    elif range_years <= 10: range_str = "10y"
    else: range_str = "max"

    try:
        index_data = api_client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': index_symbol,
            'range': range_str,
            'interval': '1d',  # Daily interval for CAGR calculation
            'region': 'IN',
            'includeAdjustedClose': True
        })
        
        if (index_data and
            isinstance(index_data, dict) and
            index_data.get('chart', {}).get('result') and
            isinstance(index_data['chart']['result'], list) and
            len(index_data['chart']['result']) > 0):
            chart_result = index_data['chart']['result'][0]
            if chart_result.get('timestamp') and chart_result.get('indicators', {}).get('adjclose', [{}])[0].get('adjclose'):
                 return chart_result
            else:
                 return None
        else:
            return None
    except Exception:
        return None

def get_index_data(index_symbol, range_years=10):
    """
    Fetches historical data for a benchmark index using yfinance.
    
    Args:
        index_symbol (str): Yahoo Finance symbol for the index (e.g., '^NSEI' for NIFTY 50)
        range_years (int): Number of years of historical data to fetch
        
    Returns:
        dict: Processed data in a format compatible with the calculator module,
              or None if data fetch fails
    """
    try:
        # Calculate start and end dates based on range_years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=range_years*365)
        
        # Fetch data from Yahoo Finance
        index_data = yf.download(
            index_symbol,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False,
            auto_adjust=True,
            interval='1d'  # Daily data for CAGR calculation
        )
        
        if index_data.empty:
            print(f"No data returned for index symbol: {index_symbol}")
            return None
            
        # Convert to format compatible with calculator.calculate_index_returns
        # The original function expects a specific structure from the Yahoo Finance API
        timestamps = []
        values = []
        
        for date, row in index_data.iterrows():
            # Convert pandas timestamp to Unix timestamp (seconds)
            unix_timestamp = int(date.timestamp())
            timestamps.append(unix_timestamp)
            values.append(row['Close'].get("^NSEI"))
        
        # Create a structure similar to what the original API returned
        result = {
            'meta': {
                'symbol': index_symbol,
                'currency': 'INR'
            },
            'timestamp': timestamps,
            'indicators': {
                'adjclose': [
                    {
                        'adjclose': values
                    }
                ]
            }
        }
        #Return the processed result
        return result
        
    except Exception as e:
        print(f"Error fetching index data for {index_symbol}: {e}")
        return None