import asyncio
import secrets
from typing import Dict, Any

class MockAccountProvisioningIntegrations:
    """Mock integrations for testing - simulates external API responses"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    async def create_merchant_account(self, merchant_data: Dict) -> Dict:
        """Mock GlobalPayments merchant account creation"""
        await asyncio.sleep(0.1)  # Simulate API delay
        return {
            "success": True,
            "merchant_id": f"GP_{secrets.token_hex(6).upper()}",
            "account_id": f"acct_{secrets.token_hex(8)}",
            "status": "ACTIVE",
            "approval_status": "APPROVED",
            "created_at": "2024-01-15T10:30:00Z",
            "globalpayments_response": {
                "response_code": "00",
                "response_message": "SUCCESS"
            }
        }
    
    async def generate_api_credentials(self, merchant_id: str) -> Dict:
        """Mock API credential generation"""
        await asyncio.sleep(0.1)
        api_key = f"sk_live_{merchant_id}_{secrets.token_urlsafe(16)}"
        webhook_secret = secrets.token_urlsafe(12)
        
        return {
            "api_key": api_key[:20] + "...",
            "webhook_secret": webhook_secret[:10] + "...",
            "credentials_stored": True,
            "vault_path": f"/secrets/merchants/{merchant_id}"
        }
    
    async def provision_database_access(self, merchant_id: str, permissions: list) -> Dict:
        """Mock database provisioning"""
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "database_user": f"merchant_{merchant_id}",
            "permissions_granted": permissions,
            "connection_string": f"postgresql://merchant_{merchant_id}:***@db.example.com/merchants",
            "schema_created": True
        }
    
    async def setup_dashboard_access(self, merchant_data: Dict) -> Dict:
        """Mock dashboard user creation"""
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "user_id": f"user_{secrets.token_hex(6)}",
            "email": merchant_data["email"],
            "role": "merchant_admin",
            "dashboard_url": f"https://dashboard.example.com/merchant/{merchant_data['merchant_id']}",
            "login_credentials_sent": True
        }
    
    async def configure_payment_processing(self, merchant_id: str, config: Dict) -> Dict:
        """Mock GlobalPayments processing configuration"""
        await asyncio.sleep(0.1)
        return {
            "success": True,
            "merchant_id": merchant_id,
            "processing_enabled": True,
            "daily_limit": config.get("credit_limit", 25000),
            "monthly_limit": config.get("credit_limit", 25000) * 30,
            "processing_fees": {
                "card_present": 2.65,
                "card_not_present": 2.95,
                "ach": 0.75,
                "international": 3.45
            },
            "settlement_schedule": config.get("settlement_schedule", "T+1"),
            "supported_methods": [
                "visa", "mastercard", "amex", "discover", 
                "ach", "echeck", "apple_pay", "google_pay"
            ],
            "globalpayments_config": {
                "terminal_id": f"GP{secrets.randbelow(999999):06d}",
                "merchant_category_code": "5734",  # Computer software stores
                "currency": "USD",
                "batch_close_time": "23:59"
            },
            "webhook_endpoints": [
                f"https://api.globalpayments.com/webhooks/transaction/{merchant_id}",
                f"https://api.globalpayments.com/webhooks/settlement/{merchant_id}",
                f"https://api.globalpayments.com/webhooks/chargeback/{merchant_id}"
            ]
        }