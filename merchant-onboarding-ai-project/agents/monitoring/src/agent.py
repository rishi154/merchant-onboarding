from typing import Dict, Any
import json

async def monitoring_agent(state) -> Dict[str, Any]:
    """Agent 12: Monitoring AI Agent"""
    
    # Calculate processing metrics
    total_agents_run = sum(1 for attr in [
        state.market_qualification,
        state.document_processing,
        state.lead_qualification,
        state.data_validation,
        state.risk_assessment,
        state.decision,
        state.compliance_verification
    ] if attr is not None)
    
    # Processing time calculation
    processing_times = []
    for agent_result in [state.market_qualification, state.document_processing, 
                        state.risk_assessment, state.decision]:
        if agent_result and "processing_time" in agent_result:
            processing_times.append(agent_result["processing_time"])
    
    total_processing_time = sum(processing_times)
    
    # Performance metrics
    metrics = {
        "total_processing_time": total_processing_time,
        "agents_executed": total_agents_run,
        "exceptions_count": len(state.exceptions),
        "automation_rate": 0.85,
        "sla_met": total_processing_time < 300,
        "quality_score": 0.92
    }
    
    # Alerts
    alerts = []
    if total_processing_time > 300:
        alerts.append("sla_breach")
    if len(state.exceptions) > 3:
        alerts.append("high_exception_count")
    
    result = {
        "metrics": metrics,
        "alerts": alerts,
        "performance_summary": {
            "status": "healthy" if not alerts else "warning",
            "processing_efficiency": min(100, (300 / max(total_processing_time, 1)) * 100)
        },
        "processing_time": 0.05
    }
    
    state.monitoring = result
    return {"monitoring": result}