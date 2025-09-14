#!/usr/bin/env python3
"""Generate realistic merchant onboarding documents with OCR challenges"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os

def add_ocr_challenges(img):
    """Add realistic OCR challenges to document images"""
    # Slight rotation (1-3 degrees)
    angle = random.uniform(-2, 2)
    img = img.rotate(angle, expand=True, fillcolor='white')
    
    # Add slight blur
    if random.random() > 0.7:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Adjust brightness/contrast
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.8, 1.2))
    
    return img

def create_drivers_license():
    """Generate realistic driver's license with phone photo artifacts"""
    img = Image.new('RGB', (800, 500), color='#E8F4FD')
    draw = ImageDraw.Draw(img)
    
    # CA DMV styling
    draw.rectangle([40, 40, 760, 460], outline='#003366', width=4)
    draw.text((60, 70), "STATE OF CALIFORNIA", fill='#003366')
    draw.text((60, 100), "DRIVER LICENSE", fill='#003366')
    
    # License info
    draw.text((60, 150), "DL D1234567", fill='black')
    draw.text((60, 180), "EXP 03/15/2028", fill='black')
    draw.text((60, 210), "DOB 08/22/1985", fill='black')
    
    # Name and address
    draw.text((60, 260), "CHEN, SARAH MICHELLE", fill='black')
    draw.text((60, 290), "1247 INNOVATION DR STE 300", fill='black')
    draw.text((60, 320), "SAN FRANCISCO, CA 94107", fill='black')
    
    # Photo area
    draw.rectangle([500, 150, 650, 300], fill='#CCCCCC', outline='black')
    draw.text((540, 215), "PHOTO", fill='black')
    
    # Signature area
    draw.text((60, 380), "Signature: Sarah Chen", fill='blue')
    
    return add_ocr_challenges(img)

def create_bank_statement():
    """Generate bank statement scan with typical artifacts"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Bank header
    draw.rectangle([30, 30, 820, 100], fill='#003366')
    draw.text((50, 50), "FIRST NATIONAL BANK", fill='white')
    draw.text((50, 70), "BUSINESS CHECKING STATEMENT", fill='white')
    
    # Account details
    draw.text((50, 130), "TechFlow Solutions LLC", fill='black')
    draw.text((50, 160), "Account: ****-****-4567", fill='black')
    draw.text((50, 190), "Period: 02/01/2024 - 02/29/2024", fill='black')
    
    # Balance summary
    draw.rectangle([50, 220, 800, 300], outline='black')
    draw.text((70, 240), "Beginning Balance:", fill='black')
    draw.text((300, 240), "$45,230.18", fill='black')
    draw.text((70, 260), "Total Deposits:", fill='black')
    draw.text((300, 260), "$127,450.00", fill='black')
    draw.text((70, 280), "Ending Balance:", fill='black')
    draw.text((300, 280), "$83,339.93", fill='black')
    
    # Transaction header
    draw.text((50, 330), "Date", fill='black')
    draw.text((150, 330), "Description", fill='black')
    draw.text((500, 330), "Amount", fill='black')
    draw.line([(50, 350), (800, 350)], fill='black')
    
    # Transactions
    transactions = [
        ("02/02", "ACH DEPOSIT - CLIENT PAYMENT", "+$15,500.00"),
        ("02/05", "WIRE TRANSFER - PROJECT FEE", "+$25,000.00"),
        ("02/07", "CHECK #1001 - OFFICE RENT", "-$4,200.00"),
        ("02/10", "ACH DEPOSIT - SUBSCRIPTION", "+$8,750.00"),
        ("02/12", "PAYROLL - EMPLOYEES", "-$28,500.00"),
        ("02/15", "ACH DEPOSIT - CLIENT PAYMENT", "+$22,300.00"),
        ("02/20", "WIRE TRANSFER - PROJECT", "+$35,900.00"),
        ("02/25", "ACH DEPOSIT - CONSULTING", "+$20,000.00")
    ]
    
    y = 370
    for date, desc, amount in transactions:
        draw.text((50, y), date, fill='black')
        draw.text((150, y), desc, fill='black')
        color = 'green' if amount.startswith('+') else 'red'
        draw.text((500, y), amount, fill=color)
        y += 25
    
    return add_ocr_challenges(img)

def create_business_license():
    """Generate business license as poor quality photo"""
    img = Image.new('RGB', (600, 800), color='#F0F0F0')
    draw = ImageDraw.Draw(img)
    
    # Document with shadow
    draw.rectangle([70, 90, 530, 710], fill='white', outline='black', width=2)
    
    # State seal area
    draw.ellipse([400, 120, 500, 220], outline='#003366', width=3)
    draw.text((420, 160), "STATE", fill='#003366')
    draw.text((430, 180), "SEAL", fill='#003366')
    
    # Header
    draw.text((90, 130), "STATE OF CALIFORNIA", fill='#003366')
    draw.text((90, 160), "DEPARTMENT OF CONSUMER AFFAIRS", fill='#003366')
    draw.text((90, 190), "BUSINESS LICENSE", fill='#003366')
    
    # License details
    draw.text((90, 250), "License Number: BL-2024-789456", fill='black')
    draw.text((90, 280), "Issue Date: March 15, 2024", fill='black')
    draw.text((90, 310), "Expiration Date: March 15, 2025", fill='black')
    
    # Business info
    draw.text((90, 360), "BUSINESS INFORMATION:", fill='black')
    draw.text((90, 390), "Business Name: TechFlow Solutions LLC", fill='black')
    draw.text((90, 420), "DBA: TechFlow Digital Services", fill='black')
    draw.text((90, 450), "Business Type: Limited Liability Company", fill='black')
    draw.text((90, 480), "Federal EIN: 87-1234567", fill='black')
    
    # Address
    draw.text((90, 530), "BUSINESS ADDRESS:", fill='black')
    draw.text((90, 560), "1247 Innovation Drive, Suite 300", fill='black')
    draw.text((90, 590), "San Francisco, CA 94107", fill='black')
    
    # Signature
    draw.text((90, 640), "Authorized Representative:", fill='black')
    draw.text((90, 670), "Sarah Chen, Managing Member", fill='blue')
    
    return add_ocr_challenges(img)

def create_tax_return():
    """Generate tax return with handwritten annotations"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Form header
    draw.text((50, 50), "Form 1065", fill='black')
    draw.text((200, 50), "U.S. Return of Partnership Income", fill='black')
    draw.text((600, 50), "2023", fill='black')
    
    # Business info
    draw.rectangle([50, 100, 800, 200], outline='black')
    draw.text((70, 120), "Name: TechFlow Solutions LLC", fill='black')
    draw.text((70, 140), "EIN: 87-1234567", fill='black')
    draw.text((70, 160), "Address: 1247 Innovation Drive, Suite 300", fill='black')
    draw.text((70, 180), "San Francisco, CA 94107", fill='black')
    
    # Income section
    draw.text((50, 230), "INCOME", fill='black')
    draw.line([(50, 250), (200, 250)], fill='black')
    
    draw.text((70, 270), "1a Gross receipts or sales", fill='black')
    draw.text((500, 270), "1,245,000", fill='black')
    draw.text((70, 300), "1c Net sales (1a minus 1b)", fill='black')
    draw.text((500, 300), "1,232,550", fill='black')
    
    # Deductions
    draw.text((50, 350), "DEDUCTIONS", fill='black')
    draw.line([(50, 370), (200, 370)], fill='black')
    
    draw.text((70, 390), "9 Salaries and wages", fill='black')
    draw.text((500, 390), "485,000", fill='black')
    draw.text((70, 420), "11 Rent", fill='black')
    draw.text((500, 420), "50,400", fill='black')
    draw.text((70, 450), "20 Total deductions", fill='black')
    draw.text((500, 450), "804,900", fill='black')
    
    # Net income
    draw.text((70, 500), "22 Ordinary business income", fill='black')
    draw.text((500, 500), "427,650", fill='black')
    
    # Handwritten note (in red)
    draw.text((600, 520), "Reviewed - MC", fill='red')
    
    # Preparer info
    draw.text((50, 600), "Paid Preparer: Martinez & Associates CPA", fill='black')
    draw.text((50, 630), "Preparer: Maria Martinez, CPA", fill='black')
    draw.text((50, 660), "Date: 03/10/2024", fill='black')
    
    return add_ocr_challenges(img)

def create_insurance_certificate():
    """Generate insurance certificate with watermark"""
    img = Image.new('RGB', (850, 650), color='white')
    draw = ImageDraw.Draw(img)
    
    # Watermark
    draw.text((300, 300), "SAMPLE", fill='#E0E0E0')
    
    # Header
    draw.text((50, 50), "CERTIFICATE OF LIABILITY INSURANCE", fill='black')
    draw.text((600, 50), "Date: 03/01/2024", fill='black')
    
    # Insurer info
    draw.rectangle([50, 100, 800, 180], outline='black')
    draw.text((70, 120), "INSURER: Pacific Insurance Company", fill='black')
    draw.text((70, 140), "NAIC #: 12345", fill='black')
    draw.text((70, 160), "Rating: A+ (Superior)", fill='black')
    
    # Insured info
    draw.rectangle([50, 200, 800, 280], outline='black')
    draw.text((70, 220), "INSURED: TechFlow Solutions LLC", fill='black')
    draw.text((70, 240), "1247 Innovation Drive, Suite 300", fill='black')
    draw.text((70, 260), "San Francisco, CA 94107", fill='black')
    
    # Coverage details
    draw.text((50, 310), "TYPE OF INSURANCE", fill='black')
    draw.text((300, 310), "POLICY NUMBER", fill='black')
    draw.text((500, 310), "LIMITS", fill='black')
    draw.line([(50, 330), (800, 330)], fill='black')
    
    draw.text((50, 350), "General Liability", fill='black')
    draw.text((300, 350), "GL-2024-789456", fill='black')
    draw.text((500, 350), "$2,000,000", fill='black')
    
    draw.text((50, 380), "Professional Liability", fill='black')
    draw.text((300, 380), "PL-2024-789457", fill='black')
    draw.text((500, 380), "$1,000,000", fill='black')
    
    # Effective dates
    draw.text((50, 430), "Policy Period: 03/01/2024 to 03/01/2025", fill='black')
    
    # Signature
    draw.text((50, 500), "Authorized Representative:", fill='black')
    draw.text((50, 530), "John Smith, Agent", fill='blue')
    
    return add_ocr_challenges(img)

def generate_all_documents():
    """Generate all realistic document images"""
    
    docs = [
        ("drivers_license.png", create_drivers_license),
        ("bank_statement.png", create_bank_statement),
        ("business_license.png", create_business_license),
        ("tax_return.png", create_tax_return),
        ("insurance_certificate.png", create_insurance_certificate)
    ]
    
    for filename, generator in docs:
        img = generator()
        filepath = f"c:/work/boarding/prototype/sample_documents/{filename}"
        img.save(filepath)
        print(f"Generated: {filename}")
    
    print(f"\nCreated {len(docs)} realistic documents with OCR challenges:")
    print("   - Slight rotations and blur")
    print("   - Brightness/contrast variations") 
    print("   - Realistic formatting and layouts")
    print("   - Mixed text types (printed, handwritten)")

if __name__ == "__main__":
    generate_all_documents()