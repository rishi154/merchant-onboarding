from typing import Dict, Any

async def application_assistant_agent(state) -> Dict[str, Any]:
    """Agent 4: Application Assistant - 85% automated"""
    
    app_data = state.application_data
    
    # Validate required fields
    required_fields = ["business_name", "annual_revenue", "country", "industry"]
    missing_fields = [field for field in required_fields if not app_data.get(field)]
    
    # Data quality checks
    completeness = (len(required_fields) - len(missing_fields)) / len(required_fields)
    
    # Auto-completion suggestions
    suggestions = []
    if app_data.get("country") == "US" and not app_data.get("state"):
        suggestions.append("state_required")
    if app_data.get("annual_revenue", 0) > 1000000 and not app_data.get("employees"):
        suggestions.append("employee_count_recommended")
    
    result = {
        "completeness_score": completeness,
        "missing_fields": missing_fields,
        "suggestions": suggestions,
        "validation_errors": len(missing_fields),
        "requires_assistance": completeness < 0.8 or len(suggestions) > 2,
        "processing_time": 0.1
    }
    
    state.application_assistant = result
    return {"application_assistant": result}