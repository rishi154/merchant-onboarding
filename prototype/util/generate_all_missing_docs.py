#!/usr/bin/env python3
"""Generate ALL missing documents in realistic formats (PDF, JPEG, PNG)"""

from PIL import Image, ImageDraw, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import random
import io

def add_ocr_challenges(img):
    """Add realistic OCR challenges"""
    angle = random.uniform(-2, 2)
    img = img.rotate(angle, expand=True, fillcolor='white')
    if random.random() > 0.7:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    return img

def create_dba_certificate():
    """Generate DBA certificate as PDF"""
    filepath = "c:/work/boarding/prototype/sample_documents/dba_certificate.pdf"
    c = canvas.Canvas(filepath, pagesize=letter)
    
    c.drawString(100, 750, "STATE OF CALIFORNIA")
    c.drawString(100, 720, "FICTITIOUS BUSINESS NAME STATEMENT")
    c.drawString(100, 680, "Filing Number: FBN-2023-456789")
    c.drawString(100, 650, "Filed: January 20, 2023")
    c.drawString(100, 600, "Fictitious Business Name: TechFlow Digital Services")
    c.drawString(100, 570, "Principal Business Address:")
    c.drawString(100, 540, "1247 Innovation Drive, Suite 300")
    c.drawString(100, 510, "San Francisco, CA 94107")
    c.drawString(100, 460, "Registrant: TechFlow Solutions LLC")
    c.drawString(100, 430, "This business is conducted by: Limited Liability Company")
    c.drawString(100, 380, "Signed: Sarah Chen, Managing Member")
    
    c.save()
    return filepath

def create_personal_financial_statement():
    """Generate personal financial statement as JPEG"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "PERSONAL FINANCIAL STATEMENT", fill='black')
    draw.text((50, 80), "Sarah Michelle Chen", fill='black')
    draw.text((50, 110), "As of December 31, 2023", fill='black')
    
    draw.text((50, 160), "ASSETS:", fill='black')
    draw.text((50, 190), "Cash & Checking Accounts: $125,000", fill='black')
    draw.text((50, 220), "Savings & CDs: $250,000", fill='black')
    draw.text((50, 250), "Investment Accounts: $450,000", fill='black')
    draw.text((50, 280), "Real Estate (Primary): $850,000", fill='black')
    draw.text((50, 310), "Business Interest: $200,000", fill='black')
    draw.text((50, 340), "Total Assets: $1,875,000", fill='black')
    
    draw.text((50, 390), "LIABILITIES:", fill='black')
    draw.text((50, 420), "Mortgage (Primary): $425,000", fill='black')
    draw.text((50, 450), "Credit Cards: $15,000", fill='black')
    draw.text((50, 480), "Auto Loan: $35,000", fill='black')
    draw.text((50, 510), "Total Liabilities: $475,000", fill='black')
    
    draw.text((50, 560), "NET WORTH: $1,400,000", fill='black')
    
    img = add_ocr_challenges(img)
    filepath = "c:/work/boarding/prototype/sample_documents/personal_financial_statement.jpg"
    img.save(filepath, 'JPEG', quality=85)
    return filepath

def create_pci_compliance():
    """Generate PCI compliance certificate"""
    img = Image.new('RGB', (850, 650), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([50, 50, 800, 600], outline='#003366', width=3)
    draw.text((70, 80), "PCI DSS COMPLIANCE CERTIFICATE", fill='#003366')
    
    draw.text((70, 140), "Entity: TechFlow Solutions LLC", fill='black')
    draw.text((70, 170), "Certificate ID: PCI-2024-789456", fill='black')
    draw.text((70, 200), "Compliance Level: SAQ A", fill='black')
    draw.text((70, 230), "Valid From: January 1, 2024", fill='black')
    draw.text((70, 260), "Valid Until: December 31, 2024", fill='black')
    
    draw.text((70, 320), "This certificate confirms compliance with", fill='black')
    draw.text((70, 350), "Payment Card Industry Data Security Standard", fill='black')
    
    draw.text((70, 420), "Qualified Security Assessor:", fill='black')
    draw.text((70, 450), "SecureAudit Partners LLC", fill='blue')
    
    img = add_ocr_challenges(img)
    filepath = "c:/work/boarding/prototype/sample_documents/pci_compliance.png"
    img.save(filepath)
    return filepath

def create_beneficial_ownership():
    """Generate FinCEN beneficial ownership form as PDF"""
    filepath = "c:/work/boarding/prototype/sample_documents/beneficial_ownership.pdf"
    c = canvas.Canvas(filepath, pagesize=letter)
    
    c.drawString(100, 750, "BENEFICIAL OWNERSHIP CERTIFICATION")
    c.drawString(100, 720, "FinCEN Form 314.81")
    c.drawString(100, 680, "Legal Entity: TechFlow Solutions LLC")
    c.drawString(100, 650, "EIN: 87-1234567")
    
    c.drawString(100, 600, "BENEFICIAL OWNERS (25% or more):")
    c.drawString(120, 570, "1. Sarah Michelle Chen - 60% ownership")
    c.drawString(140, 540, "DOB: 08/22/1985")
    c.drawString(140, 510, "Address: 456 Residential St, San Francisco, CA 94110")
    
    c.drawString(120, 470, "2. Michael Rodriguez - 25% ownership")
    c.drawString(140, 440, "DOB: 03/15/1982")
    c.drawString(140, 410, "Address: 789 Home Ave, San Francisco, CA 94115")
    
    c.drawString(100, 360, "CONTROL PERSON:")
    c.drawString(120, 330, "Sarah Michelle Chen (Managing Member)")
    
    c.drawString(100, 280, "Certification Date: March 1, 2024")
    c.drawString(100, 250, "Certified by: Sarah Chen")
    
    c.save()
    return filepath

def create_background_check_auth():
    """Generate background check authorization"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "BACKGROUND CHECK AUTHORIZATION", fill='black')
    
    draw.text((50, 120), "I, Sarah Michelle Chen, hereby authorize", fill='black')
    draw.text((50, 150), "the investigation of my background for", fill='black')
    draw.text((50, 180), "merchant account approval purposes.", fill='black')
    
    draw.text((50, 230), "Personal Information:", fill='black')
    draw.text((50, 260), "Full Name: Sarah Michelle Chen", fill='black')
    draw.text((50, 290), "DOB: August 22, 1985", fill='black')
    draw.text((50, 320), "SSN: 123-45-6789", fill='black')
    draw.text((50, 350), "Driver's License: D1234567 (CA)", fill='black')
    
    draw.text((50, 400), "Current Address:", fill='black')
    draw.text((50, 430), "456 Residential Street", fill='black')
    draw.text((50, 460), "San Francisco, CA 94110", fill='black')
    
    draw.text((50, 530), "I understand this authorization permits", fill='black')
    draw.text((50, 560), "verification of criminal history, credit", fill='black')
    draw.text((50, 590), "history, and employment verification.", fill='black')
    
    draw.text((50, 660), "Signature: Sarah Chen", fill='blue')
    draw.text((50, 690), "Date: March 1, 2024", fill='black')
    
    img = add_ocr_challenges(img)
    filepath = "c:/work/boarding/prototype/sample_documents/background_check_auth.jpg"
    img.save(filepath, 'JPEG', quality=80)
    return filepath

def create_zoning_permit():
    """Generate zoning permit"""
    img = Image.new('RGB', (700, 900), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "CITY OF SAN FRANCISCO", fill='#003366')
    draw.text((50, 80), "ZONING PERMIT", fill='#003366')
    
    draw.text((50, 140), "Permit Number: ZP-2023-1247", fill='black')
    draw.text((50, 170), "Issue Date: January 10, 2023", fill='black')
    draw.text((50, 200), "Property Address:", fill='black')
    draw.text((50, 230), "1247 Innovation Drive, Suite 300", fill='black')
    draw.text((50, 260), "San Francisco, CA 94107", fill='black')
    
    draw.text((50, 310), "Zoning District: C-3-O (Downtown Office)", fill='black')
    draw.text((50, 340), "Permitted Use: Professional Services", fill='black')
    draw.text((50, 370), "Business Type: Software Development", fill='black')
    
    draw.text((50, 420), "This permit authorizes the operation of", fill='black')
    draw.text((50, 450), "the specified business at the above location", fill='black')
    draw.text((50, 480), "in compliance with zoning regulations.", fill='black')
    
    draw.text((50, 550), "Planning Department", fill='black')
    draw.text((50, 580), "City & County of San Francisco", fill='blue')
    
    img = add_ocr_challenges(img)
    filepath = "c:/work/boarding/prototype/sample_documents/zoning_permit.png"
    img.save(filepath)
    return filepath

def create_property_insurance():
    """Generate property insurance certificate as PDF"""
    filepath = "c:/work/boarding/prototype/sample_documents/property_insurance.pdf"
    c = canvas.Canvas(filepath, pagesize=letter)
    
    c.drawString(100, 750, "COMMERCIAL PROPERTY INSURANCE")
    c.drawString(100, 720, "CERTIFICATE OF INSURANCE")
    
    c.drawString(100, 680, "Insured: TechFlow Solutions LLC")
    c.drawString(100, 650, "Policy Number: CP-2024-789456")
    c.drawString(100, 620, "Effective: 01/01/2024 - 01/01/2025")
    
    c.drawString(100, 580, "Property Address:")
    c.drawString(100, 550, "1247 Innovation Drive, Suite 300")
    c.drawString(100, 520, "San Francisco, CA 94107")
    
    c.drawString(100, 480, "Coverage:")
    c.drawString(120, 450, "Building Coverage: $500,000")
    c.drawString(120, 420, "Business Personal Property: $250,000")
    c.drawString(120, 390, "Business Income: $100,000")
    
    c.drawString(100, 350, "Carrier: Pacific Property Insurance")
    c.drawString(100, 320, "Agent: Commercial Insurance Partners")
    
    c.save()
    return filepath

def create_business_plan():
    """Generate business plan excerpt as PDF"""
    filepath = "c:/work/boarding/prototype/sample_documents/business_plan.pdf"
    c = canvas.Canvas(filepath, pagesize=letter)
    
    c.drawString(100, 750, "BUSINESS PLAN - EXECUTIVE SUMMARY")
    c.drawString(100, 720, "TechFlow Solutions LLC")
    
    c.drawString(100, 680, "COMPANY OVERVIEW:")
    c.drawString(100, 650, "TechFlow Solutions provides custom software development")
    c.drawString(100, 620, "and digital consulting services to mid-market companies.")
    
    c.drawString(100, 580, "SERVICES:")
    c.drawString(120, 550, "- Custom Web Application Development")
    c.drawString(120, 520, "- Mobile App Development (iOS/Android)")
    c.drawString(120, 490, "- API Integration & Development")
    c.drawString(120, 460, "- Digital Strategy Consulting")
    
    c.drawString(100, 420, "TARGET MARKET:")
    c.drawString(100, 390, "Mid-market companies ($10M-$500M revenue)")
    c.drawString(100, 360, "seeking digital transformation solutions.")
    
    c.drawString(100, 320, "FINANCIAL PROJECTIONS (2024):")
    c.drawString(120, 290, "Revenue: $1,500,000")
    c.drawString(120, 260, "Gross Margin: 65%")
    c.drawString(120, 230, "Net Income: $525,000")
    
    c.save()
    return filepath

def create_ofac_screening():
    """Generate OFAC screening results"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    draw.text((50, 50), "OFAC SANCTIONS SCREENING REPORT", fill='black')
    draw.text((50, 80), "Office of Foreign Assets Control", fill='black')
    
    draw.text((50, 130), "Entity Screened: TechFlow Solutions LLC", fill='black')
    draw.text((50, 160), "EIN: 87-1234567", fill='black')
    draw.text((50, 190), "Screening Date: March 1, 2024", fill='black')
    
    draw.text((50, 240), "INDIVIDUALS SCREENED:", fill='black')
    draw.text((50, 270), "1. Sarah Michelle Chen", fill='black')
    draw.text((50, 300), "2. Michael Rodriguez", fill='black')
    draw.text((50, 330), "3. Jennifer Kim", fill='black')
    
    draw.text((50, 380), "SCREENING RESULTS:", fill='green')
    draw.text((50, 410), "NO MATCHES FOUND", fill='green')
    
    draw.text((50, 460), "All individuals and the entity have been", fill='black')
    draw.text((50, 490), "screened against OFAC sanctions lists", fill='black')
    draw.text((50, 520), "with no matches identified.", fill='black')
    
    draw.text((50, 570), "Screening Provider: Compliance Solutions Inc", fill='black')
    draw.text((50, 600), "Report ID: OFAC-2024-789456", fill='black')
    
    img = add_ocr_challenges(img)
    filepath = "c:/work/boarding/prototype/sample_documents/ofac_screening.jpg"
    img.save(filepath, 'JPEG', quality=85)
    return filepath

def generate_all_missing():
    """Generate all remaining documents in mixed formats"""
    
    generators = [
        create_dba_certificate,
        create_personal_financial_statement,
        create_pci_compliance,
        create_beneficial_ownership,
        create_background_check_auth,
        create_zoning_permit,
        create_property_insurance,
        create_business_plan,
        create_ofac_screening
    ]
    
    created_files = []
    for generator in generators:
        filepath = generator()
        filename = filepath.split('/')[-1]
        created_files.append(filename)
        print(f"Generated: {filename}")
    
    print(f"\nCreated {len(created_files)} documents in mixed formats:")
    print("PDF files: 4")
    print("JPEG files: 3") 
    print("PNG files: 2")
    print("\nTotal documents now: 29")

if __name__ == "__main__":
    generate_all_missing()