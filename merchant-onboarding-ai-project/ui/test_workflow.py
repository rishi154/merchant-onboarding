"""Simple test workflow for UI testing"""
import asyncio
import time
from datetime import datetime

async def process_merchant_application(application_data, documents, progress_callback=None):
    """Test workflow with human review checkpoints"""
    
    agents = [
        'market_qualification',
        'document_processing', 
        'risk_assessment',
        'compliance_verification',
        'decision_making'
    ]
    
    results = {}
    
    for i, agent in enumerate(agents):
        print(f"[WORKFLOW] Starting {agent}", flush=True)
        
        if progress_callback:
            progress_callback(agent, 'processing', {})
        
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Create mock result
        if agent == 'market_qualification':
            result = {'qualified': True, 'reasoning': 'Business meets basic requirements'}
        elif agent == 'risk_assessment':
            result = {'risk_category': 'LOW', 'risk_score': 25, 'credit_score': 720}
        elif agent == 'decision_making':
            result = {'decision': 'APPROVED', 'reasoning': 'All checks passed'}
        else:
            result = {'status': 'completed', 'confidence': 0.85}
        
        results[agent] = result
        
        if progress_callback:
            progress_callback(agent, 'completed', result)
        
        # Add human review checkpoint after each agent
        print(f"[WORKFLOW] {agent} completed, triggering human review", flush=True)
        if progress_callback:
            progress_callback(agent, 'review_required', {
                'agent_result': result,
                'requires_human_review': True
            })
        
        # Wait for human approval (simulate with sleep)
        print(f"[WORKFLOW] Waiting for human approval of {agent}...", flush=True)
        await asyncio.sleep(5)  # Wait 5 seconds for human review
        print(f"[WORKFLOW] Continuing after review of {agent}", flush=True)
    
    return {
        'status': 'completed',
        'agents_executed': agents,
        'workflow_pattern': application_data.get('workflow_pattern', 'comprehensive_workflow'),
        **results
    }