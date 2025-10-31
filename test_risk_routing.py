#!/usr/bin/env python3
"""
Test script to verify Risk Assessment-based workflow routing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'merchant-onboarding-ai-project', 'src'))

def test_risk_routing():
    """Test risk-based workflow routing logic"""
    
    print("=== TESTING RISK-BASED WORKFLOW ROUTING ===\n")
    
    # Test scenarios with different risk levels
    test_scenarios = [
        {
            "name": "LOW Risk Scenario",
            "risk_assessment": {"risk_tier": "LOW", "risk_score": 25},
            "expected_workflow": "express_workflow"
        },
        {
            "name": "MEDIUM Risk Scenario", 
            "risk_assessment": {"risk_tier": "MEDIUM", "risk_score": 55},
            "expected_workflow": "standard_workflow"
        },
        {
            "name": "HIGH Risk Scenario",
            "risk_assessment": {"risk_tier": "HIGH", "risk_score": 85},
            "expected_workflow": "comprehensive_workflow"
        }
    ]
    
    try:
        from workflow_router import determine_workflow_pattern
        from state import MerchantOnboardingState
        
        for scenario in test_scenarios:
            print(f"Testing: {scenario['name']}")
            print(f"Risk Assessment: {scenario['risk_assessment']}")
            
            # Create mock state with risk assessment
            state = MerchantOnboardingState(
                application_id="TEST_001",
                application_data={},
                documents=[]
            )
            state.risk_assessment = scenario['risk_assessment']
            
            # Test workflow determination
            selected_workflow = determine_workflow_pattern(state)
            
            print(f"Selected Workflow: {selected_workflow}")
            print(f"Expected Workflow: {scenario['expected_workflow']}")
            
            if selected_workflow == scenario['expected_workflow']:
                print("PASS - Correct workflow selected\n")
            else:
                print("FAIL - Wrong workflow selected\n")
                
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure you're running from the correct directory")
    except Exception as e:
        print(f"Test Error: {e}")

def test_routing_workflow_steps():
    """Test routing workflow configuration"""
    
    print("=== TESTING ROUTING WORKFLOW STEPS ===\n")
    
    try:
        from workflow_router import get_workflow_steps, get_workflow_metadata
        
        # Test routing workflow steps
        routing_steps = get_workflow_steps("routing_workflow")
        print("Routing Workflow Steps:")
        for i, step in enumerate(routing_steps, 1):
            print(f"  {i}. {step['name']}: {step['description']}")
        
        # Verify it uses Risk Assessment, not Market Qualification
        step_names = [step['name'] for step in routing_steps]
        if "Risk Assessment" in step_names:
            print("PASS - Risk Assessment found in routing steps")
        else:
            print("FAIL - Risk Assessment not found in routing steps")
            
        if "Market Qualification" not in step_names:
            print("PASS - Market Qualification correctly removed from routing")
        else:
            print("FAIL - Market Qualification still in routing steps")
            
        # Test metadata
        routing_metadata = get_workflow_metadata("routing_workflow")
        print(f"\nRouting Metadata: {routing_metadata['name']}")
        print(f"Description: {routing_metadata['description']}")
        
    except Exception as e:
        print(f"Error testing routing steps: {e}")

if __name__ == "__main__":
    test_risk_routing()
    test_routing_workflow_steps()
    print("=== TESTING COMPLETE ===")