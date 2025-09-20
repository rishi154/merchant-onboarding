import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class MXIntegration:
    """Real MX Account Verification API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("MX_API_URL", "https://api.mx.com")
        self.client_id = os.getenv("MX_CLIENT_ID")
        self.api_key = os.getenv("MX_API_KEY")
        
    async def account_verification(self, bank_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify accounts using MX"""
        try:
            headers = {
                "Authorization": f"Basic {self.client_id}:{self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create user
            user_payload = {
                "user": {
                    "identifier": bank_data.get("bank_account_number", "user123")
                }
            }
            
            async with httpx.AsyncClient() as client:
                user_response = await client.post(
                    f"{self.api_url}/users",
                    json=user_payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if user_response.status_code == 200:
                    user_guid = user_response.json()["user"]["guid"]
                    
                    # Get accounts
                    accounts_response = await client.get(
                        f"{self.api_url}/users/{user_guid}/accounts",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if accounts_response.status_code == 200:
                        result = accounts_response.json()
                        return {
                            "success": True,
                            "verification_complete": True,
                            "categorized_accounts": len(result.get("accounts", [])),
                            "mx_response": result
                        }
                
                return {"success": False, "error": "MX API error"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

class MockMXIntegration:
    """Mock MX integration"""
    
    async def account_verification(self, bank_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {
            "success": True,
            "verification_complete": True,
            "categorized_accounts": secrets.randbelow(3) + 1,
            "mx_response": {"mock": True}
        }