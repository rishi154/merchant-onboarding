from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import sys
import os

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'database'))
from models import MerchantApplication, SessionLocal

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search/applications', methods=['GET'])
def search_applications():
    """Search and filter applications"""
    session = SessionLocal()
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        status = request.args.get('status', '')
        workflow = request.args.get('workflow', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        needs_review = request.args.get('needs_review', '')
        
        # Start with base query
        applications_query = session.query(MerchantApplication)
        
        # Apply text search
        if query:
            applications_query = applications_query.filter(
                or_(
                    MerchantApplication.business_name.ilike(f'%{query}%'),
                    MerchantApplication.id.ilike(f'%{query}%'),
                    MerchantApplication.current_agent.ilike(f'%{query}%')
                )
            )
        
        # Apply status filter
        if status:
            applications_query = applications_query.filter(MerchantApplication.status == status)
        
        # Apply workflow filter
        if workflow:
            applications_query = applications_query.filter(MerchantApplication.workflow_pattern == workflow)
        
        # Apply date range filter
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                applications_query = applications_query.filter(MerchantApplication.created_at >= from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                applications_query = applications_query.filter(MerchantApplication.created_at <= to_date)
            except ValueError:
                pass
        
        # Apply review filter
        if needs_review == 'true':
            applications_query = applications_query.filter(MerchantApplication.needs_review == 'true')
        elif needs_review == 'false':
            applications_query = applications_query.filter(MerchantApplication.needs_review != 'true')
        
        # Order by created date (newest first)
        applications_query = applications_query.order_by(MerchantApplication.created_at.desc())
        
        # Execute query
        applications = applications_query.all()
        
        # Format results
        results = []
        for app in applications:
            results.append({
                'application_id': app.id,
                'id': app.id,
                'business_name': app.business_name,
                'status': app.status,
                'current_agent': app.current_agent,
                'progress_percentage': app.progress_percentage,
                'documents_processed': app.documents_processed,
                'created_at': app.created_at.isoformat(),
                'updated_at': app.updated_at.isoformat(),
                'needs_review': app.needs_review == 'true',
                'review_agent': app.review_agent,
                'workflow_pattern': app.workflow_pattern,
                'agent_count': len(app.agent_results) if app.agent_results else 0,
                'processing_duration': calculate_processing_duration(app)
            })
        
        return jsonify({
            'applications': results,
            'total': len(results),
            'query': query,
            'filters': {
                'status': status,
                'workflow': workflow,
                'date_from': date_from,
                'date_to': date_to,
                'needs_review': needs_review
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@search_bp.route('/api/search/filters', methods=['GET'])
def get_filter_options():
    """Get available filter options"""
    session = SessionLocal()
    try:
        # Get unique statuses
        statuses = session.query(MerchantApplication.status).distinct().all()
        status_options = [status[0] for status in statuses if status[0]]
        
        # Get unique workflows
        workflows = session.query(MerchantApplication.workflow_pattern).distinct().all()
        workflow_options = [workflow[0] for workflow in workflows if workflow[0]]
        
        # Get unique agents
        agents = session.query(MerchantApplication.current_agent).distinct().all()
        agent_options = [agent[0] for agent in agents if agent[0]]
        
        return jsonify({
            'statuses': status_options,
            'workflows': workflow_options,
            'agents': agent_options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

def calculate_processing_duration(app):
    """Calculate processing duration in minutes"""
    if app.processing_start_time:
        end_time = app.processing_end_time or app.updated_at
        if end_time:
            delta = end_time - app.processing_start_time
            return int(delta.total_seconds() / 60)
    return 0