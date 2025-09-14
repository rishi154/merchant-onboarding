#!/usr/bin/env python3
"""
RAG Document Download and Organization Tool
Downloads regulatory documents for merchant onboarding AI knowledge base
"""

import requests
import os
from pathlib import Path
import time

# Document URLs and metadata
DOCUMENTS = {
    "pci_compliance": [
        {
            "name": "pci_dss_requirements_v4.pdf",
            "url": "https://www.pcisecuritystandards.org/documents/PCI-DSS-v4_0.pdf",
            "description": "PCI DSS Requirements v4.0"
        },
        {
            "name": "saq_guide.pdf", 
            "url": "https://www.pcisecuritystandards.org/documents/SAQ-InstrGuidelines-v4_0.pdf",
            "description": "Self-Assessment Questionnaire Guide"
        },
        {
            "name": "pci_glossary.pdf",
            "url": "https://www.pcisecuritystandards.org/documents/PCI_DSS_Glossary_v3-2.pdf",
            "description": "PCI DSS Glossary"
        }
    ],
    "kyc_aml": [
        {
            "name": "cdd_rule.pdf",
            "url": "https://www.fincen.gov/sites/default/files/2016-09/CDD_Rule_FAQ_FINAL_508.pdf",
            "description": "Customer Due Diligence Rule FAQ"
        },
        {
            "name": "beneficial_ownership.pdf",
            "url": "https://www.fincen.gov/sites/default/files/2018-04/FinCEN_Guidance_CDD_FAQ_FINAL_508_2.pdf",
            "description": "Beneficial Ownership Requirements"
        }
    ],
    "business_licensing": [
        {
            "name": "california_business_guide.pdf",
            "url": "https://www.sos.ca.gov/business-programs/business-entities/forms",
            "description": "California Business Entity Guide"
        }
    ],
    "payment_standards": [
        {
            "name": "visa_merchant_standards.pdf", 
            "url": "https://usa.visa.com/dam/VCOM/download/merchants/visa-merchant-data-security-guidelines.pdf",
            "description": "Visa Merchant Data Security Guidelines"
        }
    ]
}

def download_file(url, filepath, description):
    """Download file with error handling and progress"""
    try:
        print(f"Downloading: {description}")
        print(f"URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Downloaded: {filepath}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {description}: {e}")
        return False
    except Exception as e:
        print(f"Error downloading {description}: {e}")
        return False

def create_document_manifest():
    """Create manifest of all documents to download"""
    manifest_path = "rag_documents/document_manifest.md"
    
    with open(manifest_path, 'w') as f:
        f.write("# RAG Document Manifest\n")
        f.write("## Regulatory Documents for Merchant Onboarding AI\n\n")
        
        for category, docs in DOCUMENTS.items():
            f.write(f"### {category.replace('_', ' ').title()}\n")
            for doc in docs:
                f.write(f"- **{doc['name']}**: {doc['description']}\n")
                f.write(f"  - URL: {doc['url']}\n")
                f.write(f"  - Status: [ ] Downloaded\n\n")
    
    print(f"Created manifest: {manifest_path}")

def download_all_documents():
    """Download all documents in organized structure"""
    
    base_path = Path("rag_documents")
    success_count = 0
    total_count = 0
    
    for category, docs in DOCUMENTS.items():
        category_path = base_path / category
        category_path.mkdir(exist_ok=True)
        
        print(f"\nProcessing category: {category}")
        
        for doc in docs:
            total_count += 1
            filepath = category_path / doc['name']
            
            if filepath.exists():
                print(f"File exists, skipping: {filepath}")
                success_count += 1
                continue
            
            if download_file(doc['url'], filepath, doc['description']):
                success_count += 1
            
            # Rate limiting - be respectful to servers
            time.sleep(2)
    
    print(f"\nDownload Summary:")
    print(f"   Total documents: {total_count}")
    print(f"   Successfully downloaded: {success_count}")
    print(f"   Failed: {total_count - success_count}")

def create_manual_download_list():
    """Create list for manual downloads when automation fails"""
    
    manual_list_path = "rag_documents/manual_download_list.txt"
    
    with open(manual_list_path, 'w') as f:
        f.write("MANUAL DOWNLOAD LIST\n")
        f.write("===================\n\n")
        f.write("If automated download fails, manually download these documents:\n\n")
        
        for category, docs in DOCUMENTS.items():
            f.write(f"{category.upper()}:\n")
            for doc in docs:
                f.write(f"  {doc['name']}\n")
                f.write(f"  {doc['url']}\n")
                f.write(f"  Save to: rag_documents/{category}/{doc['name']}\n\n")
    
    print(f"Created manual download list: {manual_list_path}")

if __name__ == "__main__":
    print("RAG Document Download Tool")
    print("=" * 50)
    
    # Create directory structure
    for category in DOCUMENTS.keys():
        Path(f"rag_documents/{category}").mkdir(parents=True, exist_ok=True)
    
    # Create documentation
    create_document_manifest()
    create_manual_download_list()
    
    # Attempt automated downloads
    print("\nStarting automated downloads...")
    download_all_documents()
    
    print("\nProcess complete!")
    print("Check document_manifest.md for download status")
    print("Use manual_download_list.txt if automation failed")