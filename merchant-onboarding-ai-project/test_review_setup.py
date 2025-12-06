#!/usr/bin/env python3
"""
Test script to set an application to require compliance verification review
"""
import sys
import os
sys.path.append('database')
sys.path.append('src')

from models import MerchantApplication, SessionLocal
from datetime import datetime

def set_application_for_review(app_id=None):
    """Set an application to require compliance verification review"""
    session = SessionLocal()
    try:
        # Get application (use first one if no ID specified)
        if app_id:
            app = session.query(MerchantApplication).filter_by(id=app_id).first()
        else:
            app = session.query(MerchantApplication).first()
        
        if not app:
            print("No application found")
            return None
        
        print(f"Setting application {app.id} to require compliance review")
        
        # Ensure we have some completed agents first
        if not app.agent_results:
            app.agent_results = {}
        
        # Add document processing result if missing
        if 'document_processing' not in app.agent_results:
            app.agent_results['document_processing'] = {
                'document_processing_complete': 'True',
                'documents_processed': '5',
                'extracted_data': {'business_name': app.business_name or 'Test Business'},
                'fraud_risk': 'low',
                'overall_confidence': '0.9',
                'processing_time': '2.0'
            }
        
        # Add risk assessment result if missing
        if 'risk_assessment' not in app.agent_results:
            app.agent_results['risk_assessment'] = {
                'risk_assessment_complete': 'True',
                'credit_score': '720',
                'financial_risk': 'low',
                'industry_risk': 'medium',
                'risk_category': 'MEDIUM',
                'risk_score': '35',
                'risk_tier': 'MEDIUM',
                'processing_time': '1.5'
            }
        
        # Add data validation result if missing
        if 'data_validation' not in app.agent_results:
            app.agent_results['data_validation'] = {
                'data_validation_complete': 'True',
                'validation_score': '0.95',
                'field_validations': {
                    'business_registry': 'verified',
                    'tax_id': 'verified',
                    'address': 'verified'
                },
                'processing_time': '1.0'
            }
        
        # Add compliance verification result that needs review
        app.agent_results['compliance_verification'] = {
            'compliance_verification_complete': 'True',
            'sanctions_clear': True,
            'kyc_status': 'verified',
            'aml_status': 'clear',
            'pep_clear': True,
            'compliance_score': '0.85',
            'requires_enhanced_dd': False,
            'processing_time': '2.5',
            'agent_reasoning': 'Compliance verification completed. All checks passed but requires human review due to configuration.',
            'tools_used': ['ofac_sanctions_check', 'pep_screening', 'aml_risk_assessment', 'kyc_verification']
        }
        
        # Set review status
        app.status = 'pending_human_review'
        app.needs_review = 'true'
        app.review_agent = 'compliance_verification'
        app.current_agent = 'compliance_verification'
        app.progress_percentage = 75
        app.review_data = app.agent_results['compliance_verification']
        app.updated_at = datetime.now()
        
        session.commit()
        
        print(f"✓ Application {app.id} set to require compliance verification review")
        print(f"  Status: {app.status}")
        print(f"  Needs Review: {app.needs_review}")
        print(f"  Review Agent: {app.review_agent}")
        print(f"  Agent Results: {list(app.agent_results.keys())}")
        print(f"  Progress: {app.progress_percentage}%")
        
        return app.id
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

if __name__ == "__main__":
    app_id = sys.argv[1] if len(sys.argv) > 1 else None
    result = set_application_for_review(app_id)
    if result:
        print(f"\nTest application ready: http://localhost:5000/application/{result}")