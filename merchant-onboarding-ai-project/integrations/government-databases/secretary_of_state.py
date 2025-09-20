import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class SecretaryOfStateIntegration:
    """Real Secretary of State Business Registration API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("SOS_API_URL", "https://api.opencorporates.com/v0.4")
        self.api_key = os.getenv("SOS_API_KEY")
        
    async def business_registration_lookup(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Look up business registration"""
        try:
            state = business_data.get("state", "").lower()
            params = {
                "q": business_data.get("business_name"),
                "jurisdiction_code": f"us_{state}",
                "format": "json",
                "api_token": self.api_key
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/companies/search",
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    companies = result.get("results", {}).get("companies", [])
                    
                    if companies:
                        company = companies[0].get("company", {})
                        return {
                            "success": True,
                            "registration_found": True,
                            "business_status": company.get("current_status", "unknown").lower(),
                            "incorporation_date": company.get("incorporation_date"),
                            "sos_response": company
                        }
                    else:
                        return {
                            "success": True,
                            "registration_found": False,
                            "business_status": "not_found"
                        }
                else:
                    return {"success": False, "error": f"SOS API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

class MockSecretaryOfStateIntegration:
    """Mock Secretary of State integration"""
    
    async def business_registration_lookup(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        found = secrets.randbelow(10) > 0
        
        if found:
            return {
                "success": True,
                "registration_found": True,
                "business_status": "active",
                "incorporation_date": "2020-03-15",
                "sos_response": {"mock": True}
            }
        else:
            return {
                "success": True,
                "registration_found": False,
                "business_status": "not_found"
            }