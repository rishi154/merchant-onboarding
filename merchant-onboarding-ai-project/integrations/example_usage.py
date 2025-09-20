"""
Example usage of all external integrations with mock/real switching
"""
import asyncio
from integration_factory import IntegrationFactory

async def test_all_integrations():
    """Test all integrations with sample data"""
    
    # Sample business data
    business_data = {
        "business_name": "TechFlow Solutions LLC",
        "annual_revenue": 1200000,
        "street": "1247 Innovation Drive",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94107",
        "tax_id": "87-1234567",
        "phone": "415-555-0123"
    }
    
    # Sample owner data
    owner_data = {
        "owner_name": "Sarah Chen",
        "owner_ssn": "123-45-6789",
        "owner_date_of_birth": "1985-06-15",
        "owner_email": "sarah.chen@techflowsolutions.com"
    }
    
    # Sample bank data
    bank_data = {
        "bank_account_number": "****4567",
        "bank_routing_number": "121000248"
    }
    
    print("Testing Credit Bureau Integrations...")
    
    # Test Experian
    experian = IntegrationFactory.get_credit_bureau_integration("experian")
    experian_result = await experian.business_credit_check(business_data)
    print(f"Experian: {experian_result.get('success')} - Score: {experian_result.get('credit_score')}")
    
    # Test Equifax
    equifax = IntegrationFactory.get_credit_bureau_integration("equifax")
    equifax_result = await equifax.business_credit_check(business_data)
    print(f"Equifax: {equifax_result.get('success')} - Score: {equifax_result.get('credit_score')}")
    
    print("\nTesting KYC Provider Integrations...")
    
    # Test Jumio
    jumio = IntegrationFactory.get_kyc_provider_integration("jumio")
    jumio_result = await jumio.verify_identity(owner_data)
    print(f"Jumio: {jumio_result.get('success')} - Status: {jumio_result.get('verification_status')}")
    
    # Test Onfido
    onfido = IntegrationFactory.get_kyc_provider_integration("onfido")
    onfido_result = await onfido.identity_verification(owner_data)
    print(f"Onfido: {onfido_result.get('success')} - Status: {onfido_result.get('verification_status')}")
    
    print("\nTesting Banking API Integrations...")
    
    # Test Plaid
    plaid = IntegrationFactory.get_banking_api_integration("plaid")
    plaid_result = await plaid.verify_bank_account(bank_data)
    print(f"Plaid: {plaid_result.get('success')} - Verified: {plaid_result.get('account_verified')}")
    
    # Test Yodlee
    yodlee = IntegrationFactory.get_banking_api_integration("yodlee")
    yodlee_result = await yodlee.account_aggregation(bank_data)
    print(f"Yodlee: {yodlee_result.get('success')} - Accounts: {yodlee_result.get('accounts_found')}")
    
    print("\nTesting Government Database Integrations...")
    
    # Test OFAC
    ofac = IntegrationFactory.get_government_database_integration("ofac")
    ofac_result = await ofac.sanctions_check(business_data["business_name"], owner_data["owner_name"])
    print(f"OFAC: {ofac_result.get('success')} - Clear: {ofac_result.get('sanctions_clear')}")
    
    # Test IRS
    irs = IntegrationFactory.get_government_database_integration("irs")
    irs_result = await irs.tax_verification(business_data)
    print(f"IRS: {irs_result.get('success')} - EIN Verified: {irs_result.get('ein_verified')}")

if __name__ == "__main__":
    print("External Integrations Test")
    print("=" * 40)
    print("Set MOCK_* environment variables to 'false' to use real APIs")
    print("=" * 40)
    
    asyncio.run(test_all_integrations())