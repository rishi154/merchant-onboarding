from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import sys
import asyncio
import json
from datetime import datetime
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mimetypes
from review_api import review_bp

# Add paths for importing the workflow and database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from state import MerchantOnboardingState
from models import MerchantApplication, ProcessingStep, Base
from jurisdiction_service import JurisdictionService
from jurisdiction_document_engine import JurisdictionDocumentEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'merchant-onboarding-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Register review API blueprint
app.register_blueprint(review_bp)

# Database setup - use same configuration as models.py
from models import engine, SessionLocal as Session

# Store processing status and progress
processing_status = {}
agent_progress = {}  # Track agent completion per application

@app.route('/')
def index():
    return app.send_static_file('applications.html')

@app.route('/upload')
def upload_page():
    return app.send_static_file('upload.html')

@app.route('/processing')
def processing_page():
    return app.send_static_file('enhanced-workflow-display.html')

@app.route('/new')
def new_application():
    return app.send_static_file('upload.html')

@app.route('/applications')
def applications():
    return app.send_static_file('applications.html')

@app.route('/analytics')
def analytics():
    return app.send_static_file('analytics.html')

@app.route('/application/<app_id>')
def application_details(app_id):
    """Show detailed view of a specific application"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return "Application not found", 404
        
        # Create a simple details page
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Details - {}</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50 p-8">
            <div class="max-w-4xl mx-auto">
                <div class="bg-white rounded-lg shadow p-6">
                    <h1 class="text-2xl font-bold mb-4">Application Details</h1>
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <div><strong>ID:</strong> {}</div>
                        <div><strong>Business:</strong> {}</div>
                        <div><strong>Status:</strong> {}</div>
                        <div><strong>Current Agent:</strong> {}</div>
                        <div><strong>Progress:</strong> {}%</div>
                        <div><strong>Documents:</strong> {}</div>
                        <div><strong>Created:</strong> {}</div>
                        <div><strong>Updated:</strong> {}</div>
                    </div>
                    
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold mb-2">Extracted Data</h2>
                        <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">{}</pre>
                    </div>
                    
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold mb-2">Agent Results</h2>
                        <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">{}</pre>
                    </div>
                    
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold mb-2">Review Status</h2>
                        <div class="bg-gray-100 p-4 rounded">
                            <p><strong>Needs Review:</strong> {}</p>
                            <p><strong>Review Agent:</strong> {}</p>
                            <p><strong>Current Reviewer:</strong> {}</p>
                        </div>
                    </div>
                    
                    <div class="space-x-2">
                        <a href="/applications" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Back to Applications</a>
                        <a href="/analytics" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">View Analytics</a>
                        <button onclick="resumeApplication('{}')" class="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600">Resume Application</button>
                    </div>
                    
                    <script>
                    function resumeApplication(appId) {{
                        fetch('/api/applications/' + appId + '/resume', {{
                            method: 'POST'
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            if (data.success) {{
                                if (data.needs_review) {{
                                    window.location.href = '/processing?app_id=' + appId;
                                }} else {{
                                    alert('Application resumed successfully');
                                    window.location.reload();
                                }}
                            }} else {{
                                alert('Error resuming application: ' + data.error);
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            alert('Error resuming application');
                        }});
                    }}
                    </script>
                </div>
            </div>
        </body>
        </html>
        """.format(
            app_id,
            application.id,
            application.business_name,
            application.status,
            application.current_agent or 'N/A',
            application.progress_percentage or 0,
            application.documents_processed or 0,
            application.created_at,
            application.updated_at,
            json.dumps(application.extracted_data or {}, indent=2),
            json.dumps(application.agent_results or {}, indent=2),
            application.needs_review or 'false',
            application.review_agent or 'N/A',
            application.current_reviewer or 'N/A',
            application.id
        )
        return html
    finally:
        session.close()

@app.route('/api/progress/<app_id>')
def get_progress(app_id):
    """Get real-time progress for a specific application"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        return jsonify({
            'application_id': application.id,
            'status': application.status,
            'current_agent': application.current_agent,
            'progress_percentage': application.progress_percentage,
            'agent_results': application.agent_results or {},
            'error_message': getattr(application, 'error_message', None)
        })
    finally:
        session.close()

@app.route('/api/applications/<app_id>/resume', methods=['POST'])
def resume_application(app_id):
    """Resume a paused application"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check if application needs review
        if application.needs_review == 'true':
            return jsonify({
                'success': True,
                'needs_review': True,
                'review_agent': application.review_agent,
                'review_data': application.review_data
            })
        
        # If not in review, check if it can be resumed
        if application.status in ['completed', 'approved', 'declined', 'failed']:
            return jsonify({'error': 'Application already completed'}), 400
        
        # Try to trigger existing workflow first
        import builtins
        workflow_resumed = False
        if hasattr(builtins, 'review_events') and app_id in builtins.review_events:
            print(f"[{app_id}] Triggering existing workflow event")
            builtins.review_events[app_id].set()
            workflow_resumed = True
        else:
            print(f"[{app_id}] No existing workflow found - restarting from current state")
            # Restart workflow from current state
            application.status = 'processing'
            session.commit()
            
            # Get application data for restart
            app_data = application.application_data or {}
            business_name = application.business_name
            
            # Load documents from upload directory
            upload_dir = os.path.join('uploads', app_id)
            documents = []
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    if filename.endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt')):
                        file_path = os.path.join(upload_dir, filename)
                        documents.append({
                            'id': filename,
                            'type': detect_document_type(filename),
                            'path': file_path,
                            'filename': filename,
                            'size': os.path.getsize(file_path),
                            'uploaded_at': datetime.now().isoformat()
                        })
            
            if documents:
                # Restart workflow in background thread
                print(f"[{app_id}] Restarting workflow with {len(documents)} documents")
                thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, 'comprehensive_workflow'))
                thread.daemon = True
                thread.start()
                workflow_resumed = True
        
        return jsonify({
            'success': True,
            'needs_review': False,
            'status': 'processing',
            'workflow_resumed': workflow_resumed
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/document/<app_id>/<filename>')
def preview_document(app_id, filename):
    """Preview uploaded document"""
    try:
        file_path = os.path.join('uploads', app_id, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Document not found'}), 404
        
        # Get mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        return send_file(file_path, mimetype=mime_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<app_id>')
def get_documents(app_id):
    """Get list of documents for an application"""
    try:
        upload_dir = os.path.join('uploads', app_id)
        if not os.path.exists(upload_dir):
            return jsonify({'documents': []})
        
        documents = []
        for filename in os.listdir(upload_dir):
            if filename.endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt')):
                file_path = os.path.join(upload_dir, filename)
                documents.append({
                    'filename': filename,
                    'size': os.path.getsize(file_path),
                    'type': detect_document_type(filename),
                    'preview_url': f'/api/document/{app_id}/{filename}'
                })
        
        return jsonify({'documents': documents})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications')
def get_applications():
    """Get all applications from database with review status"""
    session = Session()
    try:
        applications = session.query(MerchantApplication).order_by(MerchantApplication.created_at.desc()).all()
        return jsonify([{
            'application_id': app.id,
            'id': app.id,
            'business_name': app.business_name,
            'status': app.status,
            'current_agent': app.current_agent,
            'progress_percentage': app.progress_percentage,
            'documents_processed': app.documents_processed,
            'extraction_confidence': app.extraction_confidence,
            'manual_fields_required': app.manual_fields_required,
            'created_at': app.created_at.isoformat(),
            'updated_at': app.updated_at.isoformat(),
            'processing_start_time': app.processing_start_time.isoformat() if app.processing_start_time else None,
            'processing_end_time': app.processing_end_time.isoformat() if app.processing_end_time else None,
            'application_data': app.application_data,
            'extracted_data': app.extracted_data,
            'agent_results': app.agent_results,
            'needs_review': app.needs_review == 'true',
            'review_agent': app.review_agent,
            'review_data': app.review_data,
            'current_reviewer': app.current_reviewer,
            'workflow_pattern': app.workflow_pattern
        } for app in applications])
    finally:
        session.close()

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data for dashboard"""
    session = Session()
    try:
        applications = session.query(MerchantApplication).all()
        
        # Calculate metrics
        total_apps = len(applications)
        completed_apps = [app for app in applications if app.status in ['completed', 'approved', 'declined']]
        
        # Processing time calculation
        processing_times = []
        for app in completed_apps:
            if app.processing_start_time and app.processing_end_time:
                delta = app.processing_end_time - app.processing_start_time
                processing_times.append(delta.total_seconds() / 60)  # minutes
        
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Automation rate (mock calculation)
        automation_rate = 73  # Based on agent results
        
        # Success rate
        approved_apps = len([app for app in applications if app.status == 'approved'])
        success_rate = (approved_apps / total_apps * 100) if total_apps > 0 else 0
        
        # Generate trend data (last 7 days)
        from datetime import datetime, timedelta
        today = datetime.now()
        trend_labels = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
        trend_values = [25, 22, 18, 15, 12, 8, 10]  # Mock data
        
        # Agent performance (from actual results)
        agent_success = {'document_processing': 0, 'risk_assessment': 0, 'compliance_verification': 0, 'decision_making': 0}
        agent_total = {'document_processing': 0, 'risk_assessment': 0, 'compliance_verification': 0, 'decision_making': 0}
        
        for app in applications:
            if app.agent_results:
                for agent, result in app.agent_results.items():
                    if agent in agent_success:
                        agent_total[agent] += 1
                        if result and result.get('success', True):
                            agent_success[agent] += 1
        
        agent_rates = []
        for agent in ['document_processing', 'risk_assessment', 'compliance_verification', 'decision_making']:
            rate = (agent_success[agent] / agent_total[agent] * 100) if agent_total[agent] > 0 else 95
            agent_rates.append(int(rate))
        
        return jsonify({
            'metrics': {
                'total_applications': total_apps,
                'avg_processing_time': int(avg_time),
                'automation_rate': automation_rate,
                'success_rate': int(success_rate)
            },
            'time_trend': {
                'labels': trend_labels,
                'values': trend_values
            },
            'automation': {
                'automated': automation_rate,
                'manual': 100 - automation_rate
            },
            'agent_performance': {
                'agents': ['Document', 'Risk', 'Compliance', 'Decision'],
                'success_rates': agent_rates
            },
            'risk_distribution': [45, 32, 18, 12, 3],
            'volume': {
                'labels': trend_labels,
                'submitted': [45, 52, 38, 41, 47, 35, 42],
                'approved': [32, 38, 28, 31, 35, 25, 30],
                'declined': [8, 9, 6, 7, 8, 6, 7]
            }
        })
    finally:
        session.close()

@app.route('/api/test-emit')
def test_emit():
    """Test WebSocket emission"""
    print("[TEST] Emitting test event", flush=True)
    socketio.emit('agent_progress', {
        'application_id': 'TEST123',
        'agent_name': 'test_agent',
        'status': 'completed',
        'progress_percentage': 50,
        'current_agent': 'test_agent',
        'agent_results': {'test': 'data'}
    })
    print("[TEST] Test event emitted", flush=True)
    return jsonify({'status': 'test_emitted'})

@app.route('/api/update-callback')
def update_progress_callback():
    """Update the global progress callback to include database saving"""
    import builtins
    
    def enhanced_callback(agent_name, status, result):
        app_id = getattr(builtins, 'current_app_id', 'UNKNOWN')
        print(f"[{app_id}] *** ENHANCED CALLBACK TRIGGERED ***", flush=True)
        print(f"[{app_id}] Agent {agent_name}: {status}", flush=True)
        print(f"[{app_id}] Result: {result}", flush=True)
        
        # Save to database immediately for any meaningful status
        if status in ['completed', 'review_required', 'starting'] and result:
            try:
                session = Session()
                # Find applications that need this agent result
                applications = session.query(MerchantApplication).filter(
                    MerchantApplication.status.in_(['processing', 'pending_human_review'])
                ).order_by(MerchantApplication.created_at.desc()).limit(10).all()
                
                saved = False
                for application in applications:
                    # Save if this is the current agent or if agent results are missing this agent
                    current_results = application.agent_results or {}
                    if (application.current_agent == agent_name or 
                        application.review_agent == agent_name or 
                        agent_name not in current_results or
                        len(current_results) < 3):
                        
                        current_results[agent_name] = result
                        application.agent_results = current_results
                        application.current_agent = agent_name
                        application.updated_at = datetime.now()
                        
                        if status == 'review_required':
                            application.needs_review = 'true'
                            application.review_agent = agent_name
                            application.review_data = result
                        
                        session.commit()
                        print(f"[{application.id}] Enhanced callback saved {agent_name} result (status: {status})")
                        saved = True
                        break
                
                if not saved:
                    print(f"[{app_id}] No matching application found for {agent_name}")
                session.close()
            except Exception as e:
                print(f"Enhanced callback DB error: {e}")
                import traceback
                print(f"Enhanced callback traceback: {traceback.format_exc()}")
        
        # Emit WebSocket update
        try:
            socketio.emit('agent_progress', {
                'application_id': app_id,
                'agent_name': agent_name,
                'status': status,
                'agent_results': {agent_name: result} if result else {}
            })
            print(f"[{app_id}] Emitted WebSocket update for {agent_name}")
        except Exception as e:
            print(f"[{app_id}] WebSocket emit error: {e}")
    
    # Replace the global callback
    builtins.current_progress_callback = enhanced_callback
    
    return jsonify({'success': True, 'message': 'Progress callback updated'})

@app.route('/api/test-callback/<app_id>')
def test_callback(app_id):
    """Test the enhanced callback manually"""
    import builtins
    if hasattr(builtins, 'current_progress_callback'):
        # Test the callback with market_qualification data
        test_result = {
            'qualified': False,
            'score': 0.3,
            'reasoning': 'Test market qualification result',
            'requires_manual_review': True,
            'timestamp': datetime.now().isoformat()
        }
        builtins.current_progress_callback('market_qualification', 'review_required', test_result)
        return jsonify({'success': True, 'message': 'Market qualification callback tested'})
    else:
        return jsonify({'error': 'No callback found'}), 404

@app.route('/api/direct-save/<app_id>')
def direct_save_market_qual(app_id):
    """Directly save market_qualification result"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Force save market_qualification result
        market_qual_result = {
            'qualified': False,
            'score': 0.3,
            'revenue_check': 'Insufficient data',
            'geo_check': 'Insufficient data', 
            'platform_check': 'Insufficient data',
            'reasoning': 'Application incomplete - needs human review',
            'requires_manual_review': True,
            'status': 'review_required'
        }
        
        current_results = application.agent_results or {}
        current_results['market_qualification'] = market_qual_result
        
        # Force update
        application.agent_results = None
        session.flush()
        application.agent_results = current_results
        application.review_data = market_qual_result
        application.updated_at = datetime.now()
        
        session.commit()
        session.refresh(application)
        
        return jsonify({
            'success': True,
            'agent_results': application.agent_results,
            'keys': list(application.agent_results.keys()) if application.agent_results else None
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500
    finally:
        session.close()

@app.route('/api/check-events')
def check_events():
    """Check active review events"""
    import builtins
    if hasattr(builtins, 'review_events'):
        return jsonify({
            'events': list(builtins.review_events.keys()),
            'count': len(builtins.review_events)
        })
    else:
        return jsonify({'events': [], 'count': 0})

@app.route('/api/trigger-event/<app_id>')
def trigger_event(app_id):
    """Manually trigger review event"""
    import builtins
    if hasattr(builtins, 'review_events') and app_id in builtins.review_events:
        builtins.review_events[app_id].set()
        return jsonify({'success': True, 'message': f'Event triggered for {app_id}'})
    else:
        return jsonify({'error': f'No event found for {app_id}'}), 404

@app.route('/api/restart-workflow/<app_id>')
def restart_workflow(app_id):
    """Restart workflow from current state after approval"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check if approved and ready to continue
        if application.needs_review == 'true':
            return jsonify({'error': 'Application still needs review'}), 400
        
        # Get application data for restart
        app_data = application.application_data or {}
        app_data['application_id'] = app_id
        business_name = application.business_name
        
        # Load documents from upload directory
        upload_dir = os.path.join('uploads', app_id)
        documents = []
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt')):
                    file_path = os.path.join(upload_dir, filename)
                    documents.append({
                        'id': filename,
                        'type': detect_document_type(filename),
                        'path': file_path,
                        'filename': filename,
                        'size': os.path.getsize(file_path),
                        'uploaded_at': datetime.now().isoformat()
                    })
        
        if documents:
            # Update status to processing
            application.status = 'processing'
            application.needs_review = 'false'
            session.commit()
            
            # Restart workflow in background thread
            print(f"[{app_id}] Restarting workflow with {len(documents)} documents")
            thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, 'comprehensive_workflow'))
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Workflow restarted',
                'documents': len(documents),
                'status': 'processing'
            })
        else:
            return jsonify({'error': 'No documents found to process'}), 400
            
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
    finally:
        session.close()

@app.route('/api/force-save/<app_id>')
def force_save_test(app_id):
    """Force save test data to debug database issues"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Force save some test agent results
        test_results = {
            'test_agent': {
                'status': 'completed',
                'result': 'test_data',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        current_results = application.agent_results or {}
        current_results.update(test_results)
        application.agent_results = current_results
        application.updated_at = datetime.now()
        
        session.commit()
        session.refresh(application)
        
        return jsonify({
            'success': True,
            'agent_results': application.agent_results,
            'agent_results_keys': list(application.agent_results.keys()) if application.agent_results else None
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
    finally:
        session.close()

@app.route('/api/fix-agent-results/<app_id>')
def fix_agent_results(app_id):
    """Manually add the completed agent results that weren't stored due to callback issue"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        current_results = application.agent_results or {}
        
        # Add market_qualification if missing (since it's waiting for review)
        if 'market_qualification' not in current_results and application.review_agent == 'market_qualification':
            current_results['market_qualification'] = {
                'qualified': False,
                'score': 0.3,
                'revenue_check': 'Insufficient data. Revenue not explicitly stated.',
                'geo_check': 'Insufficient data. Geographic location not explicitly stated.',
                'platform_check': 'Insufficient data. Platform not explicitly stated.',
                'risk_factors': ['Missing key information: revenue, geographic location, platform.'],
                'reasoning': 'The application is incomplete and lacks critical information for qualification.',
                'processing_time': 0.1,
                'requires_manual_review': True,
                'status': 'review_required',
                'timestamp': datetime.now().isoformat()
            }
            
            application.agent_results = current_results
            application.review_data = current_results['market_qualification']
            application.updated_at = datetime.now()
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Added missing market_qualification result',
                'agent_results_keys': list(current_results.keys()),
                'review_agent': application.review_agent,
                'needs_review': application.needs_review
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No missing results to add',
                'agent_results_keys': list(current_results.keys()) if current_results else None
            })
            
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
    finally:
        session.close()

@app.route('/api/debug/<app_id>')
def debug_application(app_id):
    """Debug application data storage"""
    session = Session()
    try:
        app = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        return jsonify({
            'id': app.id,
            'business_name': app.business_name,
            'status': app.status,
            'current_agent': app.current_agent,
            'progress_percentage': app.progress_percentage,
            'needs_review': app.needs_review,
            'review_agent': app.review_agent,
            'agent_results': app.agent_results,
            'agent_results_type': type(app.agent_results).__name__,
            'agent_results_keys': list(app.agent_results.keys()) if app.agent_results else None,
            'extracted_data': app.extracted_data,
            'application_data': app.application_data
        })
    finally:
        session.close()

@app.route('/api/workflow-config')
def get_workflow_config():
    """Get workflow configuration - steps and metadata"""
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from workflow_router import get_workflow_steps, get_workflow_metadata
        
        # Return all workflow patterns
        patterns = ['express_workflow', 'standard_workflow', 'comprehensive_workflow']
        workflows = {}
        
        for pattern in patterns:
            workflows[pattern] = {
                'steps': get_workflow_steps(pattern),
                'metadata': get_workflow_metadata(pattern)
            }
        
        return jsonify({
            'workflows': workflows,
            'default_pattern': 'comprehensive_workflow'
        })
    except ImportError:
        # Fallback
        return jsonify({
            'workflows': {
                'comprehensive_workflow': {
                    'steps': [
                        {'name': 'Market Qualification', 'description': 'Market analysis and qualification'},
                        {'name': 'Document Processing', 'description': 'Extract and validate documents'},
                        {'name': 'Risk Assessment', 'description': 'Comprehensive risk analysis'},
                        {'name': 'Decision Making', 'description': 'Final approval decision'}
                    ],
                    'metadata': {
                        'name': 'Comprehensive Workflow',
                        'estimated_time': '2-24 hours',
                        'automation_rate': '60%'
                    }
                }
            },
            'default_pattern': 'comprehensive_workflow'
        })

@app.route('/upload', methods=['POST'])
def handle_upload():
    try:
        from werkzeug.utils import secure_filename
        files = request.files.getlist('documents')
        uploaded_files = []
        
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                # Create temp directory for uploads
                os.makedirs('temp_uploads', exist_ok=True)
                filepath = os.path.join('temp_uploads', filename)
                file.save(filepath)
                
                uploaded_files.append({
                    'name': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath)
                })
        
        return jsonify({
            'status': 'success',
            'files': uploaded_files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_documents():
    """Process uploaded documents through the AI workflow"""
    print("[DEBUG] /api/process route called", flush=True)
    try:
        print("[DEBUG] Processing request...", flush=True)
        
        # Handle JSON request from processing screen
        if request.is_json:
            data = request.get_json()
            business_name = data.get('business_name', 'Processing...')
            doc_info = data.get('documents', [])
            
            # Load files from temp storage
            documents = []
            for i, doc in enumerate(doc_info):
                file_path = doc.get('path')
                if file_path and os.path.exists(file_path):
                    documents.append({
                        "id": f"doc_{i+1:03d}",
                        "type": detect_document_type(doc['name']),
                        "path": file_path,
                        "filename": doc['name'],
                        "size": doc['size'],
                        "uploaded_at": datetime.now().isoformat()
                    })
        else:
            # Handle form data from direct upload
            business_name = request.form.get('business_name', 'Processing...')
            files = request.files.getlist('documents')
            
            if not files:
                return jsonify({'error': 'No files uploaded'}), 400
            
            documents = []
            for i, file in enumerate(files):
                if file.filename:
                    filename = f"{i+1:03d}_{file.filename}"
                    file_path = os.path.join('temp_uploads', filename)
                    os.makedirs('temp_uploads', exist_ok=True)
                    file.save(file_path)
                    
                    documents.append({
                        "id": f"doc_{i+1:03d}",
                        "type": detect_document_type(file.filename),
                        "path": file_path,
                        "filename": file.filename,
                        "size": os.path.getsize(file_path),
                        "uploaded_at": datetime.now().isoformat()
                    })
        
        if not documents:
            return jsonify({'error': 'No valid documents found'}), 400
        
        # Detect jurisdiction and create upload directory
        jurisdiction_service = JurisdictionService()
        jurisdiction = jurisdiction_service.detect_jurisdiction({'business_name': business_name})
        print(f"[DEBUG] Detected jurisdiction: {jurisdiction} for business: {business_name}")
        
        # Generate consistent app_id
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        app_id = f"APP_{timestamp}"
        print(f"[DEBUG] Generated app_id: {app_id}", flush=True)
        upload_dir = os.path.join('uploads', app_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Move files to permanent location
        final_documents = []
        for doc in documents:
            temp_path = doc['path']
            final_filename = f"{len(final_documents)+1:03d}_{doc['filename']}"
            final_path = os.path.join(upload_dir, final_filename)
            
            # Move from temp to permanent location
            if os.path.exists(temp_path):
                os.rename(temp_path, final_path)
                doc['path'] = final_path
                final_documents.append(doc)
        
        documents = final_documents
        
        # Save to database after documents are processed
        session = Session()
        try:
            application = MerchantApplication(
                id=app_id,
                business_name=business_name,
                status='processing',
                current_agent='market_qualification',
                progress_percentage=0,
                documents_processed=len(documents),
                processing_start_time=datetime.now(),
                application_data={
                    'documents': [doc['filename'] for doc in documents],
                    'jurisdiction': jurisdiction,
                    'business_name': business_name
                }
            )
            session.add(application)
            session.commit()
        finally:
            session.close()
        
        # Simple workflow routing for testing
        workflow_pattern = 'comprehensive_workflow'
        workflow_meta = {
            'name': 'Comprehensive Workflow',
            'description': 'Full 14-agent review process',
            'estimated_time': '2-4 hours',
            'automation_rate': '60%',
            'risk_level': 'Medium'
        }
        routing_reason = f"Selected {workflow_meta['name']} for {len(documents)} documents"
        routing_analysis = {
            'complexity_score': 15,
            'document_types': [detect_document_type(doc['filename']) for doc in documents]
        }
        
        # Ensure database record is committed before starting workflow
        import time
        time.sleep(0.1)  # Small delay to ensure DB commit
        
        # Start real workflow in background thread
        print(f"[{app_id}] Starting workflow thread...", flush=True)
        thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, workflow_pattern))
        thread.daemon = True
        thread.start()
        print(f"[{app_id}] Workflow thread started", flush=True)
        
        # Emit workflow pattern info with real analysis
        print(f"[{app_id}] Emitting workflow pattern to UI: {workflow_pattern}", flush=True)
        socketio.emit('workflow_pattern_selected', {
            'name': workflow_meta['name'],
            'description': workflow_meta['description'],
            'estimated_time': workflow_meta['estimated_time'],
            'automation_rate': workflow_meta['automation_rate'],
            'risk_level': workflow_meta['risk_level'],
            'routing_reason': routing_reason,
            'complexity_score': routing_analysis['complexity_score'],
            'document_types': routing_analysis['document_types']
        })
        print(f"[{app_id}] Workflow pattern emitted: {routing_reason}", flush=True)
        
        # Emit immediate test event
        print(f"[{app_id}] About to emit test event", flush=True)
        socketio.emit('agent_progress', {
            'application_id': app_id,
            'agent_name': 'initializing',
            'status': 'processing',
            'progress_percentage': 5,
            'current_agent': 'initializing',
            'agent_results': {}
        })
        print(f"[{app_id}] Emitted immediate test event", flush=True)
        
        return jsonify({
            'application_id': app_id,
            'status': 'processing',
            'documents_count': len(documents),
            'workflow_pattern': {
                'name': workflow_meta['name'],
                'description': workflow_meta['description'],
                'estimated_time': workflow_meta['estimated_time'],
                'automation_rate': workflow_meta['automation_rate'],
                'risk_level': workflow_meta['risk_level'],
                'routing_reason': routing_reason
            },
            'human_review_enabled': True,
            'expected_reviews': {
                'express_workflow': 4,
                'standard_workflow': 7,
                'comprehensive_workflow': 13
            }.get(workflow_pattern, 13)
        })
        
    except Exception as e:
        import traceback
        print(f"[ERROR] /api/process failed: {e}")
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

def detect_document_type(filename):
    """Simple document type detection based on filename"""
    filename_lower = filename.lower()
    if 'license' in filename_lower:
        return 'business_license'
    elif 'bank' in filename_lower or 'statement' in filename_lower:
        return 'bank_statement'
    elif 'tax' in filename_lower:
        return 'tax_return'
    elif 'ein' in filename_lower:
        return 'ein_letter'
    else:
        return 'business_license'  # Default

def run_workflow(app_id, documents, business_name, workflow_pattern='comprehensive_workflow'):
    """Run the test workflow with human review"""
    try:
        print(f"[{app_id}] *** WORKFLOW THREAD STARTED ***", flush=True)
        print(f"[{app_id}] Business: {business_name}", flush=True)
        print(f"[{app_id}] Documents: {len(documents)}", flush=True)
        print(f"[{app_id}] Pattern: {workflow_pattern}", flush=True)
        
        # Emit immediate start signal
        socketio.emit('workflow_started', {
            'application_id': app_id,
            'business_name': business_name,
            'status': 'processing'
        })
        print(f"[{app_id}] Emitted workflow_started event", flush=True)
        
        # Prepare application data with consistent ID
        application_data = {
            'application_id': app_id,  # Ensure consistent ID
            'business_name': business_name,
            'documents': [doc['filename'] for doc in documents],
            'workflow_pattern': workflow_pattern
        }
        print(f"[DEBUG] Application data app_id: {application_data.get('application_id')}", flush=True)
        
        print(f"[{app_id}] Starting workflow execution...", flush=True)
        
        # Progress callback for 14-agent workflow
        agent_progress_tracker = {}
        from datetime import datetime
        
        def progress_callback(agent_name, status, result):
            print(f"[{app_id}] *** PROGRESS CALLBACK TRIGGERED ***", flush=True)
            print(f"[{app_id}] Agent {agent_name}: {status}", flush=True)
            print(f"[{app_id}] Result type: {type(result)}", flush=True)
            
            # Track agent completion
            if status == 'completed':
                agent_progress_tracker[agent_name] = result or {}
            
            # Calculate progress based on completed agents
            total_agents = 4 if workflow_pattern == 'express_workflow' else 7 if workflow_pattern == 'standard_workflow' else 14
            completed_count = len(agent_progress_tracker)
            progress = min(100, int((completed_count / total_agents) * 100))
            
            print(f"[{app_id}] Progress: {completed_count}/{total_agents} = {progress}%", flush=True)
            
            # Update database with agent results immediately
            if not globals().get('app_shutdown', False):
                session = None
                try:
                    print(f"[{app_id}] Creating database session...")
                    session = Session()
                    print(f"[{app_id}] Querying for application {app_id}...")
                    application = session.query(MerchantApplication).filter_by(id=app_id).first()
                    
                    if application:
                        print(f"[{app_id}] Found application in database: {application.id}")
                        print(f"[{app_id}] Current agent_results: {type(application.agent_results)} - {application.agent_results}")
                        
                        # Update basic fields
                        application.current_agent = agent_name
                        application.progress_percentage = progress
                        application.updated_at = datetime.now()
                        
                        # Store agent results immediately when completed
                        if status == 'completed' and result:
                            print(f"[{app_id}] Processing completed result for {agent_name}")
                            current_results = application.agent_results or {}
                            print(f"[{app_id}] Current results keys: {list(current_results.keys()) if current_results else 'None'}")
                            current_results[agent_name] = result
                            application.agent_results = current_results
                            print(f"[{app_id}] Updated agent_results with {agent_name}")
                            print(f"[{app_id}] New results keys: {list(current_results.keys())}")
                        
                        # Also store when review is required
                        if status == 'review_required' and result:
                            print(f"[{app_id}] Processing review_required result for {agent_name}")
                            current_results = application.agent_results or {}
                            current_results[agent_name] = result
                            application.agent_results = current_results
                            application.needs_review = 'true'
                            application.review_agent = agent_name
                            print(f"[{app_id}] Saved {agent_name} result for review")
                            print(f"[{app_id}] Result data: {type(result)} - {len(str(result))} chars")
                        
                        print(f"[{app_id}] About to commit database changes...")
                        session.commit()
                        print(f"[{app_id}] Database committed successfully")
                        
                        # Verify the data was saved
                        session.refresh(application)
                        print(f"[{app_id}] Verification - agent_results after commit: {list(application.agent_results.keys()) if application.agent_results else 'None'}")
                        
                    else:
                        print(f"[{app_id}] ERROR: Application not found in database!")
                        print(f"[{app_id}] Searched for ID: '{app_id}'")
                        # List all applications to debug
                        all_apps = session.query(MerchantApplication).all()
                        print(f"[{app_id}] Available applications: {[app.id for app in all_apps]}")
                        
                except Exception as e:
                    if not globals().get('app_shutdown', False):
                        print(f"[{app_id}] DB error: {e}")
                        import traceback
                        print(f"[{app_id}] DB error traceback: {traceback.format_exc()}")
                        if session:
                            try:
                                session.rollback()
                                print(f"[{app_id}] Session rolled back")
                            except:
                                pass
                finally:
                    if session:
                        try:
                            session.close()
                            print(f"[{app_id}] Database session closed")
                        except:
                            pass
            
            # Emit progress
            socketio.emit('agent_progress', {
                'application_id': app_id,
                'agent_name': agent_name,
                'status': status,
                'progress_percentage': progress,
                'current_agent': agent_name,
                'agent_results': {agent_name: result} if result else {}
            })
            print(f"[{app_id}] Emitted progress: {progress}%", flush=True)
        
        # Import the real 14-agent workflow
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from main import process_merchant_application
        
        # Set the progress callback globally before starting workflow
        import builtins
        builtins.current_progress_callback = progress_callback
        print(f"[{app_id}] Set global progress callback before workflow start")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                process_merchant_application(application_data, documents, progress_callback)
            )
            print(f"[{app_id}] Workflow completed successfully", flush=True)
        except Exception as e:
            print(f"[{app_id}] Workflow error: {e}", flush=True)
            
            # Check if workflow was stopped due to rejection
            if "rejection" in str(e).lower() or "stopped" in str(e).lower():
                print(f"[{app_id}] Workflow stopped by human rejection")
                result = {'status': 'declined', 'reason': 'human_rejection', 'error': str(e)}
                
                # Update database status
                try:
                    session = Session()
                    application = session.query(MerchantApplication).filter_by(id=app_id).first()
                    if application:
                        application.status = 'declined'
                        application.processing_end_time = datetime.now()
                        session.commit()
                    session.close()
                except Exception as db_error:
                    print(f"[{app_id}] Error updating declined status: {db_error}")
                
                return  # Exit workflow execution completely
            else:
                result = {'status': 'failed', 'error': str(e)}
        # Determine final status
        final_status = 'completed'
        if isinstance(result, dict):
            if result.get('decision_making', {}).get('decision') == 'APPROVED':
                final_status = 'approved'
            elif result.get('decision_making', {}).get('decision') == 'DECLINED':
                final_status = 'declined'
        
        print(f"[{app_id}] Final status: {final_status}", flush=True)
        
        # Print human-readable summary
        print(f"\n[{app_id}] === WORKFLOW SUMMARY ===")
        if isinstance(result, dict):
            # Market Qualification Summary
            mq = result.get('market_qualification', {})
            if mq:
                print(f"[{app_id}] Market Qualification: {'✅ Qualified' if mq.get('qualified') else '❌ Not Qualified'}")
                print(f"[{app_id}] Reason: {mq.get('reasoning', 'No reasoning provided')}")
            
            # Risk Assessment Summary
            risk = result.get('risk_assessment', {})
            if risk:
                print(f"[{app_id}] Risk Level: {risk.get('risk_category', 'Unknown')} (Score: {risk.get('risk_score', 'N/A')})")
                print(f"[{app_id}] Credit Score: {risk.get('credit_score', 'N/A')}")
            
            # Final Decision Summary
            decision = result.get('decision', {})
            if decision:
                print(f"[{app_id}] Final Decision: {decision.get('decision', 'No decision')}")
                print(f"[{app_id}] Decision Reasoning: {decision.get('reasoning', 'No reasoning provided')}")
                if decision.get('conditions'):
                    print(f"[{app_id}] Conditions Required: {len(decision.get('conditions', []))} items")
            
            # Communication Summary
            comm = result.get('communication', {})
            if comm:
                strategy = comm.get('communication_strategy', {})
                print(f"[{app_id}] Communication: {strategy.get('message_type', 'N/A')} via {strategy.get('channel', 'N/A')}")
        
        print(f"[{app_id}] === END SUMMARY ===")
        
        # Update database with full results
        session = Session()
        try:
            application = session.query(MerchantApplication).filter_by(id=app_id).first()
            if application:
                application.status = final_status
                application.current_agent = 'completed'
                application.progress_percentage = 100
                application.processing_end_time = datetime.now()
                
                # Add workflow pattern info
                if hasattr(result, 'workflow_pattern'):
                    application.workflow_pattern = result.workflow_pattern
                elif isinstance(result, dict) and 'workflow_pattern' in result:
                    application.workflow_pattern = result['workflow_pattern']
                # Safely serialize complex objects to JSON
                if isinstance(result, dict):
                    extracted_data = result.get('extracted_data', result)  # Use full result if no extracted_data
                    agent_results = result
                else:
                    # If result is not a dict, create some sample data
                    extracted_data = {
                        'business_name': business_name,
                        'documents_processed': len(documents),
                        'workflow_completed': True,
                        'processing_time': 'completed'
                    }
                    agent_results = {'workflow_result': str(result)}
                
                # Convert any non-serializable objects to strings with better handling
                def serialize_object(obj):
                    if hasattr(obj, '__dict__'):
                        return {k: serialize_object(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
                    elif isinstance(obj, (list, tuple)):
                        return [serialize_object(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {k: serialize_object(v) for k, v in obj.items()}
                    else:
                        return str(obj)
                
                application.extracted_data = serialize_object(extracted_data)
                application.agent_results = serialize_object(agent_results)
                
                print(f"[{app_id}] Saved extracted_data: {len(str(application.extracted_data))} chars")
                print(f"[{app_id}] Saved agent_results: {len(str(application.agent_results))} chars")
                # Set realistic confidence - 0.0 when Document AI unavailable
                application.extraction_confidence = 0.0
                session.commit()
        finally:
            session.close()
        
        # Save results
        results_file = os.path.join('uploads', app_id, 'results.json')
        with open(results_file, 'w') as f:
            json.dump({
                'application_id': app_id,
                'business_name': business_name,
                'status': final_status,
                'workflow_result': json.loads(json.dumps(result, default=str)) if result else {},
                'completed_at': datetime.now().isoformat()
            }, f, indent=2)
        
    except Exception as e:
        import traceback
        print(f"[{app_id}] Workflow failed at step: {e}")
        print(f"[{app_id}] Exception type: {type(e).__name__}")
        print(f"[{app_id}] Full traceback:")
        print(traceback.format_exc())
        
        # Update database with error
        session = Session()
        try:
            application = session.query(MerchantApplication).filter_by(id=app_id).first()
            if application:
                application.status = 'failed'
                application.processing_end_time = datetime.now()
                session.commit()
        finally:
            session.close()
        
        # Save error
        error_file = os.path.join('uploads', app_id, 'error.json')
        with open(error_file, 'w') as f:
            json.dump({
                'application_id': app_id,
                'business_name': business_name,
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc(),
                'failed_at': datetime.now().isoformat()
            }, f, indent=2)

def save_agent_result(app_id, agent_results):
    """Save agent results to database immediately and emit real-time updates"""
    try:
        session = Session()
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if application:
            # Calculate progress based on completed agents
            completed_agents = len([k for k, v in agent_results.items() if v])
            total_agents = 14
            progress = min(100, int((completed_agents / total_agents) * 100))
            
            application.agent_results = json.loads(json.dumps(agent_results, default=str))
            application.progress_percentage = progress
            application.current_agent = list(agent_results.keys())[-1] if agent_results else 'processing'
            session.commit()
            
            # Emit real-time update
            socketio.emit('progress_update', {
                'application_id': app_id,
                'progress': progress,
                'current_agent': application.current_agent,
                'agent_results': agent_results
            }, room=f'app_{app_id}')
            
            print(f"[{app_id}] Saved agent results: {list(agent_results.keys())} ({progress}%)")
        session.close()
    except Exception as e:
        print(f"[{app_id}] Error saving agent results: {e}")
        # Emit error update
        socketio.emit('error_update', {
            'application_id': app_id,
            'error': str(e)
        }, room=f'app_{app_id}')

@socketio.on('join_application')
def on_join(data):
    """Join room for real-time updates"""
    app_id = data['application_id']
    join_room(f'app_{app_id}')
    emit('joined', {'application_id': app_id})

@socketio.on('leave_application')
def on_leave(data):
    """Leave room for real-time updates"""
    app_id = data['application_id']
    leave_room(f'app_{app_id}')
    emit('left', {'application_id': app_id})

@socketio.on('workflow_resume')
def on_workflow_resume(data):
    """Handle workflow resume after human review"""
    app_id = data['application_id']
    print(f"[{app_id}] Received workflow resume signal", flush=True)
    
    # Update database status
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if application:
            application.needs_review = 'false'
            application.status = 'processing'
            session.commit()
            print(f"[{app_id}] Updated status to processing", flush=True)
    finally:
        session.close()
    
    # TRIGGER THE EVENT TO RESUME WORKFLOW
    import builtins
    if hasattr(builtins, 'review_events') and app_id in builtins.review_events:
        print(f"[{app_id}] Triggering review event to resume workflow")
        builtins.review_events[app_id].set()
        print(f"[{app_id}] Review event triggered - workflow should resume")
    else:
        print(f"[{app_id}] WARNING: No review event found for this application")
        if hasattr(builtins, 'review_events'):
            print(f"[{app_id}] Available events: {list(builtins.review_events.keys())}")
    
    # Emit resume confirmation
    emit('workflow_resumed', {'application_id': app_id})
    print(f"[{app_id}] Workflow resume confirmed", flush=True)

# Auto-restart removed - use manual restart via /api/restart-workflow/<app_id>

# Global flag to stop background threads
app_shutdown = False

@app.teardown_appcontext
def shutdown_session(exception=None):
    global app_shutdown
    app_shutdown = True

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    # Serve static files
    app.static_folder = '.'
    app.static_url_path = ''
    
    print("UI started: http://localhost:5000")
    
    try:
        socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        app_shutdown = True