import asyncio
import httpx
import os
import secrets
from typing import Dict, Any

class EquifaxIntegration:
    """Real Equifax Credit API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("EQUIFAX_API_URL", "https://api.equifax.com/business/commercial-credit/v1")
        self.client_id = os.getenv("EQUIFAX_CLIENT_ID")
        self.client_secret = os.getenv("EQUIFAX_CLIENT_SECRET")
        
    async def business_credit_check(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get business credit report from Equifax"""
        try:
            headers = {
                "Authorization": f"Bearer {self.client_secret}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "businessName": business_data.get("business_name"),
                "address": {
                    "street": business_data.get("street"),
                    "city": business_data.get("city"),
                    "state": business_data.get("state"),
                    "zipCode": business_data.get("zip_code")
                },
                "taxId": business_data.get("tax_id")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/credit-report",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "credit_score": result.get("creditScore", 650),
                        "credit_limit": result.get("recommendedLimit", 30000),
                        "risk_tier": "low" if result.get("creditScore", 650) >= 700 else "medium" if result.get("creditScore", 650) >= 600 else "high",
                        "approval_probability": 0.9 if result.get("creditScore", 650) >= 700 else 0.7 if result.get("creditScore", 650) >= 600 else 0.3,
                        "equifax_response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Equifax API error: {response.status_code}",
                        "credit_score": 0,
                        "credit_limit": 0
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "credit_score": 0,
                "credit_limit": 0
            }

class MockEquifaxIntegration:
    """Mock Equifax integration"""
    
    async def business_credit_check(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        revenue = business_data.get("annual_revenue", 0)
        score = 650 + (revenue // 10000) + secrets.randbelow(50) - 25
        credit_score = max(300, min(850, score))
        credit_limit = min(75000, revenue * 0.15)
        
        return {
            "success": True,
            "credit_score": credit_score,
            "credit_limit": int(credit_limit),
            "risk_tier": "low" if credit_score >= 700 else "medium" if credit_score >= 600 else "high",
            "approval_probability": 0.9 if credit_score >= 700 else 0.7 if credit_score >= 600 else "high",
            "equifax_response": {"mock": True, "creditScore": credit_score, "recommendedLimit": int(credit_limit)}
        }