import asyncio
import httpx
import base64
import os
from typing import Dict, Any
from ..interfaces import ICreditBureauIntegration

class ExperianIntegration(ICreditBureauIntegration):
    """Real Experian Business Credit API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("EXPERIAN_API_URL", "https://sandbox-us-api.experian.com/businessinformation/businesses/v1")
        self.client_id = os.getenv("EXPERIAN_CLIENT_ID")
        self.client_secret = os.getenv("EXPERIAN_CLIENT_SECRET")
        self.username = os.getenv("EXPERIAN_USERNAME")
        self.password = os.getenv("EXPERIAN_PASSWORD")
        
    async def get_access_token(self) -> str:
        """Get OAuth access token from Experian"""
        auth_url = "https://sandbox-us-api.experian.com/oauth2/v1/token"
        
        # Basic auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials",
            "username": self.username,
            "password": self.password
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(auth_url, headers=headers, data=data, timeout=30.0)
            
            if response.status_code == 200:
                return response.json()["access_token"]
            else:
                raise Exception(f"Experian auth failed: {response.status_code}")
    
    async def business_credit_check(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get business credit report from Experian"""
        try:
            access_token = await self.get_access_token()
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Experian business search payload
            payload = {
                "name": business_data.get("business_name"),
                "address": {
                    "street": business_data.get("street"),
                    "city": business_data.get("city"),
                    "state": business_data.get("state"),
                    "zip": business_data.get("zip_code")
                },
                "phone": business_data.get("phone"),
                "taxId": business_data.get("tax_id")
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/search",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract credit information
                    business_info = result.get("results", [{}])[0] if result.get("results") else {}
                    
                    return {
                        "success": True,
                        "credit_score": business_info.get("creditScore", 0),
                        "credit_limit": business_info.get("recommendedCreditLimit", 25000),
                        "risk_tier": self._calculate_risk_tier(business_info.get("creditScore", 0)),
                        "approval_probability": self._calculate_approval_probability(business_info.get("creditScore", 0)),
                        "experian_response": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Experian API error: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "credit_score": 0,
                "credit_limit": 10000
            }
    
    def _calculate_risk_tier(self, credit_score: int) -> str:
        """Calculate risk tier based on credit score"""
        if credit_score >= 700:
            return "low"
        elif credit_score >= 600:
            return "medium"
        else:
            return "high"
    
    def _calculate_approval_probability(self, credit_score: int) -> float:
        """Calculate approval probability based on credit score"""
        if credit_score >= 700:
            return 0.9
        elif credit_score >= 600:
            return 0.7
        else:
            return 0.3

class MockExperianIntegration:
    """Mock Experian integration for development/testing"""
    
    async def business_credit_check(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock business credit check with real API response structure"""
        import secrets
        
        # Generate realistic mock data
        revenue = business_data.get("annual_revenue", 0)
        
        # Base credit score calculation
        if revenue > 1000000:
            base_score = 750
        elif revenue > 500000:
            base_score = 650
        elif revenue > 100000:
            base_score = 600
        else:
            base_score = 550
            
        # Add some randomness
        credit_score = base_score + secrets.randbelow(50) - 25
        credit_score = max(300, min(850, credit_score))
        
        # Calculate credit limit
        if credit_score >= 750:
            credit_limit = min(100000, revenue * 0.2)
        elif credit_score >= 650:
            credit_limit = min(50000, revenue * 0.1)
        else:
            credit_limit = min(25000, revenue * 0.05)
        
        # Match real Experian API response structure
        mock_experian_response = {
            "results": [{
                "creditScore": credit_score,
                "recommendedCreditLimit": int(credit_limit),
                "businessInfo": {
                    "name": business_data.get("business_name", "Mock Business"),
                    "address": {
                        "street": business_data.get("street", "123 Mock St"),
                        "city": business_data.get("city", "Mock City"),
                        "state": business_data.get("state", "CA"),
                        "zip": business_data.get("zip_code", "90210")
                    }
                }
            }]
        }
        
        return {
            "success": True,
            "credit_score": credit_score,
            "credit_limit": int(credit_limit),
            "risk_tier": "low" if credit_score >= 700 else "medium" if credit_score >= 600 else "high",
            "approval_probability": 0.9 if credit_score >= 700 else 0.7 if credit_score >= 600 else 0.3,
            "experian_response": mock_experian_response
        }

