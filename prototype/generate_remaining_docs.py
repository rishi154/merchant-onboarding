#!/usr/bin/env python3
"""Generate remaining critical merchant documents"""

from PIL import Image, ImageDraw, ImageFilter
import random

def add_ocr_challenges(img):
    angle = random.uniform(-1, 1)
    img = img.rotate(angle, expand=True, fillcolor='white')
    return img

def create_professional_license():
    """Generate professional license"""
    img = Image.new('RGB', (700, 900), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([50, 50, 650, 850], outline='#003366', width=3)
    draw.text((70, 80), "STATE OF CALIFORNIA", fill='#003366')
    draw.text((70, 110), "PROFESSIONAL LICENSE", fill='#003366')
    
    draw.text((70, 180), "License Type: Software Contractor", fill='black')
    draw.text((70, 210), "License Number: SC-2023-456789", fill='black')
    draw.text((70, 240), "Issue Date: January 15, 2023", fill='black')
    draw.text((70, 270), "Expiration: January 15, 2025", fill='black')
    
    draw.text((70, 330), "Licensee: Sarah Michelle Chen", fill='black')
    draw.text((70, 360), "Business: TechFlow Solutions LLC", fill='black')
    
    return add_ocr_challenges(img)

def create_operating_agreement():
    """Generate LLC operating agreement"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "OPERATING AGREEMENT", fill='black')
    draw.text((50, 80), "TechFlow Solutions LLC", fill='black')
    
    draw.text((50, 130), "ARTICLE I - ORGANIZATION", fill='black')
    draw.text((50, 160), "The Company was formed on January 15, 2023", fill='black')
    draw.text((50, 190), "under Delaware Limited Liability Company Act.", fill='black')
    
    draw.text((50, 240), "ARTICLE II - MEMBERS", fill='black')
    draw.text((50, 270), "Sarah Chen - Managing Member (60%)", fill='black')
    draw.text((50, 300), "Michael Rodriguez - Member (25%)", fill='black')
    draw.text((50, 330), "Jennifer Kim - Member (15%)", fill='black')
    
    draw.text((50, 400), "Signatures:", fill='black')
    draw.text((50, 450), "Sarah Chen", fill='blue')
    draw.text((50, 480), "Michael Rodriguez", fill='blue')
    draw.text((50, 510), "Jennifer Kim", fill='blue')
    
    return add_ocr_challenges(img)

def create_board_resolution():
    """Generate corporate board resolution"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "BOARD RESOLUTION", fill='black')
    draw.text((50, 80), "TechFlow Solutions LLC", fill='black')
    
    draw.text((50, 130), "RESOLVED, that the Company is authorized", fill='black')
    draw.text((50, 160), "to enter into a merchant processing agreement", fill='black')
    draw.text((50, 190), "for payment processing services.", fill='black')
    
    draw.text((50, 240), "FURTHER RESOLVED, that Sarah Chen,", fill='black')
    draw.text((50, 270), "Managing Member, is authorized to execute", fill='black')
    draw.text((50, 300), "all documents related to this agreement.", fill='black')
    
    draw.text((50, 370), "Date: March 1, 2024", fill='black')
    draw.text((50, 420), "Secretary: Jennifer Kim", fill='blue')
    
    return add_ocr_challenges(img)

def create_workers_comp():
    """Generate workers compensation certificate"""
    img = Image.new('RGB', (850, 650), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "WORKERS COMPENSATION INSURANCE", fill='black')
    draw.text((50, 80), "CERTIFICATE OF COVERAGE", fill='black')
    
    draw.text((50, 130), "Insured: TechFlow Solutions LLC", fill='black')
    draw.text((50, 160), "Policy Number: WC-2024-789456", fill='black')
    draw.text((50, 190), "Effective: 01/01/2024 - 01/01/2025", fill='black')
    
    draw.text((50, 240), "Coverage Limits:", fill='black')
    draw.text((50, 270), "Bodily Injury by Accident: $1,000,000", fill='black')
    draw.text((50, 300), "Bodily Injury by Disease: $1,000,000", fill='black')
    
    draw.text((50, 370), "Carrier: State Compensation Fund", fill='black')
    draw.text((50, 420), "Agent: Pacific Insurance Services", fill='blue')
    
    return add_ocr_challenges(img)

def create_ein_letter():
    """Generate IRS EIN confirmation letter"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "INTERNAL REVENUE SERVICE", fill='black')
    draw.text((50, 80), "EMPLOYER IDENTIFICATION NUMBER", fill='black')
    
    draw.text((50, 130), "Entity: TechFlow Solutions LLC", fill='black')
    draw.text((50, 160), "EIN: 87-1234567", fill='black')
    draw.text((50, 190), "Date Assigned: January 20, 2023", fill='black')
    
    draw.text((50, 240), "This letter confirms the assignment of", fill='black')
    draw.text((50, 270), "the above Employer Identification Number", fill='black')
    draw.text((50, 300), "to the entity listed above.", fill='black')
    
    draw.text((50, 370), "Keep this notice for your records.", fill='black')
    
    return add_ocr_challenges(img)

def create_product_catalog():
    """Generate product/service catalog"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "TECHFLOW SOLUTIONS", fill='#003366')
    draw.text((50, 80), "Service Catalog 2024", fill='#003366')
    
    draw.text((50, 130), "SOFTWARE DEVELOPMENT SERVICES", fill='black')
    draw.text((50, 160), "Custom Web Applications: $150-200/hour", fill='black')
    draw.text((50, 190), "Mobile App Development: $175-225/hour", fill='black')
    draw.text((50, 220), "API Integration: $125-175/hour", fill='black')
    
    draw.text((50, 280), "CONSULTING SERVICES", fill='black')
    draw.text((50, 310), "Digital Strategy: $200-250/hour", fill='black')
    draw.text((50, 340), "Technical Architecture: $225-275/hour", fill='black')
    draw.text((50, 370), "Project Management: $150-200/hour", fill='black')
    
    draw.text((50, 430), "MANAGED SERVICES", fill='black')
    draw.text((50, 460), "Cloud Infrastructure: $2,000-5,000/month", fill='black')
    draw.text((50, 490), "Security Monitoring: $1,500-3,000/month", fill='black')
    
    return add_ocr_challenges(img)

def generate_remaining_docs():
    """Generate remaining critical documents"""
    
    docs = [
        ("professional_license.png", create_professional_license),
        ("operating_agreement.png", create_operating_agreement),
        ("board_resolution.png", create_board_resolution),
        ("workers_compensation.png", create_workers_comp),
        ("ein_letter.png", create_ein_letter),
        ("product_catalog.png", create_product_catalog)
    ]
    
    for filename, generator in docs:
        img = generator()
        filepath = f"c:/work/boarding/prototype/sample_documents/{filename}"
        img.save(filepath)
        print(f"Generated: {filename}")
    
    print(f"\nCreated {len(docs)} more documents")
    print("Total documents now: 20")

if __name__ == "__main__":
    generate_remaining_docs()