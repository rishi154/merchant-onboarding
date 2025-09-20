import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import process_merchant_application

async def run_complete_example():
    """Run a complete example with all 14 agents"""
    
    sample_application = {
        "business_name": "TechStart Solutions Inc",
        "annual_revenue": 750000,
        "country": "US",
        "state": "CA",
        "platform": "shopify",
        "industry": "technology",
        "years_in_business": 4,
        "email": "contact@techstart.com",
        "phone": "555-123-4567",
        "street": "123 Tech Ave",
        "city": "San Francisco",
        "marketing_source": "organic",
        "monthly_traffic": 15000,
        "social_followers": 5000,
        "ssn": "123-45-6789",
        "business_license": "CA-TECH-2020-001",
        "employees": 25
    }
    
    sample_documents = [
        {"id": "doc1", "type": "business_license", "path": "/uploads/license.pdf"},
        {"id": "doc2", "type": "bank_statement", "path": "/uploads/statement.pdf"},
        {"id": "doc3", "type": "tax_return", "path": "/uploads/tax_return.pdf"}
    ]
    
    print("🚀 Starting merchant onboarding workflow with all 14 agents...")
    print("=" * 60)
    
    result = await process_merchant_application(sample_application, sample_documents)
    
    print(f"📋 Application ID: {result.application_id}")
    print(f"🏪 Merchant ID: {result.merchant_id or 'Not assigned'}")
    print(f"📊 Final Status: {result.status}")
    print(f"⏱️  Total Processing Time: {result.total_processing_time or 'Not calculated'}")
    print()
    
    # Agent Results Summary
    agents_run = []
    if result.market_qualification: agents_run.append("✅ Market Qualification")
    if result.lead_qualification: agents_run.append("✅ Lead Qualification") 
    if result.application_assistant: agents_run.append("✅ Application Assistant")
    if result.document_processing: agents_run.append("✅ Document Processing")
    if result.data_validation: agents_run.append("✅ Data Validation")
    if result.risk_assessment: agents_run.append("✅ Risk Assessment")
    if result.compliance_verification: agents_run.append("✅ Compliance Verification")
    if result.decision: agents_run.append("✅ Decision Making")
    if result.exception_routing: agents_run.append("✅ Exception Routing")
    if result.communication: agents_run.append("✅ Communication")
    if result.account_provisioning: agents_run.append("✅ Account Provisioning")
    if result.monitoring: agents_run.append("✅ Monitoring")
    if result.optimization: agents_run.append("✅ Optimization")
    if result.onboarding_support: agents_run.append("✅ Onboarding Support")
    
    print("🤖 Agents Executed:")
    for agent in agents_run:
        print(f"   {agent}")
    
    print()
    if result.decision:
        print(f"🎯 Decision: {result.decision.get('decision', 'Unknown')}")
        if result.decision.get('credit_limit'):
            print(f"💳 Credit Limit: ${result.decision.get('credit_limit'):,}")
    
    if result.exceptions:
        print(f"⚠️  Exceptions: {', '.join(result.exceptions)}")
    
    print("=" * 60)
    print("✨ Workflow completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_complete_example())