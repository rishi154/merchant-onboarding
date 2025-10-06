"""Test jurisdiction detection functionality"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'merchant-onboarding-ai-project', 'src'))

from jurisdiction_service import JurisdictionService

def test_jurisdiction_detection():
    service = JurisdictionService()
    
    test_cases = [
        {"business_name": "Acme Corp", "business_address": "123 Main St, New York, NY"},
        {"business_name": "London Ltd", "business_address": "10 Downing St, London, UK"},
        {"business_name": "Berlin GmbH", "business_address": "Unter den Linden, Berlin, Germany"},
        {"business_name": "Toronto Inc", "business_address": "CN Tower, Toronto, ON, Canada"}
    ]
    
    for case in test_cases:
        jurisdiction = service.detect_jurisdiction(case)
        config = service.get_jurisdiction_config(jurisdiction)
        
        print(f"Business: {case['business_name']}")
        print(f"Detected: {jurisdiction}")
        print(f"Rules: {config.compliance_rules}")
        print(f"Config: {vars(config)}")
        print("---")

if __name__ == "__main__":
    test_jurisdiction_detection()