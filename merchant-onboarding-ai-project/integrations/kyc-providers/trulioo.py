import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class TruliooIntegration:
    """Real Trulioo Global Identity Verification API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("TRULIOO_API_URL", "https://api.globaldatacompany.com")
        self.username = os.getenv("TRULIOO_USERNAME")
        self.password = os.getenv("TRULIOO_PASSWORD")
        
    async def global_identity_verification(self, owner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify identity globally using Trulioo"""
        try:
            headers = {
                "Authorization": f"Basic {self.username}:{self.password}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "AcceptTruliooTermsAndConditions": True,
                "CountryCode": "US",
                "DataFields": {
                    "PersonInfo": {
                        "FirstGivenName": owner_data.get("owner_name", "").split()[0],
                        "FirstSurName": " ".join(owner_data.get("owner_name", "").split()[1:]),
                        "DayOfBirth": owner_data.get("owner_date_of_birth", "").split("-")[2] if owner_data.get("owner_date_of_birth") else "",
                        "MonthOfBirth": owner_data.get("owner_date_of_birth", "").split("-")[1] if owner_data.get("owner_date_of_birth") else "",
                        "YearOfBirth": owner_data.get("owner_date_of_birth", "").split("-")[0] if owner_data.get("owner_date_of_birth") else ""
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/verifications/v1/verify",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "verification_status": "verified",
                        "global_watchlist_clear": True,
                        "trulioo_response": result
                    }
                else:
                    return {"success": False, "error": f"Trulioo API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

class MockTruliooIntegration:
    """Mock Trulioo integration"""
    
    async def global_identity_verification(self, owner_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        success = secrets.randbelow(10) > 0
        return {
            "success": True,
            "verification_status": "verified" if success else "unverified",
            "global_watchlist_clear": success,
            "trulioo_response": {"mock": True, "transaction_id": f"mock-{secrets.token_hex(8)}"}
        }