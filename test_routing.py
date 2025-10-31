#!/usr/bin/env python3
"""
Quick test script to simulate different risk scenarios
Run this to test workflow routing without uploading files
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'merchant-onboarding-ai-project', 'agents', 'market-qualification', 'src'))

def test_risk_calculation():
    """Test different risk tier calculations"""
    
    # LOW Risk Scenario
    print("=== LOW RISK TEST ===")
    low_risk_data = {
        'business_type': 'retail',
        'transaction_volume': 'low',
        'document_complexity': 'simple',
        'entity_count': 1
    }
    print(f"Input: {low_risk_data}")
    print("Expected: LOW risk → Express Workflow (4 agents)")
    
    # MEDIUM Risk Scenario  
    print("\n=== MEDIUM RISK TEST ===")
    medium_risk_data = {
        'business_type': 'service',
        'transaction_volume': 'medium', 
        'document_complexity': 'moderate',
        'entity_count': 2
    }
    print(f"Input: {medium_risk_data}")
    print("Expected: MEDIUM risk → Standard Workflow (7 agents)")
    
    # HIGH Risk Scenario
    print("\n=== HIGH RISK TEST ===")
    high_risk_data = {
        'business_type': 'financial',
        'transaction_volume': 'high',
        'document_complexity': 'complex',
        'entity_count': 5
    }
    print(f"Input: {high_risk_data}")
    print("Expected: HIGH risk → Comprehensive Workflow (14 agents)")

if __name__ == "__main__":
    test_risk_calculation()