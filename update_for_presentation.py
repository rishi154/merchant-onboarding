#!/usr/bin/env python3
"""
Script to update applications with diverse business names and workflows for presentation
"""

import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add database path
sys.path.append(os.path.join(os.path.dirname(__file__), 'merchant-onboarding-ai-project', 'database'))
from models import MerchantApplication, engine

Session = sessionmaker(bind=engine)

def backup_current_data():
    session = Session()
    try:
        applications = session.query(MerchantApplication).all()
        backup_data = []
        for app in applications:
            backup_data.append({
                'id': app.id,
                'business_name': app.business_name,
                'workflow_pattern': app.workflow_pattern,
                'status': app.status
            })
        
        with open('backup_applications.json', 'w') as f:
            json.dump(backup_data, f, indent=2)
        print(f"✓ Backed up {len(backup_data)} applications")
    finally:
        session.close()

def update_applications():
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
        
        for i, app in enumerate(applications[:len(presentation_data)]):
            update_data = presentation_data[i]
            app.business_name = update_data['business_name']
            app.workflow_pattern = update_data['workflow_pattern']
            app.status = update_data['status']
            print(f"Updated {app.id}: {update_data['business_name']} ({update_data['workflow_pattern']})")
        
        session.commit()
        print(f"✅ Updated {min(len(applications), len(presentation_data))} applications")
    finally:
        session.close()

if __name__ == "__main__":
    print("🎯 Updating applications for presentation...")
    backup_current_data()
    update_applications()
    print("✅ Presentation data applied!")