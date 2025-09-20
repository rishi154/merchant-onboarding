#!/usr/bin/env python3
import asyncio
import sys
import os

# Environment setup
os.environ['GOOGLE_CLOUD_PROJECT'] = 'steam-collector-339717'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

# Path setup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import process_merchant_application

async def test_main():
    test_application = {
        "business_name": "Test Restaurant LLC",
        "business_type": "restaurant",
        "annual_revenue": 500000,
        "contact_email": "test@restaurant.com",
        "phone": "555-0123",
        "country": "US",
        "platform": "shopify"
    }
    
    test_documents = [
        {"type": "business_license", "filename": "license.pdf"},
        {"type": "tax_return", "filename": "tax_2023.pdf"}
    ]
    
    print("Testing merchant onboarding workflow...")
    
    try:
        result = await process_merchant_application(test_application, test_documents)
        
        print("\n=== SUCCESS ===")
        if hasattr(result, 'application_id'):
            print(f"Application ID: {result.application_id}")
            print(f"Status: {result.status}")
        else:
            print(f"Result type: {type(result)}")
            print("Workflow completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_main())
    print(f"Result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)