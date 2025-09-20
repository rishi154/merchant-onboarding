import os
from typing import Dict, Any, List
from google.cloud import documentai
import asyncio

class GoogleDocumentAI:
    """Real Google Document AI integration for OCR and document processing"""
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us")
        self.processor_id = os.getenv("GOOGLE_DOC_AI_PROCESSOR_ID")
        
        if self.project_id and self.processor_id:
            self.client = documentai.DocumentProcessorServiceClient()
            self.processor_name = self.client.processor_path(
                self.project_id, self.location, self.processor_id
            )
        else:
            self.client = None
    
    async def process_document(self, document_path: str, mime_type: str = "application/pdf") -> Dict[str, Any]:
        """Process document using Google Document AI"""
        
        if not self.client:
            raise Exception("Google Document AI not configured. Set GOOGLE_CLOUD_PROJECT and GOOGLE_DOC_AI_PROCESSOR_ID")
        
        try:
            # Read document file
            with open(document_path, "rb") as document_file:
                document_content = document_file.read()
            
            # Configure the process request
            raw_document = documentai.RawDocument(
                content=document_content,
                mime_type=mime_type
            )
            
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract text and entities
            extracted_text = document.text
            
            # Extract structured data from entities
            extracted_fields = {}
            for entity in document.entities:
                field_name = entity.type_.replace("_", " ").lower()
                field_value = entity.mention_text
                extracted_fields[field_name] = field_value
            
            # Calculate confidence score
            confidence_scores = [entity.confidence for entity in document.entities if entity.confidence > 0]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.8
            
            return {
                "extracted_text": extracted_text,
                "extracted_fields": extracted_fields,
                "confidence": overall_confidence,
                "page_count": len(document.pages),
                "entities_found": len(document.entities),
                "processor_version": result.document.document_layout_version
            }
            
        except Exception as e:
            raise Exception(f"Google Document AI processing failed: {str(e)}")
    
    async def classify_document_type(self, document_path: str) -> str:
        """Classify document type using Google Document AI"""
        
        try:
            result = await self.process_document(document_path)
            extracted_text = result["extracted_text"].lower()
            
            # Simple classification based on content
            if "business license" in extracted_text or "license number" in extracted_text:
                return "business_license"
            elif "bank statement" in extracted_text or "account balance" in extracted_text:
                return "bank_statement"
            elif "tax return" in extracted_text or "form 1120" in extracted_text:
                return "tax_return"
            elif "articles of incorporation" in extracted_text:
                return "incorporation_docs"
            else:
                return "unknown"
                
        except Exception:
            return "unknown"
    
    async def assess_document_quality(self, document_path: str) -> float:
        """Assess document quality using Google Document AI confidence scores"""
        
        try:
            result = await self.process_document(document_path)
            return result["confidence"]
        except Exception:
            return 0.5  # Default medium quality if processing fails