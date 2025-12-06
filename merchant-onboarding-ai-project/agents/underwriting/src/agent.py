from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def underwriting_agent(state) -> Dict[str, Any]:
    """Agent: Underwriting AI Agent - Financial risk assessment and credit analysis"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Underwriting Agent",
        "financial risk assessment, credit scoring, and underwriting decisions",
        """Perform comprehensive underwriting analysis for merchant onboarding.
        
        Analyze:
        1. Financial statements and cash flow
        2. Credit history and payment behavior
        3. Business model and revenue stability
        4. Industry-specific risk factors
        5. Debt-to-income ratios
        6. Collateral and guarantees
        
        Calculate:
        - Credit score (300-850)
        - Recommended credit limit
        - Risk-based pricing tier
        - Required conditions/covenants
        
        Return JSON with: credit_score, credit_limit, pricing_tier, underwriting_decision (APPROVE/DECLINE/CONDITIONAL), risk_factors, conditions, processing_time"""
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = await chain.ainvoke({
            "application_data": json.dumps(state.application_data),
            "documents": json.dumps(state.documents),
            "previous_results": json.dumps({
                "document_processing": state.document_processing,
                "risk_assessment": state.risk_assessment,
                "data_validation": state.data_validation
            })
        })
        
        result.setdefault("processing_time", 0.8)
        
        state.underwriting = result
        return {"underwriting": result}
        
    except Exception as e:
        # Fallback underwriting logic
        risk_score = state.risk_assessment.get("risk_score", 50) if state.risk_assessment else 50
        qualified = state.market_qualification.get("qualified", True) if state.market_qualification else True
        
        # Calculate credit score based on risk
        if risk_score <= 30:
            credit_score = 750 + (30 - risk_score) * 2
        elif risk_score <= 70:
            credit_score = 650 + (70 - risk_score) * 2.5
        else:
            credit_score = 500 + (100 - risk_score) * 1.5
        
        # Determine credit limit
        if credit_score >= 720:
            credit_limit = 100000
            pricing_tier = "PREMIUM"
        elif credit_score >= 650:
            credit_limit = 50000
            pricing_tier = "STANDARD"
        elif credit_score >= 580:
            credit_limit = 25000
            pricing_tier = "BASIC"
        else:
            credit_limit = 0
            pricing_tier = "DECLINED"
        
        # Underwriting decision
        if credit_score >= 580 and qualified:
            underwriting_decision = "APPROVE"
        elif credit_score >= 500:
            underwriting_decision = "CONDITIONAL"
        else:
            underwriting_decision = "DECLINE"
        
        result = {
            "credit_score": int(credit_score),
            "credit_limit": credit_limit,
            "pricing_tier": pricing_tier,
            "underwriting_decision": underwriting_decision,
            "risk_factors": [f"Risk score: {risk_score}", f"Qualified: {qualified}"],
            "conditions": ["Standard monitoring"] if underwriting_decision == "CONDITIONAL" else [],
            "error": str(e),
            "processing_time": 0.8
        }
        
        state.underwriting = result
        return {"underwriting": result}