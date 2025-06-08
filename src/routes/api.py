"""
API routes for mutual fund analyzer web application.
"""

from flask import Blueprint, jsonify, request
from src.analyzer import analyzer, cache_manager, category_analyzer

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize modules
cache_mgr = cache_manager

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "API is running"})

@api_bp.route('/funds', methods=['GET'])
def get_funds():
    """Get all funds or search by name."""
    search_term = request.args.get('search', '').strip()
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    all_funds, from_cache = analyzer.get_all_funds_cached(cache_mgr, force_refresh)
    
    if not all_funds:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch fund list"
        }), 500
    
    # If search term provided, filter funds
    if search_term:
        matches = []
        search_term_lower = search_term.lower()
        for fund in all_funds:
            scheme_name = fund.get("schemeName", "").lower()
            if search_term_lower in scheme_name:
                matches.append({
                    "schemeCode": fund.get("schemeCode"),
                    "schemeName": fund.get("schemeName")
                })
        
        return jsonify({
            "status": "success",
            "from_cache": from_cache,
            "search_term": search_term,
            "matches": matches[:20],  # Limit to 20 results
            "total_matches": len(matches)
        })
    
    # If no search term, return basic stats
    return jsonify({
        "status": "success",
        "from_cache": from_cache,
        "total_funds": len(all_funds),
        "message": "Use search parameter to find specific funds"
    })

@api_bp.route('/analyze/fund/<scheme_code>', methods=['GET'])
def analyze_fund(scheme_code):
    """Analyze a specific fund by scheme code."""
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    all_funds, _ = analyzer.get_all_funds_cached(cache_mgr, force_refresh)
    
    if not all_funds:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch fund list"
        }), 500
    
    # Find the fund by scheme code
    fund_name = None
    for fund in all_funds:
        if str(fund.get("schemeCode")) == str(scheme_code):
            fund_name = fund.get("schemeName")
            break
    
    if not fund_name:
        return jsonify({
            "status": "error",
            "message": f"Fund with scheme code {scheme_code} not found"
        }), 404
    
    # Analyze the fund
    result = analyzer.analyze_single_fund(fund_name, all_funds)
    return jsonify(result)

@api_bp.route('/analyze/fund', methods=['GET'])
def analyze_fund_by_name():
    """Analyze a fund by name."""
    fund_name = request.args.get('name', '').strip()
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    if not fund_name:
        return jsonify({
            "status": "error",
            "message": "Fund name parameter is required"
        }), 400
    
    all_funds, _ = analyzer.get_all_funds_cached(cache_mgr, force_refresh)
    
    if not all_funds:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch fund list"
        }), 500
    
    # Analyze the fund
    result = analyzer.analyze_single_fund(fund_name, all_funds)
    return jsonify(result)

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all fund categories."""
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    all_funds, _ = analyzer.get_all_funds_cached(cache_mgr, force_refresh)
    
    if not all_funds:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch fund list"
        }), 500
    
    # Prefetch categories
    from src.analyzer import data_fetcher as df
    categorized_funds, categories = cache_manager.prefetch_fund_categories(
        all_funds, df, force_refresh=force_refresh
    )
    
    # Handle case where no categories are found gracefully
    if not categories:
        categories = set() # Ensure categories is a set, even if empty

    # Convert set to sorted list for JSON serialization
    categories_list = sorted(list(categories))
    
    return jsonify({
        "status": "success", # Return success even if list is empty
        "categories": categories_list,
        "total_categories": len(categories_list)
    })

@api_bp.route('/analyze/category/<category_name>', methods=['GET'])
def analyze_category(category_name):
    """Analyze funds in a specific category."""
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    all_funds, _ = analyzer.get_all_funds_cached(cache_mgr, force_refresh)
    
    if not all_funds:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch fund list"
        }), 500
    
    # Prefetch categories
    from src.analyzer import data_fetcher as df, calculator as calc
    categorized_funds, categories = cache_manager.prefetch_fund_categories(
        all_funds, df, force_refresh=force_refresh
    )
    
    if not categories:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch categories"
        }), 500
    
    # Check if category exists
    if category_name not in categories:
        return jsonify({
            "status": "error",
            "message": f"Category '{category_name}' not found"
        }), 404
    
    # Analyze the category
    result = category_analyzer.analyze_category(category_name, categorized_funds, df, calc)
    return jsonify(result)

@api_bp.route('/cache/status', methods=['GET'])
def cache_status():
    """Get cache status."""
    cache = cache_mgr.load_cache(force_refresh=False)
    
    if not cache:
        return jsonify({
            "status": "success",
            "cache_exists": False,
            "message": "No cache found or cache is expired"
        })
    
    return jsonify({
        "status": "success",
        "cache_exists": True,
        "timestamp": cache.get("timestamp"),
        "has_all_funds": "all_funds" in cache,
        "has_categories": "categories" in cache,
        "prefetch_sample_size": cache.get("prefetch_sample_size")
    })

@api_bp.route('/cache/refresh', methods=['POST'])
def refresh_cache():
    """Force refresh the cache."""
    all_funds = analyzer.data_fetcher.get_all_funds_live()
    
    if not all_funds:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch fund list"
        }), 500
    
    # Save to cache
    cache_mgr.save_cache({"all_funds": all_funds})
    
    # Prefetch categories
    from src.analyzer import data_fetcher as df
    categorized_funds, categories = cache_manager.prefetch_fund_categories(
        all_funds, df, force_refresh=True
    )
    
    return jsonify({
        "status": "success",
        "message": "Cache refreshed successfully",
        "total_funds": len(all_funds),
        "total_categories": len(categories) if categories else 0
    })
