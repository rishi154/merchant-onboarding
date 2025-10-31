def create_agent_wrapper(agent_func, agent_name):
    """Wrapper with SEPARATED progress tracking and human review"""
    async def wrapped_agent(state):
        try:
            current_app_id = state.application_id
            print(f"\n[{agent_name.upper()}] *** STARTING AGENT EXECUTION ***", flush=True)
            
            # === PROGRESS TRACKING (ALWAYS HAPPENS FOR ALL AGENTS) ===
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'starting', {})
            
            # ALWAYS save starting status to database
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
            
            # === EXECUTE AGENT ===
            result = await agent_func(state)
            print(f"[{agent_name.upper()}] *** AGENT COMPLETED SUCCESSFULLY ***", flush=True)
            
            # Update agents_executed list
            if hasattr(result, 'agents_executed'):
                result.agents_executed.append(agent_name)
            elif hasattr(state, 'agents_executed'):
                state.agents_executed.append(agent_name)
            
            # Extract agent result
            if hasattr(result, agent_name):
                agent_result = getattr(result, agent_name)
            elif isinstance(result, dict) and agent_name in result:
                agent_result = result[agent_name]
            else:
                agent_result = result.__dict__ if hasattr(result, '__dict__') else result
            
            # === PROGRESS TRACKING (ALWAYS HAPPENS FOR ALL AGENTS) ===
            # ALWAYS save completed result to database
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
            
            # ALWAYS emit completed status
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'completed', agent_result)
            
            # === HUMAN REVIEW (SEPARATE FROM TRACKING) ===
            if requires_human_review(agent_name):
                print(f"[{agent_name.upper()}] Human review required - pausing workflow")
                
                # Set review state
                state.needs_review = True
                state.review_agent = agent_name
                state.review_data = agent_result
                from state import ApplicationStatus
                state.status = ApplicationStatus.PENDING_HUMAN_REVIEW
                
                # Add to review queue
                try:
                    await add_to_review_queue(state.application_id, agent_name, agent_result)
                except Exception as e:
                    print(f"[{agent_name.upper()}] Error adding to review queue: {e}")
                
                # Save review status to database
                try:
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
                
                # PAUSE FOR HUMAN REVIEW
                import asyncio
                import threading
                
                if not hasattr(builtins, 'review_events'):
                    builtins.review_events = {}
                    builtins.review_lock = threading.Lock()
                
                with builtins.review_lock:
                    if current_app_id not in builtins.review_events:
                        builtins.review_events[current_app_id] = threading.Event()
                
                # Wait for human approval
                await asyncio.to_thread(builtins.review_events[current_app_id].wait)
                print(f"[{agent_name.upper()}] Review event received - proceeding")
                
                # Check final status after event is triggered
                try:
                    session = SessionLocal()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    
                    if app and app.status == 'declined':
                        print(f"[{agent_name.upper()}] Application rejected - Stopping workflow")
                        session.close()
                        from state import ApplicationStatus
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
                    # Clean up event
                    with builtins.review_lock:
                        if current_app_id in builtins.review_events:
                            del builtins.review_events[current_app_id]
                            print(f"[{agent_name.upper()}] Cleaned up review event")
            else:
                print(f"[{agent_name.upper()}] Auto-approved - continuing workflow immediately")
                # Set state to indicate no review needed
                state.needs_review = False
                state.review_agent = None
                from state import ApplicationStatus
                state.status = ApplicationStatus.PROCESSING
            
            return result
            
        except Exception as e:
            print(f"[{agent_name.upper()}] *** AGENT FAILED *** {e}", flush=True)
            
            # Check if this is a workflow stop due to rejection
            if "rejection" in str(e).lower() or "stopped" in str(e).lower():
                print(f"[{agent_name.upper()}] Workflow stopped by human rejection - Propagating stop")
                from state import ApplicationStatus
                state.status = ApplicationStatus.DECLINED
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
            
            # ALWAYS emit error for tracking
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'failed', {'error': str(e)})
            
            return error_result
    
    return wrapped_agent