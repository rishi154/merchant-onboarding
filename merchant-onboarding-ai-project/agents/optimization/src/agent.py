from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def optimization_agent(state) -> Dict[str, Any]:
    """Agent 13: Optimization AI Agent"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Optimization Agent",
        "workflow analysis and performance optimization",
        """Analyze workflow performance and identify optimization opportunities.
        
        Perform comprehensive analysis:
        1. Processing time bottlenecks and efficiency gaps
        2. Exception patterns and root cause analysis
        3. Agent performance and accuracy metrics
        4. Resource utilization and capacity planning
        5. Automation opportunities and threshold tuning
        6. Predictive insights for future improvements
        
        Provide actionable recommendations:
        - Immediate performance improvements
        - Process automation enhancements
        - Model tuning suggestions
        - Infrastructure optimizations
        - SLA and threshold adjustments
        
        Return JSON with: bottlenecks_identified, optimization_recommendations, performance_score, automation_opportunities, model_improvements, infrastructure_suggestions"""
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
                "compliance_verification": state.compliance_verification,
                "decision": state.decision,
                "exception_routing": getattr(state, 'exception_routing', None),
                "monitoring": getattr(state, 'monitoring', None)
            })
        })
        
        result.setdefault("processing_time", 0.5)
        result.setdefault("requires_manual_review", 
                         result.get("performance_score", 100) < 70)
        
        state.optimization = result
        return {"optimization": result}
        
    except Exception as e:
        # Fallback optimization analysis
        bottlenecks = []
        recommendations = []
        
        # Check processing times
        if state.document_processing and state.document_processing.get("processing_time", 0) > 5:
            bottlenecks.append("document_processing_slow")
            recommendations.append("optimize_ocr_service")
        
        if state.risk_assessment and state.risk_assessment.get("requires_manual_review"):
            bottlenecks.append("risk_assessment_manual")
            recommendations.append("refine_risk_model")
        
        # Exception analysis
        exception_rate = len(state.exceptions) / max(1, len([x for x in [
            state.market_qualification, state.document_processing, 
            state.data_validation, state.risk_assessment
        ] if x]))
        
        if exception_rate > 0.3:
            recommendations.append("reduce_exception_triggers")
        
        result = {
            "bottlenecks_identified": bottlenecks,
            "optimization_recommendations": recommendations,
            "performance_score": max(0, 100 - (exception_rate * 50) - (len(bottlenecks) * 10)),
            "automation_opportunities": {
                "parallel_processing": exception_rate < 0.2,
                "auto_approval_threshold": state.risk_assessment.get("risk_score", 100) < 20 if state.risk_assessment else False,
                "document_pre_validation": True
            },
            "error": str(e),
            "processing_time": 0.5
        }
        
        state.optimization = result
        return {"optimization": result}