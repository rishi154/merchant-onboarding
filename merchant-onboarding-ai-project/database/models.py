from sqlalchemy import create_engine, Column, String, Integer, DateTime, JSON, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class MerchantApplication(Base):
    __tablename__ = 'merchant_applications'
    
    id = Column(String, primary_key=True)
    business_name = Column(String(255))
    status = Column(String(50))
    current_agent = Column(String(100))
    progress_percentage = Column(Integer, default=0)
    
    # Application data as JSON
    application_data = Column(JSON)
    extracted_data = Column(JSON)
    agent_results = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processing_start_time = Column(DateTime)
    processing_end_time = Column(DateTime)
    
    # Metrics
    extraction_confidence = Column(Float)
    documents_processed = Column(Integer)
    manual_fields_required = Column(Integer)

class ProcessingStep(Base):
    __tablename__ = 'processing_steps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(String, index=True)
    agent_name = Column(String(100))
    status = Column(String(50))  # pending, processing, completed, failed
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    result = Column(JSON)
    error_message = Column(Text)  # User-friendly error message
    error_details = Column(Text)  # Full traceback and technical details
    console_logs = Column(Text)   # Step-by-step processing logs

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///merchant_onboarding.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()