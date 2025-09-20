import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class YodleeIntegration:
    """Real Yodlee Account Aggregation API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("YODLEE_API_URL", "https://api.yodlee.com/ysl")
        self.client_id = os.getenv("YODLEE_CLIENT_ID")
        self.secret = os.getenv("YODLEE_SECRET")
        
    async def account_aggregation(self, bank_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate account data using Yodlee"""
        try:
            # Get access token
            auth_payload = {
                "clientId": self.client_id,
                "secret": self.secret
            }
            
            async with httpx.AsyncClient() as client:
                auth_response = await client.post(
                    f"{self.api_url}/auth/token",
                    json=auth_payload,
                    timeout=30.0
                )
                
                if auth_response.status_code == 200:
                    token = auth_response.json()["token"]["accessToken"]
                    
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    accounts_response = await client.get(
                        f"{self.api_url}/accounts",
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if accounts_response.status_code == 200:
                        result = accounts_response.json()
                        return {
                            "success": True,
                            "accounts_found": len(result.get("account", [])),
                            "total_balance": sum(acc.get("balance", {}).get("amount", 0) for acc in result.get("account", [])),
                            "yodlee_response": result
                        }
                
                return {"success": False, "error": "Yodlee API error"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

class MockYodleeIntegration:
    """Mock Yodlee integration"""
    
    async def account_aggregation(self, bank_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        return {
            "success": True,
            "accounts_found": secrets.randbelow(3) + 1,
            "total_balance": 125450.00 + secrets.randbelow(100000),
            "yodlee_response": {"mock": True}
        }