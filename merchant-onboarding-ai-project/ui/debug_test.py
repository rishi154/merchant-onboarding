"""Quick test to verify the workflow works"""
import asyncio
from test_workflow import process_merchant_application

async def test_workflow():
    print("Testing workflow...")
    
    def progress_callback(agent_name, status, result):
        print(f"CALLBACK: {agent_name} - {status} - {result}")
    
    application_data = {
        'business_name': 'Test Business',
        'workflow_pattern': 'comprehensive_workflow'
    }
    
    documents = []
    
    result = await process_merchant_application(application_data, documents, progress_callback)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_workflow())