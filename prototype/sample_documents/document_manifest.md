# Sample Document Manifest for Merchant Onboarding Prototype

## Generated Documents Overview

### 1. Business License (`business_license.txt`)
- **Type**: Government-issued business authorization
- **Key Data Points**: License number, business name, EIN, address, activities
- **Use Case**: Business verification, compliance validation
- **Extraction Targets**: Business name, license number, expiration date, business type

### 2. Bank Statement (`bank_statement.txt`)
- **Type**: Financial institution account summary
- **Key Data Points**: Account balance, transaction history, average daily balance
- **Use Case**: Financial stability assessment, cash flow analysis
- **Extraction Targets**: Account number, balance, transaction volume, banking relationship

### 3. Articles of Incorporation (`articles_of_incorporation.txt`)
- **Type**: Legal business formation document
- **Key Data Points**: Entity name, formation date, registered agent, ownership structure
- **Use Case**: Legal entity verification, ownership validation
- **Extraction Targets**: Entity name, formation date, state of incorporation, registered agent

### 4. Tax Return Summary (`tax_return_summary.txt`)
- **Type**: IRS Form 1065 partnership return summary
- **Key Data Points**: Revenue, expenses, profit, partner information
- **Use Case**: Financial performance assessment, tax compliance verification
- **Extraction Targets**: Gross receipts, net income, business code, partner details

### 5. Processing Statements (`processing_statements.txt`)
- **Type**: Existing payment processor account statements
- **Key Data Points**: Transaction volume, fees, chargeback rates, processing history
- **Use Case**: Processing history analysis, risk assessment, competitive analysis
- **Extraction Targets**: Monthly volume, chargeback rate, account age, processor type

## Document Characteristics for AI Training

### Realistic Elements Included:
- ✅ **Proper formatting** with headers, sections, official language
- ✅ **Consistent data** across documents (same business entity)
- ✅ **Realistic numbers** based on actual industry ranges
- ✅ **Official terminology** and legal language
- ✅ **Cross-document validation** points (EIN, business name, addresses)

### AI Processing Challenges Simulated:
- 📄 **Mixed formatting** (different document layouts)
- 🔢 **Number extraction** from various contexts
- 📅 **Date parsing** in different formats
- 🏢 **Entity recognition** (business names, addresses, people)
- 💰 **Financial data** extraction and validation

### Prototype Testing Scenarios:
1. **Document Classification**: Identify document type automatically
2. **Data Extraction**: Pull key fields from each document type
3. **Cross-Validation**: Verify consistency across documents
4. **Risk Assessment**: Calculate risk scores from extracted data
5. **Compliance Check**: Validate required information presence

## Usage for Prototype Development

These documents provide realistic test data for:
- OCR accuracy testing
- Document classification models
- Data extraction algorithms
- Validation rule development
- Risk assessment model training

Each document contains intentional variations and realistic imperfections that mirror real-world merchant onboarding scenarios.