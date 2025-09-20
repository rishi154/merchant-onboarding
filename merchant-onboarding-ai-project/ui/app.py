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
from workflow import create_onboarding_workflow
from state import MerchantOnboardingState
from models import MerchantApplication, ProcessingStep, Base

app = Flask(__name__)
app.config['SECRET_KEY'] = 'merchant-onboarding-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
engine = create_engine('sqlite:///merchant_onboarding.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Store processing status
processing_status = {}

@app.route('/')
def index():
    return app.send_static_file('applications.html')

@app.route('/new')
def new_application():
    return app.send_static_file('index.html')

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
                    
                    <a href="/" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Back to Applications</a>
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
        from workflow_config import get_workflow_steps, get_workflow_metadata
        
        steps = get_workflow_steps()
        metadata = get_workflow_metadata()
        
        return jsonify({
            'steps': steps,
            **metadata
        })
    except ImportError:
        # Fallback if config file doesn't exist
        return jsonify({
            'steps': [
                {'name': 'Document Processing', 'description': 'Extracting data from uploaded documents'},
                {'name': 'Data Validation', 'description': 'Validating extracted information'},
                {'name': 'Risk Assessment', 'description': 'Analyzing business risk factors'},
                {'name': 'Compliance Check', 'description': 'Verifying regulatory compliance'},
                {'name': 'Decision Making', 'description': 'Making final approval decision'}
            ],
            'workflow_name': 'Document-First Merchant Onboarding',
            'version': '1.0'
        })

@app.route('/api/process', methods=['POST'])
def process_documents():
    """Process uploaded documents through the AI workflow"""
    print("[DEBUG] /api/process route called")
    try:
        print("[DEBUG] Processing request...")
        business_name = request.form.get('business_name', 'Unknown Business')
        files = request.files.getlist('documents')
        
        if not files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        # Create upload directory
        app_id = f"APP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        upload_dir = os.path.join('uploads', app_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded files first
        documents = []
        for i, file in enumerate(files):
            if file.filename:
                filename = f"{i+1:03d}_{file.filename}"
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                documents.append({
                    "id": f"doc_{i+1:03d}",
                    "type": detect_document_type(file.filename),
                    "path": file_path,
                    "filename": file.filename,
                    "size": os.path.getsize(file_path),
                    "uploaded_at": datetime.now().isoformat()
                })
        
        # Save to database after documents are processed
        session = Session()
        try:
            application = MerchantApplication(
                id=app_id,
                business_name=business_name,
                status='processing',
                current_agent='market_qualification',
                progress_percentage=0,
                documents_processed=len(files),
                processing_start_time=datetime.now(),
                application_data={'documents': [doc['filename'] for doc in documents]}
            )
            session.add(application)
            session.commit()
        finally:
            session.close()
        
        # Start processing in background
        thread = threading.Thread(target=run_workflow, args=(app_id, documents, business_name))
        thread.start()
        
        return jsonify({
            'application_id': app_id,
            'status': 'processing',
            'documents_count': len(documents)
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

def run_workflow(app_id, documents, business_name):
    """Run the actual 14-agent LangGraph workflow"""
    try:
        print(f"[{app_id}] Starting 14-agent LangGraph workflow for {business_name}")
        print(f"[{app_id}] Processing {len(documents)} documents")
        
        print(f"[{app_id}] Creating workflow...")
        # Create workflow
        workflow = create_onboarding_workflow()
        print(f"[{app_id}] Workflow created successfully")
        
        print(f"[{app_id}] Initializing state...")
        # Initialize state
        initial_state = MerchantOnboardingState(
            application_id=app_id,
            business_name=business_name,
            documents=documents
        )
        print(f"[{app_id}] State initialized")
        
        print(f"[{app_id}] Running workflow...")
        print(f"[{app_id}] Initial state: {initial_state.__dict__}")
        
        # Run the workflow using async API with streaming
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print(f"[{app_id}] Starting workflow execution...")
        
        async def run_with_streaming():
            current_results = {}
            async for event in workflow.astream(initial_state):
                print(f"[{app_id}] Workflow event: {event}")
                # Update current results with new agent data
                if isinstance(event, dict):
                    for key, value in event.items():
                        if key in ['market_qualification', 'lead_qualification', 'application_assistant', 
                                  'document_processing', 'data_validation', 'risk_assessment', 
                                  'compliance_verification', 'decision', 'exception_routing', 
                                  'communication', 'account_provisioning', 'monitoring', 
                                  'optimization', 'onboarding_support']:
                            current_results[key] = value
                            # Save to database immediately
                            save_agent_result(app_id, current_results)
            
            # Get final result
            final_result = await workflow.ainvoke(initial_state)
            return final_result
        
        result = loop.run_until_complete(run_with_streaming())
        print(f"[{app_id}] Workflow execution completed")
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
            decision_result = result.get('decision', {})
            if isinstance(decision_result, dict):
                decision = decision_result.get('decision', 'MANUAL_REVIEW')
                if decision == 'APPROVED':
                    final_status = 'approved'
                elif decision == 'DECLINED':
                    final_status = 'declined'
                else:
                    final_status = 'manual_review'
        
        print(f"[{app_id}] Final status determined: {final_status}")
        
        # Update database with full results
        session = Session()
        try:
            application = session.query(MerchantApplication).filter_by(id=app_id).first()
            if application:
                application.status = final_status
                application.current_agent = 'onboarding_support'
                application.progress_percentage = 100
                application.processing_end_time = datetime.now()
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
                application.extraction_confidence = result.get('extraction_confidence', 0.85) if isinstance(result, dict) else 0.85
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