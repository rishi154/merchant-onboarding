"""Human Review API endpoints"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import sys
import os
import builtins
import threading

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from models import MerchantApplication, ReviewQueue, SessionLocal

review_bp = Blueprint('review', __name__)

@review_bp.route('/api/reviews/pending')
def get_pending_reviews():
    """Get all pending reviews"""
    session = SessionLocal()
    try:
        reviews = session.query(ReviewQueue).filter_by(status='pending').all()
        return jsonify([{
            'id': review.id,
            'application_id': review.application_id,
            'agent_name': review.agent_name,
            'agent_result': review.agent_result,
            'created_at': review.created_at.isoformat(),
            'status': review.status
        } for review in reviews])
    finally:
        session.close()

@review_bp.route('/api/applications/<app_id>/review')
def get_application_review(app_id):
    """Get current review for application"""
    session = SessionLocal()
    try:
        app = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        # Get pending review
        review = session.query(ReviewQueue).filter_by(
            application_id=app_id, 
            status='pending'
        ).first()
        
        return jsonify({
            'application_id': app_id,
            'business_name': app.business_name,
            'needs_review': app.needs_review == 'true',
            'review_agent': app.review_agent,
            'review_data': app.review_data,
            'current_reviewer': app.current_reviewer,
            'agent_results': app.agent_results,
            'review_id': review.id if review else None
        })
    finally:
        session.close()

@review_bp.route('/api/applications/<app_id>/review-decision', methods=['POST'])
def submit_review_decision(app_id):
    """Submit human review decision"""
    data = request.get_json()
    decision = data.get('decision')  # approved, rejected, changes_requested
    notes = data.get('notes', '')
    reviewer = data.get('reviewer', 'system')
    
    session = SessionLocal()
    try:
        # Update application
        app = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        # Update review queue
        review = session.query(ReviewQueue).filter_by(
            application_id=app_id,
            status='pending'
        ).first()
        
        if review:
            review.status = 'completed'
            review.decision = decision
            review.reviewer_notes = notes
            review.assigned_reviewer = reviewer
            review.completed_at = datetime.utcnow()
        
        # Update application status
        if decision == 'approved':
            app.status = 'processing'
            app.needs_review = 'false'
            app.current_reviewer = None
            print(f"[REVIEW] Application {app_id} approved - continuing workflow")
            
            # Just trigger existing event - don't restart workflow
            # The workflow should already be waiting for this event
                
        elif decision == 'rejected':
            app.status = 'declined'
            app.needs_review = 'false'
            app.current_reviewer = None
            print(f"[REVIEW] Application {app_id} rejected - workflow will stop")
        
        session.commit()
        
        # Trigger workflow continuation event (thread-safe)
        print(f"[REVIEW] Attempting to trigger event for {app_id}")
        
        if hasattr(builtins, 'review_events') and hasattr(builtins, 'review_lock'):
            with builtins.review_lock:
                print(f"[REVIEW] Available events: {list(builtins.review_events.keys())}")
                
                # Try exact match first
                if app_id in builtins.review_events:
                    print(f"[REVIEW] Found exact event for {app_id}, triggering...")
                    builtins.review_events[app_id].set()
                    print(f"[REVIEW] Successfully triggered continuation event for {app_id}")
                else:
                    # If no exact match, trigger the most recent event (likely the right one)
                    if builtins.review_events:
                        latest_app_id = max(builtins.review_events.keys())
                        print(f"[REVIEW] No exact match for {app_id}, triggering latest event {latest_app_id}")
                        builtins.review_events[latest_app_id].set()
                        print(f"[REVIEW] Successfully triggered continuation event for {latest_app_id}")
                    else:
                        print(f"[REVIEW] No events available to trigger")
        else:
            print(f"[REVIEW] Review events system not initialized")
        
        return jsonify({
            'success': True,
            'decision': decision,
            'application_id': app_id
        })
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@review_bp.route('/api/applications/<app_id>/resume', methods=['POST'])
def resume_application(app_id):
    """Resume paused application"""
    session = SessionLocal()
    try:
        app = session.query(MerchantApplication).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check if application needs review
        if app.needs_review == 'true':
            return jsonify({
                'success': True,
                'needs_review': True,
                'review_agent': app.review_agent,
                'review_data': app.review_data
            })
        
        # Resume workflow if no review needed
        app.status = 'processing'
        session.commit()
        
        # Trigger event if workflow is waiting
        print(f"[RESUME] Attempting to trigger event for {app_id}")
        if hasattr(builtins, 'review_events') and hasattr(builtins, 'review_lock'):
            with builtins.review_lock:
                if app_id in builtins.review_events:
                    builtins.review_events[app_id].set()
                    print(f"[RESUME] Successfully triggered continuation event for {app_id}")
                else:
                    print(f"[RESUME] No event found for {app_id} - workflow may not be waiting")
        
        return jsonify({
            'success': True,
            'needs_review': False,
            'status': 'processing'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()