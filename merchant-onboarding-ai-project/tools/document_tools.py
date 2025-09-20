from langchain.tools import BaseTool
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio
import os
from config.tool_config import ToolConfig

class DocumentProcessingInput(BaseModel):
    document_path: str = Field(description="Path to the document file")
    document_type: Optional[str] = Field(description="Type of document (business_license, bank_statement, etc.)")

class OCRProcessingTool(BaseTool):
    name: str = "ocr_processing"
    description: str = "Extract text and data from documents using Google Document AI"
    args_schema: type = DocumentProcessingInput
    
    def _run(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Synchronous version"""
        return asyncio.run(self._arun(document_path, document_type))
    
    async def _arun(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Extract text and structured data from document"""
        use_mock = ToolConfig.MOCK_DOCUMENT_PROCESSING
        
        if use_mock:
            return await self._mock_ocr(document_path, document_type)
        else:
            return await self._real_ocr(document_path, document_type)
    
    async def _mock_ocr(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Mock OCR processing using simple mock data"""
        try:
            # Simple mock data based on document type
            mock_text = "TechFlow Solutions LLC Business License"
            mock_fields = {"business_name": "TechFlow Solutions LLC"}
            
            return {
                "success": True,
                "extracted_text": mock_text,
                "extracted_fields": mock_fields,
                "confidence": 0.9,
                "page_count": 1,
                "mock_data": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "confidence": 0.0
            }
    
    async def _real_ocr(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Real Google Document AI OCR processing"""
        try:
            # Check if Document AI is configured
            processor_id = ToolConfig.GOOGLE_DOC_AI_PROCESSOR_ID
            if not processor_id:
                return {
                    "success": False,
                    "error": "Google Document AI processor ID not configured",
                    "extracted_text": "",
                    "confidence": 0.0
                }
            
            # Import Google Document AI (only when needed)
            from google.cloud import documentai
            
            # Initialize Document AI client
            client = documentai.DocumentProcessorServiceClient()
            
            # Read document file
            with open(document_path, "rb") as image:
                image_content = image.read()
            
            # Configure the process request
            name = f"projects/{ToolConfig.GOOGLE_CLOUD_PROJECT}/locations/{ToolConfig.GOOGLE_CLOUD_LOCATION}/processors/{processor_id}"
            
            request = documentai.ProcessRequest(
                name=name,
                raw_document=documentai.RawDocument(
                    content=image_content,
                    mime_type="image/png" if document_path.endswith(".png") else "application/pdf"
                )
            )
            
            # Process the document
            result = client.process_document(request=request)
            document = result.document
            
            # Extract structured data based on document type
            extracted_fields = {}
            if document_type == "business_license":
                extracted_fields = self._extract_business_license_fields(document)
            elif document_type == "bank_statement":
                extracted_fields = self._extract_bank_statement_fields(document)
            elif document_type == "tax_return":
                extracted_fields = self._extract_tax_return_fields(document)
            
            return {
                "success": True,
                "extracted_text": document.text,
                "extracted_fields": extracted_fields,
                "confidence": document.pages[0].layout.confidence if document.pages else 0.0,
                "page_count": len(document.pages),
                "google_doc_ai": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "confidence": 0.0
            }
    
    def _extract_business_license_fields(self, document) -> Dict[str, Any]:
        """Extract business license specific fields"""
        fields = {}
        # Simple text extraction - in production, use form parser
        text = document.text.lower()
        if "llc" in text:
            fields["entity_type"] = "LLC"
        if "license" in text:
            fields["document_type"] = "business_license"
        return fields
    
    def _extract_bank_statement_fields(self, document) -> Dict[str, Any]:
        """Extract bank statement specific fields"""
        fields = {}
        # Simple text extraction - in production, use form parser
        text = document.text
        # Look for dollar amounts, dates, etc.
        import re
        amounts = re.findall(r'\$[\d,]+\.\d{2}', text)
        if amounts:
            fields["amounts"] = amounts[:5]  # First 5 amounts found
        return fields
    
    def _extract_tax_return_fields(self, document) -> Dict[str, Any]:
        """Extract tax return specific fields"""
        fields = {}
        # Simple text extraction - in production, use form parser
        text = document.text
        import re
        ein_match = re.search(r'\d{2}-\d{7}', text)
        if ein_match:
            fields["ein"] = ein_match.group()
        return fields

class DocumentClassificationTool(BaseTool):
    name: str = "document_classification"
    description: str = "Classify document type (business_license, bank_statement, tax_return, etc.)"
    args_schema: type = DocumentProcessingInput
    
    def _run(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        return asyncio.run(self._arun(document_path, document_type))
    
    async def _arun(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Classify document type"""
        use_mock = ToolConfig.MOCK_DOCUMENT_PROCESSING
        
        if use_mock:
            return await self._mock_classification(document_path, document_type)
        else:
            return await self._real_classification(document_path, document_type)
    
    async def _mock_classification(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Mock document classification"""
        try:
            # Simple mock classification based on filename
            doc_type = "business_license" if "license" in document_path.lower() else "bank_statement"
            return {
                "success": True,
                "document_type": doc_type,
                "quality_score": 0.9,
                "classification_confidence": 0.9,
                "mock_data": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_type": "unknown",
                "quality_score": 0.0
            }
    
    async def _real_classification(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Real document classification using Google Document AI"""
        try:
            # Use VertexAI for document classification
            from google.cloud import aiplatform
            
            # Simple image-based classification using Vision API as fallback
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            
            with open(document_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Analyze text to classify document
            text = response.full_text_annotation.text.lower() if response.full_text_annotation else ""
            
            doc_type = "unknown"
            confidence = 0.5
            
            if "license" in text or "permit" in text:
                doc_type = "business_license"
                confidence = 0.9
            elif "bank" in text or "statement" in text or "balance" in text:
                doc_type = "bank_statement"
                confidence = 0.9
            elif "tax" in text or "return" in text or "irs" in text:
                doc_type = "tax_return"
                confidence = 0.9
            elif "ein" in text or "employer identification" in text:
                doc_type = "ein_letter"
                confidence = 0.9
            
            return {
                "success": True,
                "document_type": doc_type,
                "quality_score": 0.8,
                "classification_confidence": confidence,
                "google_vision": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_type": "unknown",
                "quality_score": 0.0
            }

class FraudDetectionTool(BaseTool):
    name: str = "fraud_detection"
    description: str = "Detect potential fraud indicators in documents"
    args_schema: type = DocumentProcessingInput
    
    def _run(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        return asyncio.run(self._arun(document_path, document_type))
    
    async def _arun(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Detect fraud indicators in document"""
        use_mock = ToolConfig.MOCK_DOCUMENT_PROCESSING
        
        if use_mock:
            return await self._mock_fraud_detection(document_path, document_type)
        else:
            return await self._real_fraud_detection(document_path, document_type)
    
    async def _mock_fraud_detection(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Mock fraud detection"""
        try:
            import secrets
            has_fraud = secrets.randbelow(20) == 0  # 5% chance of fraud indicators
            fraud_indicators = ["suspicious_alteration"] if has_fraud else []
            
            return {
                "success": True,
                "fraud_indicators": fraud_indicators,
                "fraud_risk": "high" if fraud_indicators else "low",
                "risk_score": len(fraud_indicators) * 0.3,
                "mock_data": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fraud_indicators": [],
                "fraud_risk": "unknown"
            }
    
    async def _real_fraud_detection(self, document_path: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """Real fraud detection using image analysis"""
        try:
            # Use Google Vision API for basic fraud detection
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            
            with open(document_path, "rb") as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Check for image manipulation
            response = client.image_properties(image=image)
            
            fraud_indicators = []
            risk_score = 0.0
            
            # Basic checks (in production, use specialized fraud detection)
            if response.error.message:
                fraud_indicators.append("image_processing_error")
                risk_score += 0.3
            
            # Check image quality/properties for signs of manipulation
            if response.image_properties_annotation:
                colors = response.image_properties_annotation.dominant_colors.colors
                if len(colors) < 3:  # Very few colors might indicate manipulation
                    fraud_indicators.append("suspicious_color_profile")
                    risk_score += 0.2
            
            fraud_risk = "high" if risk_score > 0.5 else "medium" if risk_score > 0.2 else "low"
            
            return {
                "success": True,
                "fraud_indicators": fraud_indicators,
                "fraud_risk": fraud_risk,
                "risk_score": risk_score,
                "google_vision": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fraud_indicators": [],
                "fraud_risk": "unknown"
            }

# Document Data Extraction Functions
async def extract_business_license_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from business license document"""
    if 'mock_data' in ocr_result:
        return {
            "business_name": "TechFlow Solutions LLC",
            "dba_name": "TechFlow Digital Services", 
            "business_type": "LLC",
            "tax_id": "87-1234567",
            "street": "1247 Innovation Drive",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94107",
            "phone": "415-555-0123",
            "email": "contact@techflowsolutions.com",
            "owner_name": "Sarah Chen",
            "owner_title": "Managing Member",
            "industry": "technology",
            "business_description": "Software Development Services, Digital Marketing Consulting, E-commerce Platform Management"
        }
    return {}

async def extract_financial_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from financial documents"""
    if 'mock_data' in ocr_result:
        return {
            "bank_name": "First National Bank",
            "bank_account_number": "****4567",
            "monthly_revenue": 127450,
            "annual_revenue": 1529400,
            "average_transaction_amount": 21242,
            "bank_account_type": "business_checking",
            "cash_flow_positive": True,
            "average_daily_balance": 78542
        }
    return {}

async def extract_tax_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from tax documents"""
    if 'mock_data' in ocr_result:
        return {
            "annual_revenue": 1200000,
            "years_in_business": 1,
            "tax_filing_status": "current",
            "gross_receipts": 1200000,
            "net_income": 180000
        }
    return {}

async def extract_ein_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from EIN letter"""
    if 'mock_data' in ocr_result:
        return {
            "tax_id": "87-1234567",
            "tax_id_type": "EIN",
            "irs_verified": True
        }
    return {}

async def extract_corporate_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from corporate documents"""
    if 'mock_data' in ocr_result:
        return {
            "incorporation_date": "2023-01-15",
            "incorporation_state": "DE",
            "registered_agent": "Corporation Service Company",
            "entity_type": "LLC",
            "authorized_shares": "unlimited"
        }
    return {}

async def extract_identity_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from identity documents"""
    if 'mock_data' in ocr_result:
        return {
            "owner_date_of_birth": "1985-06-15",
            "owner_address_verified": True,
            "identity_verification_status": "verified",
            "document_authenticity": "genuine"
        }
    return {}

async def extract_insurance_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from insurance documents"""
    if 'mock_data' in ocr_result:
        return {
            "general_liability_coverage": 1000000,
            "property_insurance_coverage": 500000,
            "workers_comp_coverage": True,
            "insurance_carrier": "State Farm Business",
            "policy_expiration": "2025-03-15"
        }
    return {}

async def extract_compliance_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from compliance documents"""
    if 'mock_data' in ocr_result:
        return {
            "pci_compliance_level": "SAQ_A",
            "pci_compliance_date": "2024-01-15",
            "ofac_screening_status": "clear",
            "compliance_verified": True
        }
    return {}

async def extract_processing_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from processing statements"""
    if 'mock_data' in ocr_result:
        return {
            "previous_processor": "Square",
            "monthly_volume": 125000,
            "average_ticket": 15000,
            "chargeback_rate": 0.02,
            "processing_history_clean": True
        }
    return {}

async def extract_address_verification_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from address verification documents"""
    if 'mock_data' in ocr_result:
        return {
            "address_verified": True,
            "lease_expiration": "2025-12-31",
            "utility_account_verified": True,
            "business_location_confirmed": True
        }
    return {}

async def extract_business_plan_data(ocr_result: Dict) -> Dict[str, Any]:
    """Extract data from business plan"""
    if 'mock_data' in ocr_result:
        return {
            "business_model": "B2B Software Services",
            "target_market": "Small to Medium Businesses",
            "revenue_projections": 2000000,
            "growth_strategy": "Digital Marketing & Partnerships"
        }
    return {}

async def extract_generic_data(ocr_result: Dict, doc_type: str) -> Dict[str, Any]:
    """Extract generic data from other document types"""
    if 'mock_data' in ocr_result:
        return {
            f"{doc_type}_processed": True,
            f"{doc_type}_confidence": ocr_result.get('confidence', 0.85)
        }
    return {}