import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class TransUnionIntegration:
    """Real TransUnion Credit Monitoring API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("TRANSUNION_API_URL", "https://api.transunion.com/v1")
        self.api_key = os.getenv("TRANSUNION_API_KEY")
        
    async def credit_monitoring_check(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit monitoring data from TransUnion"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "businessName": business_data.get("business_name"),
                "taxId": business_data.get("tax_id"),
                "address": {
                    "street": business_data.get("street"),
                    "city": business_data.get("city"),
                    "state": business_data.get("state"),
                    "zip": business_data.get("zip_code")
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/business-credit",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "credit_score": result.get("creditScore", 680),
                        "payment_history": result.get("paymentHistory", "satisfactory"),
                        "transunion_response": result
                    }
                else:
                    return {"success": False, "error": f"TransUnion API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

class MockTransUnionIntegration:
    """Mock TransUnion integration"""
    
    async def credit_monitoring_check(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        revenue = business_data.get("annual_revenue", 0)
        score = 680 + (revenue // 15000) + secrets.randbelow(40) - 20
        return {
            "success": True,
            "credit_score": max(300, min(850, score)),
            "payment_history": secrets.choice(["excellent", "satisfactory", "fair"]),
            "transunion_response": {"mock": True}
        }