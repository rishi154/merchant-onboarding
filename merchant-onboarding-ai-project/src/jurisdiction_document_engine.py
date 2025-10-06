"""Jurisdiction-specific document processing engine"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DocumentRequirement:
    document_type: str
    required: bool
    alternatives: List[str]
    validation_rules: Dict

class JurisdictionDocumentEngine:
    """Manages jurisdiction-specific document requirements and processing"""
    
    DOCUMENT_REQUIREMENTS = {
        "US": {
            "LLC": [
                DocumentRequirement("articles_of_organization", True, [], {"issuer": "state_authority"}),
                DocumentRequirement("ein_letter", True, ["ss4_form"], {"format": "irs_format"}),
                DocumentRequirement("operating_agreement", False, [], {})
            ],
            "Corporation": [
                DocumentRequirement("articles_of_incorporation", True, [], {"issuer": "state_authority"}),
                DocumentRequirement("ein_letter", True, ["ss4_form"], {"format": "irs_format"}),
                DocumentRequirement("bylaws", False, [], {})
            ]
        },
        "UK": {
            "Limited": [
                DocumentRequirement("certificate_of_incorporation", True, [], {"issuer": "companies_house"}),
                DocumentRequirement("memorandum", True, [], {}),
                DocumentRequirement("articles_of_association", True, [], {})
            ],
            "LLP": [
                DocumentRequirement("incorporation_document", True, [], {"issuer": "companies_house"}),
                DocumentRequirement("llp_agreement", False, [], {})
            ]
        },
        "EU": {
            "GmbH": [
                DocumentRequirement("handelsregister", True, [], {"issuer": "commercial_register"}),
                DocumentRequirement("gesellschaftsvertrag", True, [], {}),
                DocumentRequirement("vat_certificate", True, [], {"format": "eu_vat"})
            ],
            "SAS": [
                DocumentRequirement("kbis", True, [], {"issuer": "commercial_court"}),
                DocumentRequirement("statuts", True, [], {}),
                DocumentRequirement("vat_certificate", True, [], {"format": "eu_vat"})
            ]
        },
        "CA": {
            "Corporation": [
                DocumentRequirement("articles_of_incorporation", True, [], {"issuer": "provincial_authority"}),
                DocumentRequirement("business_number", True, [], {"format": "cra_format"}),
                DocumentRequirement("provincial_registration", True, [], {})
            ]
        }
    }
    
    def get_required_documents(self, jurisdiction: str, business_type: str) -> List[DocumentRequirement]:
        """Get required documents for jurisdiction and business type"""
        return self.DOCUMENT_REQUIREMENTS.get(jurisdiction, {}).get(business_type, [])
    
    def validate_document_set(self, jurisdiction: str, business_type: str, uploaded_documents: List[str]) -> Dict:
        """Validate if uploaded documents meet jurisdiction requirements"""
        required_docs = self.get_required_documents(jurisdiction, business_type)
        
        validation_result = {
            "is_complete": True,
            "missing_documents": [],
            "optional_documents": [],
            "validation_errors": []
        }
        
        for req_doc in required_docs:
            if req_doc.required:
                # Check if document or alternative is present
                doc_found = any(
                    doc_type in uploaded_documents 
                    for doc_type in [req_doc.document_type] + req_doc.alternatives
                )
                
                if not doc_found:
                    validation_result["is_complete"] = False
                    validation_result["missing_documents"].append(req_doc.document_type)
            else:
                if req_doc.document_type not in uploaded_documents:
                    validation_result["optional_documents"].append(req_doc.document_type)
        
        return validation_result
    
    def get_document_processing_config(self, jurisdiction: str, document_type: str) -> Dict:
        """Get processing configuration for specific document type in jurisdiction"""
        configs = {
            "US": {
                "ein_letter": {
                    "ocr_model": "irs_form_model",
                    "validation_fields": ["ein_number", "business_name", "issue_date"],
                    "fraud_checks": ["irs_format_validation", "ein_checksum"]
                },
                "articles_of_incorporation": {
                    "ocr_model": "state_document_model",
                    "validation_fields": ["corporation_name", "state", "file_date"],
                    "fraud_checks": ["state_seal_validation", "format_check"]
                }
            },
            "UK": {
                "certificate_of_incorporation": {
                    "ocr_model": "companies_house_model",
                    "validation_fields": ["company_number", "company_name", "incorporation_date"],
                    "fraud_checks": ["companies_house_seal", "format_validation"]
                }
            },
            "EU": {
                "vat_certificate": {
                    "ocr_model": "eu_vat_model", 
                    "validation_fields": ["vat_number", "company_name", "country_code"],
                    "fraud_checks": ["vat_format_validation", "eu_seal_check"]
                }
            }
        }
        
        return configs.get(jurisdiction, {}).get(document_type, {
            "ocr_model": "generic_document_model",
            "validation_fields": ["business_name"],
            "fraud_checks": ["basic_format_check"]
        })
    
    def get_localized_document_names(self, jurisdiction: str) -> Dict[str, str]:
        """Get localized names for document types"""
        localizations = {
            "US": {
                "articles_of_incorporation": "Articles of Incorporation",
                "ein_letter": "EIN Letter (IRS)",
                "operating_agreement": "Operating Agreement"
            },
            "UK": {
                "certificate_of_incorporation": "Certificate of Incorporation",
                "memorandum": "Memorandum of Association",
                "articles_of_association": "Articles of Association"
            },
            "EU": {
                "handelsregister": "Commercial Register Extract",
                "gesellschaftsvertrag": "Articles of Association",
                "vat_certificate": "VAT Registration Certificate"
            },
            "CA": {
                "articles_of_incorporation": "Articles of Incorporation",
                "business_number": "Business Number Certificate",
                "provincial_registration": "Provincial Registration"
            }
        }
        
        return localizations.get(jurisdiction, {})