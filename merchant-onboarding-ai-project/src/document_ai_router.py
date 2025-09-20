from typing import Dict, List, Any
import os
from google.cloud import documentai

def analyze_documents_with_ai(documents: List[Dict]) -> Dict[str, Any]:
    """Use Document AI for routing analysis - lightweight classification only"""
    
    # Check if Document AI is available
    try:
        from google.cloud import documentai
        client = documentai.DocumentProcessorServiceClient()
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        location = 'us'
        processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID', 'form-parser')
        
        processor_name = client.processor_path(project_id, location, processor_id)
    except (ImportError, Exception) as e:
        print(f"Document AI not available: {e}")
        # Default to comprehensive workflow when AI unavailable
        return {
            'workflow_pattern': 'comprehensive_workflow',
            'risk_level': 'High',
            'complexity_score': 20,
            'document_types': ['unknown'],
            'risk_factors': ['Document AI unavailable - unable to analyze document content', f'{len(documents)} documents require manual review'],
            'total_documents': len(documents),
            'analyzed_documents': 0,
            'ai_analysis': False
        }
    
    doc_types = []
    complexity_score = 0
    risk_factors = []
    
    # Process first 5 documents for routing (not all - that's for the agent)
    sample_docs = documents[:5]
    
    for doc in sample_docs:
        try:
            file_path = doc.get('path')
            if not file_path or not os.path.exists(file_path):
                continue
                
            # Read document
            with open(file_path, 'rb') as f:
                document_content = f.read()
            
            # Process with Document AI
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
            
            # Quick classification based on content
            text = document.text.lower()
            
            if any(term in text for term in ['tax return', 'form 1120', '1099', 'schedule']):
                doc_types.append('tax_document')
                complexity_score += 3
            elif any(term in text for term in ['bank statement', 'account summary', 'balance']):
                doc_types.append('financial')
                complexity_score += 2
            elif any(term in text for term in ['license', 'permit', 'certificate']):
                doc_types.append('business_license')
                complexity_score += 1
            elif any(term in text for term in ['insurance', 'policy', 'coverage']):
                doc_types.append('insurance')
                complexity_score += 1
            elif any(term in text for term in ['contract', 'agreement', 'lease']):
                doc_types.append('legal')
                complexity_score += 4
            elif any(term in text for term in ['audit', 'financial statement', 'cpa']):
                doc_types.append('financial_statement')
                complexity_score += 5
            else:
                doc_types.append('other')
                complexity_score += 1
                
            # Check document quality
            if len(text.strip()) < 100:
                risk_factors.append("Poor quality or unreadable documents detected")
                complexity_score += 2
                
        except Exception as e:
            print(f"Error processing document {doc.get('filename', 'unknown')}: {e}")
            complexity_score += 2  # Penalty for unprocessable docs
    
    # Additional risk factors
    if len(documents) > 25:
        risk_factors.append("High document volume requiring detailed review")
        complexity_score += 3
    elif len(documents) > 15:
        risk_factors.append("Moderate document volume")
        complexity_score += 1
    
    # Missing standard documents
    required_types = ['business_license', 'financial', 'tax_document']
    missing_types = [t for t in required_types if t not in doc_types]
    if missing_types:
        risk_factors.append(f"Missing standard documents: {', '.join(missing_types)}")
        complexity_score += len(missing_types) * 2
    
    # Determine workflow
    if complexity_score <= 5:
        workflow = "express_workflow"
        risk_level = "Low"
    elif complexity_score <= 15:
        workflow = "standard_workflow"
        risk_level = "Medium"
    else:
        workflow = "comprehensive_workflow"
        risk_level = "High"
    
    return {
        'workflow_pattern': workflow,
        'risk_level': risk_level,
        'complexity_score': complexity_score,
        'document_types': list(set(doc_types)),
        'risk_factors': risk_factors,
        'total_documents': len(documents),
        'analyzed_documents': len(sample_docs),
        'ai_analysis': True
    }