"""Add agent_summaries column to merchant_applications table"""
import sqlite3
import os

# Get database path - it's in the ui folder
db_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'merchant_onboarding.db')

# Connect and add column
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add agent_summaries column
    cursor.execute("""
        ALTER TABLE merchant_applications 
        ADD COLUMN agent_summaries TEXT
    """)
    conn.commit()
    print("Successfully added agent_summaries column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column agent_summaries already exists")
    else:
        print(f"Error: {e}")
finally:
    conn.close()
