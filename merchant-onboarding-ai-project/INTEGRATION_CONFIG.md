# Integration Configuration Guide

## Mock vs Real Service Configuration

All external integrations can be configured to use either **real APIs** or **mock implementations** via environment variables.

### Configuration Variables

Set these in your `.env` file:

```bash
# Integration Mock/Real Configuration (true=mock, false=real)
MOCK_CREDIT_BUREAUS=true          # Experian credit checks
MOCK_KYC_PROVIDERS=true           # Jumio identity verification  
MOCK_BANKING_APIS=true            # Plaid bank account verification
MOCK_GOVERNMENT_DATABASES=true    # OFAC sanctions, business registry
MOCK_GLOBALPAYMENTS=true          # GlobalPayments account creation
```

## Available Integrations

### 1. Credit Bureaus
- **Real**: Experian Business Credit API
- **Mock**: Simulated credit scoring based on revenue/business age
- **Configuration**: `MOCK_CREDIT_BUREAUS=false` + Experian API credentials

### 2. KYC Providers  
- **Real**: Jumio Identity Verification API
- **Mock**: Simulated identity verification with 90% success rate
- **Configuration**: `MOCK_KYC_PROVIDERS=false` + Jumio API credentials

### 3. Banking APIs
- **Real**: Plaid Bank Account Verification API
- **Mock**: Simulated bank account verification
- **Configuration**: `MOCK_BANKING_APIS=false` + Plaid API credentials

### 4. Government Databases
- **Real**: OFAC Sanctions List API, OpenCorporates Business Registry
- **Mock**: Simulated sanctions checks and business lookups
- **Configuration**: `MOCK_GOVERNMENT_DATABASES=false` + API access

### 5. Payment Processing
- **Real**: GlobalPayments Merchant Account Creation API
- **Mock**: Simulated merchant account provisioning
- **Configuration**: `MOCK_GLOBALPAYMENTS=false` + GlobalPayments credentials

## How to Switch to Real Services

### Step 1: Set Environment Variables
```bash
# Disable mocking for services you want to use
MOCK_CREDIT_BUREAUS=false
MOCK_KYC_PROVIDERS=false
# etc.
```

### Step 2: Add Real API Credentials
```bash
# Experian
EXPERIAN_CLIENT_ID=your-client-id
EXPERIAN_CLIENT_SECRET=your-client-secret
EXPERIAN_USERNAME=your-username
EXPERIAN_PASSWORD=your-password

# Jumio
JUMIO_API_TOKEN=your-api-token
JUMIO_API_SECRET=your-api-secret

# Plaid
PLAID_CLIENT_ID=your-client-id
PLAID_SECRET=your-secret
PLAID_ENV=sandbox  # or production

# GlobalPayments
GLOBALPAYMENTS_APP_ID=your-app-id
GLOBALPAYMENTS_APP_KEY=your-app-key
GLOBALPAYMENTS_ACCOUNT_ID=your-account-id
```

### Step 3: Test Configuration
Run the workflow - it will automatically use real APIs where configured and fall back to mocks on errors.

## Fallback Behavior

- If real API calls fail, the system automatically falls back to mock implementations
- Fallback responses include `"fallback": true` and `"error": "reason"` fields
- This ensures the workflow continues even if external services are unavailable

## Integration Status Indicators

Check the agent responses for integration status:
- `"mock_data": true` - Using mock implementation
- `"fallback": true` - Failed real API, used fallback
- `"experian_response": {...}` - Successfully used real Experian API
- `"jumio_response": {...}` - Successfully used real Jumio API
- etc.

## Development vs Production

### Development (Default)
```bash
# All mocks enabled
MOCK_CREDIT_BUREAUS=true
MOCK_KYC_PROVIDERS=true
MOCK_BANKING_APIS=true
MOCK_GOVERNMENT_DATABASES=true
MOCK_GLOBALPAYMENTS=true
```

### Production
```bash
# All real services enabled
MOCK_CREDIT_BUREAUS=false
MOCK_KYC_PROVIDERS=false
MOCK_BANKING_APIS=false
MOCK_GOVERNMENT_DATABASES=false
MOCK_GLOBALPAYMENTS=false

# Plus all real API credentials
```

### Hybrid (Recommended for Testing)
```bash
# Use real Google services, mock external APIs
MOCK_CREDIT_BUREAUS=true
MOCK_KYC_PROVIDERS=true
MOCK_BANKING_APIS=true
MOCK_GOVERNMENT_DATABASES=false  # Use real OFAC checks
MOCK_GLOBALPAYMENTS=true
```

This gives you maximum flexibility to test different integration scenarios while maintaining workflow functionality.