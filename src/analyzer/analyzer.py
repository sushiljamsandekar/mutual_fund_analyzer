"""
Main analyzer module for mutual fund analyzer.
Integrates data fetching, calculation, and suggestion generation.
"""

from src.analyzer import data_fetcher, calculator, suggestion

# Constants
YAHOO_FINANCE_INDEX_SYMBOL = "^NSEI"  # NIFTY 50 Index symbol

def analyze_single_fund(fund_name, all_funds):
    """Performs analysis for a single specified fund."""
    matches = data_fetcher.find_fund_code(fund_name, all_funds)
    if not matches:
        return {
            "status": "error",
            "message": f"Fund '{fund_name}' not found."
        }
    
    selected_fund = matches[0]
    scheme_code = selected_fund['schemeCode']
    
    fund_data = data_fetcher.get_fund_data(scheme_code)
    if not fund_data or not fund_data.get('data') or len(fund_data['data']) < 2:
        return {
            "status": "error",
            "message": "Could not fetch sufficient NAV data for this fund."
        }
    
    fund_meta = fund_data.get('meta', {})
    fund_nav = fund_data.get('data', [])
    
    fund_returns = calculator.calculate_returns(fund_nav)
        # Fetch Index Data
    index_data = data_fetcher.get_index_data(YAHOO_FINANCE_INDEX_SYMBOL)
    
    index_returns = calculator.calculate_index_returns(index_data)
    
    analysis_results = {
        "fund_info": fund_meta,
        "fund_returns": fund_returns,
        "index_returns": index_returns
    }

    # Generate suggestion
    result = suggestion.generate_suggestion(analysis_results)
    
    # Add additional matches if there were multiple
    if len(matches) > 1:
        result["additional_matches"] = matches[1:5]  # Include up to 4 additional matches
    
    return result

def get_all_funds_cached(cache_manager, force_refresh=False):
    """Fetches the list of all funds, using cache if available."""
    cache = cache_manager.load_cache(force_refresh)
    if cache and "all_funds" in cache:
        return cache["all_funds"], True  # Second value indicates from cache
        
    all_funds = data_fetcher.get_all_funds_live()
    if all_funds:
        cache_manager.save_cache({"all_funds": all_funds})
    
    return all_funds, False  # Second value indicates not from cache
