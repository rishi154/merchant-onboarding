import asyncio
import httpx
import secrets
from typing import Dict, Any

class GlobalPaymentsIntegration:
    """Real GlobalPayments API integration for merchant onboarding"""
    
    def __init__(self, config: Dict):
        self.base_url = config.get("globalpayments_url", "https://apis.globalpay.com/ucp")
        self.app_id = config.get("globalpayments_app_id")
        self.app_key = config.get("globalpayments_app_key")
        self.account_id = config.get("globalpayments_account_id")
        
    async def create_merchant_account(self, merchant_data: Dict) -> Dict:
        """Create merchant account via GlobalPayments API"""
        
        headers = {
            "Content-Type": "application/json",
            "X-GP-Version": "2021-03-22",
            "Authorization": f"Bearer {self.app_key}"
        }
        
        payload = {
            "account_id": self.account_id,
            "type": "MERCHANT",
            "name": merchant_data["business_name"],
            "status": "ACTIVE",
            "addresses": [{
                "line_1": merchant_data.get("street"),
                "city": merchant_data.get("city"),
                "state": merchant_data.get("state"),
                "country": merchant_data.get("country", "US"),
                "postal_code": merchant_data.get("zip_code")
            }],
            "payment_processing_config": {
                "default_currency": "USD",
                "merchant_category_code": "5734"  # Computer software stores
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/accounts",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "merchant_id": result.get("id"),
                    "account_id": result.get("id"),
                    "status": result.get("status"),
                    "globalpayments_response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"GlobalPayments API error: {response.status_code}",
                    "response": response.text
                }
    
    async def configure_payment_processing(self, merchant_id: str, config: Dict) -> Dict:
        """Configure payment processing settings"""
        
        headers = {
            "Content-Type": "application/json",
            "X-GP-Version": "2021-03-22",
            "Authorization": f"Bearer {self.app_key}"
        }
        
        payload = {
            "processing_config": {
                "card_processing": {
                    "enabled": True,
                    "daily_limit": config.get("credit_limit", 25000),
                    "monthly_limit": config.get("credit_limit", 25000) * 30
                },
                "ach_processing": {
                    "enabled": True,
                    "daily_limit": config.get("credit_limit", 25000)
                },
                "settlement": {
                    "schedule": config.get("settlement_schedule", "T+1"),
                    "currency": "USD"
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/accounts/{merchant_id}",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "merchant_id": merchant_id,
                    "processing_enabled": True,
                    "globalpayments_config": result.get("processing_config", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"GlobalPayments config error: {response.status_code}",
                    "response": response.text
                }
    
    async def generate_api_credentials(self, merchant_id: str) -> Dict:
        """Generate API credentials for merchant"""
        
        headers = {
            "Content-Type": "application/json", 
            "X-GP-Version": "2021-03-22",
            "Authorization": f"Bearer {self.app_key}"
        }
        
        payload = {
            "permissions": ["TRN_POST_Authorize", "TRN_POST_Capture", "TRN_POST_Refund"],
            "name": f"API Key for {merchant_id}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/accounts/{merchant_id}/credentials",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "api_key": result.get("app_key"),
                    "app_id": result.get("app_id"),
                    "credentials_id": result.get("id"),
                    "permissions": result.get("permissions", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"GlobalPayments credentials error: {response.status_code}",
                    "response": response.text
                }