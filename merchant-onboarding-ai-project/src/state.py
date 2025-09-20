from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum

class ApplicationStatus(Enum):
    SUBMITTED = "submitted"
    QUALIFYING = "qualifying"
    PROCESSING = "processing"
    VALIDATING = "validating"
    ASSESSING_RISK = "assessing_risk"
    DECIDING = "deciding"
    APPROVED = "approved"
    DECLINED = "declined"
    EXCEPTION = "exception"

class MerchantOnboardingState(BaseModel):
    # Application Info
    application_id: str
    merchant_id: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    
    # Raw Application Data
    application_data: Dict[str, Any] = {}
    documents: List[Dict[str, Any]] = []
    
    # Agent Results
    market_qualification: Optional[Dict] = None
    document_processing: Optional[Dict] = None
    lead_qualification: Optional[Dict] = None
    application_assistant: Optional[Dict] = None
    data_validation: Optional[Dict] = None
    risk_assessment: Optional[Dict] = None
    decision: Optional[Dict] = None
    exception_routing: Optional[Dict] = None
    communication: Optional[Dict] = None
    compliance_verification: Optional[Dict] = None
    account_provisioning: Optional[Dict] = None
    monitoring: Optional[Dict] = None
    optimization: Optional[Dict] = None
    onboarding_support: Optional[Dict] = None
    
    # Routing & Exceptions
    exceptions: List[str] = []
    routing_queue: Optional[str] = None
    
    # Communication
    communications_sent: List[Dict] = []
    
    # Metadata
    processing_start_time: Optional[str] = None
    processing_end_time: Optional[str] = None
    total_processing_time: Optional[float] = None