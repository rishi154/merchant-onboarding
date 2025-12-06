#!/usr/bin/env python3
"""
Script to revert applications back to original state after presentation
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

def revert_applications():
    if not os.path.exists('backup_applications.json'):
        print("✗ No backup file found. Cannot revert.")
        return
    
    # Load backup data
    with open('backup_applications.json', 'r') as f:
        backup_data = json.load(f)
    
    print(f"📁 Found backup with {len(backup_data)} applications")
    
    session = Session()
    try:
        for backup_app in backup_data:
            app = session.query(MerchantApplication).filter_by(id=backup_app['id']).first()
            if app:
                app.business_name = backup_app['business_name']
                app.workflow_pattern = backup_app['workflow_pattern']
                app.status = backup_app['status']
                print(f"Reverted {app.id}: {backup_app['business_name']}")
        
        session.commit()
        print("✅ Applications reverted to original state!")
    finally:
        session.close()
    
    # Clean up backup file
    os.remove('backup_applications.json')
    print("🗑️  Backup file cleaned up")

if __name__ == "__main__":
    print("🔄 Reverting applications from presentation...")
    revert_applications()