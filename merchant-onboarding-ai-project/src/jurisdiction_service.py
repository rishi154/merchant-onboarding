"""Jurisdiction detection and management service"""
import re
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass

@dataclass
class JurisdictionConfig:
    code: str
    name: str
    currency: str
    date_format: str
    language: str
    compliance_rules: List[str]
    processing_sla_hours: int

class JurisdictionService:
    """Core service for jurisdiction detection and configuration"""
    
    JURISDICTIONS = {
        "US": JurisdictionConfig(
            code="US", name="United States", currency="USD", 
            date_format="MM/DD/YYYY", language="en-US",
            compliance_rules=["BSA", "OFAC", "FinCEN", "State_Licensing"],
            processing_sla_hours=72
        ),
        "UK": JurisdictionConfig(
            code="UK", name="United Kingdom", currency="GBP",
            date_format="DD/MM/YYYY", language="en-GB", 
            compliance_rules=["FCA", "PCI-DSS", "MLR_2017"],
            processing_sla_hours=96
        ),
        "EU": JurisdictionConfig(
            code="EU", name="European Union", currency="EUR",
            date_format="DD/MM/YYYY", language="en-EU",
            compliance_rules=["GDPR", "PSD2", "5AMLD", "MiFID_II"],
            processing_sla_hours=120
        ),
        "CA": JurisdictionConfig(
            code="CA", name="Canada", currency="CAD",
            date_format="DD/MM/YYYY", language="en-CA",
            compliance_rules=["FINTRAC", "PIPEDA", "Provincial_Regs"],
            processing_sla_hours=96
        )
    }
    
    def detect_jurisdiction(self, merchant_data: Dict) -> str:
        """Detect jurisdiction from merchant data"""
        # Check business address
        if 'business_address' in merchant_data:
            country = self._extract_country(merchant_data['business_address'])
            if country in self.JURISDICTIONS:
                return country
        
        # Check incorporation country
        if 'incorporation_country' in merchant_data:
            country = merchant_data['incorporation_country'].upper()
            if country in self.JURISDICTIONS:
                return country
                
        # Default to US
        return "US"
    
    def get_jurisdiction_config(self, jurisdiction: str) -> JurisdictionConfig:
        """Get configuration for jurisdiction"""
        return self.JURISDICTIONS.get(jurisdiction, self.JURISDICTIONS["US"])
    
    def get_workflow_config(self, jurisdiction: str, business_type: str) -> Dict:
        """Get jurisdiction-specific workflow configuration"""
        config = self.get_jurisdiction_config(jurisdiction)
        
        workflow = {
            "jurisdiction": jurisdiction,
            "sla_hours": config.processing_sla_hours,
            "compliance_agents": self._get_compliance_agents(jurisdiction),
            "document_requirements": self._get_document_requirements(jurisdiction, business_type),
            "integration_providers": self._get_integration_providers(jurisdiction)
        }
        
        return workflow
    
    def _extract_country(self, address: str) -> str:
        """Extract country from address string"""
        address_upper = address.upper()
        
        if any(indicator in address_upper for indicator in ["USA", "UNITED STATES", "US"]):
            return "US"
        elif any(indicator in address_upper for indicator in ["UK", "UNITED KINGDOM", "ENGLAND", "SCOTLAND"]):
            return "UK"
        elif any(indicator in address_upper for indicator in ["CANADA", "CA"]):
            return "CA"
        elif any(indicator in address_upper for indicator in ["GERMANY", "FRANCE", "ITALY", "SPAIN", "NETHERLANDS"]):
            return "EU"
            
        return "US"  # Default
    
    def _get_compliance_agents(self, jurisdiction: str) -> List[str]:
        """Get compliance agents for jurisdiction"""
        base_agents = ["kyc_verification", "aml_screening"]
        
        if jurisdiction == "EU":
            base_agents.append("gdpr_compliance")
        elif jurisdiction == "US":
            base_agents.append("state_licensing_check")
        elif jurisdiction == "UK":
            base_agents.append("fca_compliance")
            
        return base_agents
    
    def _get_document_requirements(self, jurisdiction: str, business_type: str) -> List[str]:
        """Get required documents for jurisdiction and business type"""
        requirements = {
            "US": {
                "LLC": ["articles_of_organization", "ein_letter", "operating_agreement"],
                "Corporation": ["articles_of_incorporation", "ein_letter", "bylaws"],
                "Partnership": ["partnership_agreement", "ein_letter"]
            },
            "UK": {
                "Limited": ["certificate_of_incorporation", "memorandum", "articles"],
                "LLP": ["incorporation_document", "llp_agreement"]
            },
            "EU": {
                "GmbH": ["handelsregister", "gesellschaftsvertrag", "vat_certificate"],
                "SAS": ["kbis", "statuts", "vat_certificate"]
            },
            "CA": {
                "Corporation": ["articles_of_incorporation", "business_number", "provincial_registration"],
                "LLC": ["articles_of_organization", "business_number"]
            }
        }
        
        return requirements.get(jurisdiction, {}).get(business_type, ["business_license", "tax_document"])
    
    def _get_integration_providers(self, jurisdiction: str) -> Dict:
        """Get integration providers for jurisdiction"""
        providers = {
            "US": {
                "credit_bureau": "experian_us",
                "bank_verification": "plaid",
                "business_registry": "secretary_of_state",
                "sanctions_screening": "ofac"
            },
            "UK": {
                "credit_bureau": "experian_uk",
                "bank_verification": "truelayer", 
                "business_registry": "companies_house",
                "sanctions_screening": "hmt_sanctions"
            },
            "EU": {
                "credit_bureau": "schufa",
                "bank_verification": "tink",
                "business_registry": "european_business_registry",
                "sanctions_screening": "eu_sanctions"
            },
            "CA": {
                "credit_bureau": "equifax_ca",
                "bank_verification": "flinks",
                "business_registry": "corporations_canada",
                "sanctions_screening": "fintrac"
            }
        }
        
        return providers.get(jurisdiction, providers["US"])