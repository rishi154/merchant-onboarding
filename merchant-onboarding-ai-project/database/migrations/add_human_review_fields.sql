-- Migration to add human review fields to existing database

-- Add human review fields to merchant_applications table
ALTER TABLE merchant_applications ADD COLUMN needs_review VARCHAR(10) DEFAULT 'false';
ALTER TABLE merchant_applications ADD COLUMN review_agent VARCHAR(100);
ALTER TABLE merchant_applications ADD COLUMN review_data JSON;
ALTER TABLE merchant_applications ADD COLUMN current_reviewer VARCHAR(100);
ALTER TABLE merchant_applications ADD COLUMN workflow_pattern VARCHAR(50);

-- Create review_queue table
CREATE TABLE IF NOT EXISTS review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id VARCHAR(255),
    agent_name VARCHAR(100),
    agent_result JSON,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_reviewer VARCHAR(100),
    reviewer_notes TEXT,
    decision VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_review_queue_app_id ON review_queue(application_id);
CREATE INDEX IF NOT EXISTS idx_review_queue_status ON review_queue(status);
CREATE INDEX IF NOT EXISTS idx_merchant_applications_review ON merchant_applications(needs_review, review_agent);