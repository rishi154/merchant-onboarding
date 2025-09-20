import asyncio
import secrets
from typing import Dict, Any, List

class MockComplianceIntegrations:
    """Mock compliance and regulatory services (non-Google)"""
    
    async def ofac_sanctions_check(self, business_name: str, owner_name: str = None) -> Dict:
        """Mock OFAC sanctions screening"""
        await asyncio.sleep(0.5)
        
        # Simulate sanctions check (99.9% clear rate)
        is_clear = secrets.randbelow(1000) > 0
        
        return {
            "sanctions_clear": is_clear,
            "business_name": business_name,
            "owner_name": owner_name,
            "matches_found": 0 if is_clear else 1,
            "risk_score": 0.01 if is_clear else 0.95,
            "last_updated": "2024-01-15T10:00:00Z"
        }
    
    async def pep_screening(self, owner_name: str) -> Dict:
        """Mock Politically Exposed Persons screening"""
        await asyncio.sleep(0.3)
        
        # Simulate PEP check (99% clear rate)
        is_clear = secrets.randbelow(100) > 0
        
        return {
            "pep_clear": is_clear,
            "person_name": owner_name,
            "pep_matches": 0 if is_clear else 1,
            "risk_level": "low" if is_clear else "high",
            "jurisdiction": None if is_clear else "foreign"
        }
    
    async def aml_risk_assessment(self, business_data: Dict) -> Dict:
        """Mock AML risk scoring"""
        await asyncio.sleep(0.4)
        
        industry = business_data.get("industry", "")
        country = business_data.get("country", "")
        revenue = business_data.get("annual_revenue", 0)
        
        # Calculate mock AML risk
        risk_score = 0.1  # Base low risk
        
        if industry in ["gambling", "crypto", "money_services"]:
            risk_score += 0.4
        if country not in ["US", "CA", "UK", "AU"]:
            risk_score += 0.3
        if revenue > 10000000:  # $10M+
            risk_score += 0.2
        
        risk_level = "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low"
        
        return {
            "aml_risk_score": min(risk_score, 1.0),
            "risk_level": risk_level,
            "risk_factors": [
                f"high_risk_industry: {industry}" if industry in ["gambling", "crypto"] else None,
                f"high_revenue: ${revenue:,}" if revenue > 10000000 else None,
                f"foreign_jurisdiction: {country}" if country not in ["US", "CA", "UK"] else None
            ],
            "enhanced_dd_required": risk_score > 0.5
        }
    
    async def kyc_identity_verification(self, identity_data: Dict) -> Dict:
        """Mock KYC identity verification"""
        await asyncio.sleep(0.6)
        
        # Simulate identity verification
        verification_success = secrets.randbelow(10) > 0  # 95% success
        
        return {
            "identity_verified": verification_success,
            "verification_method": "document_and_biometric",
            "confidence_score": 0.95 if verification_success else 0.3,
            "document_authentic": verification_success,
            "biometric_match": verification_success,
            "verification_id": f"kyc_{secrets.token_hex(8)}"
        }
    
    async def regulatory_license_check(self, industry: str, state: str) -> Dict:
        """Mock regulatory license verification"""
        await asyncio.sleep(0.3)
        
        # Industries requiring special licenses
        regulated_industries = {
            "financial_services": ["money_transmitter_license"],
            "gambling": ["gaming_license"],
            "healthcare": ["healthcare_provider_license"],
            "cannabis": ["cannabis_business_license"]
        }
        
        required_licenses = regulated_industries.get(industry, [])
        
        return {
            "licenses_required": required_licenses,
            "licenses_verified": len(required_licenses) == 0,  # Assume no licenses for simplicity
            "regulatory_compliant": len(required_licenses) == 0,
            "jurisdiction": state,
            "additional_requirements": ["enhanced_monitoring"] if required_licenses else []
        }