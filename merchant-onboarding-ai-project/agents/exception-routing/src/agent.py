from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def exception_routing_agent(state) -> Dict[str, Any]:
    """Agent 8: Exception Routing AI Agent"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Exception Routing Agent",
        "intelligent exception analysis and routing optimization",
        """Analyze application exceptions and determine optimal routing strategy.
        
        Consider multiple factors:
        1. Exception severity and complexity
        2. Specialist availability and expertise
        3. SLA requirements and urgency
        4. Historical resolution patterns
        5. Merchant profile and business impact
        6. Workload distribution across teams
        
        Determine:
        - Routing queue assignment
        - Priority level (CRITICAL/HIGH/MEDIUM/LOW)
        - Estimated resolution time
        - Required specialist skills
        - Escalation triggers
        
        Return JSON with: routing_queue, priority, estimated_resolution_hours, required_skills, escalation_conditions, routing_reasoning"""
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
                "data_validation": state.data_validation,
                "compliance_verification": state.compliance_verification
            })
        })
        
        result.setdefault("processing_time", 0.3)
        
        # Extract exceptions for state
        exceptions = []
        if state.market_qualification and not state.market_qualification.get("qualified"):
            exceptions.append("market_qualification_failed")
        if state.document_processing and state.document_processing.get("requires_manual_review"):
            exceptions.append("document_review_required")
        if state.risk_assessment and state.risk_assessment.get("requires_manual_review"):
            exceptions.append("high_risk_review")
        if state.data_validation and state.data_validation.get("requires_manual_review"):
            exceptions.append("data_discrepancy")
        
        result["exceptions_found"] = len(exceptions)
        result["exception_types"] = exceptions
        
        state.exceptions = exceptions
        state.routing_queue = result.get("routing_queue", "standard")
        
        return {"exception_routing": result}
        
    except Exception as e:
        # Fallback routing logic
        exceptions = []
        routing_queue = "standard"
        
        if state.market_qualification and not state.market_qualification.get("qualified"):
            exceptions.append("market_qualification_failed")
            routing_queue = "decline_queue"
        
        if state.document_processing and state.document_processing.get("requires_manual_review"):
            exceptions.append("document_review_required")
            routing_queue = "document_specialist"
        
        if state.risk_assessment and state.risk_assessment.get("requires_manual_review"):
            exceptions.append("high_risk_review")
            routing_queue = "senior_underwriter"
        
        priority = "HIGH" if "high_risk_review" in exceptions else "MEDIUM" if exceptions else "LOW"
        
        result = {
            "exceptions_found": len(exceptions),
            "exception_types": exceptions,
            "routing_queue": routing_queue,
            "priority": priority,
            "estimated_resolution_hours": len(exceptions) * 0.5,
            "error": str(e),
            "processing_time": 0.3
        }
        
        state.exceptions = exceptions
        state.routing_queue = routing_queue
        
        return {"exception_routing": result}