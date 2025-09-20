import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from main import process_merchant_application

async def run_real_ai_agents():
    """Run with real AI agents using VertexAI"""
    
    sample_application = {
        "business_name": "InnovateTech Solutions LLC",
        "annual_revenue": 850000,
        "country": "US",
        "state": "CA", 
        "platform": "shopify",
        "industry": "technology",
        "years_in_business": 3,
        "business_model": "B2B SaaS platform for small businesses",
        "employees": 12,
        "monthly_transactions": 2500,
        "average_transaction": 340
    }
    
    sample_documents = [
        {
            "id": "doc1", 
            "type": "business_license", 
            "path": "/uploads/ca_business_license.pdf",
            "description": "California LLC business license"
        },
        {
            "id": "doc2", 
            "type": "bank_statement", 
            "path": "/uploads/bank_statement_q3.pdf",
            "description": "Q3 2024 business bank statements"
        },
        {
            "id": "doc3",
            "type": "tax_return",
            "path": "/uploads/2023_tax_return.pdf", 
            "description": "2023 business tax return"
        }
    ]
    
    print("🤖 Running REAL AI Agents with VertexAI...")
    print("🧠 Agents have memory, reasoning, and LLM capabilities")
    print("=" * 60)
    
    try:
        result = await process_merchant_application(sample_application, sample_documents)
        
        print(f"📋 Application ID: {result.application_id}")
        print(f"📊 Final Status: {result.status}")
        print()
        
        # Show AI agent analysis
        if result.market_qualification:
            qual = result.market_qualification
            print(f"🎯 Market Qualification:")
            print(f"   Qualified: {qual.get('qualified')}")
            print(f"   AI Reasoning: {qual.get('reasoning', 'N/A')[:100]}...")
            print(f"   Risk Factors: {qual.get('risk_factors', [])}")
            print()
        
        if result.document_processing:
            docs = result.document_processing
            print(f"📄 Document Analysis:")
            print(f"   Confidence: {docs.get('overall_confidence', 0):.2f}")
            print(f"   Fraud Risk: {docs.get('fraud_risk', 'Unknown')}")
            print(f"   Documents Processed: {docs.get('documents_processed', 0)}")
            print()
        
        if result.risk_assessment:
            risk = result.risk_assessment
            print(f"⚠️ Risk Assessment:")
            print(f"   Risk Score: {risk.get('risk_score', 0)}/100")
            print(f"   Category: {risk.get('risk_category', 'Unknown')}")
            print(f"   Key Factors: {risk.get('risk_factors', [])}")
            print()
        
        print("=" * 60)
        print("✨ AI-powered workflow completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to set up Google Cloud credentials and project ID")

if __name__ == "__main__":
    asyncio.run(run_real_ai_agents())