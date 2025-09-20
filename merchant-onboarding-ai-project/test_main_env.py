#!/usr/bin/env python3
"""
Test main.py with proper environment setup
"""
import asyncio
import sys
import os

# Set up environment variables from .env.example
os.environ['GOOGLE_CLOUD_PROJECT'] = 'steam-collector-339717'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['AGENT_TEMPERATURE'] = '0.1'
os.environ['AGENT_MAX_TOKENS'] = '2048'

# Add all necessary paths
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, project_root)

try:
    from main import process_merchant_application
    
    async def test_main():
        """Test the main function"""
        
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
        print(f"Application: {test_application}")
        print(f"Documents: {test_documents}")
        
        try:
            result = await process_merchant_application(test_application, test_documents)
            
            print("\n=== Test Results ===")
            print(f"✓ Application ID: {result.application_id}")
            print(f"✓ Status: {result.status}")
            print(f"✓ Processing Start: {result.processing_start_time}")
            print(f"✓ Processing End: {result.processing_end_time}")
            
            if hasattr(result, 'market_qualification') and result.market_qualification:
                print(f"✓ Market Qualification: {result.market_qualification}")
            
            if result.exceptions:
                print(f"⚠ Exceptions: {result.exceptions}")
            
            print("\n✅ Test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        success = asyncio.run(test_main())
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("This indicates there are missing dependencies or import issues.")
    print("The main.py structure looks correct, but the workflow dependencies need to be resolved.")
    sys.exit(1)