from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum

class DocumentType(Enum):
    """Document types supported by the system"""
    BUSINESS_LICENSE = "business_license"
    BANK_STATEMENT = "bank_statement"
    TAX_RETURN = "tax_return"
    ID_DOCUMENT = "id_document"
    PROCESSING_STATEMENT = "processing_statement"
    OWNERSHIP_DOCUMENT = "ownership_document"

class VerificationLevel(Enum):
    """Verification levels for business verification"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"

class IDocumentProcessor(ABC):
    """Base interface for document processing services"""
    
    @abstractmethod
    async def ocr_extract_text(self, document_path: str) -> Dict[str, Any]:
        """Extract text from document using OCR
        Returns:
            Dict with keys:
            - extracted_text: str
            - confidence: float
            - extracted_fields: Dict[str, Any]
        """
        pass
    
    @abstractmethod
    async def detect_fraud_indicators(self, document_path: str, extracted_data: Dict) -> Dict[str, Any]:
        """Check for potential fraud indicators
        Returns:
            Dict with keys:
            - indicators: List[Dict] with type, severity, details
            - risk_score: float
            - risk_level: str
        """
        pass
    
    @abstractmethod
    async def assess_document_quality(self, document_path: str) -> float:
        """Assess document quality and return score between 0-1"""
        pass
    
    @abstractmethod
    async def classify_document(self, document_path: str, extracted_text: str) -> Dict[str, Any]:
        """Classify document type
        Returns:
            Dict with keys:
            - document_type: str
            - confidence: float
            - scores: Dict[str, float]
        """
        pass

class IDocumentContentProvider(ABC):
    """Base interface for document content access"""
    
    @abstractmethod
    def read_document_content(self, document_path: str) -> Dict[str, Any]:
        """Read document content
        Returns:
            Dict with keys:
            - success: bool
            - content: str or bytes
            - binary: bool
            - error: str (optional)
        """
        pass
    
    @abstractmethod
    def get_document_type(self, document_path: str) -> str:
        """Get document type from path or content"""
        pass

class IDocumentStorage(ABC):
    """Base interface for document storage"""
    
    @abstractmethod
    async def store_document(self, document_path: str, metadata: Dict[str, Any]) -> str:
        """Store document and return storage ID"""
        pass
    
    @abstractmethod
    async def retrieve_document(self, storage_id: str) -> Dict[str, Any]:
        """Retrieve document and metadata"""
        pass
    
    @abstractmethod
    async def delete_document(self, storage_id: str) -> bool:
        """Delete stored document"""
        pass

class IDocumentValidator(ABC):
    """Base interface for document validation"""
    
    @abstractmethod
    async def validate_document(self, document_path: str, extracted_data: Dict) -> Dict[str, Any]:
        """Validate document content and structure
        Returns:
            Dict with keys:
            - valid: bool
            - errors: List[str]
            - warnings: List[str]
        """
        pass

class IBusinessVerifier(ABC):
    """Base interface for business verification services"""
    
    @abstractmethod
    async def verify_business(self,
                            business_name: str,
                            tax_id: str,
                            state: str,
                            level: VerificationLevel = VerificationLevel.STANDARD
                            ) -> Dict[str, Any]:
        """Verify business details with external services
        Returns:
            Dict with verification results including registration, licenses, and risk data
        """
        pass

class IFraudDetector(ABC):
    """Base interface for fraud detection services"""
    
    @abstractmethod
    async def detect_fraud(self,
                         document_path: str,
                         document_type: DocumentType,
                         extracted_data: Dict[str, Any]
                         ) -> Dict[str, Any]:
        """Detect potential fraud in documents
        Returns:
            Dict with fraud detection results including indicators and risk scores
        """
        pass
    
    @abstractmethod
    async def analyze_document_authenticity(self,
                                         document_path: str,
                                         document_type: DocumentType
                                         ) -> Dict[str, Any]:
        """Analyze document for signs of tampering or manipulation
        Returns:
            Dict with authenticity analysis results
        """
        pass