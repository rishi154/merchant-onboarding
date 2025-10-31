from langgraph.graph import StateGraph, END
from state import MerchantOnboardingState, ApplicationStatus
import sys
import os
import importlib.util
import builtins

# Add current directory to path
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))

# Configuration for which agents require human review
AGENT_REVIEW_CONFIG = {
    # Set to True to require human review, False to auto-approve
    'document_processing': False,  # Auto-approve for routing phase
    'data_validation': True,   # Enable review for proper UI tracking
    'risk_assessment': False,  # Auto-approve for routing phase
    'compliance_verification': True,
    'decision_making': False,   # Enable review for decision validation
    'account_provisioning': False,
    'communication': False,
    'market_qualification': False,
    'lead_qualification': False,
    'exception_routing': False,
    'monitoring': False,
    'optimization': False,
    'onboarding_support': False
}

def requires_human_review(agent_name):
    """Check if agent requires human review based on configuration"""
    return AGENT_REVIEW_CONFIG.get(agent_name, True)  # Default to True for safety

def load_agent(agent_path, agent_name):
    spec = importlib.util.spec_from_file_location(agent_name, agent_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, agent_name)

def create_agent_wrapper(agent_func, agent_name):
    """Wrapper to add progress tracking and human review to agents"""
    async def wrapped_agent(state):
        try:
            print(f"\n[{agent_name.upper()}] *** STARTING AGENT EXECUTION ***", flush=True)
            print(f"[{agent_name.upper()}] Processing merchant application...", flush=True)
            
            # Store app_id locally to prevent mixing
            current_app_id = state.application_id
            print(f"[{agent_name.upper()}] Processing app_id: {current_app_id}")
            
            # Reset review status for this agent (only if review required)
            if requires_human_review(agent_name):
                try:
                    from models import MerchantApplication, SessionLocal
                    
                    session = SessionLocal()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    if app:
                        app.needs_review = 'true'  # Reset for this agent
                        app.review_agent = agent_name
                        session.commit()
                        print(f"[{agent_name.upper()}] Reset review status for new agent")
                    else:
                        print(f"[{agent_name.upper()}] WARNING: App {current_app_id} not found during reset")
                    session.close()
                except Exception as e:
                    print(f"[{agent_name.upper()}] Error resetting review status: {e}")
            else:
                print(f"[{agent_name.upper()}] Skipping review setup - auto-approved agent")
            
            # ALWAYS emit progress update and save to database for ALL agents
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'starting', {})
            
            # ALWAYS save to database directly for ALL agents
            try:
                from models import MerchantApplication, SessionLocal
                from datetime import datetime
                session = SessionLocal()
                app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                if app:
                    app.current_agent = agent_name
                    app.updated_at = datetime.now()
                    session.commit()
                session.close()
            except Exception as e:
                print(f"[{agent_name.upper()}] Error updating start status: {e}")
            
            result = await agent_func(state)
            print(f"[{agent_name.upper()}] *** AGENT COMPLETED SUCCESSFULLY ***", flush=True)
            if requires_human_review(agent_name):
                print(f"[{agent_name.upper()}] Results generated - PAUSING FOR HUMAN REVIEW\n", flush=True)
            else:
                print(f"[{agent_name.upper()}] Results generated - AUTO-APPROVED\n", flush=True)
            
            # Update agents_executed list
            if hasattr(result, 'agents_executed'):
                result.agents_executed.append(agent_name)
            elif hasattr(state, 'agents_executed'):
                state.agents_executed.append(agent_name)
            
            # Extract actual agent result first
            if hasattr(result, agent_name):
                agent_result = getattr(result, agent_name)
            elif isinstance(result, dict) and agent_name in result:
                agent_result = result[agent_name]
            else:
                # Fallback - use the entire result if agent-specific result not found
                agent_result = result.__dict__ if hasattr(result, '__dict__') else result
            
            # ALWAYS save completed result to database for ALL agents
            try:
                from models import MerchantApplication, SessionLocal
                from datetime import datetime
                session = SessionLocal()
                app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                if app:
                    current_results = app.agent_results or {}
                    current_results[agent_name] = agent_result
                    app.agent_results = current_results
                    app.current_agent = agent_name
                    app.updated_at = datetime.now()
                    session.commit()
                    print(f"[{agent_name.upper()}] Saved agent result to database")
                session.close()
            except Exception as e:
                print(f"[{agent_name.upper()}] Error saving result: {e}")
            
            # ALWAYS emit completed status for ALL agents
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'completed', agent_result)
            
            print(f"[{agent_name.upper()}] Agent result: {agent_result}")
            print(f"[{agent_name.upper()}] Review required: {requires_human_review(agent_name)}")
            
            # Check if this agent requires human review
            if requires_human_review(agent_name):
                print(f"[{agent_name.upper()}] Human review required - pausing workflow")
                
                # Set review state
                state.needs_review = True
                state.review_agent = agent_name
                state.review_data = agent_result
                state.status = ApplicationStatus.PENDING_HUMAN_REVIEW
                
                # Add to review queue
                try:
                    await add_to_review_queue(state.application_id, agent_name, agent_result)
                except Exception as e:
                    print(f"[{agent_name.upper()}] Error adding to review queue: {e}")
                
                # Save review required status to database
                try:
                    from models import MerchantApplication, SessionLocal
                    from datetime import datetime
                    session = SessionLocal()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    if app:
                        current_results = app.agent_results or {}
                        current_results[agent_name] = agent_result
                        app.agent_results = current_results
                        app.needs_review = 'true'
                        app.review_agent = agent_name
                        app.review_data = agent_result
                        app.updated_at = datetime.now()
                        session.commit()
                        print(f"[{agent_name.upper()}] Saved review required status")
                    session.close()
                except Exception as e:
                    print(f"[{agent_name.upper()}] Error saving review status: {e}")
                
                # Emit review required event
                if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                    builtins.current_progress_callback(agent_name, 'review_required', agent_result)
                
                # ACTUALLY PAUSE - Wait for human approval using event
                import asyncio
                print(f"[{agent_name.upper()}] WORKFLOW PAUSED - Waiting for human review...")
                
                # Store the app_id locally to prevent mixing
                current_app_id = state.application_id
                print(f"[{agent_name.upper()}] Stored app_id for this agent: {current_app_id}")
                
                # Create or get event for this application (thread-safe)
                import threading
                if not hasattr(builtins, 'review_events'):
                    builtins.review_events = {}
                    builtins.review_lock = threading.Lock()
                    print(f"[{agent_name.upper()}] Initialized review events system")
                
                with builtins.review_lock:
                    if current_app_id not in builtins.review_events:
                        # Use threading.Event for cross-thread compatibility
                        builtins.review_events[current_app_id] = threading.Event()
                        print(f"[{agent_name.upper()}] Created new event for {current_app_id}")
                        print(f"[{agent_name.upper()}] Total events now: {len(builtins.review_events)}")
                        print(f"[{agent_name.upper()}] Event keys: {list(builtins.review_events.keys())}")
                    else:
                        print(f"[{agent_name.upper()}] Using existing event for {current_app_id}")
                
                # Wait for the event to be set (indefinite wait for human review)
                print(f"[{agent_name.upper()}] Waiting for review event (can wait days)...")
                print(f"[{agent_name.upper()}] Event object: {builtins.review_events[current_app_id]}")
                print(f"[{agent_name.upper()}] Event is_set: {builtins.review_events[current_app_id].is_set()}")
                
                # Wait indefinitely for human review - no timeout
                await asyncio.to_thread(builtins.review_events[current_app_id].wait)
                print(f"[{agent_name.upper()}] Review event received - proceeding")
                
                # Check final status after event is triggered
                try:
                    from models import MerchantApplication, SessionLocal
                    
                    session = SessionLocal()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    
                    if app and app.status == 'declined':
                        print(f"[{agent_name.upper()}] Application rejected - Stopping workflow")
                        session.close()
                        state.status = ApplicationStatus.DECLINED
                        raise Exception("Workflow stopped due to human rejection")
                    else:
                        print(f"[{agent_name.upper()}] Human review completed - Continuing workflow")
                    
                    session.close()
                except Exception as e:
                    if "rejection" in str(e).lower():
                        raise e
                    print(f"[{agent_name.upper()}] Error checking final status: {e}")
                finally:
                    # Clean up event after final status check
                    with builtins.review_lock:
                        if current_app_id in builtins.review_events:
                            del builtins.review_events[current_app_id]
                            print(f"[{agent_name.upper()}] Cleaned up review event")
            else:
                print(f"[{agent_name.upper()}] Auto-approved - continuing workflow immediately")
                # Set state to indicate no review needed
                state.needs_review = False
                state.review_agent = None
                state.status = ApplicationStatus.PROCESSING
            
            return result
            
        except Exception as e:
            print(f"[{agent_name.upper()}] *** AGENT FAILED *** {e}", flush=True)
            print(f"[{agent_name.upper()}] Error details: {str(e)[:200]}...\n", flush=True)
            
            # Check if this is a workflow stop due to rejection
            if "rejection" in str(e).lower() or "stopped" in str(e).lower():
                print(f"[{agent_name.upper()}] Workflow stopped by human rejection - Propagating stop")
                state.status = ApplicationStatus.DECLINED
                # Re-raise to stop the entire workflow
                raise e
            
            # Return state with error info but don't break the workflow for other errors
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

async def add_to_review_queue(application_id, agent_name, agent_result):
    """Add agent result to review queue"""
    try:
        from models import ReviewQueue, SessionLocal
        
        session = SessionLocal()
        
        review_item = ReviewQueue(
            application_id=application_id,
            agent_name=agent_name,
            agent_result=agent_result,
            status='pending'
        )
        
        session.add(review_item)
        session.commit()
        session.close()
        
        print(f"[REVIEW] Added {agent_name} result to review queue for {application_id}")
    except Exception as e:
        print(f"[ERROR] Failed to add to review queue: {e}")
        import traceback
        print(traceback.format_exc())

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
    workflow.add_edge("document_processing", "risk_assessment")
    workflow.add_edge("risk_assessment", "data_validation")
    workflow.add_edge("risk_assessment", "compliance_verification")
    workflow.add_edge("compliance_verification", "decision_making")
    workflow.add_edge("decision_making", "account_provisioning")
    workflow.add_edge("account_provisioning", "communication")
    workflow.add_edge("communication", END)
    
    return workflow.compile()

def create_comprehensive_workflow():
    """12 agent document-first workflow for high-risk merchants"""
    workflow = StateGraph(MerchantOnboardingState)
    
    # Load agents in document-first order (removed application_assistant)
    document_processing_agent = load_agent(
        os.path.join(base_path, 'agents', 'document-processing', 'src', 'agent.py'),
        'document_processing_agent'
    )
    market_qualification_agent = load_agent(
        os.path.join(base_path, 'agents', 'market-qualification', 'src', 'agent.py'),
        'market_qualification_agent'
    )
    lead_qualification_agent = load_agent(
        os.path.join(base_path, 'agents', 'lead-qualification', 'src', 'agent.py'),
        'lead_qualification_agent'
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
    
    # Add nodes in document-first order
    workflow.add_node("document_processing", create_agent_wrapper(document_processing_agent, "document_processing"))
    workflow.add_node("market_qualification", create_agent_wrapper(market_qualification_agent, "market_qualification"))
    workflow.add_node("lead_qualification", create_agent_wrapper(lead_qualification_agent, "lead_qualification"))
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
    
    # Define document-first 12-agent flow with risk assessment early
    workflow.set_entry_point("document_processing")
    workflow.add_edge("document_processing", "risk_assessment")
    workflow.add_edge("risk_assessment", "market_qualification")
    workflow.add_edge("market_qualification", "lead_qualification")
    workflow.add_edge("lead_qualification", "data_validation")
    workflow.add_edge("data_validation", "compliance_verification")
    workflow.add_edge("compliance_verification", "decision_making")
    workflow.add_edge("decision_making", "exception_routing")
    workflow.add_edge("exception_routing", "communication")
    workflow.add_edge("communication", "account_provisioning")
    workflow.add_edge("account_provisioning", "monitoring")
    workflow.add_edge("monitoring", "optimization")
    workflow.add_edge("optimization", "onboarding_support")
    workflow.add_edge("onboarding_support", END)
    
    return workflow.compile()

def create_routing_workflow():
    """2-agent routing workflow to determine optimal pattern"""
    workflow = StateGraph(MerchantOnboardingState)
    
    # Load routing agents
    document_processing_agent = load_agent(
        os.path.join(base_path, 'agents', 'document-processing', 'src', 'agent.py'),
        'document_processing_agent'
    )
    risk_assessment_agent = load_agent(
        os.path.join(base_path, 'agents', 'risk-assessment', 'src', 'agent.py'),
        'risk_assessment_agent'
    )
    
    # Add routing nodes with progress tracking
    workflow.add_node("document_processing", create_agent_wrapper(document_processing_agent, "document_processing"))
    workflow.add_node("risk_assessment", create_agent_wrapper(risk_assessment_agent, "risk_assessment"))
    
    # Define routing flow: Document Processing → Risk Assessment → END
    workflow.set_entry_point("document_processing")
    workflow.add_edge("document_processing", "risk_assessment")
    workflow.add_edge("risk_assessment", END)
    
    return workflow.compile()

def get_workflow_graph(pattern):
    """Get workflow graph for specified pattern"""
    if pattern == "express_workflow":
        return create_express_workflow()
    elif pattern == "standard_workflow":
        return create_standard_workflow()
    elif pattern == "routing_workflow":
        return create_routing_workflow()
    else:
        return create_comprehensive_workflow()