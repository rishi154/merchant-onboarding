from typing import Dict, List, Any
import os
import re
from google.cloud import documentai

def analyze_documents_with_ai(documents: List[Dict]) -> Dict[str, Any]:
    """Document-based routing analysis matching the workflow diagram exactly"""
    
    # Check if Document AI is available
    try:
        from google.cloud import documentai
        client = documentai.DocumentProcessorServiceClient()
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = 'us'
        processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID', 'form-parser')
        processor_name = client.processor_path(project_id, location, processor_id)
        ai_available = True
    except (ImportError, Exception) as e:
        print(f"Document AI not available: {e}")
        ai_available = False
    
    # Initialize analysis results
    extracted_industry = None
    extracted_revenue = None
    business_age = None
    ocr_confidence = 0.0
    compliance_flags = []
    risk_factors = []
    doc_types = []
    
    # Process documents for extraction
    if ai_available:
        for doc in documents[:5]:  # Sample first 5 docs
            try:
                file_path = doc.get('path')
                if not file_path or not os.path.exists(file_path):
                    continue
                    
                with open(file_path, 'rb') as f:
                    document_content = f.read()
                
                raw_document = documentai.RawDocument(
                    content=document_content,
                    mime_type='application/pdf' if file_path.endswith('.pdf') else 'image/png'
                )
                
                request = documentai.ProcessRequest(
                    name=processor_name,
                    raw_document=raw_document
                )
                
                result = client.process_document(request=request)
                document = result.document
                text = document.text.lower()
                
                # Calculate OCR confidence
                if hasattr(document, 'pages') and document.pages:
                    confidences = []
                    for page in document.pages:
                        if hasattr(page, 'tokens'):
                            for token in page.tokens:
                                if hasattr(token, 'detection_confidence'):
                                    confidences.append(token.detection_confidence)
                    ocr_confidence = sum(confidences) / len(confidences) if confidences else 0.5
                
                # Extract industry
                if not extracted_industry:
                    if any(term in text for term in ['cryptocurrency', 'crypto', 'bitcoin', 'blockchain']):
                        extracted_industry = 'crypto'
                    elif any(term in text for term in ['adult', 'escort', 'massage']):
                        extracted_industry = 'adult'
                    elif any(term in text for term in ['gambling', 'casino', 'betting', 'poker']):
                        extracted_industry = 'gambling'
                    elif any(term in text for term in ['firearm', 'gun', 'weapon']):
                        extracted_industry = 'firearms'
                    elif any(term in text for term in ['bank', 'financial', 'investment', 'loan']):
                        extracted_industry = 'finance'
                    elif any(term in text for term in ['medical', 'healthcare', 'hospital', 'clinic']):
                        extracted_industry = 'healthcare'
                    elif any(term in text for term in ['technology', 'software', 'tech', 'development']):
                        extracted_industry = 'technology'
                    else:
                        extracted_industry = 'standard'
                
                # Extract financial data
                import re
                revenue_patterns = [r'revenue[:\s]*\$?([\d,]+)', r'annual[\s]+sales[:\s]*\$?([\d,]+)', r'gross[\s]+income[:\s]*\$?([\d,]+)']
                for pattern in revenue_patterns:
                    match = re.search(pattern, text)
                    if match and not extracted_revenue:
                        extracted_revenue = int(match.group(1).replace(',', ''))
                        break
                
                # Extract business age
                age_patterns = [r'established[:\s]*(\d{4})', r'incorporated[:\s]*(\d{4})', r'founded[:\s]*(\d{4})']
                for pattern in age_patterns:
                    match = re.search(pattern, text)
                    if match:
                        year = int(match.group(1))
                        business_age = 2024 - year
                        break
                
                # Check for compliance flags
                if any(term in text for term in ['sanction', 'ofac', 'blocked', 'denied']):
                    compliance_flags.append('sanctions_match')
                if any(term in text for term in ['lawsuit', 'litigation', 'court', 'judgment']):
                    compliance_flags.append('legal_issues')
                if any(term in text for term in ['bankruptcy', 'insolvent', 'chapter 11', 'chapter 7']):
                    compliance_flags.append('bankruptcy')
                
                # Document type classification
                if any(term in text for term in ['license', 'permit', 'certificate']):
                    doc_types.append('business_license')
                elif any(term in text for term in ['bank statement', 'account summary']):
                    doc_types.append('financial')
                elif any(term in text for term in ['tax return', '1120', '1099']):
                    doc_types.append('tax_document')
                    
            except Exception as e:
                print(f"Error processing document {doc.get('filename', 'unknown')}: {e}")
                ocr_confidence = 0.3  # Low confidence for failed processing
    
    # Apply routing decision logic from diagram
    
    # Step 1: Industry Analysis
    if extracted_industry in ['firearms', 'drugs']:  # Prohibited
        return {
            'workflow_pattern': 'rejected',
            'risk_level': 'Prohibited',
            'risk_factors': [f'Prohibited industry: {extracted_industry}'],
            'routing_reason': 'Auto-rejected due to prohibited industry',
            'total_documents': len(documents),
            'ai_analysis': ai_available
        }
    
    if extracted_industry in ['crypto', 'adult', 'gambling']:  # High-Risk
        risk_level = 'High'
        risk_factors.append(f'High-risk industry: {extracted_industry}')
    elif extracted_industry in ['finance', 'healthcare']:  # Regulated
        risk_level = 'Medium'
        risk_factors.append(f'Regulated industry: {extracted_industry}')
    else:  # Standard Business - check financial
        risk_level = 'Low'  # Default, may be overridden
    
    # Step 2: Financial Analysis
    if extracted_revenue and business_age:
        if extracted_revenue < 100000 and business_age < 2:  # New + Low Revenue
            risk_level = 'High'
            risk_factors.append('Low revenue + new business')
        elif 100000 <= extracted_revenue <= 10000000 and business_age >= 2:  # Established
            if risk_level != 'High':  # Don't downgrade high-risk industries
                risk_level = 'Low'
        elif extracted_revenue > 10000000:  # Large business
            if risk_level == 'Low':  # Upgrade to medium for large businesses
                risk_level = 'Medium'
                risk_factors.append('Large business requiring enhanced review')
    elif not extracted_revenue:
        risk_level = 'High'
        risk_factors.append('Inconsistent or missing financial data')
    
    # Step 3: Compliance Flags
    if 'sanctions_match' in compliance_flags:
        return {
            'workflow_pattern': 'rejected',
            'risk_level': 'Prohibited',
            'risk_factors': ['Sanctions match detected'],
            'routing_reason': 'Auto-rejected due to sanctions match',
            'total_documents': len(documents),
            'ai_analysis': ai_available
        }
    
    if 'legal_issues' in compliance_flags or 'bankruptcy' in compliance_flags:
        risk_level = 'High'
        risk_factors.extend([f'Compliance flag: {flag}' for flag in compliance_flags])
    
    # Check for missing required documents
    required_types = ['business_license', 'financial', 'tax_document']
    missing_types = [t for t in required_types if t not in doc_types]
    if missing_types:
        if risk_level == 'Low':
            risk_level = 'Medium'
        risk_factors.append(f'Missing required documents: {", ".join(missing_types)}')
    
    # Step 4: Document Quality Analysis
    if ocr_confidence < 0.7:  # Poor OCR confidence
        risk_level = 'High'
        risk_factors.append(f'Poor document quality (OCR confidence: {ocr_confidence:.1%})')
    
    # Check for document inconsistencies
    if len(set(doc_types)) < len(doc_types) * 0.5:  # Many unclassified docs
        risk_level = 'High'
        risk_factors.append('Document inconsistencies detected')
    
    # Final workflow determination
    if risk_level == 'High':
        workflow = 'comprehensive_workflow'
    elif risk_level == 'Medium':
        workflow = 'standard_workflow'
    else:
        workflow = 'express_workflow'
    
    # Fallback when AI unavailable
    if not ai_available:
        workflow = 'comprehensive_workflow'
        risk_level = 'High'
        risk_factors = ['Document AI unavailable - defaulting to comprehensive review']
    
    return {
        'workflow_pattern': workflow,
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'extracted_industry': extracted_industry,
        'extracted_revenue': extracted_revenue,
        'business_age': business_age,
        'ocr_confidence': ocr_confidence,
        'compliance_flags': compliance_flags,
        'document_types': list(set(doc_types)),
        'total_documents': len(documents),
        'analyzed_documents': min(5, len(documents)),
        'ai_analysis': ai_available
    }