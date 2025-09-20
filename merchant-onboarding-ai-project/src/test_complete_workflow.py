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
        # Core Business Documents
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

                "type": "ein_letter",        },

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

        if doc['type'] in ['business_license', 'ein_letter']:

            verification_result = await business_verifier.verify_business(            "business_name": "Tech Innovations LLC",

                business_name=application_data['business_name'],

                tax_id=application_data['tax_id'],    # Sample application data        "tax_id": "82-1234567",

                state=application_data['address']['state']

            )    application_data = {        "business_type": "llc",

            result['verification'] = verification_result

                "business_name": "Tech Innovations LLC",        "industry": "technology",

        # Check for fraud

        fraud_result = await fraud_detector.detect_fraud(        "tax_id": "82-1234567",        "years_in_business": 3,

            document_path=doc['path'],

            document_type=DocumentType.BANK_STATEMENT if doc['type'] == 'bank_statement' else DocumentType.BUSINESS_LICENSE,        "business_type": "llc",        "annual_revenue": 1500000,

            extracted_data=result.get('extracted_data', {})

        )        "industry": "technology",        "merchant_category_code": "7372",

        result['fraud_check'] = fraud_result

                "years_in_business": 3,        "address": {

        processed_documents.append({

            **doc,        "annual_revenue": 1500000,            "street": "123 Innovation Way",

            'processing_result': result,

            'storage_id': storage_result['document_id']        "merchant_category_code": "7372",            "city": "San Francisco",

        })

            "address": {            "state": "CA",

    # Create initial state

    state = MerchantOnboardingState(            "street": "123 Innovation Way",            "zip": "94105"

        application_id=app_id,

        application_data=application_data,            "city": "San Francisco",        },

        documents=processed_documents,

        processing_start_time=datetime.now().isoformat()            "state": "CA",        "owner": {

    )

                "zip": "94105"            "name": "John Smith",

    # Create and run the 14-agent workflow

    workflow = create_onboarding_workflow()        },            "title": "CEO",

    print("\n[WORKFLOW] Starting 14-agent workflow...")

            "owner": {            "ownership_percentage": 100,

    try:

        result = await workflow.ainvoke(state)            "name": "John Smith",            "ssn_last_4": "1234",

        print(f"\n[SUCCESS] Workflow completed!")

        print(f"[RESULT] Final status: {result.status}")            "title": "CEO",            "dob": "1980-01-15"

        

        # Display workflow results            "ownership_percentage": 100,        }

        if result.status == ApplicationStatus.APPROVED:

            print("\nApplication APPROVED!")            "ssn_last_4": "1234",    }

            print(f"Risk Score: {result.risk_score}")

            print(f"Processing Time: {result.processing_end_time}")            "dob": "1980-01-15"    

        elif result.status == ApplicationStatus.REJECTED:

            print("\nApplication REJECTED")        }    # Initialize state

            print("Reasons:")

            for reason in result.rejection_reasons:    }    app_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                print(f"- {reason}")

        else:        print(f"\n[START] Starting merchant onboarding for {app_id}")

            print(f"\nApplication requires manual review")

            print("Pending items:")    # Initialize state    print(f"[INFO] Business: {application_data['business_name']}")

            for item in result.pending_items:

                print(f"- {item}")    app_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"    

        

        return result    print(f"\n[START] Starting merchant onboarding for {app_id}")    # Process documents first

        

    except Exception as e:    print(f"[INFO] Business: {application_data['business_name']}")    processed_documents = []

        print(f"[ERROR] Workflow failed: {str(e)}")

        raise        for doc in uploaded_documents:



if __name__ == "__main__":    # Process documents first        print(f"\n[DOCUMENT] Processing {doc['filename']}...")

    asyncio.run(run_complete_workflow())
    processed_documents = []        

    for doc in uploaded_documents:        # Process document

        print(f"\n[DOCUMENT] Processing {doc['filename']}...")        result = await doc_processor.process_document(doc['path'])

                

        # Process document        # Store document with metadata

        result = await doc_processor.process_document(doc['path'])        storage_result = await doc_storage.store_document(

                    doc['path'],

        # Store document with metadata            {**result, **doc}

        storage_result = await doc_storage.store_document(        )

            doc['path'],        

            {**result, **doc}        # Verify business information (if business license or EIN)

        )        if doc['type'] in ['business_license', 'ein_letter']:

                    verification_result = await business_verifier.verify_business(

        # Verify business information (if business license or EIN)                business_name=application_data['business_name'],

        if doc['type'] in ['business_license', 'ein_letter']:                tax_id=application_data['tax_id'],

            verification_result = await business_verifier.verify_business(                state=application_data['address']['state']

                business_name=application_data['business_name'],            )

                tax_id=application_data['tax_id'],            result['verification'] = verification_result

                state=application_data['address']['state']        

            )        # Check for fraud

            result['verification'] = verification_result        fraud_result = await fraud_detector.detect_fraud(

                    document_path=doc['path'],

        # Check for fraud            document_type=doc['type'],

        fraud_result = await fraud_detector.detect_fraud(            extracted_data=result.get('extracted_data', {})

            document_path=doc['path'],        )

            document_type=doc['type'],        result['fraud_check'] = fraud_result

            extracted_data=result.get('extracted_data', {})        

        )        processed_documents.append({

        result['fraud_check'] = fraud_result            **doc,

                    'processing_result': result,

        processed_documents.append({            'storage_id': storage_result['document_id']

            **doc,        })

            'processing_result': result,    

            'storage_id': storage_result['document_id']    # Create initial state

        })    state = MerchantOnboardingState(

            application_id=app_id,

    # Create initial state        application_data=application_data,

    state = MerchantOnboardingState(        documents=processed_documents,

        application_id=app_id,        processing_start_time=datetime.now().isoformat()

        application_data=application_data,    )

        documents=processed_documents,    

        processing_start_time=datetime.now().isoformat()    # Create and run the 14-agent workflow

    )    workflow = create_onboarding_workflow()

        print("\n[WORKFLOW] Starting 14-agent workflow...")

    # Create and run the 14-agent workflow    

    workflow = create_onboarding_workflow()    try:

    print("\n[WORKFLOW] Starting 14-agent workflow...")        result = await workflow.ainvoke(state)

            print(f"\n[SUCCESS] Workflow completed!")

    try:        print(f"[RESULT] Final status: {result.status}")

        result = await workflow.ainvoke(state)        

        print(f"\n[SUCCESS] Workflow completed!")        # Display workflow results

        print(f"[RESULT] Final status: {result.status}")        if result.status == ApplicationStatus.APPROVED:

                    print("\nApplication APPROVED!")

        # Display workflow results            print(f"Risk Score: {result.risk_score}")

        if result.status == ApplicationStatus.APPROVED:            print(f"Processing Time: {result.processing_end_time}")

            print("\nApplication APPROVED!")        elif result.status == ApplicationStatus.REJECTED:

            print(f"Risk Score: {result.risk_score}")            print("\nApplication REJECTED")

            print(f"Processing Time: {result.processing_end_time}")            print("Reasons:")

        elif result.status == ApplicationStatus.REJECTED:            for reason in result.rejection_reasons:

            print("\nApplication REJECTED")                print(f"- {reason}")

            print("Reasons:")        else:

            for reason in result.rejection_reasons:            print(f"\nApplication requires manual review")

                print(f"- {reason}")            print("Pending items:")

        else:            for item in result.pending_items:

            print(f"\nApplication requires manual review")                print(f"- {item}")

            print("Pending items:")        

            for item in result.pending_items:        return result

                print(f"- {item}")        

            except Exception as e:

        return result        print(f"[ERROR] Workflow failed: {str(e)}")

                raise

    except Exception as e:

        print(f"[ERROR] Workflow failed: {str(e)}")if __name__ == "__main__":

        raise    asyncio.run(run_complete_workflow())

if __name__ == "__main__":
    asyncio.run(run_complete_workflow())