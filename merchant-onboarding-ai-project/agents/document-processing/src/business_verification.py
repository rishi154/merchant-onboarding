from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
import os
from datetime import datetime
from enum import Enum

class VerificationLevel(Enum):
    BASIC = "basic"          # Basic registration check
    STANDARD = "standard"    # Registration + license
    ENHANCED = "enhanced"    # Full verification including risk data

class BusinessVerificationService:
    """Comprehensive business verification using multiple providers"""
    
    def __init__(self):
        # API credentials from environment
        self.dnb_api_key = os.getenv("DNB_API_KEY", "")
        self.dnb_endpoint = os.getenv("DNB_ENDPOINT", "https://api.dnb.com/v1")
        
        self.lexis_api_key = os.getenv("LEXISNEXIS_API_KEY", "")
        self.lexis_endpoint = os.getenv("LEXISNEXIS_ENDPOINT", "https://api.lexisnexis.com/v1")
        
        # SOS API credentials (state-specific)
        self.sos_credentials = self._load_sos_credentials()
        
        # Initialize session
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _load_sos_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load Secretary of State API credentials for each state"""
        # In production, load from secure configuration
        return {
            state: {
                "api_key": os.getenv(f"SOS_{state}_API_KEY", ""),
                "endpoint": os.getenv(f"SOS_{state}_ENDPOINT", "")
            }
            for state in ["CA", "NY", "DE", "TX"]  # Add more states as needed
        }
    
    async def verify_business(self, 
                            business_name: str,
                            tax_id: str,
                            state: str,
                            level: VerificationLevel = VerificationLevel.STANDARD
                            ) -> Dict[str, Any]:
        """Perform comprehensive business verification"""
        try:
            # Basic verification tasks
            tasks = [
                self._verify_registration(business_name, state),
                self._verify_tax_id(tax_id)
            ]
            
            # Add enhanced verification if needed
            if level in [VerificationLevel.STANDARD, VerificationLevel.ENHANCED]:
                tasks.extend([
                    self._verify_license(business_name, state),
                    self._get_dnb_report(business_name, tax_id)
                ])
            
            # Add risk verification for enhanced level
            if level == VerificationLevel.ENHANCED:
                tasks.extend([
                    self._get_lexis_risk_report(business_name, tax_id),
                    self._verify_ownership(business_name, tax_id)
                ])
            
            # Run all verifications in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            verification_result = self._combine_verification_results(results, level)
            
            return {
                "success": True,
                "verification_level": level.value,
                "timestamp": datetime.utcnow().isoformat(),
                "results": verification_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "verification_level": level.value
            }
    
    async def _verify_registration(self, business_name: str, state: str) -> Dict[str, Any]:
        """Verify business registration with Secretary of State"""
        if state not in self.sos_credentials:
            raise ValueError(f"No SOS integration for state: {state}")
        
        credentials = self.sos_credentials[state]
        endpoint = f"{credentials['endpoint']}/business/search"
        
        async with self.session.get(
            endpoint,
            params={"name": business_name},
            headers={"Authorization": f"Bearer {credentials['api_key']}"}
        ) as response:
            data = await response.json()
            
            return {
                "source": "sos",
                "state": state,
                "registered": data.get("found", False),
                "status": data.get("status"),
                "registration_date": data.get("registration_date"),
                "expiration_date": data.get("expiration_date")
            }
    
    async def _verify_license(self, business_name: str, state: str) -> Dict[str, Any]:
        """Verify business licenses with state agencies"""
        if state not in self.sos_credentials:
            raise ValueError(f"No license verification for state: {state}")
        
        credentials = self.sos_credentials[state]
        endpoint = f"{credentials['endpoint']}/license/verify"
        
        async with self.session.get(
            endpoint,
            params={"business_name": business_name},
            headers={"Authorization": f"Bearer {credentials['api_key']}"}
        ) as response:
            data = await response.json()
            
            return {
                "source": "state_license",
                "state": state,
                "has_license": data.get("has_license", False),
                "license_type": data.get("license_type"),
                "license_status": data.get("status"),
                "expiration_date": data.get("expiration_date")
            }
    
    async def _get_dnb_report(self, business_name: str, tax_id: str) -> Dict[str, Any]:
        """Get Dun & Bradstreet business report"""
        endpoint = f"{self.dnb_endpoint}/company/report"
        
        async with self.session.post(
            endpoint,
            json={
                "business_name": business_name,
                "tax_id": tax_id,
                "report_type": "business_verification"
            },
            headers={"Authorization": f"Bearer {self.dnb_api_key}"}
        ) as response:
            data = await response.json()
            
            return {
                "source": "dnb",
                "duns_number": data.get("duns"),
                "business_score": data.get("business_score"),
                "years_in_business": data.get("years_in_business"),
                "financial_stability": data.get("financial_stability"),
                "risk_indicators": data.get("risk_indicators", [])
            }
    
    async def _get_lexis_risk_report(self, business_name: str, tax_id: str) -> Dict[str, Any]:
        """Get LexisNexis risk assessment report"""
        endpoint = f"{self.lexis_endpoint}/business/risk"
        
        async with self.session.post(
            endpoint,
            json={
                "business_name": business_name,
                "tax_id": tax_id,
                "report_type": "comprehensive"
            },
            headers={"Authorization": f"Bearer {self.lexis_api_key}"}
        ) as response:
            data = await response.json()
            
            return {
                "source": "lexisnexis",
                "risk_score": data.get("risk_score"),
                "risk_factors": data.get("risk_factors", []),
                "compliance_alerts": data.get("compliance_alerts", []),
                "legal_events": data.get("legal_events", []),
                "sanctions_check": data.get("sanctions_check", {})
            }
    
    async def _verify_tax_id(self, tax_id: str) -> Dict[str, Any]:
        """Verify Tax ID format and status"""
        # In production, integrate with IRS API
        # For now, basic format validation
        is_valid = len(tax_id) == 9 and tax_id.isdigit()
        
        return {
            "source": "tax_id",
            "is_valid": is_valid,
            "format_check": "valid" if is_valid else "invalid"
        }
    
    async def _verify_ownership(self, business_name: str, tax_id: str) -> Dict[str, Any]:
        """Verify business ownership structure"""
        endpoint = f"{self.lexis_endpoint}/business/ownership"
        
        async with self.session.post(
            endpoint,
            json={
                "business_name": business_name,
                "tax_id": tax_id
            },
            headers={"Authorization": f"Bearer {self.lexis_api_key}"}
        ) as response:
            data = await response.json()
            
            return {
                "source": "ownership",
                "ownership_type": data.get("ownership_type"),
                "beneficial_owners": data.get("beneficial_owners", []),
                "ownership_changes": data.get("ownership_changes", []),
                "verification_level": data.get("verification_level")
            }
    
    def _combine_verification_results(self, results: List[Dict[str, Any]], 
                                   level: VerificationLevel) -> Dict[str, Any]:
        """Combine results from different verification sources"""
        verification_result = {
            "registration": None,
            "license": None,
            "tax_id": None,
            "dnb_report": None,
            "risk_assessment": None,
            "ownership": None
        }
        
        for result in results:
            if isinstance(result, Exception):
                continue
                
            source = result.get("source")
            if source == "sos":
                verification_result["registration"] = result
            elif source == "state_license":
                verification_result["license"] = result
            elif source == "tax_id":
                verification_result["tax_id"] = result
            elif source == "dnb":
                verification_result["dnb_report"] = result
            elif source == "lexisnexis":
                verification_result["risk_assessment"] = result
            elif source == "ownership":
                verification_result["ownership"] = result
        
        # Add verification summary
        verification_result["summary"] = self._generate_verification_summary(
            verification_result, level
        )
        
        return verification_result
    
    def _generate_verification_summary(self, results: Dict[str, Any], 
                                    level: VerificationLevel) -> Dict[str, Any]:
        """Generate a summary of verification results"""
        summary = {
            "verified": True,
            "risk_level": "low",
            "warnings": [],
            "flags": []
        }
        
        # Check registration
        reg = results.get("registration", {})
        if not reg.get("registered"):
            summary["verified"] = False
            summary["flags"].append("business_not_registered")
        
        # Check license if required
        if level != VerificationLevel.BASIC:
            lic = results.get("license", {})
            if not lic.get("has_license"):
                summary["verified"] = False
                summary["flags"].append("no_valid_license")
        
        # Check risk factors for enhanced verification
        if level == VerificationLevel.ENHANCED:
            risk = results.get("risk_assessment", {})
            risk_score = risk.get("risk_score", 0)
            
            if risk_score > 70:
                summary["risk_level"] = "high"
                summary["flags"].extend(risk.get("risk_factors", []))
            elif risk_score > 40:
                summary["risk_level"] = "medium"
                summary["warnings"].extend(risk.get("risk_factors", []))
        
        return summary