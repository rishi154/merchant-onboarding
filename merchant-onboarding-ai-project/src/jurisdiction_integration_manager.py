"""Jurisdiction-aware integration manager for regional providers"""
from typing import Dict, Any, Optional
import asyncio
from jurisdiction_service import JurisdictionService

class JurisdictionIntegrationManager:
    """Manages jurisdiction-specific integration providers"""
    
    REGIONAL_PROVIDERS = {
        "US": {
            "credit_bureau": {
                "primary": "experian_us",
                "secondary": "equifax_us",
                "tertiary": "transunion_us"
            },
            "bank_verification": {
                "primary": "plaid",
                "secondary": "yodlee",
                "tertiary": "finicity"
            },
            "business_registry": {
                "primary": "secretary_of_state",
                "secondary": "duns_bradstreet"
            },
            "sanctions_screening": {
                "primary": "ofac",
                "secondary": "dow_jones"
            },
            "identity_verification": {
                "primary": "jumio",
                "secondary": "onfido"
            }
        },
        "UK": {
            "credit_bureau": {
                "primary": "experian_uk",
                "secondary": "equifax_uk",
                "tertiary": "callcredit"
            },
            "bank_verification": {
                "primary": "truelayer",
                "secondary": "yapily",
                "tertiary": "token"
            },
            "business_registry": {
                "primary": "companies_house",
                "secondary": "creditsafe_uk"
            },
            "sanctions_screening": {
                "primary": "hmt_sanctions",
                "secondary": "world_check"
            },
            "identity_verification": {
                "primary": "onfido",
                "secondary": "jumio"
            }
        },
        "EU": {
            "credit_bureau": {
                "primary": "schufa",
                "secondary": "creditreform",
                "tertiary": "coface"
            },
            "bank_verification": {
                "primary": "tink",
                "secondary": "nordigen",
                "tertiary": "salt_edge"
            },
            "business_registry": {
                "primary": "european_business_registry",
                "secondary": "creditsafe_eu"
            },
            "sanctions_screening": {
                "primary": "eu_sanctions",
                "secondary": "world_check"
            },
            "identity_verification": {
                "primary": "trulioo",
                "secondary": "onfido"
            }
        },
        "CA": {
            "credit_bureau": {
                "primary": "equifax_ca",
                "secondary": "transunion_ca"
            },
            "bank_verification": {
                "primary": "flinks",
                "secondary": "yodlee_ca"
            },
            "business_registry": {
                "primary": "corporations_canada",
                "secondary": "provincial_registries"
            },
            "sanctions_screening": {
                "primary": "fintrac",
                "secondary": "osfi_sanctions"
            },
            "identity_verification": {
                "primary": "jumio",
                "secondary": "trulioo"
            }
        }
    }
    
    def __init__(self, jurisdiction: str = "US"):
        self.jurisdiction = jurisdiction
        self.jurisdiction_service = JurisdictionService()
        self.providers = self.REGIONAL_PROVIDERS.get(jurisdiction, self.REGIONAL_PROVIDERS["US"])
        
    def get_provider(self, service_type: str, preference: str = "primary") -> Optional[str]:
        """Get provider for service type and preference"""
        service_providers = self.providers.get(service_type, {})
        return service_providers.get(preference)
    
    async def call_service_with_fallback(self, service_type: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call service with automatic fallback to secondary providers"""
        
        providers_to_try = ["primary", "secondary", "tertiary"]
        last_error = None
        
        for preference in providers_to_try:
            provider = self.get_provider(service_type, preference)
            if not provider:
                continue
                
            try:
                result = await self._call_provider(provider, method, data)
                result["provider_used"] = provider
                result["fallback_level"] = preference
                return result
                
            except Exception as e:
                last_error = e
                print(f"Provider {provider} failed: {e}, trying next...")
                continue
        
        # All providers failed
        return {
            "success": False,
            "error": f"All providers failed. Last error: {last_error}",
            "provider_used": None,
            "fallback_level": "failed"
        }
    
    async def _call_provider(self, provider: str, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call specific provider - implement actual API calls here"""
        
        # Credit Bureau Calls
        if provider.startswith("experian"):
            return await self._call_experian(provider, method, data)
        elif provider.startswith("equifax"):
            return await self._call_equifax(provider, method, data)
        elif provider == "schufa":
            return await self._call_schufa(method, data)
            
        # Bank Verification Calls
        elif provider == "plaid":
            return await self._call_plaid(method, data)
        elif provider == "truelayer":
            return await self._call_truelayer(method, data)
        elif provider == "tink":
            return await self._call_tink(method, data)
        elif provider == "flinks":
            return await self._call_flinks(method, data)
            
        # Business Registry Calls
        elif provider == "companies_house":
            return await self._call_companies_house(method, data)
        elif provider == "secretary_of_state":
            return await self._call_secretary_of_state(method, data)
        elif provider == "corporations_canada":
            return await self._call_corporations_canada(method, data)
            
        # Sanctions Screening
        elif provider == "ofac":
            return await self._call_ofac(method, data)
        elif provider == "hmt_sanctions":
            return await self._call_hmt_sanctions(method, data)
        elif provider == "eu_sanctions":
            return await self._call_eu_sanctions(method, data)
        elif provider == "fintrac":
            return await self._call_fintrac(method, data)
            
        # Identity Verification
        elif provider == "jumio":
            return await self._call_jumio(method, data)
        elif provider == "onfido":
            return await self._call_onfido(method, data)
        elif provider == "trulioo":
            return await self._call_trulioo(method, data)
            
        else:
            raise Exception(f"Unknown provider: {provider}")
    
    # Provider-specific implementations (mock for now)
    async def _call_experian(self, provider: str, method: str, data: Dict) -> Dict:
        """Call Experian API (US/UK variants)"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        if method == "credit_check":
            return {
                "success": True,
                "credit_score": 720,
                "credit_grade": "B",
                "provider": provider,
                "jurisdiction": "US" if "us" in provider else "UK"
            }
        
        return {"success": True, "provider": provider}
    
    async def _call_equifax(self, provider: str, method: str, data: Dict) -> Dict:
        """Call Equifax API (US/CA variants)"""
        await asyncio.sleep(0.1)
        
        if method == "credit_check":
            return {
                "success": True,
                "credit_score": 680,
                "credit_grade": "C",
                "provider": provider,
                "jurisdiction": "US" if "us" in provider else "CA"
            }
        
        return {"success": True, "provider": provider}
    
    async def _call_schufa(self, method: str, data: Dict) -> Dict:
        """Call SCHUFA API (Germany/EU)"""
        await asyncio.sleep(0.1)
        
        if method == "credit_check":
            return {
                "success": True,
                "schufa_score": 85,
                "risk_class": "B",
                "provider": "schufa",
                "jurisdiction": "EU"
            }
        
        return {"success": True, "provider": "schufa"}
    
    async def _call_plaid(self, method: str, data: Dict) -> Dict:
        """Call Plaid API (US)"""
        await asyncio.sleep(0.1)
        
        if method == "verify_account":
            return {
                "success": True,
                "account_verified": True,
                "account_type": "checking",
                "bank_name": "Chase Bank",
                "provider": "plaid"
            }
        
        return {"success": True, "provider": "plaid"}
    
    async def _call_truelayer(self, method: str, data: Dict) -> Dict:
        """Call TrueLayer API (UK)"""
        await asyncio.sleep(0.1)
        
        if method == "verify_account":
            return {
                "success": True,
                "account_verified": True,
                "account_type": "current",
                "bank_name": "Barclays",
                "provider": "truelayer"
            }
        
        return {"success": True, "provider": "truelayer"}
    
    async def _call_tink(self, method: str, data: Dict) -> Dict:
        """Call Tink API (EU)"""
        await asyncio.sleep(0.1)
        
        if method == "verify_account":
            return {
                "success": True,
                "account_verified": True,
                "account_type": "checking",
                "bank_name": "Deutsche Bank",
                "provider": "tink"
            }
        
        return {"success": True, "provider": "tink"}
    
    async def _call_flinks(self, method: str, data: Dict) -> Dict:
        """Call Flinks API (Canada)"""
        await asyncio.sleep(0.1)
        
        if method == "verify_account":
            return {
                "success": True,
                "account_verified": True,
                "account_type": "chequing",
                "bank_name": "Royal Bank of Canada",
                "provider": "flinks"
            }
        
        return {"success": True, "provider": "flinks"}
    
    async def _call_companies_house(self, method: str, data: Dict) -> Dict:
        """Call Companies House API (UK)"""
        await asyncio.sleep(0.1)
        
        if method == "lookup_company":
            return {
                "success": True,
                "company_status": "active",
                "company_number": "12345678",
                "incorporation_date": "2020-01-15",
                "provider": "companies_house"
            }
        
        return {"success": True, "provider": "companies_house"}
    
    async def _call_secretary_of_state(self, method: str, data: Dict) -> Dict:
        """Call Secretary of State API (US)"""
        await asyncio.sleep(0.1)
        
        if method == "lookup_business":
            return {
                "success": True,
                "business_status": "active",
                "registration_number": "LLC123456",
                "registration_date": "2020-03-10",
                "provider": "secretary_of_state"
            }
        
        return {"success": True, "provider": "secretary_of_state"}
    
    async def _call_corporations_canada(self, method: str, data: Dict) -> Dict:
        """Call Corporations Canada API"""
        await asyncio.sleep(0.1)
        
        if method == "lookup_corporation":
            return {
                "success": True,
                "corporation_status": "active",
                "corporation_number": "123456789",
                "incorporation_date": "2019-11-20",
                "provider": "corporations_canada"
            }
        
        return {"success": True, "provider": "corporations_canada"}
    
    async def _call_ofac(self, method: str, data: Dict) -> Dict:
        """Call OFAC API (US)"""
        await asyncio.sleep(0.1)
        
        if method == "sanctions_check":
            return {
                "success": True,
                "sanctions_match": False,
                "confidence_score": 0.95,
                "provider": "ofac"
            }
        
        return {"success": True, "provider": "ofac"}
    
    async def _call_hmt_sanctions(self, method: str, data: Dict) -> Dict:
        """Call HM Treasury Sanctions API (UK)"""
        await asyncio.sleep(0.1)
        
        if method == "sanctions_check":
            return {
                "success": True,
                "sanctions_match": False,
                "confidence_score": 0.92,
                "provider": "hmt_sanctions"
            }
        
        return {"success": True, "provider": "hmt_sanctions"}
    
    async def _call_eu_sanctions(self, method: str, data: Dict) -> Dict:
        """Call EU Sanctions API"""
        await asyncio.sleep(0.1)
        
        if method == "sanctions_check":
            return {
                "success": True,
                "sanctions_match": False,
                "confidence_score": 0.90,
                "provider": "eu_sanctions"
            }
        
        return {"success": True, "provider": "eu_sanctions"}
    
    async def _call_fintrac(self, method: str, data: Dict) -> Dict:
        """Call FINTRAC API (Canada)"""
        await asyncio.sleep(0.1)
        
        if method == "sanctions_check":
            return {
                "success": True,
                "sanctions_match": False,
                "confidence_score": 0.88,
                "provider": "fintrac"
            }
        
        return {"success": True, "provider": "fintrac"}
    
    async def _call_jumio(self, method: str, data: Dict) -> Dict:
        """Call Jumio API"""
        await asyncio.sleep(0.1)
        
        if method == "verify_identity":
            return {
                "success": True,
                "identity_verified": True,
                "confidence_score": 0.95,
                "document_type": "passport",
                "provider": "jumio"
            }
        
        return {"success": True, "provider": "jumio"}
    
    async def _call_onfido(self, method: str, data: Dict) -> Dict:
        """Call Onfido API"""
        await asyncio.sleep(0.1)
        
        if method == "verify_identity":
            return {
                "success": True,
                "identity_verified": True,
                "confidence_score": 0.93,
                "document_type": "driving_license",
                "provider": "onfido"
            }
        
        return {"success": True, "provider": "onfido"}
    
    async def _call_trulioo(self, method: str, data: Dict) -> Dict:
        """Call Trulioo API"""
        await asyncio.sleep(0.1)
        
        if method == "verify_identity":
            return {
                "success": True,
                "identity_verified": True,
                "confidence_score": 0.91,
                "document_type": "national_id",
                "provider": "trulioo"
            }
        
        return {"success": True, "provider": "trulioo"}