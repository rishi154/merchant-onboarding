from typing import Dict, List, Any
import os

def analyze_documents_for_routing(documents: List[Dict]) -> Dict[str, Any]:
    """Analyze uploaded documents to determine workflow routing"""
    
    doc_types = []
    total_size = 0
    complexity_score = 0
    
    for doc in documents:
        filename = doc.get('filename', '').lower()
        size = doc.get('size', 0)
        total_size += size
        
        # Categorize document types
        if any(term in filename for term in ['license', 'permit', 'registration']):
            doc_types.append('business_license')
            complexity_score += 1
        elif any(term in filename for term in ['bank', 'statement', 'account']):
            doc_types.append('financial')
            complexity_score += 2
        elif any(term in filename for term in ['tax', 'return', 'ein', 'ssn']):
            doc_types.append('tax_document')
            complexity_score += 3
        elif any(term in filename for term in ['insurance', 'certificate', 'policy']):
            doc_types.append('insurance')
            complexity_score += 1
        elif any(term in filename for term in ['contract', 'agreement', 'lease']):
            doc_types.append('legal')
            complexity_score += 4
        elif any(term in filename for term in ['financial', 'audit', 'cpa']):
            doc_types.append('financial_statement')
            complexity_score += 5
        else:
            doc_types.append('other')
            complexity_score += 1
    
    # Risk assessment based on document analysis
    risk_factors = []
    
    # Document count factor - refined logic
    if len(documents) > 30:
        risk_factors.append("Exceptionally high document volume")
        complexity_score += 4
    elif len(documents) > 20:
        # Check if over-documentation (many simple docs)
        simple_docs = sum(1 for t in doc_types if t in ['business_license', 'insurance', 'other'])
        if simple_docs > len(documents) * 0.7:  # 70% simple docs
            risk_factors.append("Well-documented application with comprehensive supporting materials")
            complexity_score -= 1  # Actually reduces risk
        else:
            risk_factors.append("High document volume requiring detailed review")
            complexity_score += 2
    elif len(documents) > 10:
        risk_factors.append("Moderate document volume")
        complexity_score += 1
    
    # Document type complexity
    if 'financial_statement' in doc_types:
        risk_factors.append("Complex financial documents detected")
        complexity_score += 3
    if 'legal' in doc_types:
        risk_factors.append("Legal agreements requiring compliance review")
        complexity_score += 2
    if 'tax_document' in doc_types:
        risk_factors.append("Tax documents requiring verification")
        complexity_score += 2
    
    # Missing standard documents
    required_types = ['business_license', 'financial', 'tax_document']
    missing_types = [t for t in required_types if t not in doc_types]
    if missing_types:
        risk_factors.append(f"Missing standard documents: {', '.join(missing_types)}")
        complexity_score += len(missing_types) * 2
    
    # File size analysis
    if total_size > 50 * 1024 * 1024:  # 50MB
        risk_factors.append("Large file sizes indicating complex documentation")
        complexity_score += 2
    
    # Determine workflow based on complexity score
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
        'total_size_mb': round(total_size / (1024 * 1024), 2)
    }