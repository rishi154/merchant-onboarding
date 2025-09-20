"""Document-first workflow for merchant onboarding"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from workflow import create_onboarding_workflow
from state import MerchantOnboardingState

async def document_first_onboarding(documents: List[Dict], business_name: str = None) -> Dict[str, Any]:
    """Complete document-first onboarding workflow"""
    
    # Initialize workflow
    workflow = create_onboarding_workflow()
    
    # Create initial state
    state = MerchantOnboardingState(
        application_id=f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        business_name=business_name or "Unknown Business",
        documents=documents,
        application_data={},  # Will be populated from document processing
        processing_start_time=datetime.now().isoformat()
    )
    
    try:
        # Execute workflow
        print("\n[WORKFLOW] Starting document-first merchant onboarding...")
        result = await workflow.ainvoke(state)
        
        # Update completion time
        result.processing_end_time = datetime.now().isoformat()
        
        return {
            "application_id": result.application_id,
            "status": result.status.value if hasattr(result.status, 'value') else str(result.status),
            "workflow_type": "document_first",
            "documents": result.documents,
            "application_data": result.application_data,
            "agent_results": {
                "market_qualification": result.market_qualification,
                "lead_qualification": result.lead_qualification,
                "document_processing": result.document_processing,
                "data_validation": result.data_validation,
                "risk_assessment": result.risk_assessment,
                "compliance_verification": result.compliance_verification,
                "decision": result.decision,
                "exception_routing": result.exception_routing,
                "communication": result.communication,
                "account_provisioning": result.account_provisioning,
                "monitoring": result.monitoring,
                "optimization": result.optimization,
                "onboarding_support": result.onboarding_support
            },
            "processing_start_time": result.processing_start_time,
            "processing_end_time": result.processing_end_time
        }
        
    except Exception as e:
        print(f"[ERROR] Workflow failed: {str(e)}")
        raise