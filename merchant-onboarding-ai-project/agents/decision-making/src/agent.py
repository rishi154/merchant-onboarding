from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def decision_making_agent(state) -> Dict[str, Any]:
    """Agent 7: Decision Making AI Agent"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Decision Making Agent",
        "final approval/decline decisions and credit limit determination",
        """Make final merchant onboarding decision based on all agent assessments.
        
        Consider all factors:
        1. Market qualification results
        2. Document processing confidence
        3. Risk assessment scores
        4. Data validation results
        5. Compliance requirements
        6. Business policy rules
        
        Determine:
        - Approval/decline decision
        - Credit limit (if approved)
        - Pricing tier
        - Special conditions
        
        Return JSON with: decision (APPROVED/DECLINED/MANUAL_REVIEW), credit_limit, pricing_tier, decision_factors, confidence, reasoning, conditions"""
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = await chain.ainvoke({
            "application_data": json.dumps(state.application_data),
            "documents": json.dumps(state.documents),
            "previous_results": json.dumps({
                "market_qualification": state.market_qualification,
                "document_processing": state.document_processing,
                "risk_assessment": state.risk_assessment,
                "data_validation": state.data_validation
            })
        })
        
        result.setdefault("processing_time", 0.5)
        
        # Update state status based on decision
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
        from state import ApplicationStatus
        if result.get("decision") == "APPROVED":
            state.status = ApplicationStatus.APPROVED
        elif result.get("decision") == "DECLINED":
            state.status = ApplicationStatus.DECLINED
        else:
            state.status = ApplicationStatus.EXCEPTION
        
        state.decision = result
        return {"decision": result}
        
    except Exception as e:
        # Fallback decision logic
        qualified = state.market_qualification.get("qualified", False) if state.market_qualification else False
        risk_score = state.risk_assessment.get("risk_score", 100) if state.risk_assessment else 100
        
        if qualified and risk_score <= 50:
            decision = "APPROVED"
            credit_limit = 25000
        elif not qualified or risk_score >= 80:
            decision = "DECLINED"
            credit_limit = 0
        else:
            decision = "MANUAL_REVIEW"
            credit_limit = 0
        
        result = {
            "decision": decision,
            "credit_limit": credit_limit,
            "error": str(e),
            "processing_time": 0.5
        }
        
        state.decision = result
        return {"decision": result}