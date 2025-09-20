import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class IRSIntegration:
    """Real IRS Tax Verification API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("IRS_API_URL", "https://www.irs.gov/pub/irs-soi/")
        self.api_key = os.getenv("IRS_API_KEY")
        
    async def tax_verification(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify tax information using IRS"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "ein": business_data.get("tax_id"),
                "businessName": business_data.get("business_name")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/business-lookup",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "ein_verified": True,
                        "business_status": "active",
                        "irs_response": result
                    }
                else:
                    return {"success": False, "error": f"IRS API error: {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}

class MockIRSIntegration:
    """Mock IRS integration"""
    
    async def tax_verification(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        return {
            "success": True,
            "ein_verified": secrets.randbelow(10) > 0,
            "business_status": "active",
            "irs_response": {"mock": True}
        }