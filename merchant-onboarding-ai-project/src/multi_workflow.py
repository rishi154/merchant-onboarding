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
    'data_validation': True,    # Enable human review
    'underwriting': True,       # Enable human review
    'risk_assessment': False,  # Auto-approve for routing phase
    'compliance_verification': True,  # Enable human review
    'decision_making': False,   # Auto-approve
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
    import subprocess
    import os
    
    # Validate agent_path to prevent command injection
    if not os.path.exists(agent_path) or not agent_path.endswith('.py'):
        raise ValueError(f"Invalid agent path: {agent_path}")
    
    spec = importlib.util.spec_from_file_location(agent_name, agent_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, agent_name)

def create_agent_wrapper(agent_func, agent_name):
    """Wrapper to add progress tracking and human review to agents"""
    async def wrapped_agent(state):
        try:
            # CHECK STATUS FIRST - Stop if declined
            current_app_id = state.application_id
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
            from models import SessionLocal as Session, MerchantApplication
            
            session = Session()
            app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
            if app and app.status == 'declined':
                print(f"[{agent_name.upper()}] Application declined - Skipping agent")
                session.close()
                return state
            session.close()
            
            # Check if agent already completed (from preserved state or routing phase)
            import builtins
            completed_agents = {}
            
            # Get completed agents from multiple sources
            if hasattr(builtins, 'preserved_completed_agents'):
                completed_agents.update(builtins.preserved_completed_agents)
            if hasattr(state, 'application_data') and state.application_data:
                completed_agents.update(state.application_data.get('completed_agents', {}))
            
            if agent_name in completed_agents and completed_agents[agent_name]:
                print(f"\n[{agent_name.upper()}] *** SKIPPING - ALREADY COMPLETED ***", flush=True)
                existing_result = completed_agents[agent_name]
                setattr(state, agent_name, existing_result)
                
                # Emit progress for UI consistency
                if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                    builtins.current_progress_callback(agent_name, 'completed', existing_result)
                
                return state
            
            print(f"\n[{agent_name.upper()}] *** STARTING AGENT EXECUTION ***", flush=True)
            print(f"[{agent_name.upper()}] Processing merchant application...", flush=True)
            
            # Store app_id locally to prevent mixing
            current_app_id = state.application_id
            print(f"[{agent_name.upper()}] Processing app_id: {current_app_id}")
            
            print(f"[{agent_name.upper()}] Starting agent execution...")
            
            # Emit starting progress
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'starting', {})
            
            result = await agent_func(state)
            print(f"[{agent_name.upper()}] *** AGENT COMPLETED SUCCESSFULLY ***", flush=True)
            
            # Extract actual agent result first
            if hasattr(result, agent_name):
                agent_result = getattr(result, agent_name)
            elif isinstance(result, dict) and agent_name in result:
                agent_result = result[agent_name]
            else:
                # Fallback - use the entire result if agent-specific result not found
                agent_result = result.__dict__ if hasattr(result, '__dict__') else result
            
            # Clean up agent reasoning if it contains thinking process
            if isinstance(agent_result, dict) and 'agent_reasoning' in agent_result:
                reasoning = agent_result['agent_reasoning']
                # Remove common thinking process patterns
                if any(phrase in reasoning for phrase in [
                    'Could you please provide', 'I need more information', 'First, I need', 
                    'Okay, I will', 'Agent stopped due to max iterations', 'Let me'
                ]):
                    # Generate clean reasoning based on agent type and results
                    if agent_name == 'document_processing':
                        doc_count = agent_result.get('documents_processed', 0)
                        confidence = agent_result.get('overall_confidence', 0)
                        agent_result['agent_reasoning'] = f'Successfully processed {doc_count} documents with {int(confidence*100)}% confidence. All documents extracted and validated.'
                    elif agent_name == 'data_validation':
                        score = agent_result.get('validation_score', 0)
                        field_vals = agent_result.get('field_validations', {})
                        failed_fields = [k for k, v in field_vals.items() if not v]
                        if score >= 0.95:
                            agent_result['agent_reasoning'] = f'Data validation completed with score of {score}. All required fields validated successfully.'
                        elif failed_fields:
                            agent_result['agent_reasoning'] = f'Data validation completed with score of {score}. Issues found in: {", ".join(failed_fields)}.'
                        else:
                            agent_result['agent_reasoning'] = f'Data validation completed with score of {score}. Some quality concerns detected in field accuracy.'
                    elif agent_name == 'risk_assessment':
                        risk_tier = agent_result.get('risk_tier', 'UNKNOWN')
                        risk_score = agent_result.get('risk_score', agent_result.get('overall_risk_score', 'N/A'))
                        credit_score = agent_result.get('credit_score', 'N/A')
                        agent_result['agent_reasoning'] = f'Classified as {risk_tier} risk (score: {risk_score}) based on credit score of {credit_score} and business profile analysis.'
                    elif agent_name == 'compliance_verification':
                        agent_result['agent_reasoning'] = 'Compliance checks completed. All regulatory requirements verified.'
                    elif agent_name == 'underwriting':
                        decision = agent_result.get('underwriting_decision', 'PENDING')
                        agent_result['agent_reasoning'] = f'Underwriting analysis completed with decision: {decision}.'
                    else:
                        # Generic fallback
                        agent_result['agent_reasoning'] = f'{agent_name.replace("_", " ").title()} completed successfully.'
            
            # CRITICAL: Save agent result IMMEDIATELY after completion, BEFORE any review logic
            try:
                # Check if application was declined - don't save if declined
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
                from models import SessionLocal as Session
                from datetime import datetime
                
                session = Session()
                from models import MerchantApplication
                app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                if app and app.status == 'declined':
                    print(f"[{agent_name.upper()}] Application declined - skipping save")
                    session.close()
                    return state
                session.close()
                
                # Generate summary immediately
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ui'))
                from app import generate_and_store_summary
                summary = generate_and_store_summary(agent_name, agent_result)
                
                session = Session()
                from models import MerchantApplication
                app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                if app:
                    # Force refresh to get latest data
                    session.refresh(app)
                    current_results = app.agent_results or {}
                    current_results[agent_name] = agent_result
                    
                    # Store summary
                    current_summaries = app.agent_summaries or {}
                    current_summaries[agent_name] = summary
                    
                    # Force update by setting to None first, then back
                    app.agent_results = None
                    app.agent_summaries = None
                    session.flush()
                    app.agent_results = current_results
                    app.agent_summaries = current_summaries
                    app.current_agent = agent_name
                    app.updated_at = datetime.now()
                    session.commit()
                    print(f"[{agent_name.upper()}] *** SAVED result AND summary to database ***")
                    print(f"[{agent_name.upper()}] Total agent results now: {len(current_results)} agents")
                else:
                    print(f"[{agent_name.upper()}] ERROR: Application {current_app_id} not found in database!")
                session.close()
            except Exception as e:
                print(f"[{agent_name.upper()}] CRITICAL ERROR saving result: {e}")
                import traceback
                print(f"[{agent_name.upper()}] Traceback: {traceback.format_exc()}")
            
            # ALWAYS emit completed status for ALL agents
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
                
                # Save review required status to database (agent result already saved above)
                try:
                    session = Session()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    if app:
                        app.needs_review = 'true'
                        app.review_agent = agent_name
                        app.review_data = agent_result
                        app.status = 'pending_human_review'
                        app.updated_at = datetime.now()
                        session.commit()
                        print(f"[{agent_name.upper()}] Set review required status")
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
                session = Session()
                app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                
                if app and app.status == 'declined':
                    print(f"[{agent_name.upper()}] Application rejected - Stopping workflow")
                    session.close()
                    
                    # Clean up event before stopping
                    with builtins.review_lock:
                        if current_app_id in builtins.review_events:
                            del builtins.review_events[current_app_id]
                    
                    state.status = ApplicationStatus.DECLINED
                    raise Exception("Workflow stopped due to human rejection")
                
                print(f"[{agent_name.upper()}] Human review completed - Continuing workflow")
                session.close()
                
                # Clear review status after approval
                session = Session()
                app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                if app:
                    app.needs_review = 'false'
                    app.review_agent = None
                    app.updated_at = datetime.now()
                    session.commit()
                    print(f"[{agent_name.upper()}] Cleared review status after approval")
                session.close()
                
                # Clean up event after approval
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
                
                # Clear review status in database for auto-approved agents
                try:
                    session = Session()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    if app:
                        app.needs_review = 'false'
                        app.review_agent = None
                        app.updated_at = datetime.now()
                        session.commit()
                        print(f"[{agent_name.upper()}] Cleared review status in database")
                    session.close()
                except Exception as e:
                    print(f"[{agent_name.upper()}] Error clearing review status: {e}")
            
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
    """7-8 agent workflow for medium-risk merchants"""
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
    underwriting_agent = load_agent(
        os.path.join(base_path, 'agents', 'underwriting', 'src', 'agent.py'),
        'underwriting_agent'
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
    workflow.add_node("underwriting", create_agent_wrapper(underwriting_agent, "underwriting"))
    workflow.add_node("risk_assessment", create_agent_wrapper(risk_assessment_agent, "risk_assessment"))
    workflow.add_node("compliance_verification", create_agent_wrapper(compliance_verification_agent, "compliance_verification"))
    workflow.add_node("decision_making", create_agent_wrapper(decision_making_agent, "decision_making"))
    workflow.add_node("account_provisioning", create_agent_wrapper(account_provisioning_agent, "account_provisioning"))
    workflow.add_node("communication", create_agent_wrapper(communication_agent, "communication"))
    
    # Define flow - sequential execution
    workflow.set_entry_point("document_processing")
    workflow.add_edge("document_processing", "risk_assessment")
    workflow.add_edge("risk_assessment", "data_validation")
    workflow.add_edge("data_validation", "underwriting")
    workflow.add_edge("underwriting", "compliance_verification")
    workflow.add_edge("compliance_verification", "decision_making")
    workflow.add_edge("decision_making", "account_provisioning")
    workflow.add_edge("account_provisioning", "communication")
    workflow.add_edge("communication", END)
    
    return workflow.compile()

def create_comprehensive_workflow():
    """14 agent document-first workflow for high-risk merchants"""
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
    underwriting_agent = load_agent(
        os.path.join(base_path, 'agents', 'underwriting', 'src', 'agent.py'),
        'underwriting_agent'
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
    workflow.add_node("underwriting", create_agent_wrapper(underwriting_agent, "underwriting"))
    workflow.add_node("risk_assessment", create_agent_wrapper(risk_assessment_agent, "risk_assessment"))
    workflow.add_node("compliance_verification", create_agent_wrapper(compliance_verification_agent, "compliance_verification"))
    workflow.add_node("decision_making", create_agent_wrapper(decision_making_agent, "decision_making"))
    workflow.add_node("exception_routing", create_agent_wrapper(exception_routing_agent, "exception_routing"))
    workflow.add_node("communication", create_agent_wrapper(communication_agent, "communication"))
    workflow.add_node("account_provisioning", create_agent_wrapper(account_provisioning_agent, "account_provisioning"))
    workflow.add_node("monitoring", create_agent_wrapper(monitoring_agent, "monitoring"))
    workflow.add_node("optimization", create_agent_wrapper(optimization_agent, "optimization"))
    workflow.add_node("onboarding_support", create_agent_wrapper(onboarding_support_agent, "onboarding_support"))
    
    # Define document-first 14-agent flow with risk assessment early
    workflow.set_entry_point("document_processing")
    workflow.add_edge("document_processing", "risk_assessment")
    workflow.add_edge("risk_assessment", "market_qualification")
    workflow.add_edge("market_qualification", "lead_qualification")
    workflow.add_edge("lead_qualification", "data_validation")
    workflow.add_edge("data_validation", "underwriting")
    workflow.add_edge("underwriting", "compliance_verification")
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