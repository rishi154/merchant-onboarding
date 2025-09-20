"""Mock document content for testing document processing agents"""

BUSINESS_LICENSE_CONTENT = {
    "extracted_text": """
CALIFORNIA SECRETARY OF STATE
BUSINESS LICENSE

License Number: BL-2024-001234
Business Name: TechFlow Solutions LLC
Business Type: Limited Liability Company
Issue Date: January 1, 2024
Expiration Date: December 31, 2024
Status: ACTIVE

Registered Address:
123 Innovation Drive
San Francisco, CA 94105

Principal Officer: John Smith
Title: Managing Member

This license authorizes the above named business to operate
in the State of California subject to all applicable laws.
""",
    "extracted_fields": {
        "license_number": "BL-2024-001234",
        "business_name": "TechFlow Solutions LLC",
        "business_type": "Limited Liability Company",
        "issue_date": "2024-01-01",
        "expiration_date": "2024-12-31",
        "status": "ACTIVE",
        "state": "California",
        "principal_officer": "John Smith"
    },
    "confidence": 0.95
}

BANK_STATEMENT_CONTENT = {
    "extracted_text": """
FIRST NATIONAL BANK
BUSINESS ACCOUNT STATEMENT

Account Number: ****1234
Statement Period: October 1 - December 31, 2023
Business Name: TechFlow Solutions LLC

ACCOUNT SUMMARY
Beginning Balance: $45,230.00
Total Deposits: $125,450.00
Total Withdrawals: $85,680.00
Ending Balance: $85,000.00

DEPOSIT DETAILS
10/15/2023  ACH DEPOSIT - CLIENT PAYMENT    $25,000.00
11/20/2023  WIRE TRANSFER - INVESTMENT      $50,000.00
12/10/2023  ACH DEPOSIT - RECURRING REV     $35,450.00
12/28/2023  CHECK DEPOSIT                   $15,000.00

WITHDRAWAL DETAILS
10/05/2023  PAYROLL                        $12,500.00
11/01/2023  RENT PAYMENT                    $8,500.00
12/15/2023  VENDOR PAYMENTS                 $45,680.00
12/30/2023  TAX PAYMENT                     $19,000.00
""",
    "extracted_fields": {
        "account_number": "****1234",
        "statement_period": "October 1 - December 31, 2023",
        "business_name": "TechFlow Solutions LLC",
        "beginning_balance": 45230.00,
        "total_deposits": 125450.00,
        "total_withdrawals": 85680.00,
        "ending_balance": 85000.00,
        "bank_name": "First National Bank"
    },
    "confidence": 0.92
}

TAX_RETURN_CONTENT = {
    "extracted_text": """
FORM 1120S - U.S. INCOME TAX RETURN
FOR AN S CORPORATION

Tax Year: 2023
EIN: 12-3456789
Business Name: TechFlow Solutions LLC

INCOME
Gross receipts or sales: $850,000
Total income: $850,000

DEDUCTIONS
Salaries and wages: $245,000
Rent: $102,000
Other deductions: $178,000
Total deductions: $525,000

TAXABLE INCOME: $325,000
TAX LIABILITY: $85,000

Prepared by: Smith & Associates CPA
Date: March 15, 2024
""",
    "extracted_fields": {
        "form_type": "1120S",
        "tax_year": "2023",
        "ein": "12-3456789",
        "business_name": "TechFlow Solutions LLC",
        "gross_receipts": 850000,
        "total_income": 850000,
        "total_deductions": 525000,
        "taxable_income": 325000,
        "tax_liability": 85000,
        "preparer": "Smith & Associates CPA"
    },
    "confidence": 0.88
}

FRAUDULENT_DOCUMENT_CONTENT = {
    "extracted_text": """
CALIFORNIA SECRETARY OF STATE
BUSINESS LICENSE

License Number: BL-2024-FAKE1
Business Name: Suspicious Business Inc
Business Type: Corporation
Issue Date: January 1, 2024
Expiration Date: December 31, 2024
Status: ACTIVE

[ALTERED TEXT DETECTED]
[FONT INCONSISTENCY DETECTED]
""",
    "extracted_fields": {
        "license_number": "BL-2024-FAKE1",
        "business_name": "Suspicious Business Inc",
        "fraud_indicators": ["altered_text", "font_inconsistency"]
    },
    "confidence": 0.45
}

DOCUMENT_SAMPLES = {
    "business_license": BUSINESS_LICENSE_CONTENT,
    "bank_statement": BANK_STATEMENT_CONTENT,
    "tax_return": TAX_RETURN_CONTENT,
    "fraudulent": FRAUDULENT_DOCUMENT_CONTENT
}