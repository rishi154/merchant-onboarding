"""Centralized configuration for tools"""
import os
from typing import Dict, Any

class ToolConfig:
    """Centralized tool configuration"""
    
    # Mock modes
    MOCK_DOCUMENT_PROCESSING = os.getenv("MOCK_DOCUMENT_PROCESSING", "true").lower() == "true"
    MOCK_GOVERNMENT_DATABASES = os.getenv("MOCK_GOVERNMENT_DATABASES", "true").lower() == "true"
    MOCK_KYC_PROVIDERS = os.getenv("MOCK_KYC_PROVIDERS", "true").lower() == "true"
    MOCK_CREDIT_BUREAUS = os.getenv("MOCK_CREDIT_BUREAUS", "true").lower() == "true"
    
    # Google Cloud
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    GOOGLE_DOC_AI_PROCESSOR_ID = os.getenv("GOOGLE_DOC_AI_PROCESSOR_ID")
    
    # CRM
    SALESFORCE_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID")
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    
    # Risk thresholds
    RISK_THRESHOLD_HIGH = float(os.getenv("RISK_THRESHOLD_HIGH", "0.7"))
    RISK_THRESHOLD_MEDIUM = float(os.getenv("RISK_THRESHOLD_MEDIUM", "0.4"))
    
    # Credit scoring
    CREDIT_SCORE_MIN = int(os.getenv("CREDIT_SCORE_MIN", "300"))
    CREDIT_SCORE_MAX = int(os.getenv("CREDIT_SCORE_MAX", "850"))
    CREDIT_LIMIT_MAX = int(os.getenv("CREDIT_LIMIT_MAX", "100000"))
    
    @classmethod
    def is_configured_for_production(cls) -> bool:
        """Check if all production configs are set"""
        return all([
            cls.GOOGLE_CLOUD_PROJECT,
            cls.GOOGLE_DOC_AI_PROCESSOR_ID,
            cls.SALESFORCE_CLIENT_ID,
            cls.HUBSPOT_API_KEY
        ])
    
    @classmethod
    def get_document_config(cls) -> Dict[str, Any]:
        """Get document processing configuration"""
        return {
            "use_mock": cls.MOCK_DOCUMENT_PROCESSING,
            "google_project": cls.GOOGLE_CLOUD_PROJECT,
            "google_location": cls.GOOGLE_CLOUD_LOCATION,
            "processor_id": cls.GOOGLE_DOC_AI_PROCESSOR_ID
        }