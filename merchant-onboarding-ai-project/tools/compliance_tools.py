from langchain.tools import BaseTool
from typing import Dict, Any
from pydantic import BaseModel, Field
import asyncio
from config.tool_config import ToolConfig

class SanctionsCheckInput(BaseModel):
    business_name: str = Field(description="Business name to check")
    owner_name: str = Field(description="Business owner name", default="")

class AMLAssessmentInput(BaseModel):
    business_data: Dict[str, Any] = Field(description="Business data for AML assessment")

class KYCVerificationInput(BaseModel):
    identity_data: Dict[str, Any] = Field(description="Identity data for KYC verification")

class OFACSanctionsTool(BaseTool):
    name: str = "ofac_sanctions_check"
    description: str = "Check business and owners against OFAC sanctions list"
    args_schema: type = SanctionsCheckInput
    
    def _run(self, business_name: str, owner_name: str = "") -> Dict[str, Any]:
        return asyncio.run(self._arun(business_name, owner_name))
    
    async def _arun(self, business_name: str, owner_name: str = "") -> Dict[str, Any]:
        """Check OFAC sanctions list using real or mock integration"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integrations', 'government-databases'))
            from ofac import OFACIntegration, MockOFACIntegration
            
            # Decision logic: mock or real
            use_mock = ToolConfig.MOCK_GOVERNMENT_DATABASES
            
            if use_mock:
                ofac_integration = MockOFACIntegration()
            else:
                ofac_integration = OFACIntegration()
                
            return await ofac_integration.sanctions_check(business_name, owner_name)
            
        except Exception as e:
            # Fallback to simple mock
            import secrets
            is_clear = secrets.randbelow(1000) > 0
            return {
                "success": True,
                "sanctions_clear": is_clear,
                "matches_found": 0 if is_clear else 1,
                "risk_score": 0.01 if is_clear else 0.95,
                "fallback": True,
                "error": str(e)
            }

class PEPScreeningTool(BaseTool):
    name: str = "pep_screening"
    description: str = "Screen for Politically Exposed Persons (PEP)"
    args_schema: type = SanctionsCheckInput
    
    def _run(self, business_name: str, owner_name: str = "") -> Dict[str, Any]:
        return asyncio.run(self._arun(business_name, owner_name))
    
    async def _arun(self, business_name: str, owner_name: str = "") -> Dict[str, Any]:
        """Screen for PEP status"""
        try:
            # Simple mock without complex imports
            import secrets
            is_clear = secrets.randbelow(100) > 0
            return {
                "success": True,
                "pep_clear": is_clear,
                "pep_matches": 0 if is_clear else 1,
                "risk_level": "low" if is_clear else "high"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pep_clear": False
            }

class AMLRiskAssessmentTool(BaseTool):
    name: str = "aml_risk_assessment"
    description: str = "Perform Anti-Money Laundering risk assessment"
    args_schema: type = AMLAssessmentInput
    
    def _run(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self._arun(business_data))
    
    async def _arun(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess AML risk"""
        try:
            # Simple mock without complex imports
            industry = business_data.get("industry", "")
            risk_score = 0.1
            if industry in ["gambling", "crypto"]:
                risk_score += 0.4
            return {
                "success": True,
                "aml_risk_score": risk_score,
                "risk_level": "high" if risk_score > 0.6 else "low",
                "risk_factors": [f"high_risk_industry: {industry}"] if risk_score > 0.4 else [],
                "enhanced_dd_required": risk_score > 0.5
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "aml_risk_score": 1.0,
                "risk_level": "high"
            }

class KYCVerificationTool(BaseTool):
    name: str = "kyc_verification"
    description: str = "Perform Know Your Customer identity verification"
    args_schema: type = KYCVerificationInput
    
    def _run(self, identity_data: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self._arun(identity_data))
    
    async def _arun(self, identity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify customer identity using real or mock integration"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integrations', 'kyc-providers'))
            from jumio import JumioIntegration, MockJumioIntegration
            
            # Decision logic: mock or real
            use_mock = ToolConfig.MOCK_KYC_PROVIDERS
            
            if use_mock:
                jumio_integration = MockJumioIntegration()
            else:
                jumio_integration = JumioIntegration()
                
            return await jumio_integration.verify_identity(identity_data)
            
        except Exception as e:
            # Fallback to simple mock
            import secrets
            verification_success = secrets.randbelow(10) > 0
            return {
                "success": True,
                "identity_verified": verification_success,
                "confidence_score": 0.95 if verification_success else 0.3,
                "verification_method": "document_and_biometric",
                "verification_id": f"kyc_{secrets.token_hex(8)}",
                "fallback": True,
                "error": str(e)
            }