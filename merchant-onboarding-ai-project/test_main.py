#!/usr/bin/env python3
"""
Simple test script for main.py functionality
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import process_merchant_application

async def test_main():
    """Test the main function with sample data"""
    
    # Sample application data
    test_application = {
        "business_name": "Test Restaurant LLC",
        "business_type": "restaurant",
        "annual_revenue": 500000,
        "contact_email": "test@restaurant.com",
        "phone": "555-0123"
    }
    
    # Sample documents
    test_documents = [
        {"type": "business_license", "filename": "license.pdf"},
        {"type": "tax_return", "filename": "tax_2023.pdf"}
    ]
    
    print("Testing merchant onboarding workflow...")
    print(f"Application: {test_application}")
    print(f"Documents: {test_documents}")
    
    try:
        result = await process_merchant_application(test_application, test_documents)
        
        print("\n=== Test Results ===")
        print(f"Application ID: {result.application_id}")
        print(f"Status: {result.status}")
        print(f"Processing Start: {result.processing_start_time}")
        print(f"Processing End: {result.processing_end_time}")
        
        if result.exceptions:
            print(f"Exceptions: {result.exceptions}")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_main())
    sys.exit(0 if success else 1)