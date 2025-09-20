import asyncio
from typing import Dict, Any, List
from .document_content_provider import DocumentContentProvider

class MockDocumentProcessingIntegrations:
    """Mock document processing services using real sample data"""
    
    def __init__(self):
        self.content_provider = DocumentContentProvider()
        self.document_patterns = {
            "business_license": {
                "keywords": ["license", "permit", "certificate", "registration"],
                "required_fields": ["license_number", "issue_date", "expiry_date"],
                "patterns": [
                    r"license[:\s]+([A-Z0-9-]+)",
                    r"permit[:\s]+([A-Z0-9-]+)",
                    r"expires?[:\s]+(\d{4}-\d{2}-\d{2})"
                ]
            },
            "bank_statement": {
                "keywords": ["bank statement", "account", "balance", "transaction"],
                "required_fields": ["account_number", "balance", "period"],
                "patterns": [
                    r"account[:\s]+([*\d]+)",
                    r"balance[:\s]+[\$]?([\d,.]+)",
                    r"period[:\s]+([Q\d\s]+\d{4})"
                ]
            },
            "tax_return": {
                "keywords": ["tax return", "income", "ein", "tax paid"],
                "required_fields": ["business_income", "tax_paid", "ein"],
                "patterns": [
                    r"ein[:\s]+([\d-]+)",
                    r"income[:\s]+[\$]?([\d,.]+)",
                    r"tax paid[:\s]+[\$]?([\d,.]+)"
                ]
            },
            "processing_statement": {
                "keywords": ["processing", "transactions", "volume", "fees"],
                "required_fields": ["total_volume", "transaction_count", "period"],
                "patterns": [
                    r"volume[:\s]+[\$]?([\d,.]+)",
                    r"transactions?[:\s]+(\d+)",
                    r"period[:\s]+([Q\d\s]+\d{4})"
                ]
            }
        }
    
    async def classify_document(self, document_path: str, extracted_text: str) -> Dict[str, Any]:
        """Classify document type based on content patterns and metadata"""
        scores = {doc_type: 0.0 for doc_type in self.document_patterns.keys()}
        
        # Normalize text for consistent matching
        text_lower = extracted_text.lower()
        
        for doc_type, pattern_info in self.document_patterns.items():
            # Keyword matching
            keyword_matches = sum(1 for kw in pattern_info["keywords"] if kw in text_lower)
            scores[doc_type] += keyword_matches * 0.2
            
            # Pattern matching
            import re
            pattern_matches = sum(1 for pattern in pattern_info["patterns"] 
                                if re.search(pattern, extracted_text, re.IGNORECASE))
            scores[doc_type] += pattern_matches * 0.3
            
            # Required fields check
            field_matches = sum(1 for field in pattern_info["required_fields"] 
                              if field.lower() in text_lower)
            scores[doc_type] += (field_matches / len(pattern_info["required_fields"])) * 0.5
        
        # Get the highest scoring type
        best_type = max(scores.items(), key=lambda x: x[1])
        
        return {
            "document_type": best_type[0],
            "confidence": min(best_type[1], 1.0),
            "scores": scores
        }
    
    async def ocr_extract_text(self, document_path: str) -> Dict:
        """Enhanced OCR extraction with better error handling and field extraction"""
        await asyncio.sleep(0.2)
        
        # Get document content
        doc_result = self.content_provider.read_document_content(document_path)
        if not doc_result["success"]:
            return {
                "error": "Failed to read document",
                "confidence": 0.0,
                "extracted_text": "",
                "extracted_fields": {}
            }
        
        # For text documents, use content directly
        if not doc_result["binary"]:
            text_content = doc_result["content"]
            # Get document type
            doc_type = await self.classify_document(document_path, text_content)
            
            # Extract fields based on document type
            fields = self._extract_fields(text_content, doc_type["document_type"])
            
            return {
                "extracted_text": text_content,
                "confidence": 0.98,  # High confidence for text documents
                "extracted_fields": fields,
                "document_type": doc_type
            }
        elif "bank" in document_path:
            return {
                "extracted_text": "BANK STATEMENT\nAccount: ****1234\nBalance: $125,450.00\nDeposits: $85,000.00\nWithdrawals: $12,500.00\nPeriod: Q4 2023",
                "confidence": 0.92,
                "extracted_fields": {
                    "account_number": "****1234",
                    "balance": 125450.00,
                    "deposits": 85000.00,
                    "withdrawals": 12500.00,
                    "period": "Q4 2023"
                }
            }
        else:
            return {
                "extracted_text": "TAX RETURN 2023\nBusiness Income: $850,000\nTax Paid: $85,000\nEIN: 12-3456789",
                "confidence": 0.88,
                "extracted_fields": {
                    "business_income": 850000,
                    "tax_paid": 85000,
                    "ein": "12-3456789",
                    "year": 2023
                }
            }
    
    async def detect_fraud_indicators(self, document_path: str, extracted_data: Dict) -> Dict[str, Any]:
        """Enhanced fraud detection with detailed analysis and risk levels"""
        await asyncio.sleep(0.1)
        
        indicators = []
        risk_score = 0.0
        doc_type = extracted_data.get("document_type", {}).get("document_type")
        fields = extracted_data.get("extracted_fields", {})
        
        if doc_type == "business_license":
            # Verify license number format and consistency
            license_number = fields.get("license_number", "")
            if not license_number.startswith("BL-"):
                indicators.append({
                    "type": "invalid_license_format",
                    "severity": "high",
                    "details": "License number does not follow required format"
                })
                risk_score += 0.4
            
            # Check expiration and issue dates
            expiry_date = fields.get("expiry_date", "")
            issue_date = fields.get("issue_date", "")
            
            from datetime import datetime
            try:
                if expiry_date and issue_date:
                    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                    issued = datetime.strptime(issue_date, "%Y-%m-%d")
                    
                    if expiry < datetime.now():
                        indicators.append({
                            "type": "expired_license",
                            "severity": "high",
                            "details": "License has expired"
                        })
                        risk_score += 0.5
                    
                    if issued > datetime.now():
                        indicators.append({
                            "type": "future_issue_date",
                            "severity": "critical",
                            "details": "License issued in the future"
                        })
                        risk_score += 0.8
                    
                    if (expiry - issued).days > 365 * 2:
                        indicators.append({
                            "type": "unusual_validity_period",
                            "severity": "medium",
                            "details": "License valid for more than 2 years"
                        })
                        risk_score += 0.2
            except ValueError:
                indicators.append({
                    "type": "invalid_dates",
                    "severity": "high",
                    "details": "Invalid date format in license"
                })
                risk_score += 0.4

        elif doc_type == "bank_statement":
            # Analyze transaction patterns
            balance = fields.get("balance", 0)
            deposits = fields.get("deposits", 0)
            withdrawals = fields.get("withdrawals", 0)
            
            if balance > 0 and deposits > 0:
                # Check for unusually large deposits
                if deposits > balance * 2:
                    indicators.append({
                        "type": "suspicious_deposits",
                        "severity": "high",
                        "details": "Deposits significantly larger than balance"
                    })
                    risk_score += 0.4
                
                # Check for round number transactions
                if deposits % 1000 == 0 or withdrawals % 1000 == 0:
                    indicators.append({
                        "type": "round_number_transactions",
                        "severity": "low",
                        "details": "Suspicious round number transactions"
                    })
                    risk_score += 0.1
            
        elif doc_type == "processing_statement":
            # Analyze processing patterns
            volume = fields.get("total_volume", 0)
            transactions = fields.get("transaction_count", 0)
            
            if volume > 0 and transactions > 0:
                avg_transaction = volume / transactions
                if avg_transaction > 10000:
                    indicators.append({
                        "type": "high_average_transaction",
                        "severity": "medium",
                        "details": f"Unusually high average transaction: ${avg_transaction:,.2f}"
                    })
                    risk_score += 0.3
            
            chargeback_amount = fields.get("chargeback_amount", 0)
            if chargeback_amount > volume * 0.02:
                indicators.append({
                    "type": "high_chargeback_rate",
                    "severity": "high",
                    "details": "Chargebacks exceed 2% of volume"
                })
                risk_score += 0.5

        return {
            "indicators": indicators,
            "risk_score": min(risk_score, 1.0),
            "risk_level": "critical" if risk_score > 0.7 else "high" if risk_score > 0.4 else "medium" if risk_score > 0.2 else "low"
        }
    
    async def validate_document(self, document_path: str, extracted_data: Dict) -> Dict[str, Any]:
        """Validate document content against type-specific rules"""
        doc_type = extracted_data.get("document_type", {}).get("document_type")
        if not doc_type or doc_type not in self.document_patterns:
            return {
                "valid": False,
                "errors": ["Unknown or invalid document type"],
                "warnings": []
            }
        
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = self.document_patterns[doc_type]["required_fields"]
        for field in required_fields:
            if field not in extracted_data.get("extracted_fields", {}):
                errors.append(f"Missing required field: {field}")
        
        # Document type specific validations
        if doc_type == "business_license":
            fields = extracted_data.get("extracted_fields", {})
            # Check expiration date
            expiry_date = fields.get("expiry_date")
            if expiry_date:
                from datetime import datetime
                try:
                    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                    if expiry < datetime.now():
                        errors.append("License has expired")
                    elif (expiry - datetime.now()).days < 90:
                        warnings.append("License expires in less than 90 days")
                except ValueError:
                    errors.append("Invalid expiration date format")
        
        elif doc_type == "bank_statement":
            fields = extracted_data.get("extracted_fields", {})
            # Check balance and transaction consistency
            balance = fields.get("balance", 0)
            deposits = fields.get("deposits", 0)
            withdrawals = fields.get("withdrawals", 0)
            
            if balance < 0:
                errors.append("Negative balance")
            if deposits < 0 or withdrawals < 0:
                errors.append("Invalid transaction amounts")
            if balance < 10000:
                warnings.append("Low account balance")
        
        elif doc_type == "processing_statement":
            fields = extracted_data.get("extracted_fields", {})
            # Check processing volume and transaction count
            volume = fields.get("total_volume", 0)
            transactions = fields.get("transaction_count", 0)
            
            if volume < 0 or transactions < 0:
                errors.append("Invalid processing statistics")
            if transactions > 0:
                avg_transaction = volume / transactions
                if avg_transaction > 10000:
                    warnings.append("Unusually high average transaction amount")
                elif avg_transaction < 1:
                    warnings.append("Unusually low average transaction amount")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _extract_fields(self, text_content: str, doc_type: str) -> Dict[str, Any]:
        """Extract fields from text content based on document type patterns"""
        import re
        fields = {}
        
        if doc_type not in self.document_patterns:
            return fields
            
        patterns = self.document_patterns[doc_type]["patterns"]
        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                # Convert field values to appropriate types
                value = match.group(1).strip()
                if any(c.isdigit() for c in value):
                    # Try to convert to number if it looks like one
                    try:
                        # Remove currency symbols and commas
                        cleaned = value.replace("$", "").replace(",", "")
                        if "." in cleaned:
                            fields[pattern.split("[")[0]] = float(cleaned)
                        else:
                            fields[pattern.split("[")[0]] = int(cleaned)
                    except ValueError:
                        fields[pattern.split("[")[0]] = value
                else:
                    fields[pattern.split("[")[0]] = value
                    
        return fields

    async def assess_document_quality(self, document_path: str) -> float:
        """Assess document quality"""
        await asyncio.sleep(0.1)
        
        doc_result = self.content_provider.read_document_content(document_path)
        if not doc_result["success"]:
            return 0.5
        
        if doc_result["binary"]:
            # Image/PDF quality assessment
            if document_path.endswith('.pdf'):
                return 0.95  # Assume PDFs are high quality
            elif document_path.endswith('.png'):
                return 0.90  # Assume PNGs are good quality
            elif document_path.endswith('.jpg'):
                return 0.85  # Assume JPGs are acceptable quality
        else:
            # Text document quality assessment
            content = doc_result["content"]
            if len(content) < 10:
                return 0.3  # Too short
            elif len(content.split('\n')) < 2:
                return 0.5  # Not properly formatted
            else:
                return 0.98  # Text documents are typically high quality
        
        return 0.7  # Default quality score