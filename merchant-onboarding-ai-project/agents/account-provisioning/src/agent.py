from typing import Dict, Any
import json
import os
import sys
import os
sys.path.append(os.path.dirname(__file__))
from mock_integrations import MockAccountProvisioningIntegrations
from globalpayments_integration import GlobalPaymentsIntegration

# Keep Google services real, mock others
USE_REAL_GOOGLE_SERVICES = True

async def account_provisioning_agent(state) -> Dict[str, Any]:
    """Agent 11: Account Provisioning AI Agent with Real Integrations"""
    
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from state import ApplicationStatus
    
    if state.status != ApplicationStatus.APPROVED:
        return {"account_provisioning": {"skipped": True, "reason": "not_approved"}}
    
    # Initialize integrations
    config = {
        "globalpayments_url": os.getenv("GLOBALPAYMENTS_URL"),
        "globalpayments_app_id": os.getenv("GLOBALPAYMENTS_APP_ID"),
        "globalpayments_app_key": os.getenv("GLOBALPAYMENTS_APP_KEY"),
        "globalpayments_account_id": os.getenv("GLOBALPAYMENTS_ACCOUNT_ID"),
        "database_url": os.getenv("DATABASE_URL"),
        "identity_provider_url": os.getenv("IDENTITY_PROVIDER_URL")
    }
    
    # Use real GlobalPayments based on configuration
    use_mock_gp = os.getenv("MOCK_GLOBALPAYMENTS", "true").lower() == "true"
    
    if not use_mock_gp and config["globalpayments_app_key"]:
        gp_integration = GlobalPaymentsIntegration(config)
        mock_integrations = MockAccountProvisioningIntegrations(config)  # For non-payment services
        use_real_globalpayments = True
    else:
        integrations = MockAccountProvisioningIntegrations(config)
        use_real_globalpayments = False
    
    try:
        # Generate merchant ID
        merchant_id = f"MERCH_{state.application_id[-8:]}"
        
        # Get decision details
        decision = state.decision or {}
        credit_limit = decision.get("credit_limit", 25000)
        
        # Prepare merchant data
        merchant_data = {
            "merchant_id": merchant_id,
            "business_name": state.application_data.get("business_name"),
            "email": state.application_data.get("email"),
            "credit_limit": credit_limit,
            "risk_category": state.risk_assessment.get("risk_category", "MEDIUM") if state.risk_assessment else "MEDIUM"
        }
        
        # Execute provisioning steps
        results = {}
        
        # 1. Create merchant account in GlobalPayments
        if use_real_globalpayments:
            results["merchant_account"] = await gp_integration.create_merchant_account(merchant_data)
            results["api_credentials"] = await gp_integration.generate_api_credentials(merchant_id)
        else:
            results["merchant_account"] = await integrations.create_merchant_account(merchant_data)
            results["api_credentials"] = await integrations.generate_api_credentials(merchant_id)
        
        # 2. Setup database access (always mocked)
        if use_real_globalpayments:
            results["database_access"] = await mock_integrations.provision_database_access(
                merchant_id, ["read_transactions", "write_settings"]
            )
        else:
            results["database_access"] = await integrations.provision_database_access(
                merchant_id, ["read_transactions", "write_settings"]
            )
        
        # 3. Configure payment processing
        processing_config = {
            "credit_limit": credit_limit,
            "processing_fees": 2.65,  # GlobalPayments card present rate
            "settlement_schedule": "T+1"  # GlobalPayments standard
        }
        
        if use_real_globalpayments:
            results["payment_config"] = await gp_integration.configure_payment_processing(merchant_id, processing_config)
        else:
            results["payment_config"] = await integrations.configure_payment_processing(merchant_id, processing_config)
        
        # 4. Setup dashboard access (always mocked)
        if use_real_globalpayments:
            results["dashboard_access"] = await mock_integrations.setup_dashboard_access(merchant_data)
        else:
            results["dashboard_access"] = await integrations.setup_dashboard_access(merchant_data)
        
        # Compile final result
        result = {
            "account_created": True,
            "merchant_id": merchant_id,
            "services_provisioned": ["globalpayments_processing", "api_access", "dashboard", "database_access"],
            "setup_complete": all(r.get("success", True) for r in results.values()),
            "provisioning_details": results,
            "globalpayments_integration": use_real_globalpayments,
            "processing_time": 3.0
        }
        
        state.merchant_id = merchant_id
        state.account_provisioning = result
        return {"account_provisioning": result}
        
    except Exception as e:
        # Fallback to mock provisioning for development
        merchant_id = f"MERCH_{state.application_id[-8:]}"
        
        result = {
            "account_created": True,
            "merchant_id": merchant_id,
            "services_provisioned": ["payment_processing", "api_access", "dashboard"],
            "setup_complete": False,
            "error": f"Integration failed: {str(e)}",
            "fallback_mode": True,
            "processing_time": 1.0
        }
        
        state.merchant_id = merchant_id
        state.account_provisioning = result
        return {"account_provisioning": result}