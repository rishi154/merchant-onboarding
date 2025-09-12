#!/usr/bin/env python3
"""
Generate realistic merchant onboarding documents as images
Simulates real-world document submission challenges
"""

from PIL import Image, ImageDraw, ImageFont
import io
import base64

def create_drivers_license():
    """Generate realistic driver's license image with OCR challenges"""
    # Create image with slight angle and lighting issues
    img = Image.new('RGB', (800, 500), color='#E8F4FD')
    draw = ImageDraw.Draw(img)
    
    # Add realistic elements
    draw.rectangle([50, 50, 750, 450], outline='#003366', width=3)
    draw.text((70, 80), "STATE OF CALIFORNIA", fill='#003366', font_size=24)
    draw.text((70, 120), "DRIVER LICENSE", fill='#003366', font_size=32)
    
    # Personal info with realistic formatting
    draw.text((70, 180), "LIC# D1234567", fill='black')
    draw.text((70, 210), "EXP: 03/15/2028", fill='black')
    draw.text((70, 240), "DOB: 08/22/1985", fill='black')
    
    draw.text((70, 280), "CHEN, SARAH MICHELLE", fill='black', font_size=18)
    draw.text((70, 310), "1247 INNOVATION DR STE 300", fill='black')
    draw.text((70, 340), "SAN FRANCISCO, CA 94107", fill='black')
    
    # Add photo placeholder
    draw.rectangle([500, 180, 650, 330], fill='#CCCCCC')
    draw.text((520, 240), "PHOTO", fill='black')
    
    return img

def create_bank_statement_scan():
    """Generate realistic scanned bank statement with typical scan artifacts"""
    img = Image.new('RGB', (850, 1100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Bank header
    draw.text((50, 50), "FIRST NATIONAL BANK", fill='#003366', font_size=20)
    draw.text((50, 80), "BUSINESS CHECKING STATEMENT", fill='black', font_size=16)
    
    # Account info
    draw.text((50, 130), "Account: TechFlow Solutions LLC", fill='black')
    draw.text((50, 160), "Account Number: ****-****-4567", fill='black')
    draw.text((50, 190), "Statement Period: 02/01/2024 - 02/29/2024", fill='black')
    
    # Balance info
    draw.text((50, 240), "Beginning Balance: $45,230.18", fill='black')
    draw.text((50, 270), "Ending Balance: $83,339.93", fill='black')
    
    # Transaction table header
    draw.text((50, 320), "Date        Description                 Amount", fill='black')
    draw.line([(50, 340), (750, 340)], fill='black', width=1)
    
    # Sample transactions
    transactions = [
        "02/02  ACH DEPOSIT CLIENT PMT      +$15,500.00",
        "02/05  WIRE TRANSFER PROJECT       +$25,000.00", 
        "02/07  CHECK #1001 OFFICE RENT     -$4,200.00",
        "02/10  ACH DEPOSIT SUBSCRIPTION    +$8,750.00",
        "02/12  PAYROLL EMPLOYEES           -$28,500.00"
    ]
    
    y_pos = 360
    for transaction in transactions:
        draw.text((50, y_pos), transaction, fill='black')
        y_pos += 30
    
    return img

def create_business_license_photo():
    """Generate business license as phone photo with realistic issues"""
    img = Image.new('RGB', (600, 800), color='#F5F5F5')
    draw = ImageDraw.Draw(img)
    
    # Document background (slightly angled)
    draw.rectangle([80, 100, 520, 700], fill='white', outline='black')
    
    # Official header
    draw.text((100, 130), "STATE OF CALIFORNIA", fill='#003366', font_size=16)
    draw.text((100, 160), "DEPARTMENT OF CONSUMER AFFAIRS", fill='#003366')
    draw.text((100, 190), "BUSINESS LICENSE", fill='#003366', font_size=18)
    
    # License details
    draw.text((100, 240), "License No: BL-2024-789456", fill='black')
    draw.text((100, 270), "Issue Date: March 15, 2024", fill='black')
    draw.text((100, 300), "Expiration: March 15, 2025", fill='black')
    
    draw.text((100, 350), "Business Name:", fill='black')
    draw.text((100, 380), "TechFlow Solutions LLC", fill='black', font_size=14)
    
    draw.text((100, 430), "Business Address:", fill='black')
    draw.text((100, 460), "1247 Innovation Drive, Suite 300", fill='black')
    draw.text((100, 490), "San Francisco, CA 94107", fill='black')
    
    draw.text((100, 540), "Federal EIN: 87-1234567", fill='black')
    
    # Official seal placeholder
    draw.ellipse([350, 550, 450, 650], outline='#003366', width=2)
    draw.text((375, 590), "OFFICIAL", fill='#003366')
    draw.text((385, 610), "SEAL", fill='#003366')
    
    return img

def save_sample_images():
    """Save all sample document images"""
    
    # Create drivers license
    dl_img = create_drivers_license()
    dl_img.save('c:/work/boarding/prototype/sample_documents/drivers_license.png')
    
    # Create bank statement
    bank_img = create_bank_statement_scan()
    bank_img.save('c:/work/boarding/prototype/sample_documents/bank_statement.png')
    
    # Create business license
    license_img = create_business_license_photo()
    license_img.save('c:/work/boarding/prototype/sample_documents/business_license.png')
    
    print("✅ Generated realistic document images:")
    print("   - drivers_license.png (ID verification)")
    print("   - bank_statement.png (financial document)")
    print("   - business_license.png (business verification)")

if __name__ == "__main__":
    save_sample_images()