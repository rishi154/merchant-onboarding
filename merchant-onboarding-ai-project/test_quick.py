import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import process_merchant_application

async def test_simple():
    test_application = {
        "business_name": "Test Pizza Shop",
        "annual_revenue": 50000,
        "industry": "restaurant",
        "country": "US"
    }
    
    try:
        result = await process_merchant_application(test_application, [])
        print(f"Success: {result.status}")
        print(f"Workflow: {result.workflow_pattern}")
        print(f"Risk Tier: {result.market_qualification.get('risk_tier') if result.market_qualification else 'None'}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())