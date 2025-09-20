from langgraph.graph import StateGraph, END
from state import MerchantOnboardingState, ApplicationStatus
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

# Import agents using proper folder names with hyphens
import importlib.util

def load_agent(agent_path, agent_name):
    spec = importlib.util.spec_from_file_location(agent_name, agent_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, agent_name)

# Load all agents (fix path to go up one level to find agents directory)
base_path = os.path.join(os.path.dirname(__file__), '..')
market_qualification_agent = load_agent(
    os.path.join(base_path, 'agents', 'market-qualification', 'src', 'agent.py'),
    'market_qualification_agent'
)
document_processing_agent = load_agent(
    os.path.join(base_path, 'agents', 'document-processing', 'src', 'agent.py'),
    'document_processing_agent'
)
risk_assessment_agent = load_agent(
    os.path.join(base_path, 'agents', 'risk-assessment', 'src', 'agent.py'),
    'risk_assessment_agent'
)
lead_qualification_agent = load_agent(
    os.path.join(base_path, 'agents', 'lead-qualification', 'src', 'agent.py'),
    'lead_qualification_agent'
)
application_assistant_agent = load_agent(
    os.path.join(base_path, 'agents', 'application-assistant', 'src', 'agent.py'),
    'application_assistant_agent'
)
exception_routing_agent = load_agent(
    os.path.join(base_path, 'agents', 'exception-routing', 'src', 'agent.py'),
    'exception_routing_agent'
)

def should_continue_processing(state: MerchantOnboardingState) -> str:
    """Router function to determine next step"""
    if state.status == ApplicationStatus.EXCEPTION:
        return "exception_routing"
    elif state.market_qualification and not state.market_qualification.get("qualified"):
        return "decline"
    elif state.document_processing and state.document_processing.get("requires_manual_review"):
        return "exception_routing"
    elif state.risk_assessment and state.risk_assessment.get("requires_manual_review"):
        return "exception_routing"
    else:
        return "continue"

def create_onboarding_workflow():
    """Create the LangGraph workflow for merchant onboarding"""
    
    workflow = StateGraph(MerchantOnboardingState)
    
    # Load additional agents
    data_validation_agent = load_agent(
        os.path.join(base_path, 'agents', 'data-validation', 'src', 'agent.py'),
        'data_validation_agent'
    )
    decision_making_agent = load_agent(
        os.path.join(base_path, 'agents', 'decision-making', 'src', 'agent.py'),
        'decision_making_agent'
    )
    communication_agent = load_agent(
        os.path.join(base_path, 'agents', 'communication', 'src', 'agent.py'),
        'communication_agent'
    )
    compliance_verification_agent = load_agent(
        os.path.join(base_path, 'agents', 'compliance-verification', 'src', 'agent.py'),
        'compliance_verification_agent'
    )
    account_provisioning_agent = load_agent(
        os.path.join(base_path, 'agents', 'account-provisioning', 'src', 'agent.py'),
        'account_provisioning_agent'
    )
    monitoring_agent = load_agent(
        os.path.join(base_path, 'agents', 'monitoring', 'src', 'agent.py'),
        'monitoring_agent'
    )
    optimization_agent = load_agent(
        os.path.join(base_path, 'agents', 'optimization', 'src', 'agent.py'),
        'optimization_agent'
    )
    onboarding_support_agent = load_agent(
        os.path.join(base_path, 'agents', 'onboarding-support', 'src', 'agent.py'),
        'onboarding_support_agent'
    )
    
    # Add nodes (all 14 agents)
    workflow.add_node("market_qualification", market_qualification_agent)
    workflow.add_node("lead_qualification", lead_qualification_agent)
    workflow.add_node("application_assistant", application_assistant_agent)
    workflow.add_node("document_processing", document_processing_agent)
    workflow.add_node("data_validation", data_validation_agent)
    workflow.add_node("risk_assessment", risk_assessment_agent)
    workflow.add_node("compliance_verification", compliance_verification_agent)
    workflow.add_node("decision_making", decision_making_agent)
    workflow.add_node("exception_routing", exception_routing_agent)
    workflow.add_node("communication", communication_agent)
    workflow.add_node("account_provisioning", account_provisioning_agent)
    workflow.add_node("monitoring", monitoring_agent)
    workflow.add_node("optimization", optimization_agent)
    workflow.add_node("onboarding_support", onboarding_support_agent)
    
    # Define the flow
    workflow.set_entry_point("market_qualification")
    
    # Complete 14-agent flow
    workflow.add_edge("market_qualification", "lead_qualification")
    workflow.add_edge("lead_qualification", "application_assistant")
    workflow.add_edge("application_assistant", "document_processing")
    workflow.add_edge("document_processing", "data_validation")
    workflow.add_edge("data_validation", "risk_assessment")
    workflow.add_edge("risk_assessment", "compliance_verification")
    workflow.add_edge("compliance_verification", "decision_making")
    workflow.add_edge("decision_making", "exception_routing")
    workflow.add_edge("exception_routing", "communication")
    workflow.add_edge("communication", "account_provisioning")
    workflow.add_edge("account_provisioning", "monitoring")
    workflow.add_edge("monitoring", "optimization")
    workflow.add_edge("optimization", "onboarding_support")
    workflow.add_edge("onboarding_support", END)
    
    return workflow.compile()