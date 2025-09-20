from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def market_qualification_agent(state) -> Dict[str, Any]:
    """Agent 1: Market Qualification AI Agent"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Market Qualification Agent",
        "merchant market analysis and qualification",
        """Analyze the merchant application to determine market qualification.
        
        Evaluate:
        1. Revenue requirements (minimum $100k annually)
        2. Geographic eligibility (US, CA, UK markets)
        3. Platform compatibility (Shopify, WooCommerce, custom)
        4. Industry risk factors
        5. Business model viability
        
        Return JSON with: qualified (boolean), score (0-1), revenue_check, geo_check, platform_check, risk_factors, reasoning"""
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        print(f"[DEBUG] Market Qualification Agent starting...")
        result = await chain.ainvoke({
            "application_data": json.dumps(state.application_data),
            "documents": json.dumps(state.documents),
            "previous_results": "{}"
        })
        
        result.setdefault("processing_time", 0.1)
        result.setdefault("requires_manual_review", result.get("score", 0) < 0.67)
        
        print(f"[DEBUG] Market Qualification completed: {result.get('qualified', 'unknown')}")
        return {"market_qualification": result}
        
    except Exception as e:
        print(f"[DEBUG] Market Qualification using fallback due to: {e}")
        app_data = state.application_data
        revenue_qualified = app_data.get("annual_revenue", 0) >= 100000
        geo_qualified = app_data.get("country", "US") in ["US", "CA", "UK"]
        platform_qualified = True  # Default to qualified
        
        # Add risk assessment for workflow routing
        risk_score = 0
        if app_data.get("annual_revenue", 0) < 100000: risk_score += 25
        if app_data.get("industry", "").lower() in ["gambling", "crypto", "adult"]: risk_score += 40
        if app_data.get("country", "US") not in ["US", "CA", "UK"]: risk_score += 15
        
        risk_tier = "HIGH" if risk_score > 50 else "MEDIUM" if risk_score > 25 else "LOW"
        workflow_pattern = "comprehensive" if risk_tier == "HIGH" else "standard" if risk_tier == "MEDIUM" else "express"
        
        result = {
            "qualified": all([revenue_qualified, geo_qualified, platform_qualified]),
            "score": sum([revenue_qualified, geo_qualified, platform_qualified]) / 3,
            "revenue_check": revenue_qualified,
            "geo_check": geo_qualified,
            "platform_check": platform_qualified,
            "risk_score": risk_score,
            "risk_tier": risk_tier,
            "workflow_pattern": workflow_pattern,
            "error": str(e),
            "processing_time": 0.1
        }
        
        return {"market_qualification": result}