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
                    print(f"[{agent_name.upper()}] Updated current agent in database")
                session.close()
            except Exception as e:
                print(f"[{agent_name.upper()}] Error updating start status: {e}")
            
            # === EXECUTE AGENT ===
            result = await agent_func(state)
            print(f"[{agent_name.upper()}] *** AGENT COMPLETED SUCCESSFULLY ***", flush=True)
            
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
                state.status = ApplicationStatus.PENDING_HUMAN_REVIEW
                
                # Save review status to database
                try:
                    session = SessionLocal()
                    app = session.query(MerchantApplication).filter_by(id=current_app_id).first()
                    if app:
                        app.needs_review = 'true'
                        app.review_agent = agent_name
                        app.review_data = agent_result
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
                print(f"[{agent_name.upper()}] Review completed - continuing workflow")
                
                # Clean up event
                with builtins.review_lock:
                    if current_app_id in builtins.review_events:
                        del builtins.review_events[current_app_id]
            else:
                print(f"[{agent_name.upper()}] Auto-approved - continuing workflow")
            
            return result
            
        except Exception as e:
            print(f"[{agent_name.upper()}] *** AGENT FAILED *** {e}", flush=True)
            
            # ALWAYS emit error for tracking
            import builtins
            if hasattr(builtins, 'current_progress_callback') and builtins.current_progress_callback:
                builtins.current_progress_callback(agent_name, 'failed', {'error': str(e)})
            
            raise e
    
    return wrapped_agent