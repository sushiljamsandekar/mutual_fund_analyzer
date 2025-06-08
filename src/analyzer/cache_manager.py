"""
Cache management module for mutual fund analyzer.
Handles storing and retrieving data from cache.
"""

import json
import os
from datetime import datetime, timedelta, timezone
import random

# Constants
CACHE_FILE = "/home/ubuntu/mutual_fund_analyzer_web/src/static/cache/mf_data_cache.json"
CACHE_EXPIRY_HOURS = 24
CATEGORY_PREFETCH_SAMPLE_SIZE = 500

def ensure_cache_dir():
    """Ensures the cache directory exists."""
    cache_dir = os.path.dirname(CACHE_FILE)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

def load_cache(force_refresh=False):
    """Loads data from the cache file if it exists and is not expired."""
    if force_refresh:
        return None
    
    ensure_cache_dir()
    
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, "r") as f:
            cache_data = json.load(f)
        
        timestamp_str = cache_data.get("timestamp")
        if not timestamp_str:
            return None
        
        cache_timestamp = datetime.fromisoformat(timestamp_str)
        if datetime.now(timezone.utc) - cache_timestamp > timedelta(hours=CACHE_EXPIRY_HOURS):
            return None
            
        # Convert categories list back to set if needed
        if "categories" in cache_data and isinstance(cache_data["categories"], list):
             cache_data["categories"] = set(cache_data["categories"])
        
        return cache_data
    except (json.JSONDecodeError, FileNotFoundError, Exception):
        return None

def save_cache(data):
    """Saves data to the cache file with a current timestamp."""
    try:
        ensure_cache_dir()
        
        data["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Convert categories set to list for JSON serialization
        if "categories" in data and isinstance(data["categories"], set):
             data["categories"] = list(data["categories"])
             
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=4)
        
        # Convert back to set after saving if needed for internal use
        if "categories" in data and isinstance(data["categories"], list):
             data["categories"] = set(data["categories"])
             
        return True
    except Exception:
        return False

def prefetch_fund_categories(all_funds, data_fetcher, sample_size=CATEGORY_PREFETCH_SAMPLE_SIZE, force_refresh=False):
    """Fetches details for a sample of funds to build a category map, using cache."""
    cache = load_cache(force_refresh)
    
    # Check if cache has both categorized_funds and categories, and the sample size matches
    if cache and "categorized_funds" in cache and "categories" in cache and cache.get("prefetch_sample_size") == sample_size:
        # Ensure categories is a set
        if isinstance(cache["categories"], list):
             cache["categories"] = set(cache["categories"])
        return cache["categorized_funds"], cache["categories"]
    
    categorized_funds = []
    categories = set()
    
    # Ensure sample size is not larger than the total number of funds
    actual_sample_size = min(len(all_funds), sample_size)
    if actual_sample_size == 0:
        return [], set()
    
    sampled_codes = random.sample([f['schemeCode'] for f in all_funds if 'schemeCode' in f], actual_sample_size)
    
    for code in sampled_codes:
        fund_data = data_fetcher.get_fund_data(code)
        if fund_data and 'meta' in fund_data:
            meta = fund_data['meta']
            category = meta.get('scheme_category')
            if category:
                categories.add(category)
                categorized_funds.append({
                    'schemeCode': meta.get('scheme_code'),
                    'schemeName': meta.get('scheme_name'),
                    'schemeCategory': category
                })
    
    if categorized_funds or categories:
        # Load existing cache to merge data
        existing_cache_data = load_cache(force_refresh=True)
        if existing_cache_data is None:
            existing_cache_data = {}
        
        save_data = {
            **existing_cache_data,
            "categorized_funds": categorized_funds,
            "categories": categories,
            "prefetch_sample_size": sample_size
        }
        save_cache(save_data)
        
    return categorized_funds, categories
