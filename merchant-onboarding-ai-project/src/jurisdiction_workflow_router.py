"""Jurisdiction-aware workflow router"""
from typing import Dict, Any, List
from jurisdiction_service import JurisdictionService
from jurisdiction_document_engine import JurisdictionDocumentEngine

class JurisdictionWorkflowRouter:
    """Routes applications through jurisdiction-specific workflows"""
    
    def __init__(self):
        self.jurisdiction_service = JurisdictionService()
        self.document_engine = JurisdictionDocumentEngine()
    
    def route_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route application based on jurisdiction and complexity"""
        
        # Detect jurisdiction
        jurisdiction = self.jurisdiction_service.detect_jurisdiction(application_data)
        config = self.jurisdiction_service.get_jurisdiction_config(jurisdiction)
        
        # Get workflow configuration
        workflow_config = self.jurisdiction_service.get_workflow_config(
            jurisdiction, 
            application_data.get('business_type', 'LLC')
        )
        
        # Modify agent sequence based on jurisdiction
        agents = self._get_base_agents()
        
        if jurisdiction == "EU":
            # Add GDPR compliance agent
            agents.insert(2, "gdpr_compliance_agent")
        elif jurisdiction == "US":
            # Add state-specific licensing check
            agents.insert(3, "state_licensing_agent")
        elif jurisdiction == "UK":
            # Add FCA compliance check
            agents.insert(2, "fca_compliance_agent")
        elif jurisdiction == "CA":
            # Add FINTRAC compliance check
            agents.insert(2, "fintrac_compliance_agent")
        
        # Replace standard compliance with multi-jurisdiction compliance
        if "compliance_verification" in agents:
            idx = agents.index("compliance_verification")
            agents[idx] = "multi_jurisdiction_compliance"
        
        return {
            "jurisdiction": jurisdiction,
            "workflow_agents": agents,
            "compliance_rules": config.compliance_rules,
            "document_requirements": workflow_config["document_requirements"],
            "integration_providers": workflow_config["integration_providers"],
            "processing_sla_hours": config.processing_sla_hours,
            "currency": config.currency,
            "language": config.language
        }
    
    def _get_base_agents(self) -> List[str]:
        """Get base agent sequence"""
        return [
            "market_qualification",
            "document_processing", 
            "compliance_verification",
            "data_validation",
            "risk_assessment",
            "decision_making",
            "communication",
            "account_provisioning"
        ]
    
    def get_jurisdiction_specific_prompts(self, jurisdiction: str, agent_name: str) -> str:
        """Get jurisdiction-specific prompts for agents"""
        
        prompts = {
            "US": {
                "compliance_verification": """
                You are performing compliance verification for a US merchant. Focus on:
                - OFAC sanctions screening
                - BSA (Bank Secrecy Act) compliance
                - FinCEN requirements
                - State-specific licensing requirements
                - Federal and state tax compliance
                """,
                "risk_assessment": """
                Assess risk for US merchant using:
                - US credit scoring models (FICO)
                - State-specific risk factors
                - Industry risk based on US regulations
                - Previous bankruptcy history
                - IRS tax compliance status
                """
            },
            "UK": {
                "compliance_verification": """
                You are performing compliance verification for a UK merchant. Focus on:
                - HM Treasury sanctions screening
                - FCA authorization requirements
                - MLR 2017 (Money Laundering Regulations)
                - PCI-DSS compliance
                - Companies House verification
                """,
                "risk_assessment": """
                Assess risk for UK merchant using:
                - UK credit scoring models
                - Companies House status
                - VAT registration status
                - County-specific risk factors
                - HMRC compliance history
                """
            },
            "EU": {
                "compliance_verification": """
                You are performing compliance verification for an EU merchant. Focus on:
                - EU sanctions list screening
                - GDPR compliance verification
                - PSD2 requirements
                - 5AMLD (Anti-Money Laundering Directive)
                - MiFID II compliance (if applicable)
                """,
                "risk_assessment": """
                Assess risk for EU merchant using:
                - EU credit scoring models
                - VAT registration status
                - Trade register verification
                - Country-specific risk factors
                - EU regulatory compliance
                """
            },
            "CA": {
                "compliance_verification": """
                You are performing compliance verification for a Canadian merchant. Focus on:
                - FINTRAC compliance
                - PIPEDA privacy requirements
                - Provincial regulatory requirements
                - OSFI sanctions screening
                - CRA tax compliance
                """,
                "risk_assessment": """
                Assess risk for Canadian merchant using:
                - Canadian credit scoring models
                - Provincial risk factors
                - CRA compliance status
                - Previous insolvency history
                - Industry risk based on Canadian regulations
                """
            }
        }
        
        return prompts.get(jurisdiction, {}).get(agent_name, "")
    
    def get_jurisdiction_decision_criteria(self, jurisdiction: str) -> Dict[str, Any]:
        """Get jurisdiction-specific decision criteria"""
        
        criteria = {
            "US": {
                "auto_approve_threshold": 30,
                "manual_review_threshold": 70,
                "required_credit_score": 600,
                "max_risk_score": 85,
                "prohibited_industries": ["adult", "gambling", "cryptocurrency"]
            },
            "UK": {
                "auto_approve_threshold": 35,
                "manual_review_threshold": 65,
                "required_credit_score": 650,
                "max_risk_score": 80,
                "prohibited_industries": ["adult", "gambling", "high_risk_crypto"]
            },
            "EU": {
                "auto_approve_threshold": 40,
                "manual_review_threshold": 60,
                "required_credit_score": 700,
                "max_risk_score": 75,
                "prohibited_industries": ["adult", "gambling", "unregulated_crypto"]
            },
            "CA": {
                "auto_approve_threshold": 35,
                "manual_review_threshold": 65,
                "required_credit_score": 650,
                "max_risk_score": 80,
                "prohibited_industries": ["adult", "gambling", "unregulated_investments"]
            }
        }
        
        return criteria.get(jurisdiction, criteria["US"])
    
    def validate_jurisdiction_requirements(self, jurisdiction: str, application_data: Dict) -> Dict[str, Any]:
        """Validate application meets jurisdiction requirements"""
        
        validation_result = {
            "is_valid": True,
            "missing_requirements": [],
            "warnings": [],
            "next_steps": []
        }
        
        # Get jurisdiction-specific requirements
        config = self.jurisdiction_service.get_jurisdiction_config(jurisdiction)
        business_type = application_data.get("business_type", "LLC")
        
        # Validate document requirements
        required_docs = self.document_engine.get_required_documents(jurisdiction, business_type)
        uploaded_docs = application_data.get("documents", [])
        
        doc_validation = self.document_engine.validate_document_set(
            jurisdiction, business_type, uploaded_docs
        )
        
        if not doc_validation["is_complete"]:
            validation_result["is_valid"] = False
            validation_result["missing_requirements"].extend(doc_validation["missing_documents"])
        
        # Jurisdiction-specific validations
        if jurisdiction == "EU" and not application_data.get("gdpr_compliant", False):
            validation_result["warnings"].append("GDPR compliance declaration required")
        
        if jurisdiction == "UK" and not application_data.get("companies_house_number"):
            validation_result["warnings"].append("Companies House number recommended")
        
        if jurisdiction == "US" and not application_data.get("ein_number"):
            validation_result["missing_requirements"].append("EIN number required")
        
        return validation_result