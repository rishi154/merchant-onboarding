from langgraph.graph import StateGraph, END
from state import MerchantOnboardingState, ApplicationStatus
import sys
import os
import importlib.util

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

def load_agent(agent_path, agent_name):
    spec = importlib.util.spec_from_file_location(agent_name, agent_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, agent_name)

def create_agent_wrapper(agent_func, agent_name):
    """Wrapper to add progress tracking to agents"""
    async def wrapped_agent(state):
        try:
            print(f"\n[{agent_name.upper()}] *** STARTING AGENT EXECUTION ***", flush=True)
            print(f"[{agent_name.upper()}] Processing merchant application...", flush=True)
            
            # Emit progress update
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'starting', {})
            
            result = await agent_func(state)
            print(f"[{agent_name.upper()}] *** AGENT COMPLETED SUCCESSFULLY ***", flush=True)
            print(f"[{agent_name.upper()}] Results generated and passed to next agent\n", flush=True)
            
            # Update agents_executed list
            if hasattr(result, 'agents_executed'):
                result.agents_executed.append(agent_name)
            elif hasattr(state, 'agents_executed'):
                state.agents_executed.append(agent_name)
            
            # Emit completion update
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                agent_result = getattr(result, agent_name, {}) if hasattr(result, agent_name) else {}
                builtins.current_progress_callback(agent_name, 'completed', agent_result)
            
            return result
        except Exception as e:
            print(f"[{agent_name.upper()}] *** AGENT FAILED *** {e}", flush=True)
            print(f"[{agent_name.upper()}] Error details: {str(e)[:200]}...\n", flush=True)
            
            # Return state with error info but don't break the workflow
            error_result = state
            setattr(error_result, agent_name, {
                'error': str(e),
                'status': 'failed',
                'processing_time': 0.1
            })
            
            if hasattr(error_result, 'agents_executed'):
                error_result.agents_executed.append(f"{agent_name}_failed")
            
            # Emit error update
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'failed', {'error': str(e)})
            
            return error_result
    
    return wrapped_agent

# Load agents
base_path = os.path.join(os.path.dirname(__file__), '..')

def create_express_workflow():
    """3-4 agent workflow for low-risk merchants"""
    workflow = StateGraph(MerchantOnboardingState)
    
    # Load required agents
    document_processing_agent = load_agent(
        os.path.join(base_path, 'agents', 'document-processing', 'src', 'agent.py'),
        'document_processing_agent'
    )
    risk_assessment_agent = load_agent(
        os.path.join(base_path, 'agents', 'risk-assessment', 'src', 'agent.py'),
        'risk_assessment_agent'
    )
    decision_making_agent = load_agent(
        os.path.join(base_path, 'agents', 'decision-making', 'src', 'agent.py'),
        'decision_making_agent'
    )
    account_provisioning_agent = load_agent(
        os.path.join(base_path, 'agents', 'account-provisioning', 'src', 'agent.py'),
        'account_provisioning_agent'
    )
    
    # Add nodes with progress tracking
    workflow.add_node("document_processing", create_agent_wrapper(document_processing_agent, "document_processing"))
    workflow.add_node("risk_assessment", create_agent_wrapper(risk_assessment_agent, "risk_assessment"))
    workflow.add_node("decision_making", create_agent_wrapper(decision_making_agent, "decision_making"))
    workflow.add_node("account_provisioning", create_agent_wrapper(account_provisioning_agent, "account_provisioning"))
    
    # Define flow
    workflow.set_entry_point("document_processing")
    workflow.add_edge("document_processing", "risk_assessment")
    workflow.add_edge("risk_assessment", "decision_making")
    workflow.add_edge("decision_making", "account_provisioning")
    workflow.add_edge("account_provisioning", END)
    
    return workflow.compile()

def create_standard_workflow():
    """6-8 agent workflow for medium-risk merchants"""
    workflow = StateGraph(MerchantOnboardingState)
    
    # Load required agents
    document_processing_agent = load_agent(
        os.path.join(base_path, 'agents', 'document-processing', 'src', 'agent.py'),
        'document_processing_agent'
    )
    data_validation_agent = load_agent(
        os.path.join(base_path, 'agents', 'data-validation', 'src', 'agent.py'),
        'data_validation_agent'
    )
    risk_assessment_agent = load_agent(
        os.path.join(base_path, 'agents', 'risk-assessment', 'src', 'agent.py'),
        'risk_assessment_agent'
    )
    compliance_verification_agent = load_agent(
        os.path.join(base_path, 'agents', 'compliance-verification', 'src', 'agent.py'),
        'compliance_verification_agent'
    )
    decision_making_agent = load_agent(
        os.path.join(base_path, 'agents', 'decision-making', 'src', 'agent.py'),
        'decision_making_agent'
    )
    account_provisioning_agent = load_agent(
        os.path.join(base_path, 'agents', 'account-provisioning', 'src', 'agent.py'),
        'account_provisioning_agent'
    )
    communication_agent = load_agent(
        os.path.join(base_path, 'agents', 'communication', 'src', 'agent.py'),
        'communication_agent'
    )
    
    # Add nodes with progress tracking
    workflow.add_node("document_processing", create_agent_wrapper(document_processing_agent, "document_processing"))
    workflow.add_node("data_validation", create_agent_wrapper(data_validation_agent, "data_validation"))
    workflow.add_node("risk_assessment", create_agent_wrapper(risk_assessment_agent, "risk_assessment"))
    workflow.add_node("compliance_verification", create_agent_wrapper(compliance_verification_agent, "compliance_verification"))
    workflow.add_node("decision_making", create_agent_wrapper(decision_making_agent, "decision_making"))
    workflow.add_node("account_provisioning", create_agent_wrapper(account_provisioning_agent, "account_provisioning"))
    workflow.add_node("communication", create_agent_wrapper(communication_agent, "communication"))
    
    # Define flow
    workflow.set_entry_point("document_processing")
    workflow.add_edge("document_processing", "data_validation")
    workflow.add_edge("data_validation", "risk_assessment")
    workflow.add_edge("risk_assessment", "compliance_verification")
    workflow.add_edge("compliance_verification", "decision_making")
    workflow.add_edge("decision_making", "account_provisioning")
    workflow.add_edge("account_provisioning", "communication")
    workflow.add_edge("communication", END)
    
    return workflow.compile()

def create_comprehensive_workflow():
    """14 agent workflow for high-risk merchants (existing implementation)"""
    workflow = StateGraph(MerchantOnboardingState)
    
    # Load all agents
    market_qualification_agent = load_agent(
        os.path.join(base_path, 'agents', 'market-qualification', 'src', 'agent.py'),
        'market_qualification_agent'
    )
    lead_qualification_agent = load_agent(
        os.path.join(base_path, 'agents', 'lead-qualification', 'src', 'agent.py'),
        'lead_qualification_agent'
    )
    application_assistant_agent = load_agent(
        os.path.join(base_path, 'agents', 'application-assistant', 'src', 'agent.py'),
        'application_assistant_agent'
    )
    document_processing_agent = load_agent(
        os.path.join(base_path, 'agents', 'document-processing', 'src', 'agent.py'),
        'document_processing_agent'
    )
    data_validation_agent = load_agent(
        os.path.join(base_path, 'agents', 'data-validation', 'src', 'agent.py'),
        'data_validation_agent'
    )
    risk_assessment_agent = load_agent(
        os.path.join(base_path, 'agents', 'risk-assessment', 'src', 'agent.py'),
        'risk_assessment_agent'
    )
    compliance_verification_agent = load_agent(
        os.path.join(base_path, 'agents', 'compliance-verification', 'src', 'agent.py'),
        'compliance_verification_agent'
    )
    decision_making_agent = load_agent(
        os.path.join(base_path, 'agents', 'decision-making', 'src', 'agent.py'),
        'decision_making_agent'
    )
    exception_routing_agent = load_agent(
        os.path.join(base_path, 'agents', 'exception-routing', 'src', 'agent.py'),
        'exception_routing_agent'
    )
    communication_agent = load_agent(
        os.path.join(base_path, 'agents', 'communication', 'src', 'agent.py'),
        'communication_agent'
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
    
    # Add all nodes with progress tracking
    workflow.add_node("market_qualification", create_agent_wrapper(market_qualification_agent, "market_qualification"))
    workflow.add_node("lead_qualification", create_agent_wrapper(lead_qualification_agent, "lead_qualification"))
    workflow.add_node("application_assistant", create_agent_wrapper(application_assistant_agent, "application_assistant"))
    workflow.add_node("document_processing", create_agent_wrapper(document_processing_agent, "document_processing"))
    workflow.add_node("data_validation", create_agent_wrapper(data_validation_agent, "data_validation"))
    workflow.add_node("risk_assessment", create_agent_wrapper(risk_assessment_agent, "risk_assessment"))
    workflow.add_node("compliance_verification", create_agent_wrapper(compliance_verification_agent, "compliance_verification"))
    workflow.add_node("decision_making", create_agent_wrapper(decision_making_agent, "decision_making"))
    workflow.add_node("exception_routing", create_agent_wrapper(exception_routing_agent, "exception_routing"))
    workflow.add_node("communication", create_agent_wrapper(communication_agent, "communication"))
    workflow.add_node("account_provisioning", create_agent_wrapper(account_provisioning_agent, "account_provisioning"))
    workflow.add_node("monitoring", create_agent_wrapper(monitoring_agent, "monitoring"))
    workflow.add_node("optimization", create_agent_wrapper(optimization_agent, "optimization"))
    workflow.add_node("onboarding_support", create_agent_wrapper(onboarding_support_agent, "onboarding_support"))
    
    # Define complete 14-agent flow
    workflow.set_entry_point("market_qualification")
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

def get_workflow_graph(pattern):
    """Get workflow graph for specified pattern"""
    if pattern == "express_workflow":
        return create_express_workflow()
    elif pattern == "standard_workflow":
        return create_standard_workflow()
    else:
        return create_comprehensive_workflow()