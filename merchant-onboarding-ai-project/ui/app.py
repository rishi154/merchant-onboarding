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
from api.search import search_bp

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

# Register API blueprints
app.register_blueprint(review_bp)
app.register_blueprint(search_bp)

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
    return app.send_static_file('application_list.html')

@app.route('/applications/legacy')
def applications_legacy():
    return app.send_static_file('applications.html')

@app.route('/analytics')
def analytics():
    return app.send_static_file('analytics.html')

@app.route('/application/<app_id>')
def application_details(app_id):
    """Show detailed review page for a specific application"""
    return app.send_static_file('application_review.html')

@app.route('/api/progress/<app_id>')
def get_progress(app_id):
    """Get real-time progress for a specific application"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Extract business name from various sources
        business_name = application.business_name
        if business_name == 'Processing...' or not business_name:
            if application.extracted_data and 'business_name' in application.extracted_data:
                business_name = application.extracted_data['business_name']
            elif application.agent_results:
                for agent_name, result in application.agent_results.items():
                    if isinstance(result, dict) and 'extracted_data' in result and 'business_name' in result['extracted_data']:
                        business_name = result['extracted_data']['business_name']
                        break
        
        return jsonify({
            'application_id': application.id,
            'business_name': business_name,
            'status': application.status,
            'current_agent': application.current_agent,
            'progress_percentage': application.progress_percentage,
            'agent_results': application.agent_results or {},
            'needs_review': application.needs_review == 'true',
            'review_agent': application.review_agent,
            'error_message': getattr(application, 'error_message', None)
        })
    finally:
        session.close()

@app.route('/api/applications/<app_id>/resume', methods=['POST'])
def resume_application(app_id):
    """Resume a paused application from where it left off"""
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
            print(f"[{app_id}] No existing workflow found - resuming from completed agents")
            # Resume workflow from current state (preserve completed agents)
            application.status = 'processing'
            session.commit()
            
            # Get application data for resume
            app_data = application.application_data or {}
            app_data['application_id'] = app_id
            business_name = application.business_name
            workflow_pattern = application.workflow_pattern or 'comprehensive_workflow'
            
            # Preserve completed agents to avoid re-execution
            completed_agents = application.agent_results or {}
            app_data['completed_agents'] = completed_agents
            print(f"[{app_id}] Preserving {len(completed_agents)} completed agents: {list(completed_agents.keys())}")
            
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
                # Resume workflow with preserved state
                print(f"[{app_id}] Resuming {workflow_pattern} with {len(documents)} documents")
                thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, workflow_pattern, app_data))
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
        from werkzeug.utils import secure_filename
        
        # Secure the filename and app_id
        safe_app_id = secure_filename(app_id)
        safe_filename = secure_filename(filename)
        
        # Construct safe path
        upload_base = os.path.abspath('uploads')
        file_path = os.path.join(upload_base, safe_app_id, safe_filename)
        
        # Ensure path is within uploads directory
        if not file_path.startswith(upload_base):
            return jsonify({'error': 'Invalid file path'}), 400
        
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
        from werkzeug.utils import secure_filename
        
        # Secure the app_id
        safe_app_id = secure_filename(app_id)
        
        # Construct safe path
        upload_base = os.path.abspath('uploads')
        upload_dir = os.path.join(upload_base, safe_app_id)
        
        # Ensure path is within uploads directory
        if not upload_dir.startswith(upload_base):
            return jsonify({'error': 'Invalid path'}), 400
        
        if not os.path.exists(upload_dir):
            return jsonify({'documents': []})
        
        documents = []
        for filename in os.listdir(upload_dir):
            if filename.endswith(('.pdf', '.png', '.jpg', '.jpeg', '.txt')):
                safe_filename = secure_filename(filename)
                file_path = os.path.join(upload_dir, safe_filename)
                if os.path.exists(file_path):
                    documents.append({
                        'filename': safe_filename,
                        'size': os.path.getsize(file_path),
                        'type': detect_document_type(safe_filename),
                        'preview_url': f'/api/document/{safe_app_id}/{safe_filename}'
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
            'business_name': extract_business_name(app),
            'status': app.status,
            'current_agent': app.current_agent,
            'progress_percentage': calculate_dynamic_progress(app),
            'status': app.status,
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
            'workflow_pattern': app.workflow_pattern,
            'agent_count': count_actual_agents(app.agent_results, app.needs_review == 'true', app.review_agent) if app.agent_results else 0,
            'processing_duration': calculate_processing_duration(app)
        } for app in applications])
    finally:
        session.close()

def get_expected_reviews_count(workflow_pattern):
    """Get expected human reviews count dynamically from workflow stages API"""
    try:
        # Get workflow stages dynamically from the API
        import requests
        response = requests.get(f'http://localhost:5000/api/workflow-stages/{workflow_pattern}')
        if response.status_code == 200:
            stages = response.json().get('stages', [])
        else:
            # Fallback to default stages if API fails
            stages = get_default_workflow_stages(workflow_pattern)
        
        # Get review configuration dynamically
        review_config = get_review_configuration()
        
        # Count how many agents require review
        review_count = 0
        for agent in stages:
            if review_config.get(agent, True):  # Default to True for safety
                review_count += 1
        
        return review_count
    except Exception as e:
        print(f"Error getting dynamic review count: {e}")
        # Fallback: only compliance_verification requires review currently
        stages = get_default_workflow_stages(workflow_pattern)
        return 1 if 'compliance_verification' in stages else 0

def get_default_workflow_stages(workflow_pattern):
    """Get default workflow stages as fallback"""
    stages_map = {
        'express_workflow': ['document_processing', 'risk_assessment', 'decision_making', 'account_provisioning'],
        'standard_workflow': ['document_processing', 'risk_assessment', 'data_validation', 'underwriting', 'compliance_verification', 'decision_making', 'account_provisioning', 'communication'],
        'comprehensive_workflow': ['document_processing', 'risk_assessment', 'market_qualification', 'lead_qualification', 'data_validation', 'underwriting', 'compliance_verification', 'decision_making', 'exception_routing', 'communication', 'account_provisioning', 'monitoring', 'optimization', 'onboarding_support']
    }
    return stages_map.get(workflow_pattern, stages_map['comprehensive_workflow'])

def get_review_configuration():
    """Get current review configuration"""
    # This reflects the current AGENT_REVIEW_CONFIG from multi_workflow.py
    return {
        'document_processing': False,
        'data_validation': False,
        'underwriting': False,
        'risk_assessment': False,
        'compliance_verification': True,  # Only this requires review
        'decision_making': False,
        'account_provisioning': False,
        'communication': False,
        'market_qualification': False,
        'lead_qualification': False,
        'exception_routing': False,
        'monitoring': False,
        'optimization': False,
        'onboarding_support': False
    }

def count_actual_agents(agent_results, needs_review=False, review_agent=None):
    """Count only actual agent names, excluding nested data structures and agents under review"""
    if not agent_results or not isinstance(agent_results, dict):
        return 0
    
    # Known agent names from the workflow
    known_agents = {
        'document_processing', 'risk_assessment', 'data_validation', 'underwriting',
        'compliance_verification', 'decision_making', 'communication', 'account_provisioning',
        'market_qualification', 'lead_qualification', 'exception_routing', 'monitoring',
        'optimization', 'onboarding_support'
    }
    
    # Count actual completed agents (exclude agents under review)
    count = 0
    for key in agent_results.keys():
        if key in known_agents:
            # Don't count agents that are currently under review
            if needs_review and review_agent == key:
                continue
            count += 1
        elif key == 'decision' and 'decision_making' not in agent_results:
            # Don't count if decision_making is under review
            if not (needs_review and review_agent == 'decision_making'):
                count += 1
    
    return count

def extract_business_name(app):
    """Extract business name from various sources"""
    business_name = app.business_name
    if business_name == 'Processing...' or not business_name:
        # Try document_processing agent result first (most reliable)
        if app.agent_results and 'document_processing' in app.agent_results:
            doc_result = app.agent_results['document_processing']
            if isinstance(doc_result, dict) and doc_result.get('extracted_data', {}).get('business_name'):
                business_name = doc_result['extracted_data']['business_name']
        
        # Try other agent results if still not found
        if (business_name == 'Processing...' or not business_name) and app.agent_results:
            for agent_name, result in app.agent_results.items():
                if isinstance(result, dict) and result.get('extracted_data', {}).get('business_name'):
                    business_name = result['extracted_data']['business_name']
                    break
    
    return business_name or 'Unknown Business'

def calculate_processing_duration(app):
    """Calculate processing duration in minutes"""
    if app.processing_start_time:
        end_time = app.processing_end_time or app.updated_at
        if end_time and end_time > app.processing_start_time:
            delta = end_time - app.processing_start_time
            return int(delta.total_seconds() / 60)
    return 0

def get_corrected_status(app):
    """Get corrected status based on decision results for existing applications"""
    # Always check decision results for status correction
    if app.agent_results:
        # Check decision_making result
        decision_result = app.agent_results.get('decision_making') or app.agent_results.get('decision')
        if decision_result and isinstance(decision_result, dict):
            decision = decision_result.get('decision') or decision_result.get('final_decision')
            if decision == 'DECLINED':
                return 'declined'
            elif decision in ['APPROVED', 'CONDITIONAL']:
                # Check if account provisioning was skipped due to not_approved
                account_prov = app.agent_results.get('account_provisioning')
                if account_prov and account_prov.get('skipped') == 'True' and account_prov.get('reason') == 'not_approved':
                    return 'declined'  # Actually declined despite CONDITIONAL decision
                return 'approved'
    
    return app.status

def calculate_dynamic_progress(app):
    """Calculate progress based on completed agents"""
    if not app.agent_results:
        return 0
    
    # Define agents per workflow
    workflow_agents = {
        'express_workflow': ['document_processing', 'risk_assessment', 'decision_making', 'account_provisioning'],
        'standard_workflow': ['document_processing', 'risk_assessment', 'data_validation', 'underwriting', 'compliance_verification', 'decision_making', 'account_provisioning', 'communication'],
        'comprehensive_workflow': ['document_processing', 'risk_assessment', 'market_qualification', 'lead_qualification', 'data_validation', 'underwriting', 'compliance_verification', 'decision_making', 'exception_routing', 'communication', 'account_provisioning', 'monitoring', 'optimization', 'onboarding_support']
    }
    
    agents_to_check = workflow_agents.get(app.workflow_pattern, workflow_agents['standard_workflow'])
    total_agents = len(agents_to_check)
    
    # Count completed agents for this workflow
    completed_count = 0
    for agent in agents_to_check:
        if agent == 'decision_making':
            # Handle decision_making stored as 'decision'
            if app.agent_results.get('decision_making') or app.agent_results.get('decision'):
                completed_count += 1
        elif app.agent_results.get(agent):
            completed_count += 1
    
    # Exclude agent under review
    if app.needs_review == 'true' and app.review_agent and app.review_agent in app.agent_results:
        completed_count -= 1
    
    return min(100, int((completed_count / total_agents) * 100))

@app.route('/api/application-state/<app_id>')
def get_application_state(app_id):
    """Get complete application state for processing page"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Get workflow pattern info with dynamic review count
        workflow_pattern = application.workflow_pattern or 'comprehensive_workflow'
        expected_reviews = get_expected_reviews_count(workflow_pattern)
        
        workflow_info = {
            'comprehensive_workflow': {
                'name': 'Comprehensive Workflow',
                'estimated_time': '2-4 hours',
                'expected_reviews': expected_reviews
            },
            'standard_workflow': {
                'name': 'Standard Workflow', 
                'estimated_time': '1-2 hours',
                'expected_reviews': expected_reviews
            },
            'express_workflow': {
                'name': 'Express Workflow',
                'estimated_time': '30-60 minutes', 
                'expected_reviews': expected_reviews
            }
        }.get(workflow_pattern, {
            'name': 'Comprehensive Workflow',
            'estimated_time': '2-4 hours',
            'expected_reviews': expected_reviews
        })
        
        # Extract business name from various sources
        business_name = application.business_name
        if business_name == 'Processing...' or not business_name:
            # Try to get from extracted data
            if application.extracted_data and 'business_name' in application.extracted_data:
                business_name = application.extracted_data['business_name']
            # Try to get from agent results
            elif application.agent_results:
                for agent_name, result in application.agent_results.items():
                    if isinstance(result, dict):
                        if 'extracted_data' in result and 'business_name' in result['extracted_data']:
                            business_name = result['extracted_data']['business_name']
                            break
                        elif 'processed_documents' in result:
                            for doc in result['processed_documents']:
                                if 'extracted_data' in doc and 'business_name' in doc['extracted_data']:
                                    business_name = doc['extracted_data']['business_name']
                                    break
                            if business_name != 'Processing...':
                                break
        
        return jsonify({
            'application_id': application.id,
            'business_name': business_name,
            'status': get_corrected_status(application),
            'current_agent': application.current_agent,
            'progress_percentage': application.progress_percentage or 0,
            'agent_results': application.agent_results or {},
            'agent_summaries': application.agent_summaries or {},
            'needs_review': application.needs_review == 'true',
            'review_agent': application.review_agent,
            'review_data': application.review_data,
            'workflow_pattern': workflow_pattern,
            'workflow_info': workflow_info,
            'created_at': application.created_at.isoformat(),
            'updated_at': application.updated_at.isoformat(),
            'processing_duration': calculate_processing_duration(application),
            'extracted_data': application.extracted_data,
            'application_data': application.application_data
        })
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
            
            # Resume workflow with preserved state
            app_data = application.application_data or {}
            app_data['application_id'] = app_id
            app_data['completed_agents'] = application.agent_results or {}
            workflow_pattern = application.workflow_pattern or 'comprehensive_workflow'
            
            print(f"[{app_id}] Resuming workflow with {len(documents)} documents")
            print(f"[{app_id}] Preserving {len(app_data.get('completed_agents', {}))} completed agents")
            thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, workflow_pattern, app_data))
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

@app.route('/api/applications/<app_id>/set-review-required', methods=['POST'])
def set_review_required(app_id):
    """Set application to require human review for testing"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Set application to require compliance verification review
        application.status = 'pending_human_review'
        application.needs_review = 'true'
        application.review_agent = 'compliance_verification'
        application.current_agent = 'compliance_verification'
        application.progress_percentage = 75
        
        # Ensure compliance verification result exists
        if not application.agent_results:
            application.agent_results = {}
        
        application.agent_results['compliance_verification'] = {
            'compliance_verification_complete': 'True',
            'sanctions_clear': True,
            'kyc_status': 'verified',
            'aml_status': 'clear',
            'pep_clear': True,
            'compliance_score': '0.85',
            'requires_enhanced_dd': False,
            'processing_time': '2.5',
            'agent_reasoning': 'Compliance verification completed. All checks passed but requires human review due to configuration.',
            'tools_used': ['ofac_sanctions_check', 'pep_screening', 'aml_risk_assessment', 'kyc_verification']
        }
        
        application.review_data = application.agent_results['compliance_verification']
        application.updated_at = datetime.now()
        
        session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Application {app_id} set to require compliance verification review',
            'status': application.status,
            'needs_review': application.needs_review,
            'review_agent': application.review_agent
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

@app.route('/api/applications/<app_id>/review-decision', methods=['POST'])
def submit_review_decision(app_id):
    """Submit human review decision"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        data = request.get_json()
        decision = data.get('decision')  # 'approved' or 'rejected'
        notes = data.get('notes', '')
        reviewer = data.get('reviewer', 'system')
        
        if decision == 'approved':
            # Clear review flags and continue workflow
            application.needs_review = 'false'
            application.current_reviewer = None
            application.status = 'processing'
            session.commit()
            
            # Try to trigger existing workflow first
            import builtins
            if hasattr(builtins, 'review_events') and app_id in builtins.review_events:
                print(f"[{app_id}] Triggering existing workflow event")
                builtins.review_events[app_id].set()
                return jsonify({
                    'success': True,
                    'decision': 'approved',
                    'message': 'Application approved and workflow resumed'
                })
            else:
                print(f"[{app_id}] No existing workflow - restarting from current state")
                # Restart workflow from current state
                app_data = application.application_data or {}
                app_data['application_id'] = app_id
                app_data['completed_agents'] = application.agent_results or {}
                business_name = application.business_name
                workflow_pattern = application.workflow_pattern or 'comprehensive_workflow'
                
                # Load documents
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
                    print(f"[{app_id}] Restarting workflow with {len(documents)} documents")
                    thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, workflow_pattern, app_data))
                    thread.daemon = True
                    thread.start()
                
                return jsonify({
                    'success': True,
                    'decision': 'approved',
                    'message': 'Application approved and workflow restarted'
                })
            
        elif decision == 'rejected':
            # Mark as declined
            application.status = 'declined'
            application.needs_review = 'false'
            application.processing_end_time = datetime.now()
            session.commit()
            
            # Trigger event to stop workflow
            import builtins
            if hasattr(builtins, 'review_events') and app_id in builtins.review_events:
                builtins.review_events[app_id].set()
            
            return jsonify({
                'success': True,
                'decision': 'rejected',
                'message': 'Application rejected and workflow stopped'
            })
        else:
            return jsonify({'error': 'Invalid decision'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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

@app.route('/api/admin/clear-all', methods=['DELETE'])
def clear_all_applications():
    """Delete all applications from database"""
    session = Session()
    try:
        count = session.query(MerchantApplication).count()
        session.query(MerchantApplication).delete()
        session.commit()
        return jsonify({
            'success': True,
            'message': f'Deleted {count} applications',
            'deleted_count': count
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/admin/update-business-names', methods=['POST'])
def update_business_names():
    """Update applications with unique business names for presentation"""
    business_names = [
        'TechFlow Solutions LLC',
        'Green Valley Organics', 
        'Metro Coffee Roasters',
        'Digital Marketing Pro',
        'Coastal Construction Co',
        'Artisan Bakery & Cafe'
    ]
    
    session = Session()
    try:
        applications = session.query(MerchantApplication).order_by(MerchantApplication.created_at.desc()).all()
        updated = 0
        
        for i, app in enumerate(applications[:len(business_names)]):
            app.business_name = business_names[i]
            updated += 1
        
        session.commit()
        return jsonify({'success': True, 'updated': updated, 'names': business_names[:updated]})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/workflow-stages/<pattern>')
def get_workflow_stages(pattern):
    """Get workflow stages for a specific pattern"""
    # Define stages based on actual workflow definitions
    workflow_stages = {
        'routing_workflow': ['document_processing', 'risk_assessment'],
        'express_workflow': ['document_processing', 'risk_assessment', 'decision_making', 'account_provisioning'],
        'standard_workflow': ['document_processing', 'risk_assessment', 'data_validation', 'underwriting', 'compliance_verification', 'decision_making', 'account_provisioning', 'communication'],
        'comprehensive_workflow': ['document_processing', 'risk_assessment', 'market_qualification', 'lead_qualification', 'data_validation', 'underwriting', 'compliance_verification', 'decision_making', 'exception_routing', 'communication', 'account_provisioning', 'monitoring', 'optimization', 'onboarding_support']
    }
    
    stages = workflow_stages.get(pattern, workflow_stages['comprehensive_workflow'])
    return jsonify({'stages': stages})

@app.route('/api/force-pipeline-update/<app_id>')
def force_pipeline_update(app_id):
    """Force pipeline update for completed agents"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        agent_results = application.agent_results or {}
        review_agent = application.review_agent
        needs_review = application.needs_review == 'true'
        
        # Emit pipeline updates for all completed agents
        for agent_name in agent_results.keys():
            status = 'review' if (needs_review and agent_name == review_agent) else 'completed'
            socketio.emit('force_pipeline_update', {
                'application_id': app_id,
                'agent_name': agent_name,
                'status': status
            })
        
        return jsonify({
            'success': True,
            'updated_agents': list(agent_results.keys()),
            'review_agent': review_agent,
            'needs_review': needs_review
        })
    finally:
        session.close()

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
        
        # Intelligent workflow routing - will be determined after document processing
        workflow_pattern = 'routing_workflow'  # Special pattern for routing phase
        
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
                workflow_pattern=workflow_pattern,
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
        workflow_meta = {
            'name': 'Analyzing Documents',
            'description': 'Processing documents to determine optimal workflow',
            'estimated_time': 'Determining...',
            'automation_rate': 'TBD',
            'risk_level': 'Analyzing'
        }
        routing_reason = f"Analyzing {len(documents)} documents to determine optimal workflow"
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
            'document_types': routing_analysis['document_types'],
            'expected_reviews': get_expected_reviews_count('routing_workflow')
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

def run_workflow(app_id, documents, business_name, workflow_pattern='comprehensive_workflow', preserved_data=None):
    """Run the workflow with state preservation to avoid re-executing completed agents"""
    try:
        print(f"[{app_id}] *** WORKFLOW THREAD STARTED ***", flush=True)
        print(f"[{app_id}] Business: {business_name}", flush=True)
        print(f"[{app_id}] Documents: {len(documents)}", flush=True)
        print(f"[{app_id}] Pattern: {workflow_pattern}", flush=True)
        
        # Check if this is a resume with preserved state
        if preserved_data and preserved_data.get('completed_agents'):
            completed_agents = preserved_data['completed_agents']
            print(f"[{app_id}] RESUMING with {len(completed_agents)} completed agents: {list(completed_agents.keys())}")
        else:
            print(f"[{app_id}] STARTING fresh workflow")
        
        # Emit immediate start signal
        socketio.emit('workflow_started', {
            'application_id': app_id,
            'business_name': business_name,
            'status': 'processing'
        })
        print(f"[{app_id}] Emitted workflow_started event", flush=True)
        
        # Prepare application data with consistent ID and preserved state
        application_data = preserved_data or {}
        application_data.update({
            'application_id': app_id,  # Ensure consistent ID
            'business_name': business_name,
            'documents': [doc['filename'] for doc in documents],
            'workflow_pattern': workflow_pattern
        })
        print(f"[DEBUG] Application data app_id: {application_data.get('application_id')}", flush=True)
        
        print(f"[{app_id}] Starting workflow execution...", flush=True)
        
        # Progress callback for workflow with state preservation
        agent_progress_tracker = {}
        if preserved_data and preserved_data.get('completed_agents'):
            # Pre-populate with already completed agents to avoid re-execution
            agent_progress_tracker.update(preserved_data['completed_agents'])
            print(f"[{app_id}] Pre-populated progress tracker with {len(agent_progress_tracker)} completed agents")
        
        from datetime import datetime
        
        def progress_callback(agent_name, status, result):
            print(f"[{app_id}] *** PROGRESS CALLBACK TRIGGERED ***", flush=True)
            print(f"[{app_id}] Agent {agent_name}: {status}", flush=True)
            
            # Track agent completion
            if status == 'completed':
                agent_progress_tracker[agent_name] = result or {}
            
            # Calculate progress
            completed_count = len(agent_progress_tracker)
            total_agents = 8  # Standard workflow
            progress = min(100, int((completed_count / total_agents) * 100))
            
            print(f"[{app_id}] Progress: {completed_count}/{total_agents} = {progress}%", flush=True)
            
            # Emit progress with business name update
            emit_data = {
                'application_id': app_id,
                'agent_name': agent_name,
                'status': status,
                'progress_percentage': progress,
                'current_agent': agent_name,
                'agent_results': {agent_name: result} if result else {}
            }
            
            # Add business name update for document processing
            if agent_name == 'document_processing' and status == 'completed' and result:
                extracted_business_name = None
                if 'processed_documents' in result:
                    for doc in result['processed_documents']:
                        if 'extracted_data' in doc and 'business_name' in doc['extracted_data']:
                            extracted_business_name = doc['extracted_data']['business_name']
                            break
                elif 'extracted_data' in result and 'business_name' in result['extracted_data']:
                    extracted_business_name = result['extracted_data']['business_name']
                
                if extracted_business_name:
                    emit_data['business_name'] = extracted_business_name
            
            socketio.emit('agent_progress', emit_data)
            print(f"[{app_id}] Emitted progress: {progress}%", flush=True)
            
            # Emit review_required event for UI consistency
            if status == 'review_required':
                socketio.emit('review_required', {
                    'application_id': app_id,
                    'agent_name': agent_name,
                    'review_data': result
                })
                print(f"[{app_id}] Emitted review_required for {agent_name}", flush=True)
        
        # Import the real 14-agent workflow
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from main import process_merchant_application
        
        # Set the progress callback globally before starting workflow
        import builtins
        builtins.current_progress_callback = progress_callback
        print(f"[{app_id}] Set global progress callback before workflow start")
        
        # Store preserved data globally for agent access
        if preserved_data and preserved_data.get('completed_agents'):
            builtins.preserved_completed_agents = preserved_data['completed_agents']
            print(f"[{app_id}] Stored {len(preserved_data['completed_agents'])} completed agents globally")
        else:
            builtins.preserved_completed_agents = {}
            print(f"[{app_id}] No preserved agents to store globally")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Check if this is routing phase
            if workflow_pattern == 'routing_workflow':
                print(f"[{app_id}] Starting routing workflow to determine optimal pattern")
                
                # Run routing workflow first (document_processing + market_qualification)
                result = loop.run_until_complete(
                    process_merchant_application(application_data, documents, progress_callback)
                )
                
                # Determine actual workflow from risk assessment result
                selected_pattern = 'comprehensive_workflow'  # Default fallback
                risk_tier = 'HIGH'  # Default fallback
                
                if result and 'risk_assessment' in result:
                    risk_assessment = result['risk_assessment']
                    risk_tier = risk_assessment.get('risk_tier', 'HIGH')
                    
                    if risk_tier == 'LOW':
                        selected_pattern = 'express_workflow'
                    elif risk_tier == 'MEDIUM':
                        selected_pattern = 'standard_workflow'
                    else:
                        selected_pattern = 'comprehensive_workflow'
                    
                    print(f"[{app_id}] Routing determined: {selected_pattern} (risk: {risk_tier})")
                else:
                    print(f"[{app_id}] No risk assessment result - defaulting to comprehensive")
                
                # Update database with selected pattern
                session = Session()
                try:
                    application = session.query(MerchantApplication).filter_by(id=app_id).first()
                    if application:
                        application.workflow_pattern = selected_pattern
                        session.commit()
                        print(f"[{app_id}] Updated database with workflow pattern: {selected_pattern}")
                finally:
                    session.close()
                
                # Emit workflow selection to UI
                workflow_meta = {
                    'express_workflow': {'name': 'Express Workflow', 'estimated_time': '15-30 min', 'agents': 4},
                    'standard_workflow': {'name': 'Standard Workflow', 'estimated_time': '1-2 hours', 'agents': 7},
                    'comprehensive_workflow': {'name': 'Comprehensive Workflow', 'estimated_time': '2-4 hours', 'agents': 14}
                }[selected_pattern]
                

                
                print(f"[{app_id}] Emitted workflow_selected event: {workflow_meta['name']}")
                
                # Include routing results in workflow_selected event
                routing_results = {}
                if result and isinstance(result, dict):
                    for agent_name in ['document_processing', 'risk_assessment']:
                        if agent_name in result:
                            routing_results[agent_name] = result[agent_name]
                
                # Get expected reviews count for selected pattern
                expected_reviews = get_expected_reviews_count(selected_pattern)
                
                # Update workflow_selected emission to include routing results
                socketio.emit('workflow_selected', {
                    'application_id': app_id,
                    'pattern': selected_pattern,
                    'name': workflow_meta['name'],
                    'estimated_time': workflow_meta['estimated_time'],
                    'total_agents': workflow_meta['agents'],
                    'expected_reviews': expected_reviews,
                    'risk_tier': risk_tier,
                    'routing_results': routing_results
                })
                
                # Continue with selected workflow (preserve routing results)
                application_data['workflow_pattern'] = selected_pattern
                # Preserve routing results - don't reset progress
                # Keep document_processing and risk_assessment results from routing phase
                
                # Skip routing agents in selected workflow by pre-populating state
                if result and isinstance(result, dict):
                    application_data['completed_agents'] = {
                        'document_processing': result.get('document_processing'),
                        'risk_assessment': result.get('risk_assessment')
                    }
                    print(f"[{app_id}] Pre-populated completed agents: {list(application_data['completed_agents'].keys())}")
                
                print(f"[{app_id}] Starting selected workflow: {selected_pattern}")
                # Create new progress callback for selected workflow
                selected_progress_tracker = agent_progress_tracker.copy()  # Preserve routing progress
                
                # Pre-populate with routing results to avoid double execution
                if result and isinstance(result, dict):
                    if 'document_processing' in result:
                        selected_progress_tracker['document_processing'] = result['document_processing']
                    if 'risk_assessment' in result:
                        selected_progress_tracker['risk_assessment'] = result['risk_assessment']
                    print(f"[{app_id}] Pre-populated progress tracker with routing results")
                
                def selected_progress_callback(agent_name, status, result):
                    print(f"[{app_id}] *** SELECTED WORKFLOW PROGRESS ***", flush=True)
                    print(f"[{app_id}] Agent {agent_name}: {status}", flush=True)
                    
                    # Skip if agent already completed in routing phase
                    if agent_name in ['document_processing', 'risk_assessment'] and agent_name in selected_progress_tracker:
                        print(f"[{app_id}] Skipping {agent_name} - already completed in routing phase")
                        return
                    
                    # Track agent completion for selected workflow
                    if status == 'completed':
                        selected_progress_tracker[agent_name] = result or {}
                    
                    # Get correct total agents for selected workflow
                    total_agents = 4 if selected_pattern == 'express_workflow' else 8 if selected_pattern == 'standard_workflow' else 14
                    completed_count = len(selected_progress_tracker)
                    progress = min(100, int((completed_count / total_agents) * 100))
                    
                    print(f"[{app_id}] Selected workflow progress: {completed_count}/{total_agents} = {progress}%")
                    
                    # Emit progress
                    socketio.emit('agent_progress', {
                        'application_id': app_id,
                        'agent_name': agent_name,
                        'status': status,
                        'progress_percentage': progress,
                        'current_agent': agent_name,
                        'agent_results': {agent_name: result} if result else {}
                    })
                
                result = loop.run_until_complete(
                    process_merchant_application(application_data, documents, selected_progress_callback)
                )
            else:
                # Direct workflow execution
                result = loop.run_until_complete(
                    process_merchant_application(application_data, documents, progress_callback)
                )
            
            print(f"[{app_id}] Workflow completed successfully", flush=True)
        except Exception as e:
            print(f"[{app_id}] Workflow error: {e}", flush=True)
            
            # Check if workflow was stopped due to rejection
            if "rejection" in str(e).lower() or "stopped" in str(e).lower():
                print(f"[{app_id}] Workflow stopped by human rejection - exiting completely")
                return  # Exit completely, don't continue to final update
            
            final_status = 'failed'
        
        # Check if declined before final update
        session_check = Session()
        app_check = session_check.query(MerchantApplication).filter_by(id=app_id).first()
        if app_check and app_check.status == 'declined':
            session_check.close()
            print(f"[{app_id}] Application declined - skipping final update")
            return
        session_check.close()
        
        final_status = 'completed'
        if isinstance(result, dict):
            # Check decision_making result (could be under 'decision_making' or 'decision' key)
            decision_result = result.get('decision_making') or result.get('decision')
            if decision_result and isinstance(decision_result, dict):
                decision = decision_result.get('decision') or decision_result.get('final_decision')
                if decision == 'APPROVED':
                    final_status = 'approved'
                elif decision == 'DECLINED':
                    final_status = 'declined'
                elif decision == 'CONDITIONAL':
                    final_status = 'approved'  # Conditional approval is still approval
            # If no clear decision found, check if workflow failed
            elif result.get('status') == 'failed':
                final_status = 'failed'
        
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
                
                # Clear any remaining review status when workflow completes
                application.needs_review = 'false'
                application.review_agent = None
                application.review_data = None
                print(f"[{app_id}] Cleared review status on workflow completion")
                print(f"[{app_id}] Final business outcome: {final_status.upper()}")
                
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
                print(f"[{app_id}] Final database update completed - Status: {final_status}")
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

def generate_and_store_summary(agent_name, result):
    """Generate summary when agent completes and return it"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from llm_config import get_llm
        
        llm = get_llm()
        prompt = f"""Summarize these {agent_name} results for a human reviewer in 3-4 sentences with HTML formatting:
{json.dumps(result, indent=2)[:1000]}

Use <p>, <strong>, and color classes (text-green-600, text-red-600, text-yellow-600)."""
        
        summary = llm.invoke(prompt)
        summary_text = summary.content if hasattr(summary, 'content') else str(summary)
        
        if len(summary_text) > 50 and '<' in summary_text:
            return summary_text
    except Exception as e:
        print(f"[SUMMARY] LLM unavailable for {agent_name}: {e}")
    
    return generate_fallback_summary(agent_name, result)

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
        else:
            print(f"[{app_id}] Application not found for resume")
            return
    finally:
        session.close()
    
    # TRIGGER THE EVENT TO RESUME WORKFLOW OR RESTART
    import builtins
    if hasattr(builtins, 'review_events') and app_id in builtins.review_events:
        print(f"[{app_id}] Triggering review event to resume workflow")
        builtins.review_events[app_id].set()
        print(f"[{app_id}] Review event triggered - workflow should resume")
    else:
        print(f"[{app_id}] No active workflow found - workflow may have completed or failed")
        # DO NOT restart workflow - just log that no active workflow exists
    
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

@app.route('/api/admin/delete-application/<app_id>', methods=['DELETE'])
def delete_application(app_id):
    """Delete specific application by ID"""
    session = Session()
    try:
        app = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        session.delete(app)
        session.commit()
        return jsonify({'success': True, 'deleted': app_id})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/summarize-agent-result', methods=['POST'])
def summarize_agent_result():
    """Get pre-generated summary or generate on-demand if not available"""
    try:
        data = request.get_json()
        agent_name = data.get('agent_name')
        result = data.get('result')
        app_id = data.get('application_id')
        
        if not agent_name or not result:
            return jsonify({'error': 'Missing agent_name or result'}), 400
        
        # Try to get pre-generated summary from database first
        if app_id:
            session = Session()
            try:
                application = session.query(MerchantApplication).filter_by(id=app_id).first()
                if application and application.agent_summaries and agent_name in application.agent_summaries:
                    print(f"[SUMMARY] Returning stored summary for {agent_name}")
                    return jsonify({'summary': application.agent_summaries[agent_name]})
            finally:
                session.close()
        
        # Generate on-demand if not stored
        print(f"[SUMMARY] Generating on-demand summary for {agent_name}")
        summary = generate_and_store_summary(agent_name, result)
        return jsonify({'summary': summary})
        
    except Exception as e:
        print(f"[SUMMARY] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'summary': generate_fallback_summary(agent_name if 'agent_name' in locals() else 'unknown', result if 'result' in locals() else {})})

def generate_fallback_summary(agent_name, result):
    """Generate a simple HTML summary when LLM is unavailable"""
    html = f'<div class="space-y-3"><h4 class="font-semibold text-gray-800">{agent_name.replace("_", " ").title()} Results</h4>'
    
    if isinstance(result, dict):
        for key, value in result.items():
            if key.startswith('_') or key in ['tools_used']:
                continue
            
            if isinstance(value, (str, int, float, bool)):
                formatted_key = key.replace('_', ' ').title()
                color_class = ''
                
                if 'error' in key.lower() or 'fail' in key.lower() or value is False:
                    color_class = 'text-red-600'
                elif 'success' in key.lower() or 'pass' in key.lower() or 'clear' in key.lower() or value is True:
                    color_class = 'text-green-600'
                elif 'warning' in key.lower() or 'risk' in key.lower():
                    color_class = 'text-yellow-600'
                
                html += f'<p class="{color_class}"><strong>{formatted_key}:</strong> {value}</p>'
            elif isinstance(value, list) and value:
                formatted_key = key.replace('_', ' ').title()
                html += f'<p><strong>{formatted_key}:</strong></p><ul class="ml-4 list-disc">'
                for item in value[:5]:
                    html += f'<li>{item}</li>'
                if len(value) > 5:
                    html += f'<li>... and {len(value) - 5} more</li>'
                html += '</ul>'
    
    html += '<p class="text-sm text-gray-500 mt-4"><em>Note: LLM summary unavailable, showing structured data</em></p></div>'
    return html

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
@app.route('/api/admin/update-for-presentation', methods=['POST'])
def update_for_presentation():
    """Update applications with presentation data"""
    presentation_data = [
        {'business_name': 'TechFlow Solutions LLC', 'workflow_pattern': 'comprehensive_workflow', 'status': 'approved'},
        {'business_name': 'Green Valley Organics', 'workflow_pattern': 'standard_workflow', 'status': 'declined'},
        {'business_name': 'Metro Coffee Roasters', 'workflow_pattern': 'express_workflow', 'status': 'approved'},
        {'business_name': 'Digital Marketing Pro', 'workflow_pattern': 'standard_workflow', 'status': 'pending_human_review'},
        {'business_name': 'Coastal Construction Co', 'workflow_pattern': 'comprehensive_workflow', 'status': 'processing'},
        {'business_name': 'Artisan Bakery & Cafe', 'workflow_pattern': 'express_workflow', 'status': 'approved'}
    ]
    
    session = Session()
    try:
        applications = session.query(MerchantApplication).all()
        updated = 0
        
        for i, app in enumerate(applications[:len(presentation_data)]):
            update_data = presentation_data[i]
            app.business_name = update_data['business_name']
            app.workflow_pattern = update_data['workflow_pattern']
            app.status = update_data['status']
            updated += 1
        
        session.commit()
        return jsonify({'success': True, 'updated': updated})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
@app.route('/api/admin/update-business-names', methods=['POST'])
def update_business_names():
    """Update applications with unique business names for presentation"""
    business_names = [
        'TechFlow Solutions LLC',
        'Green Valley Organics', 
        'Metro Coffee Roasters',
        'Digital Marketing Pro',
        'Coastal Construction Co',
        'Artisan Bakery & Cafe'
    ]
    
    session = Session()
    try:
        applications = session.query(MerchantApplication).order_by(MerchantApplication.created_at.desc()).all()
        updated = 0
        
        for i, app in enumerate(applications[:len(business_names)]):
            app.business_name = business_names[i]
            updated += 1
        
        session.commit()
        return jsonify({'success': True, 'updated': updated, 'names': business_names[:updated]})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()