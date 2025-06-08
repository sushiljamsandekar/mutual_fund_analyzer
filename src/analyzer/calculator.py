"""
Calculation module for mutual fund analyzer.
Handles return calculations and performance metrics.
"""

from datetime import datetime, timedelta

# Constants
RETURN_PERIODS = [1, 3, 5, 10]  # Years

def calculate_returns(nav_data, periods_years=RETURN_PERIODS):
    """Calculates annualized returns (CAGR) for specified periods from NAV data."""
    if not nav_data or len(nav_data) < 2:
        return {}
    try:
        parsed_data = []

        for record in nav_data:
            try:
                nav_value = float(record['nav'])
                if nav_value <= 0: continue
                date_str = record.get('date')
                if not date_str or not isinstance(date_str, str) or len(date_str.split('-')) != 3:
                    date_str = date_str.strftime('%d-%m-%Y')
                
                parsed_data.append({
                    'date': datetime.strptime(date_str, '%d-%m-%Y'),
                    'nav': nav_value
                })
            except (ValueError, TypeError, KeyError): continue
        if not parsed_data or len(parsed_data) < 2:
            return {}
        parsed_data.sort(key=lambda x: x['date'])
    except Exception:
        return {}
    
    returns = {}
    latest_record = parsed_data[-1]
    latest_date = latest_record['date']
    latest_nav = latest_record['nav']
    
    for years in periods_years:
        start_date_target = latest_date - timedelta(days=years * 365.25)
        start_record = None
        for record in parsed_data[-2::-1]:
            if record['date'] <= start_date_target:
                start_record = record
                break
        if not start_record:
            first_record = parsed_data[0]
            if first_record['date'] <= start_date_target + timedelta(days=90):
                 start_record = first_record
            else:
                 returns[f"{years}Y"] = None
                 continue
        
        start_nav = start_record['nav']
        start_date_actual = start_record['date']
        actual_years = (latest_date - start_date_actual).days / 365.25
        
        if actual_years < (1/12):
             returns[f"{years}Y"] = None
             continue
        try:
            if start_nav == 0: raise ValueError("Start NAV is zero")
            ratio = latest_nav / start_nav
            if ratio < 0:
                returns[f"{years}Y"] = None
                continue
            cagr = (ratio ** (1 / actual_years)) - 1
            returns[f"{years}Y"] = cagr * 100
        except (ZeroDivisionError, ValueError, OverflowError, TypeError):
            returns[f"{years}Y"] = None
    return returns

def calculate_index_returns(index_data, periods_years=RETURN_PERIODS):
    """Calculates annualized returns (CAGR) for the index from Yahoo Finance data."""
    if not index_data:
        return {}
    try:
        timestamps = index_data.get('timestamp', [])
        
        adj_close_list = index_data.get('indicators', {}).get('adjclose', [])
        if not adj_close_list or not isinstance(adj_close_list, list) or not adj_close_list[0].get('adjclose'):
             return {}
        adj_close_prices = adj_close_list[0]['adjclose']
        
        if not timestamps or not adj_close_prices or len(timestamps) != len(adj_close_prices):
            return {}
        
        parsed_data = []
        for ts, price in zip(timestamps, adj_close_prices):
            if ts is not None and price is not None:
                try:
                    dt_object = datetime.fromtimestamp(ts)
                    parsed_data.append({'date': dt_object, 'nav': float(price)})
                except (ValueError, TypeError): continue
        
        if len(parsed_data) < 2:
            return {}
        parsed_data.sort(key=lambda x: x['date'])
    except Exception as e:
        print(f"Error calculting index returns : {e}")
        return {}
    
    # Use the same calculation logic as for funds
    return calculate_returns(parsed_data, periods_years)
