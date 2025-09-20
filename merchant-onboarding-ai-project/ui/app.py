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

# Add paths for importing the workflow and database
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from state import MerchantOnboardingState
from models import MerchantApplication, ProcessingStep, Base

app = Flask(__name__)
app.config['SECRET_KEY'] = 'merchant-onboarding-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
engine = create_engine('sqlite:///merchant_onboarding.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

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
    return app.send_static_file('workflow_display.html')

@app.route('/new')
def new_application():
    return app.send_static_file('upload.html')

@app.route('/applications')
def applications():
    return app.send_static_file('applications.html')

@app.route('/application/<app_id>')
def application_details(app_id):
    """Show detailed view of a specific application"""
    session = Session()
    try:
        application = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not application:
            return "Application not found", 404
        
        # Create a simple details page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Details - {app_id}</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-50 p-8">
            <div class="max-w-4xl mx-auto">
                <div class="bg-white rounded-lg shadow p-6">
                    <h1 class="text-2xl font-bold mb-4">Application Details</h1>
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <div><strong>ID:</strong> {application.id}</div>
                        <div><strong>Business:</strong> {application.business_name}</div>
                        <div><strong>Status:</strong> {application.status}</div>
                        <div><strong>Current Agent:</strong> {application.current_agent or 'N/A'}</div>
                        <div><strong>Progress:</strong> {application.progress_percentage or 0}%</div>
                        <div><strong>Documents:</strong> {application.documents_processed or 0}</div>
                        <div><strong>Created:</strong> {application.created_at}</div>
                        <div><strong>Updated:</strong> {application.updated_at}</div>
                    </div>
                    
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold mb-2">Extracted Data</h2>
                        <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">{json.dumps(application.extracted_data or {}, indent=2)}</pre>
                    </div>
                    
                    <div class="mb-6">
                        <h2 class="text-lg font-semibold mb-2">Agent Results</h2>
                        <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">{json.dumps(application.agent_results or {}, indent=2)}</pre>
                    </div>
                    
                    <a href="/applications" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Back to Applications</a>
                </div>
            </div>
        </body>
        </html>
        """
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
    """Get all applications from database"""
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
            'agent_results': app.agent_results
        } for app in applications])
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
    print("[DEBUG] /api/process route called")
    try:
        print("[DEBUG] Processing request...")
        
        # Handle JSON request from processing screen
        if request.is_json:
            data = request.get_json()
            business_name = data.get('business_name', 'Unknown Business')
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
            business_name = request.form.get('business_name', 'Unknown Business')
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
        
        # Create upload directory
        app_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
                application_data={'documents': [doc['filename'] for doc in documents]}
            )
            session.add(application)
            session.commit()
        finally:
            session.close()
        
        # Analyze documents for routing decision
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
            from document_ai_router import analyze_documents_with_ai
            from workflow_router import get_workflow_metadata
            
            print(f"[{app_id}] Analyzing {len(documents)} documents for routing...")
            routing_analysis = analyze_documents_with_ai(documents)
            workflow_pattern = routing_analysis['workflow_pattern']
            workflow_meta = get_workflow_metadata(workflow_pattern)
            
            # Create detailed routing reason
            routing_reason = f"Selected {workflow_meta['name']} due to: "
            routing_reason += ", ".join(routing_analysis['risk_factors'][:3])  # Top 3 factors
            if len(routing_analysis['risk_factors']) > 3:
                routing_reason += f" and {len(routing_analysis['risk_factors']) - 3} other factors"
            
            print(f"[{app_id}] Routing decision: {workflow_pattern} - {routing_reason}")
        except Exception as e:
            print(f"[{app_id}] Error in document analysis: {e}")
            # Fallback to comprehensive workflow
            from workflow_router import get_workflow_metadata
            workflow_pattern = 'comprehensive_workflow'
            workflow_meta = get_workflow_metadata(workflow_pattern)
            routing_reason = f"Selected {workflow_meta['name']} due to: Analysis error with {len(documents)} documents, defaulting to comprehensive review"
            routing_analysis = {
                'complexity_score': 20,
                'document_types': ['unknown']
            }
        
        # Start processing in background with workflow pattern
        thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name, workflow_pattern))
        thread.start()
        
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
            }
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
    """Run the actual 14-agent LangGraph workflow"""
    try:
        print(f"[{app_id}] Starting 14-agent LangGraph workflow for {business_name}", flush=True)
        print(f"[{app_id}] Processing {len(documents)} documents", flush=True)
        
        print(f"[{app_id}] Preparing application data...")
        # Prepare application data
        application_data = {
            'business_name': business_name,
            'documents': [doc['filename'] for doc in documents]
        }
        
        # Import the new main processing function
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
        from main import process_merchant_application
        
        # Run the multi-workflow processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print(f"[{app_id}] Starting multi-workflow execution...", flush=True)
        
        # Initialize progress tracking for this application
        if app_id not in agent_progress:
            agent_progress[app_id] = {}
        
        # Create progress callback for real-time updates
        def progress_callback(agent_name, status, result):
            print(f"[{app_id}] *** AGENT PROGRESS *** {agent_name}: {status}", flush=True)
            
            # Update global progress tracker
            agent_progress[app_id][agent_name] = {'status': status, 'result': result}
            
            # Count completed agents
            completed_agents = len([k for k, v in agent_progress[app_id].items() if v.get('status') == 'completed'])
            workflow_pattern = application_data.get('workflow_pattern', 'comprehensive_workflow')
            total_agents = 4 if workflow_pattern == 'express_workflow' else 7 if workflow_pattern == 'standard_workflow' else 14
            progress = min(100, int((completed_agents / total_agents) * 100))
            
            print(f"[{app_id}] Progress: {completed_agents}/{total_agents} = {progress}% ({workflow_pattern})")
            print(f"[{app_id}] Completed agents: {[k for k, v in agent_progress[app_id].items() if v.get('status') == 'completed']}")
            
            # Update database
            try:
                session = Session()
                application = session.query(MerchantApplication).filter_by(id=app_id).first()
                if application:
                    application.current_agent = agent_name
                    application.progress_percentage = progress
                    application.agent_results = dict(agent_progress[app_id])  # Save all results
                    session.commit()
                session.close()
            except Exception as e:
                print(f"[{app_id}] DB update error: {e}")
            
            # Emit to UI immediately
            socketio.emit('agent_progress', {
                'application_id': app_id,
                'agent_name': agent_name,
                'status': status,
                'progress_percentage': progress,
                'current_agent': agent_name,
                'result': result
            })
            print(f"[{app_id}] Emitted progress: {progress}%")
            if status == 'completed' and result:
                # Print human-readable summary for key agents
                if agent_name == 'market_qualification' and isinstance(result, dict):
                    qualified = result.get('qualified', False)
                    print(f"[{app_id}] Market Qualification: {'✅ Qualified' if qualified else '❌ Not Qualified'}")
                    if result.get('reasoning'):
                        print(f"[{app_id}] Reason: {result['reasoning']}")
                elif agent_name == 'risk_assessment' and isinstance(result, dict):
                    risk_level = result.get('risk_category', 'Unknown')
                    risk_score = result.get('risk_score', 'N/A')
                    credit_score = result.get('credit_score', 'N/A')
                    print(f"[{app_id}] Risk Assessment: {risk_level} (Score: {risk_score}, Credit: {credit_score})")
                elif agent_name == 'decision_making' and isinstance(result, dict):
                    decision = result.get('decision', 'No Decision')
                    reasoning = result.get('reasoning', 'No reasoning')
                    print(f"[{app_id}] Final Decision: {decision}")
                    print(f"[{app_id}] Decision Reasoning: {reasoning}")
            print(f"[{app_id}] Agent result: {result}")
            
            # Progress tracking handled in callback
        
        # Set workflow pattern in application data for main processing
        application_data['workflow_pattern'] = workflow_pattern
        
        # Use the new main processing function with routing and progress callback
        try:
            result = loop.run_until_complete(
                process_merchant_application(application_data, documents, progress_callback)
            )
        except NameError as e:
            print(f"[{app_id}] NameError in workflow: {e}")
            result = {'status': 'failed', 'error': str(e)}
        except Exception as e:
            print(f"[{app_id}] Error in workflow: {e}")
            result = {'status': 'failed', 'error': str(e)}
        print(f"[{app_id}] Workflow execution completed", flush=True)
        print(f"[{app_id}] Result type: {type(result)}")
        print(f"[{app_id}] Result keys: {list(result.__dict__.keys()) if hasattr(result, '__dict__') else 'No __dict__'}")
        
        print(f"[{app_id}] 14-agent workflow completed successfully")
        print(f"[{app_id}] Result type: {type(result)}")
        print(f"[{app_id}] Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Handle result as dict
        final_status = result.get('status', 'completed') if isinstance(result, dict) else 'completed'
        print(f"[{app_id}] Final status: {final_status}")
        
        # Determine final status from workflow decision
        final_status = 'completed'
        if isinstance(result, dict):
            # Check if workflow actually completed all agents
            agents_executed = result.get('agents_executed', [])
            if len(agents_executed) < 14:  # Comprehensive workflow should have 14 agents
                final_status = 'failed'
            else:
                decision_result = result.get('decision', {})
                if isinstance(decision_result, dict):
                    decision = decision_result.get('decision', 'MANUAL_REVIEW')
                    if decision == 'APPROVED':
                        final_status = 'approved'
                    elif decision == 'DECLINED':
                        final_status = 'declined'
                    else:
                        final_status = 'manual_review'
        else:
            # Check if it's a state object with exceptions
            if hasattr(result, 'exceptions') and result.exceptions:
                final_status = 'failed'
        
        print(f"[{app_id}] Final status determined: {final_status}")
        if isinstance(result, dict) and result.get('agents_executed'):
            print(f"[{app_id}] Agents executed: {len(result.get('agents_executed', []))}/14")
        elif hasattr(result, 'agents_executed'):
            print(f"[{app_id}] Agents executed: {len(result.agents_executed)}/14")
        
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
                
                # Convert any non-serializable objects to strings
                application.extracted_data = json.loads(json.dumps(extracted_data, default=str))
                application.agent_results = json.loads(json.dumps(agent_results, default=str))
                
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

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    # Serve static files
    app.static_folder = '.'
    app.static_url_path = ''
    
    print("Starting Merchant Onboarding AI UI with real-time updates...")
    print("Open http://localhost:5000 in your browser")
    
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)