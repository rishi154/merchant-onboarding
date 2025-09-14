#!/usr/bin/env python3
"""Generate all missing merchant onboarding documents"""

from PIL import Image, ImageDraw, ImageFilter
import random

def add_ocr_challenges(img):
    """Add realistic OCR challenges"""
    angle = random.uniform(-1.5, 1.5)
    img = img.rotate(angle, expand=True, fillcolor='white')
    if random.random() > 0.8:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
    return img

def create_social_security_card():
    """Generate SSN card image"""
    img = Image.new('RGB', (540, 340), color='#E6F3FF')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([20, 20, 520, 320], outline='#003366', width=2)
    draw.text((40, 50), "SOCIAL SECURITY", fill='#003366')
    draw.text((40, 80), "123-45-6789", fill='black')
    draw.text((40, 120), "SARAH MICHELLE CHEN", fill='black')
    draw.text((40, 280), "THIS NUMBER HAS BEEN ESTABLISHED FOR", fill='black')
    draw.text((40, 300), "SARAH MICHELLE CHEN", fill='black')
    
    return add_ocr_challenges(img)

def create_lease_agreement():
    """Generate lease agreement"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "COMMERCIAL LEASE AGREEMENT", fill='black')
    draw.text((50, 100), "Landlord: Innovation Properties LLC", fill='black')
    draw.text((50, 130), "Tenant: TechFlow Solutions LLC", fill='black')
    draw.text((50, 180), "PREMISES:", fill='black')
    draw.text((50, 210), "1247 Innovation Drive, Suite 300", fill='black')
    draw.text((50, 240), "San Francisco, CA 94107", fill='black')
    draw.text((50, 290), "TERM: 36 months", fill='black')
    draw.text((50, 320), "RENT: $4,200.00 per month", fill='black')
    draw.text((50, 350), "SECURITY DEPOSIT: $8,400.00", fill='black')
    draw.text((50, 400), "Lease Date: January 1, 2023", fill='black')
    draw.text((50, 450), "Landlord Signature: John Smith", fill='blue')
    draw.text((50, 480), "Tenant Signature: Sarah Chen", fill='blue')
    
    return add_ocr_challenges(img)

def create_utility_bill():
    """Generate utility bill"""
    img = Image.new('RGB', (650, 850), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([30, 30, 620, 100], fill='#FF6600')
    draw.text((50, 50), "PG&E - Pacific Gas & Electric", fill='white')
    draw.text((50, 70), "Business Energy Services", fill='white')
    
    draw.text((50, 130), "Account: TechFlow Solutions LLC", fill='black')
    draw.text((50, 160), "Service Address:", fill='black')
    draw.text((50, 190), "1247 Innovation Drive, Suite 300", fill='black')
    draw.text((50, 220), "San Francisco, CA 94107", fill='black')
    
    draw.text((50, 270), "Billing Period: Feb 1 - Feb 29, 2024", fill='black')
    draw.text((50, 300), "Account Number: 1234567890", fill='black')
    
    draw.text((50, 350), "CHARGES:", fill='black')
    draw.text((50, 380), "Electricity Usage: $456.78", fill='black')
    draw.text((50, 410), "Gas Usage: $123.45", fill='black')
    draw.text((50, 440), "Total Amount Due: $580.23", fill='black')
    draw.text((50, 470), "Due Date: March 25, 2024", fill='black')
    
    return add_ocr_challenges(img)

def create_financial_statement():
    """Generate P&L statement"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "PROFIT & LOSS STATEMENT", fill='black')
    draw.text((50, 80), "TechFlow Solutions LLC", fill='black')
    draw.text((50, 110), "Year Ended December 31, 2023", fill='black')
    
    draw.text((50, 160), "REVENUE:", fill='black')
    draw.text((50, 190), "Software Development", fill='black')
    draw.text((400, 190), "$890,000", fill='black')
    draw.text((50, 220), "Consulting Services", fill='black')
    draw.text((400, 220), "$342,550", fill='black')
    draw.text((50, 250), "Total Revenue", fill='black')
    draw.text((400, 250), "$1,232,550", fill='black')
    
    draw.text((50, 300), "EXPENSES:", fill='black')
    draw.text((50, 330), "Salaries & Benefits", fill='black')
    draw.text((400, 330), "$485,000", fill='black')
    draw.text((50, 360), "Office Rent", fill='black')
    draw.text((400, 360), "$50,400", fill='black')
    draw.text((50, 390), "Equipment & Software", fill='black')
    draw.text((400, 390), "$125,800", fill='black')
    draw.text((50, 420), "Total Expenses", fill='black')
    draw.text((400, 420), "$804,900", fill='black')
    
    draw.text((50, 470), "NET INCOME", fill='black')
    draw.text((400, 470), "$427,650", fill='black')
    
    return add_ocr_challenges(img)

def create_cpa_letter():
    """Generate CPA verification letter"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "MARTINEZ & ASSOCIATES CPA", fill='black')
    draw.text((50, 80), "Certified Public Accountants", fill='black')
    draw.text((50, 110), "123 Financial Plaza, San Francisco, CA 94105", fill='black')
    
    draw.text((50, 180), "March 15, 2024", fill='black')
    
    draw.text((50, 230), "To Whom It May Concern:", fill='black')
    
    draw.text((50, 280), "This letter serves to verify that we have prepared", fill='black')
    draw.text((50, 310), "the tax returns and financial statements for", fill='black')
    draw.text((50, 340), "TechFlow Solutions LLC (EIN: 87-1234567)", fill='black')
    draw.text((50, 370), "for the years 2022 and 2023.", fill='black')
    
    draw.text((50, 420), "The financial information provided is accurate", fill='black')
    draw.text((50, 450), "and complete to the best of our knowledge.", fill='black')
    
    draw.text((50, 520), "Sincerely,", fill='black')
    draw.text((50, 570), "Maria Martinez, CPA", fill='blue')
    draw.text((50, 600), "License #: CPA-12345", fill='black')
    
    return add_ocr_challenges(img)

def create_website_screenshots():
    """Generate website screenshot"""
    img = Image.new('RGB', (1200, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Browser frame
    draw.rectangle([0, 0, 1200, 60], fill='#E0E0E0')
    draw.text((20, 20), "https://www.techflowsolutions.com", fill='black')
    
    # Header
    draw.rectangle([0, 60, 1200, 150], fill='#003366')
    draw.text((50, 90), "TechFlow Solutions", fill='white')
    draw.text((50, 120), "Digital Innovation Partners", fill='white')
    
    # Navigation
    draw.text((800, 100), "Home  Services  About  Contact", fill='white')
    
    # Content
    draw.text((50, 200), "Our Services:", fill='black')
    draw.text((50, 240), "• Custom Software Development", fill='black')
    draw.text((50, 270), "• E-commerce Platform Management", fill='black')
    draw.text((50, 300), "• Digital Marketing Consulting", fill='black')
    draw.text((50, 330), "• Cloud Infrastructure Solutions", fill='black')
    
    draw.text((50, 400), "Contact Information:", fill='black')
    draw.text((50, 430), "Phone: (415) 555-0123", fill='black')
    draw.text((50, 460), "Email: contact@techflowsolutions.com", fill='black')
    
    return add_ocr_challenges(img)

def generate_missing_documents():
    """Generate all missing document types"""
    
    docs = [
        ("social_security_card.png", create_social_security_card),
        ("lease_agreement.png", create_lease_agreement),
        ("utility_bill.png", create_utility_bill),
        ("financial_statement.png", create_financial_statement),
        ("cpa_letter.png", create_cpa_letter),
        ("website_screenshot.png", create_website_screenshots)
    ]
    
    for filename, generator in docs:
        img = generator()
        filepath = f"c:/work/boarding/prototype/sample_documents/{filename}"
        img.save(filepath)
        print(f"Generated: {filename}")
    
    print(f"\nCreated {len(docs)} additional documents")
    print("Total documents now: 14 (8 existing + 6 new)")

if __name__ == "__main__":
    generate_missing_documents()