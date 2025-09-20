from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from .interfaces import (
    IDocumentProcessor,
    IDocumentStorage,
    IDocumentContentProvider,
    IDocumentValidator,
    IBusinessVerifier,
    IFraudDetector
)

@dataclass
class ServiceConfig:
    """Configuration for all document processing services"""
    # Environment
    use_mock: bool = True
    
    # Document Processing Settings
    max_file_size_mb: int = 10
    supported_formats: list = field(default_factory=lambda: [".pdf", ".png", ".jpg", ".jpeg", ".tiff"])
    
    @classmethod
    def from_env(cls) -> 'ServiceConfig':
        """Load configuration from environment variables"""
        import os
        config = cls()
        
        # Core settings
        config.use_mock = os.getenv("USE_MOCK", "true").lower() == "true"
        
        # Document processing settings
        if max_size := os.getenv("MAX_FILE_SIZE_MB"):
            config.max_file_size_mb = int(max_size)
        if formats := os.getenv("SUPPORTED_FORMATS"):
            config.supported_formats = formats.split(",")
            
        return config

class ServiceFactory:
    """Factory for creating document processing service instances"""
    
    def __init__(self):
        self.config = ServiceConfig.from_env()
    
    def create_document_processor(self) -> IDocumentProcessor:
        """Create document processor instance"""
        from .mock_implementations import MockDocumentProcessingIntegrations
        return MockDocumentProcessingIntegrations()
    
    def create_document_storage(self) -> IDocumentStorage:
        """Create document storage instance"""
        from .mock_implementations import MockDocumentStorage
        return MockDocumentStorage()
    
    def create_content_provider(self) -> IDocumentContentProvider:
        """Create content provider instance"""
        from .mock_implementations import MockDocumentContentProvider
        return MockDocumentContentProvider()
    
    def create_validator(self) -> IDocumentValidator:
        """Create validator instance"""
        from .mock_implementations import MockDocumentValidator
        return MockDocumentValidator()
            
    def create_business_verifier(self) -> IBusinessVerifier:
        """Create business verification service"""
        from .mock_implementations import MockBusinessVerifier
        return MockBusinessVerifier()
    
    def create_fraud_detector(self) -> IFraudDetector:
        """Create fraud detection service"""
        from .mock_implementations import MockFraudDetector
        return MockFraudDetector()