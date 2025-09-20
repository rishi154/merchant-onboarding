"""Workflow configuration for the merchant onboarding system."""

def get_workflow_steps():
    """Return the 14-agent workflow steps in order."""
    return [
        {'name': 'Market Qualification', 'description': 'Analyzing market and business viability'},
        {'name': 'Lead Qualification', 'description': 'Qualifying lead quality and potential'},
        {'name': 'Application Assistant', 'description': 'Assisting with application completion'},
        {'name': 'Document Processing', 'description': 'Processing and extracting document data'},
        {'name': 'Data Validation', 'description': 'Validating extracted information'},
        {'name': 'Risk Assessment', 'description': 'Analyzing business risk factors'},
        {'name': 'Compliance Verification', 'description': 'Verifying regulatory compliance'},
        {'name': 'Decision Making', 'description': 'Making final approval decision'},
        {'name': 'Exception Routing', 'description': 'Routing exceptions and edge cases'},
        {'name': 'Communication', 'description': 'Managing customer communications'},
        {'name': 'Account Provisioning', 'description': 'Setting up merchant accounts'},
        {'name': 'Monitoring', 'description': 'Monitoring account setup and status'},
        {'name': 'Optimization', 'description': 'Optimizing account configuration'},
        {'name': 'Onboarding Support', 'description': 'Providing onboarding support'}
    ]

def get_workflow_metadata():
    """Return workflow metadata."""
    return {
        'workflow_name': '14-Agent Merchant Onboarding AI',
        'version': '2.0',
        'total_agents': 14
    }