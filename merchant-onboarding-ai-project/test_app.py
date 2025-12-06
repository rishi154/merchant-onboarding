#!/usr/bin/env python3
"""
Simple test to create an application requiring review
"""
from flask import Flask, jsonify
import sys
import os
sys.path.append('database')
sys.path.append('src')

from models import MerchantApplication, SessionLocal
from datetime import datetime

app = Flask(__name__)

@app.route('/create-test-app')
def create_test_app():
    """Create a test application that requires compliance review"""
    session = SessionLocal()
    try:
        # Create test application
        test_app = MerchantApplication(
            id='TEST_REVIEW_APP',
            business_name='Test Business Requiring Review',
            status='pending_human_review',
            current_agent='compliance_verification',
            progress_percentage=75,
            documents_processed=4,
            processing_start_time=datetime.now(),
            workflow_pattern='standard_workflow',
            needs_review='true',
            review_agent='compliance_verification',
            agent_results={
                'document_processing': {
                    'document_processing_complete': 'True',
                    'documents_processed': '4',
                    'extracted_data': {'business_name': 'Test Business Requiring Review'},
                    'fraud_risk': 'low',
                    'overall_confidence': '0.9',
                    'processing_time': '2.0'
                },
                'risk_assessment': {
                    'risk_assessment_complete': 'True',
                    'credit_score': '720',
                    'financial_risk': 'low',
                    'industry_risk': 'medium',
                    'risk_category': 'MEDIUM',
                    'risk_score': '35',
                    'risk_tier': 'MEDIUM',
                    'processing_time': '1.5'
                },
                'data_validation': {
                    'data_validation_complete': 'True',
                    'validation_score': '0.95',
                    'field_validations': {
                        'business_registry': 'verified',
                        'tax_id': 'verified',
                        'address': 'verified'
                    },
                    'processing_time': '1.0'
                },
                'compliance_verification': {
                    'compliance_verification_complete': 'True',
                    'sanctions_clear': True,
                    'kyc_status': 'verified',
                    'aml_status': 'clear',
                    'pep_clear': True,
                    'compliance_score': '0.85',
                    'requires_enhanced_dd': False,
                    'processing_time': '2.5',
                    'agent_reasoning': 'All compliance checks passed. Requires human review.',
                    'tools_used': ['ofac_sanctions_check', 'pep_screening', 'aml_risk_assessment', 'kyc_verification']
                }
            },
            review_data={
                'compliance_verification_complete': 'True',
                'sanctions_clear': True,
                'kyc_status': 'verified',
                'aml_status': 'clear',
                'pep_clear': True,
                'compliance_score': '0.85',
                'agent_reasoning': 'All compliance checks passed. Requires human review.'
            },
            application_data={
                'business_name': 'Test Business Requiring Review',
                'documents': ['business_license.pdf', 'bank_statement.pdf', 'tax_return.pdf', 'ein_letter.pdf'],
                'jurisdiction': 'US'
            }
        )
        
        session.add(test_app)
        session.commit()
        
        return jsonify({
            'success': True,
            'application_id': test_app.id,
            'message': 'Test application created',
            'review_url': f'http://localhost:5000/application/{test_app.id}',
            'agent_count': 4,
            'needs_review': test_app.needs_review,
            'review_agent': test_app.review_agent
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(port=5001, debug=True)