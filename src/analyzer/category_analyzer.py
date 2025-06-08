"""
Category analysis module for mutual fund analyzer.
Handles category-based fund analysis and ranking.
"""

# Constants
CATEGORY_RANKING_PERIOD = "5Y"  # Period used for ranking funds within a category
TOP_N_FUNDS_TO_SUGGEST = 3
MAX_FUNDS_PER_CATEGORY_ANALYSIS = 50  # Limit funds analyzed per category for performance

def analyze_category(selected_category, categorized_funds, data_fetcher, calculator):
    """Analyzes funds within a selected category using prefetched data."""
    # Filter the prefetched list for the selected category
    funds_in_category = [
        fund for fund in categorized_funds
        if fund.get('schemeCategory') == selected_category and fund.get('schemeCode')
    ]
    
    if not funds_in_category:
        return {
            "status": "error",
            "message": "No funds found for this category in the sample."
        }
    
    # Limit the number of funds to analyze for performance
    funds_to_analyze = funds_in_category[:MAX_FUNDS_PER_CATEGORY_ANALYSIS]
    
    fund_performance = []
    funds_analyzed_count = 0
    
    for fund_summary in funds_to_analyze:
        fund_data = data_fetcher.get_fund_data(fund_summary['schemeCode'])
        if fund_data and fund_data.get('data') and len(fund_data['data']) > 1:
            returns = calculator.calculate_returns(fund_data['data'], [int(CATEGORY_RANKING_PERIOD[:-1])])
            ranking_return = returns.get(CATEGORY_RANKING_PERIOD)
            if ranking_return is not None:
                fund_performance.append({
                    'name': fund_summary['schemeName'],
                    'code': fund_summary['schemeCode'],
                    'return': ranking_return
                })
                funds_analyzed_count += 1
    
    if not fund_performance:
        return {
            "status": "error",
            "message": f"Could not calculate {CATEGORY_RANKING_PERIOD} returns for any fund in this category sample."
        }
    
    # Sort funds by the ranking return in descending order
    fund_performance.sort(key=lambda x: x['return'], reverse=True)
    
    # Format the top funds for the response
    top_funds = []
    for i, fund in enumerate(fund_performance[:TOP_N_FUNDS_TO_SUGGEST]):
        top_funds.append({
            "rank": i + 1,
            "name": fund['name'],
            "code": fund['code'],
            "return": round(fund['return'], 2)
        })
    
    result = {
        "status": "success",
        "category": selected_category,
        "ranking_period": CATEGORY_RANKING_PERIOD,
        "top_funds": top_funds,
        "funds_analyzed": funds_analyzed_count,
        "total_funds_in_category": len(funds_in_category)
    }
    
    return result
