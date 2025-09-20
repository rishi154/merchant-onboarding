from typing import Dict, Any
from state import MerchantOnboardingState

def determine_workflow_pattern(state: MerchantOnboardingState) -> str:
    """Route to appropriate workflow based on risk assessment"""
    market_qual = state.market_qualification
    
    if market_qual and market_qual.get("risk_tier"):
        risk_tier = market_qual["risk_tier"]
        if risk_tier == "LOW":
            return "express_workflow"
        elif risk_tier == "MEDIUM":
            return "standard_workflow"
        else:
            return "comprehensive_workflow"
    
    return "comprehensive_workflow"  # Default fallback

def get_workflow_steps(pattern: str) -> list:
    """Get workflow steps for UI display"""
    workflows = {
        "express_workflow": [
            {"name": "Document Processing", "description": "Extract and validate document data"},
            {"name": "Risk Assessment", "description": "Quick risk evaluation"},
            {"name": "Auto Decision", "description": "Automated approval decision"},
            {"name": "Account Setup", "description": "Provision merchant account"}
        ],
        "standard_workflow": [
            {"name": "Document Processing", "description": "Extract and validate document data"},
            {"name": "Data Validation", "description": "Cross-reference extracted data"},
            {"name": "Risk Assessment", "description": "Comprehensive risk analysis"},
            {"name": "Compliance Check", "description": "Regulatory compliance verification"},
            {"name": "Decision Making", "description": "Approval decision with review"},
            {"name": "Account Setup", "description": "Provision merchant account"},
            {"name": "Communication", "description": "Send notifications and documentation"}
        ],
        "comprehensive_workflow": [
            {"name": "Market Qualification", "description": "Market and business model analysis"},
            {"name": "Lead Qualification", "description": "Lead quality assessment"},
            {"name": "Application Assistant", "description": "Application completeness check"},
            {"name": "Document Processing", "description": "Advanced document analysis"},
            {"name": "Data Validation", "description": "Multi-source data verification"},
            {"name": "Risk Assessment", "description": "Comprehensive risk modeling"},
            {"name": "Compliance Verification", "description": "Full regulatory compliance"},
            {"name": "Decision Making", "description": "Multi-factor decision analysis"},
            {"name": "Exception Routing", "description": "Handle special cases"},
            {"name": "Communication", "description": "Stakeholder communications"},
            {"name": "Account Provisioning", "description": "Full account setup"},
            {"name": "Monitoring", "description": "Setup monitoring and alerts"},
            {"name": "Optimization", "description": "Performance optimization"},
            {"name": "Onboarding Support", "description": "Support and training setup"}
        ]
    }
    
    return workflows.get(pattern, workflows["comprehensive_workflow"])

def get_workflow_metadata(pattern: str) -> Dict[str, Any]:
    """Get workflow metadata for UI"""
    metadata = {
        "express_workflow": {
            "name": "Express Workflow",
            "description": "Fast-track processing for low-risk merchants",
            "estimated_time": "5-15 minutes",
            "automation_rate": "95%",
            "risk_level": "Low",
            "color": "green"
        },
        "standard_workflow": {
            "name": "Standard Workflow", 
            "description": "Balanced verification for medium-risk merchants",
            "estimated_time": "30-60 minutes",
            "automation_rate": "75%",
            "risk_level": "Medium",
            "color": "blue"
        },
        "comprehensive_workflow": {
            "name": "Comprehensive Workflow",
            "description": "Full verification for high-risk merchants",
            "estimated_time": "2-24 hours", 
            "automation_rate": "60%",
            "risk_level": "High",
            "color": "red"
        }
    }
    
    return metadata.get(pattern, metadata["comprehensive_workflow"])