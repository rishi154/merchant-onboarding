"""Test script for multi-jurisdictional support"""
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(__file__))

from jurisdiction_service import JurisdictionService
from jurisdiction_document_engine import JurisdictionDocumentEngine
from regional_risk_assessment import RegionalRiskAssessment
from jurisdiction_integration_manager import JurisdictionIntegrationManager
from jurisdiction_workflow_router import JurisdictionWorkflowRouter

async def test_jurisdiction_detection():
    """Test jurisdiction detection"""
    print("=== Testing Jurisdiction Detection ===")
    
    service = JurisdictionService()
    
    test_cases = [
        {"business_address": "123 Main St, New York, NY, USA", "expected": "US"},
        {"business_address": "10 Downing Street, London, UK", "expected": "UK"},
        {"business_address": "Unter den Linden 1, Berlin, Germany", "expected": "EU"},
        {"business_address": "100 Queen Street, Toronto, ON, Canada", "expected": "CA"},
        {"incorporation_country": "UK", "expected": "UK"}
    ]
    
    for case in test_cases:
        detected = service.detect_jurisdiction(case)
        status = "✅" if detected == case["expected"] else "❌"
        print(f"{status} {case} -> {detected}")

async def test_document_requirements():
    """Test jurisdiction-specific document requirements"""
    print("\n=== Testing Document Requirements ===")
    
    engine = JurisdictionDocumentEngine()
    
    test_cases = [
        ("US", "LLC"),
        ("UK", "Limited"),
        ("EU", "GmbH"),
        ("CA", "Corporation")
    ]
    
    for jurisdiction, business_type in test_cases:
        docs = engine.get_required_documents(jurisdiction, business_type)
        print(f"{jurisdiction} {business_type}: {len(docs)} documents required")
        for doc in docs:
            print(f"  - {doc.document_type} ({'required' if doc.required else 'optional'})")

async def test_regional_risk_assessment():
    """Test regional risk assessment"""
    print("\n=== Testing Regional Risk Assessment ===")
    
    test_merchant = {
        "business_name": "Test Corp",
        "business_address": "London, UK",
        "credit_score": 720,
        "business_age_years": 3,
        "industry": "retail",
        "annual_revenue": 500000,
        "companies_house_status": "active",
        "vat_registered": True
    }
    
    risk_assessor = RegionalRiskAssessment("UK")
    result = await risk_assessor.assess_risk(test_merchant)
    
    print(f"Jurisdiction: {result['jurisdiction']}")
    print(f"Risk Score: {result['overall_risk_score']}")
    print(f"Risk Category: {result['risk_category']}")
    print(f"Processing Limits: {result['processing_limits']}")

async def test_integration_manager():
    """Test jurisdiction integration manager"""
    print("\n=== Testing Integration Manager ===")
    
    jurisdictions = ["US", "UK", "EU", "CA"]
    
    for jurisdiction in jurisdictions:
        manager = JurisdictionIntegrationManager(jurisdiction)
        
        # Test credit bureau call
        result = await manager.call_service_with_fallback(
            "credit_bureau", "credit_check", {"business_name": "Test Corp"}
        )
        
        print(f"{jurisdiction} Credit Bureau: {result['provider_used']} - {result.get('credit_score', 'N/A')}")

async def test_workflow_router():
    """Test jurisdiction workflow router"""
    print("\n=== Testing Workflow Router ===")
    
    router = JurisdictionWorkflowRouter()
    
    test_applications = [
        {"business_address": "New York, USA", "business_type": "LLC"},
        {"business_address": "London, UK", "business_type": "Limited"},
        {"business_address": "Berlin, Germany", "business_type": "GmbH"},
        {"business_address": "Toronto, Canada", "business_type": "Corporation"}
    ]
    
    for app_data in test_applications:
        workflow = router.route_application(app_data)
        print(f"\nJurisdiction: {workflow['jurisdiction']}")
        print(f"Agents: {len(workflow['workflow_agents'])}")
        print(f"SLA Hours: {workflow['processing_sla_hours']}")
        print(f"Compliance Rules: {workflow['compliance_rules']}")

async def test_compliance_validation():
    """Test jurisdiction compliance validation"""
    print("\n=== Testing Compliance Validation ===")
    
    router = JurisdictionWorkflowRouter()
    
    # Test US application
    us_app = {
        "business_address": "New York, USA",
        "business_type": "LLC",
        "documents": ["articles_of_organization", "ein_letter"],
        "ein_number": "12-3456789"
    }
    
    validation = router.validate_jurisdiction_requirements("US", us_app)
    print(f"US Validation: {'✅ Valid' if validation['is_valid'] else '❌ Invalid'}")
    if validation['missing_requirements']:
        print(f"Missing: {validation['missing_requirements']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")

async def main():
    """Run all tests"""
    print("🌍 Multi-Jurisdictional Support Test Suite")
    print("=" * 50)
    
    await test_jurisdiction_detection()
    await test_document_requirements()
    await test_regional_risk_assessment()
    await test_integration_manager()
    await test_workflow_router()
    await test_compliance_validation()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())