"""
Suggestion module for mutual fund analyzer.
Handles generating analysis suggestions and recommendations.
"""

def generate_suggestion(analysis_results):
    """Generates a textual suggestion based on the analysis results (fund vs index)."""
    fund_returns = analysis_results.get("fund_returns", {})
    index_returns = analysis_results.get("index_returns", {})
    fund_name = analysis_results.get("fund_info", {}).get("schemeName", "The fund")
    
    if not fund_returns:
        return {
            "status": "error",
            "message": "Could not generate suggestion due to missing fund return data."
        }
      # Check if any index data is available at all
    has_index_data = any(i_ret is not None for i_ret in index_returns.values())
    
    summary_points = []
    overall_score = 0  # Simple scoring: +1 for outperform index, -1 for underperform
    periods_compared = 0 # Counts periods where BOTH fund and index data are available
    
    # Use sorted periods for consistent output
    sorted_periods = sorted([p for p in fund_returns if fund_returns[p] is not None], 
                           key=lambda p: int(p[:-1]))
    
    period_details = []
    for period in sorted_periods:
        f_ret = fund_returns.get(period)
        i_ret = index_returns.get(period)
        
        period_summary = []
        
        period_data = {
            "period": period,
            "fund_return": round(f_ret, 2) if f_ret is not None else None,
            "index_return": round(i_ret, 2) if i_ret is not None else None,
            "difference": None,
            "outperforms": None
        }
        
        # Compare with Index only if index data exists for this period
        if i_ret is not None:
            diff = f_ret - i_ret
            comparison = "outperformed" if diff > 0 else "underperformed"
            period_summary.append(f"{comparison} index ({i_ret:.2f}%) by {abs(diff):.2f}%pts")
            overall_score += 1 if diff > 0 else -1
            periods_compared += 1 # Increment only when comparison is possible
            
            period_data["difference"] = round(diff, 2)
            period_data["outperforms"] = diff > 0
        elif has_index_data: # If index data exists overall but not for this period
             period_summary.append("index N/A for period")
        # If no index data exists at all, don't mention index in period summary
        
        if period_summary:
            summary_points.append(f"- {period} ({f_ret:.2f}%): {', '.join(period_summary)}.") # Corrected this line
        else: # If only fund return is available
            summary_points.append(f"- {period} ({f_ret:.2f}%): Fund return available.")
            
        period_details.append(period_data)
    
    # Generate conclusion text
    conclusion = ""
    if not has_index_data:
        conclusion = "Benchmark index (NIFTY 50) data is currently unavailable. Cannot perform comparison."
    elif periods_compared == 0:
        conclusion = "Not enough comparable periods with benchmark data to draw a conclusion."
    else:
        relative_score = overall_score / periods_compared
        if relative_score > 0.5:
            conclusion = "Shows strong outperformance relative to the index across compared periods."
        elif relative_score > 0:
            conclusion = "Shows moderate outperformance relative to the index."
        elif relative_score == 0:
            conclusion = "Performance is roughly in line with the index."
        elif relative_score > -0.5:
            conclusion = "Shows moderate underperformance relative to the index."
        else:
            conclusion = "Shows significant underperformance relative to the index across compared periods."
    
    # Format the result as a structured object for API response
    result = {
        "status": "success",
        "fund_name": fund_name,
        "fund_category": analysis_results.get("fund_info", {}).get("scheme_category", "N/A"),
        "scheme_code": analysis_results.get("fund_info", {}).get("scheme_code", "N/A"),
        "period_details": period_details,
        "conclusion": conclusion,
        "summary_text": "\n".join(summary_points) if summary_points else "Insufficient data for comparison."
    }
    
    return result
