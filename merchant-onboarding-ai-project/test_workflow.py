#!/usr/bin/env python3
"""Test script to verify the workflow system works."""

import sys
import os
import asyncio

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

from workflow import create_onboarding_workflow
from state import MerchantOnboardingState

async def test_workflow():
    """Test the 14-agent workflow."""
    print("Testing 14-agent workflow...")
    
    try:
        # Create workflow
        workflow = create_onboarding_workflow()
        print("[OK] Workflow created successfully")
        
        # Create test state
        initial_state = MerchantOnboardingState(
            application_id="TEST_001",
            business_name="Test Business LLC",
            documents=[{
                "id": "doc_001",
                "type": "business_license",
                "filename": "test_license.pdf"
            }]
        )
        print("[OK] Initial state created")
        
        # Run workflow
        print("Running workflow...")
        result = await workflow.ainvoke(initial_state)
        print("[OK] Workflow completed successfully")
        
        # Check result
        if hasattr(result, '__dict__'):
            print(f"Result keys: {list(result.__dict__.keys())}")
        elif isinstance(result, dict):
            print(f"Result keys: {list(result.keys())}")
        
        # Check for decision result
        if 'decision' in result:
            decision = result['decision']
            print(f"Decision: {decision.get('decision', 'Unknown')}")
            print(f"Credit Limit: ${decision.get('credit_limit', 0)}")
        else:
            print(f"Result type: {type(result)}")
        
        # Check for decision in state
        if hasattr(result, 'decision') and result.decision:
            print(f"Decision: {result.decision.get('decision', 'Unknown')}")
            print(f"Credit Limit: ${result.decision.get('credit_limit', 0)}")
        
        print("[OK] Workflow test passed!")
        
        # Show final status
        if hasattr(result, 'status'):
            print(f"Final Status: {result.status}")
        elif isinstance(result, dict) and 'status' in result:
            print(f"Final Status: {result['status']}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Workflow test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    sys.exit(0 if success else 1)