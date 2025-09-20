import sys
import os
import asyncio
from datetime import datetime

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Imports
from workflow import create_onboarding_workflow
from state import MerchantOnboardingState, ApplicationStatus
from agents.document_processing.src.interfaces import DocumentType, VerificationLevel
from agents.document_processing.src.service_factory import ServiceFactory

async def run_complete_workflow():
    """Run complete merchant onboarding workflow with document processing"""
    
    # Initialize document processing services
    service_factory = ServiceFactory()
    doc_processor = service_factory.create_document_processor()
    doc_storage = service_factory.create_document_storage()
    business_verifier = service_factory.create_business_verifier()
    fraud_detector = service_factory.create_fraud_detector()
    
    # Sample documents setup
    sample_docs_path = os.path.join(project_root, 'prototype', 'sample_documents')
    uploaded_documents = [
        {
            "id": "doc_001",
            "type": "business_license",
            "path": os.path.join(sample_docs_path, "business_license.png"),
            "filename": "business_license.png"
        },
        {
            "id": "doc_002", 
            "type": "ein_letter",
            "path": os.path.join(sample_docs_path, "ein_letter.png"),
            "filename": "ein_letter.png"
        },
        {
            "id": "doc_003",
            "type": "bank_statement",
            "path": os.path.join(sample_docs_path, "bank_statement.png"),
            "filename": "bank_statement.png"
        }
    ]
    
    # Sample application data
    application_data = {
        "business_name": "Tech Innovations LLC",
        "tax_id": "82-1234567",
        "business_type": "llc",
        "industry": "technology",
        "years_in_business": 3,
        "annual_revenue": 1500000,
        "merchant_category_code": "7372",
        "address": {
            "street": "123 Innovation Way",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105"
        },
        "owner": {
            "name": "John Smith",
            "title": "CEO",
            "ownership_percentage": 100,
            "ssn_last_4": "1234",
            "dob": "1980-01-15"
        }
    }
    
    # Initialize state
    app_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n[START] Starting merchant onboarding for {app_id}")
    print(f"[INFO] Business: {application_data['business_name']}")
    
    # Process documents first
    processed_documents = []
    for doc in uploaded_documents:
        print(f"\n[DOCUMENT] Processing {doc['filename']}...")
        
        # Process document
        result = await doc_processor.process_document(doc['path'])
        
        # Store document with metadata
        storage_result = await doc_storage.store_document(
            doc['path'],
            {**result, **doc}
        )
        
        # Verify business information (if business license or EIN)
        if doc['type'] in ['business_license', 'ein_letter']:
            verification_result = await business_verifier.verify_business(
                business_name=application_data['business_name'],
                tax_id=application_data['tax_id'],
                state=application_data['address']['state']
            )
            result['verification'] = verification_result
        
        # Check for fraud
        fraud_result = await fraud_detector.detect_fraud(
            document_path=doc['path'],
            document_type=DocumentType.BANK_STATEMENT if doc['type'] == 'bank_statement' else DocumentType.BUSINESS_LICENSE,
            extracted_data=result.get('extracted_data', {})
        )
        result['fraud_check'] = fraud_result
        
        processed_documents.append({
            **doc,
            'processing_result': result,
            'storage_id': storage_result['document_id']
        })
    
    # Create initial state
    state = MerchantOnboardingState(
        application_id=app_id,
        application_data=application_data,
        documents=processed_documents,
        processing_start_time=datetime.now().isoformat()
    )
    
    # Create and run the 14-agent workflow
    workflow = create_onboarding_workflow()
    print("\n[WORKFLOW] Starting 14-agent workflow...")
    
    try:
        result = await workflow.ainvoke(state)
        print(f"\n[SUCCESS] Workflow completed!")
        print(f"[RESULT] Final status: {result.status}")
        
        # Display workflow results
        if result.status == ApplicationStatus.APPROVED:
            print("\nApplication APPROVED!")
            print(f"Risk Score: {result.risk_score}")
            print(f"Processing Time: {result.processing_end_time}")
        elif result.status == ApplicationStatus.REJECTED:
            print("\nApplication REJECTED")
            print("Reasons:")
            for reason in result.rejection_reasons:
                print(f"- {reason}")
        else:
            print(f"\nApplication requires manual review")
            print("Pending items:")
            for item in result.pending_items:
                print(f"- {item}")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Workflow failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_complete_workflow())