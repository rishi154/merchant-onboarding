import asyncio
from src.service_factory import ServiceFactory
from src.interfaces import DocumentType, VerificationLevel

async def test_document_processing_workflow():
    """Test the complete document processing workflow"""
    
    # Initialize services
    factory = ServiceFactory()
    doc_processor = factory.create_document_processor()
    doc_storage = factory.create_document_storage()
    doc_validator = factory.create_validator()
    business_verifier = factory.create_business_verifier()
    fraud_detector = factory.create_fraud_detector()
    
    # Sample document path (using a bank statement from sample documents)
    document_path = "../../../prototype/sample_documents/bank_statement.png"
    
    print("\n1. Document Processing Test:")
    print("---------------------------")
    
    # Process document
    print("Processing document...")
    processing_result = await doc_processor.process_document(document_path)
    print(f"Processing complete. Extracted {len(processing_result.get('extracted_fields', []))} fields")
    
    # Store document
    print("\nStoring document...")
    storage_result = await doc_storage.store_document(document_path, processing_result)
    print(f"Document stored with ID: {storage_result.get('document_id')}")
    
    # Validate document
    print("\nValidating document...")
    validation_result = await doc_validator.validate_document(processing_result)
    print(f"Validation {'passed' if validation_result.get('is_valid') else 'failed'}")
    
    print("\n2. Business Verification Test:")
    print("-----------------------------")
    
    # Test business verification
    business_name = "Test Merchant LLC"
    tax_id = "123456789"
    state = "CA"
    
    print("Performing business verification...")
    verification_result = await business_verifier.verify_business(
        business_name=business_name,
        tax_id=tax_id,
        state=state,
        level=VerificationLevel.ENHANCED
    )
    
    print(f"Verification level: {verification_result.get('verification_level')}")
    print(f"Verification success: {verification_result.get('success')}")
    
    print("\n3. Fraud Detection Test:")
    print("-----------------------")
    
    # Test fraud detection
    print("Performing fraud detection...")
    fraud_result = await fraud_detector.detect_fraud(
        document_path=document_path,
        document_type=DocumentType.BANK_STATEMENT,
        extracted_data=processing_result.get('extracted_data', {})
    )
    
    print(f"Fraud risk score: {fraud_result.get('risk_score', 0):.2f}")
    if fraud_result.get('indicators'):
        print("Fraud indicators found:")
        for indicator in fraud_result['indicators']:
            print(f"- {indicator['type']}: {indicator['details']}")
    else:
        print("No fraud indicators detected")
    
    # Test document authenticity
    print("\nChecking document authenticity...")
    auth_result = await fraud_detector.analyze_document_authenticity(
        document_path=document_path,
        document_type=DocumentType.BANK_STATEMENT
    )
    
    print(f"Document authentic: {auth_result.get('is_authentic')}")
    print(f"Confidence score: {auth_result.get('confidence'):.2f}")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_document_processing_workflow())