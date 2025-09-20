from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def onboarding_support_agent(state) -> Dict[str, Any]:
    """Agent 14: Onboarding Support AI Agent"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from state import ApplicationStatus
    
    if state.status != ApplicationStatus.APPROVED:
        return {"onboarding_support": {"skipped": True, "reason": "not_approved"}}
    
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Onboarding Support Agent",
        "personalized merchant onboarding and support planning",
        """Create personalized onboarding plan for approved merchant.
        
        Analyze merchant profile to determine:
        1. Technical sophistication level
        2. Integration complexity requirements
        3. Business size and transaction volume expectations
        4. Industry-specific onboarding needs
        5. Risk profile considerations
        6. Support level and communication preferences
        
        Generate:
        - Customized onboarding checklist with priorities
        - Support level assignment (basic/standard/premium/enterprise)
        - Follow-up schedule based on merchant needs
        - Integration timeline and milestones
        - Training recommendations
        - Success metrics and checkpoints
        
        Return JSON with: onboarding_checklist, support_level, followup_schedule, estimated_completion_days, training_plan, success_metrics"""
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = await chain.ainvoke({
            "application_data": json.dumps(state.application_data),
            "documents": json.dumps(state.documents),
            "previous_results": json.dumps({
                "risk_assessment": state.risk_assessment,
                "decision": state.decision,
                "account_provisioning": state.account_provisioning
            })
        })
        
        result.setdefault("processing_time", 0.8)
        result.setdefault("requires_dedicated_support", 
                         state.application_data.get("annual_revenue", 0) > 1000000)
        
        state.onboarding_support = result
        return {"onboarding_support": result}
        
    except Exception as e:
        # Fallback onboarding plan
        business_size = "large" if state.application_data.get("annual_revenue", 0) > 1000000 else "small"
        support_level = "premium" if business_size == "large" else "standard"
        
        checklist_items = [
            {"task": "api_integration_guide", "status": "pending", "priority": "high"},
            {"task": "test_transaction", "status": "pending", "priority": "high"},
            {"task": "webhook_setup", "status": "pending", "priority": "medium"},
            {"task": "dashboard_training", "status": "pending", "priority": "medium"},
            {"task": "compliance_documentation", "status": "pending", "priority": "low"}
        ]
        
        followup_schedule = [
            {"type": "welcome_call", "days": 1},
            {"type": "integration_check", "days": 7},
            {"type": "first_month_review", "days": 30}
        ]
        
        result = {
            "onboarding_checklist": checklist_items,
            "support_level": support_level,
            "followup_schedule": followup_schedule,
            "estimated_completion_days": 10,
            "requires_dedicated_support": business_size == "large",
            "error": str(e),
            "processing_time": 0.8
        }
        
        state.onboarding_support = result
        return {"onboarding_support": result}