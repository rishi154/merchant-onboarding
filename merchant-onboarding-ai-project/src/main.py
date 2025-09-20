import asyncio
import logging
from datetime import datetime
from workflow import create_onboarding_workflow
from state import MerchantOnboardingState, ApplicationStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def process_merchant_application(application_data: dict, documents: list = None):
    """Main entry point for processing merchant applications"""
    
    # Initialize state
    app_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n[START] Starting merchant onboarding for {app_id}")
    print(f"[INFO] Business: {application_data.get('business_name', 'Unknown')}")
    
    state = MerchantOnboardingState(
        application_id=app_id,
        application_data=application_data,
        documents=documents or [],
        processing_start_time=datetime.now().isoformat()
    )
    
    # Create and run workflow
    workflow = create_onboarding_workflow()
    
    try:
        print("\n[WORKFLOW] Executing 14-agent workflow...")
        print(f"[DEBUG] Initial state: {state.status}")
        
        # Execute the workflow
        result = await workflow.ainvoke(state)
        print(f"\n[SUCCESS] Workflow completed successfully!")
        print(f"[DEBUG] Final state: {result.status}")
        
        # Update final processing time - handle both dict and object results
        if hasattr(result, 'processing_end_time'):
            result.processing_end_time = datetime.now().isoformat()
        elif isinstance(result, dict):
            result['processing_end_time'] = datetime.now().isoformat()
        else:
            # Convert dict result back to state object
            if isinstance(result, dict):
                # Create new state with updated values
                updated_state = MerchantOnboardingState(
                    application_id=state.application_id,
                    application_data=state.application_data,
                    documents=state.documents,
                    processing_start_time=state.processing_start_time,
                    processing_end_time=datetime.now().isoformat()
                )
                # Copy over any agent results
                for key, value in result.items():
                    if hasattr(updated_state, key):
                        setattr(updated_state, key, value)
                result = updated_state
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] Workflow execution failed: {e}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        state.status = ApplicationStatus.EXCEPTION
        state.exceptions.append(str(e))
        return state

if __name__ == "__main__":
    # Test application data matching sample documents
    test_application = {
        # Business Information (matches documents)
        "business_name": "TechFlow Solutions LLC",
        "dba_name": "TechFlow Digital Services",
        "business_type": "LLC",
        "industry": "technology",
        "sub_industry": "software_development",
        "business_description": "Software Development Services, Digital Marketing Consulting, E-commerce Platform Management",
        "website": "https://techflowsolutions.com",
        "years_in_business": 1,
        "incorporation_date": "2023-01-15",
        "incorporation_state": "DE",
        
        # Financial Information (based on bank statement)
        "annual_revenue": 1200000,
        "monthly_revenue": 100000,
        "average_transaction_amount": 15000,
        "monthly_transaction_volume": 8,
        "seasonal_business": False,
        "high_season_months": [],
        "bank_name": "First National Bank",
        "bank_account_type": "business_checking",
        "bank_routing_number": "121000248",
        "bank_account_number": "****4567",
        
        # Business Address (matches business license)
        "street": "1247 Innovation Drive",
        "suite": "Suite 300",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94107",
        "country": "US",
        
        # Mailing Address (if different)
        "mailing_same_as_business": True,
        "mailing_street": "",
        "mailing_city": "",
        "mailing_state": "",
        "mailing_zip_code": "",
        
        # Contact Information (matches documents)
        "phone": "415-555-0123",
        "fax": "415-555-0124",
        "email": "contact@techflowsolutions.com",
        "customer_service_phone": "415-555-0125",
        
        # Tax Information (matches business license)
        "tax_id": "87-1234567",
        "tax_id_type": "EIN",
        "state_tax_id": "CA123456789",
        
        # Owner/Principal Information (matches documents)
        "owner_name": "Sarah Chen",
        "owner_title": "Managing Member",
        "owner_ownership_percentage": 100,
        "owner_ssn": "123-45-6789",
        "owner_date_of_birth": "1985-06-15",
        "owner_phone": "415-555-0126",
        "owner_email": "sarah.chen@techflowsolutions.com",
        "owner_address_same_as_business": True,
        "owner_street": "",
        "owner_city": "",
        "owner_state": "",
        "owner_zip_code": "",
        
        # Additional Owners/Principals (if any)
        "additional_owners": [],
        
        # Processing Information
        "processing_type": "card_present_and_not_present",
        "card_present_percentage": 60,
        "card_not_present_percentage": 40,
        "average_ticket": 2500,
        "highest_ticket": 15000,
        "refund_policy": "30_days",
        "delivery_timeframe": "immediate",
        "customer_deposit_percentage": 0,
        
        # Risk Factors
        "international_sales": False,
        "international_sales_percentage": 0,
        "recurring_billing": True,
        "recurring_billing_percentage": 30,
        "previous_processing_terminated": False,
        "previous_chargebacks": False,
        "bankruptcy_history": False,
        
        # Compliance
        "pci_compliance_level": "SAQ_A",
        "data_security_standards": ["PCI_DSS", "SOC2"],
        "regulatory_licenses": [],
        
        # Equipment/Integration
        "pos_system": "Square",
        "ecommerce_platform": "Shopify",
        "accounting_software": "QuickBooks",
        "integration_requirements": ["API", "webhook"],
        
        # Application Metadata
        "application_source": "direct_application",
        "referral_source": "website",
        "sales_rep": None,
        "application_date": "2024-01-15",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Test documents (using real sample documents)
    sample_docs_path = "C:\\work\\boarding\\prototype\\sample_documents"
    test_documents = [
        {
            "id": "doc_001",
            "type": "business_license",
            "path": f"{sample_docs_path}\\business_license.png",
            "filename": "business_license.png",
            "size": 245760,
            "uploaded_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "doc_002",
            "type": "bank_statement",
            "path": f"{sample_docs_path}\\bank_statement.png",
            "filename": "bank_statement.png",
            "size": 189440,
            "uploaded_at": "2024-01-15T10:32:00Z"
        },
        {
            "id": "doc_003",
            "type": "tax_return",
            "path": f"{sample_docs_path}\\tax_return.png",
            "filename": "tax_return.png",
            "size": 312580,
            "uploaded_at": "2024-01-15T10:35:00Z"
        },
        {
            "id": "doc_004",
            "type": "ein_letter",
            "path": f"{sample_docs_path}\\ein_letter.png",
            "filename": "ein_letter.png",
            "size": 156320,
            "uploaded_at": "2024-01-15T10:37:00Z"
        }
    ]
    
    print("MERCHANT ONBOARDING AI SYSTEM - TEST RUN")
    print("=" * 50)
    
    # Run the test
    result = asyncio.run(process_merchant_application(test_application, test_documents))
    
    print("\n[RESULT] Final Result:")
    print(f"Status: {result.status.value if hasattr(result, 'status') else 'Unknown'}")
    print(f"Application ID: {result.application_id if hasattr(result, 'application_id') else 'Unknown'}")
    
    if hasattr(result, 'decision') and result.decision:
        print(f"Decision: {result.decision.get('final_decision', 'No decision recorded')}")
    
    # Show processing summary
    start_time = getattr(result, 'processing_start_time', None) or result.get('processing_start_time') if isinstance(result, dict) else None
    end_time = getattr(result, 'processing_end_time', None) or result.get('processing_end_time') if isinstance(result, dict) else None
    if start_time and end_time:
        print(f"Processing Time: {start_time} to {end_time}")
    
    # Show agent results summary - handle both object and dict
    def get_result(key):
        if hasattr(result, key):
            return getattr(result, key)
        elif isinstance(result, dict):
            return result.get(key)
        return None
    
    agent_results = [
        ('Market Qualification', get_result('market_qualification')),
        ('Document Processing', get_result('document_processing')),
        ('Risk Assessment', get_result('risk_assessment')),
        ('Decision Making', get_result('decision'))
    ]
    
    print("\n[AGENTS] Key Results:")
    for agent_name, agent_result in agent_results:
        if agent_result:
            print(f"  {agent_name}: ✓ Completed")
        else:
            print(f"  {agent_name}: - Not executed")
    
    print("\n[COMPLETE] Test completed!")