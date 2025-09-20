#!/usr/bin/env python3
"""Debug script to test workflow step by step."""

import sys
import os
import asyncio

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

from workflow import create_onboarding_workflow
from state import MerchantOnboardingState

async def debug_workflow():
    """Debug the workflow step by step."""
    print("=== DEBUGGING WORKFLOW ===")
    
    try:
        # Create workflow
        workflow = create_onboarding_workflow()
        print("[OK] Workflow created successfully")
        
        # Create test state
        initial_state = MerchantOnboardingState(
            application_id="DEBUG_001",
            business_name="Test Business LLC",
            documents=[{
                "id": "doc_001",
                "type": "business_license",
                "filename": "test_license.pdf"
            }]
        )
        print("[OK] Initial state created")
        
        # Run workflow with streaming to see each step
        print("\n=== STREAMING WORKFLOW EXECUTION ===")
        step_count = 0
        
        async for event in workflow.astream(initial_state):
            step_count += 1
            print(f"\n--- Step {step_count} ---")
            print(f"Event type: {type(event)}")
            
            if isinstance(event, dict):
                for key, value in event.items():
                    print(f"Agent: {key}")
                    if isinstance(value, dict):
                        print(f"  Result keys: {list(value.keys())}")
                        if 'error' in value:
                            print(f"  ERROR: {value['error']}")
                    else:
                        print(f"  Result: {value}")
            else:
                print(f"Event: {event}")
            
            # Stop after 10 steps to avoid infinite loop
            if step_count >= 15:
                print("\n!!! Stopping after 15 steps to prevent infinite loop")
                break
        
        print(f"\n=== WORKFLOW COMPLETED ===")
        print(f"Total steps executed: {step_count}")
        
        # Try to get final result
        try:
            final_result = await workflow.ainvoke(initial_state)
            print(f"Final result type: {type(final_result)}")
            if hasattr(final_result, '__dict__'):
                print(f"Final result keys: {list(final_result.__dict__.keys())}")
        except Exception as e:
            print(f"Error getting final result: {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Workflow debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_workflow())
    print(f"\nDebug completed: {'SUCCESS' if success else 'FAILED'}")