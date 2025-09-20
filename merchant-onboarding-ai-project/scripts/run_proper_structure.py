import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import process_merchant_application

async def run_with_proper_structure():
    """Run example using proper agent folder structure"""
    
    sample_application = {
        "business_name": "TechStart Solutions Inc",
        "annual_revenue": 750000,
        "country": "US",
        "platform": "shopify",
        "industry": "technology",
        "years_in_business": 4,
        "marketing_source": "organic",
        "monthly_traffic": 15000,
        "social_followers": 5000
    }
    
    sample_documents = [
        {"id": "doc1", "type": "business_license", "path": "/uploads/license.pdf"},
        {"id": "doc2", "type": "bank_statement", "path": "/uploads/statement.pdf"}
    ]
    
    print("🚀 Running with proper agent folder structure...")
    print("=" * 50)
    
    result = await process_merchant_application(sample_application, sample_documents)
    
    print(f"📋 Application ID: {result.application_id}")
    print(f"📊 Final Status: {result.status}")
    print()
    
    # Show agent results
    if result.market_qualification:
        print(f"✅ Market Qualification: {result.market_qualification.get('qualified')}")
    if result.lead_qualification:
        print(f"✅ Lead Score: {result.lead_qualification.get('lead_score')}")
    if result.document_processing:
        print(f"✅ Documents Processed: {result.document_processing.get('documents_processed')}")
    if result.risk_assessment:
        print(f"✅ Risk Category: {result.risk_assessment.get('risk_category')}")
    
    print("=" * 50)
    print("✨ Workflow completed using proper agent structure!")

if __name__ == "__main__":
    asyncio.run(run_with_proper_structure())