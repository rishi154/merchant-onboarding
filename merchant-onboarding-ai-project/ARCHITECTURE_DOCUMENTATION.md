# Architecture Documentation: AI Agent Implementation
## Complete Technical Architecture with Code Structure and Fallback Systems

---

## 🏗️ **Agent-by-Agent Architecture Breakdown**

### **1. Market Qualification Agent**
**File**: `agents/market-qualification/src/agent.py`
**Purpose**: Determines if merchant meets basic market criteria
**Processing**: Uses LLM with structured prompts to analyze merchant data

**How it Works**:
1. Receives merchant application data (business name, revenue, country, industry)
2. Uses LangChain LLM with JsonOutputParser for structured analysis
3. Evaluates qualification criteria:
   - Revenue thresholds ($100K+ annual revenue)
   - Geographic eligibility (US, CA, UK supported)
   - Industry restrictions (excludes high-risk sectors)
   - Platform compatibility (Shopify, WooCommerce, custom)

**External APIs**: None (pure LLM analysis)
**Fallback**: Basic rule-based qualification if LLM fails
**Output**: Qualification status, reasoning, market segment classification

---

### **2. Document Processing Agent**
**File**: `agents/document-processing/src/agent_with_tools.py`
**Purpose**: Extracts and validates information from uploaded documents
**Processing**: Uses LangChain tool-calling agent with external document AI services

**How it Works**:
1. **Tool Integration**: Uses LangChain `create_tool_calling_agent` with specialized tools:
   - `DocumentExtractionTool`: Google Document AI integration
   - `BusinessVerificationTool`: Cross-references extracted data
   - `DocumentValidationTool`: Validates document authenticity

2. **External API Connections**:
   - **Google Document AI**: OCR and structured data extraction
   - **Google Vision API**: Document type classification and quality assessment
   - **Business registry APIs**: Verification of extracted business information

3. **Processing Flow**:
   - Agent analyzes uploaded documents using tools
   - Extracts structured data (business name, address, tax ID, etc.)
   - Validates document authenticity and cross-references data
   - Returns confidence scores and extracted fields

**3-Layer Fallback System**:
1. **Primary**: Real Google Document AI + Vision API
2. **Secondary**: Mock document processing with simulated extraction
3. **Tertiary**: Basic document metadata analysis

**Output**: Extracted business data, document validation results, confidence scores

---

### **3. Lead Qualification Agent**
**File**: `agents/lead-qualification/src/agent.py`
**Purpose**: Evaluates lead quality using CRM data and marketing attribution
**Processing**: Uses LangChain tool-calling agent with CRM and attribution tools

**How it Works**:
1. **Tool Integration**: Uses LangChain agent with specialized tools:
   - `ConsolidatedCRMTool`: Multi-CRM data aggregation
   - `AttributionAnalysisTool`: Marketing channel analysis

2. **External API Connections**:
   - **Salesforce API**: Lead data and engagement history
   - **HubSpot API**: Marketing automation and lead scoring
   - **Google Analytics**: Attribution and conversion tracking
   - **Facebook/LinkedIn APIs**: Social media engagement data

3. **Lead Analysis Process**:
   - Retrieves consolidated CRM data across multiple systems
   - Analyzes marketing attribution and channel performance
   - Calculates consolidated lead score using weighted factors
   - Determines conversion probability and priority level

**3-Layer Fallback System**:
1. **Primary**: Real CRM and attribution API integrations
2. **Secondary**: Mock CRM data with simulated lead scores
3. **Tertiary**: Basic qualification using application data only

**Output**: Lead qualification status, consolidated score, conversion probability, marketing insights

---

### **4. Application Assistant Agent**
**File**: `agents/application-assistant/src/agent.py`
**Purpose**: Validates application completeness and provides assistance
**Processing**: Direct data validation with intelligent suggestions

**How it Works**:
1. **Field Validation**: Checks required fields completeness
2. **Data Quality Assessment**: Calculates completeness score
3. **Smart Suggestions**: Provides context-aware recommendations:
   - State requirements for US businesses
   - Employee count for high-revenue businesses
   - Industry-specific field requirements

4. **Assistance Triggers**: Determines when human assistance is needed

**External APIs**: None (direct data analysis)
**Fallback**: Built-in validation rules
**Output**: Completeness score, missing fields, suggestions, assistance requirements

---

### **5. Data Validation Agent**
**File**: `agents/data-validation/src/agent.py`
**Purpose**: Verifies merchant data accuracy using external sources
**Processing**: Uses LangChain tool-calling agent with validation tools

**How it Works**:
1. **Tool Integration**: Uses LangChain agent with validation tools:
   - `BusinessRegistryTool`: Secretary of State verification
   - `TaxIdValidationTool`: IRS Tax ID verification
   - `AddressVerificationTool`: USPS address validation

2. **External API Connections**:
   - **Secretary of State APIs**: Business registration verification
   - **IRS Tax ID Verification**: Federal tax ID validation
   - **USPS Address Validation**: Address standardization and verification
   - **D&B Business Registry**: Additional business verification

3. **Validation Process**:
   - Extracts business data from application and documents
   - Verifies business registration with state authorities
   - Validates Tax ID format and IRS verification
   - Confirms business address with postal services

**3-Layer Fallback System**:
1. **Primary**: Real government and postal API integrations
2. **Secondary**: Direct tool usage with mock responses
3. **Tertiary**: Basic format validation and consistency checks

**Output**: Validation score, field-by-field verification results, manual review flags

---

### **6. Risk Assessment Agent**
**File**: `agents/risk-assessment/src/agent.py`
**Purpose**: Evaluates merchant risk profile using multiple data sources
**Processing**: Uses LangChain tool-calling agent with risk analysis tools

**How it Works**:
1. **Tool Integration**: Uses LangChain agent with risk assessment tools:
   - `CreditCheckTool`: Experian credit bureau integration
   - `FraudScreeningTool`: Identity verification and fraud detection
   - `IndustryRiskTool`: Industry-specific risk analysis

2. **External API Connections**:
   - **Experian Credit API**: Business credit scores and history
   - **Jumio Identity Verification**: KYC and identity validation
   - **OFAC Sanctions Screening**: Compliance and sanctions checking
   - **Industry risk databases**: Sector-specific risk metrics

3. **Risk Calculation**:
   - Combines multiple risk factors with weighted scoring
   - Uses ML-based risk models for pattern recognition
   - Generates risk category (LOW/MEDIUM/HIGH/CRITICAL)

**3-Layer Fallback System**:
1. **Primary**: Real credit bureau + identity verification APIs
2. **Secondary**: Mock risk assessment with simulated scores
3. **Tertiary**: Basic rule-based risk evaluation

**Output**: Risk score, risk category, contributing factors, manual review flags

---

### **7. Decision Making Agent**
**File**: `agents/decision-making/src/agent.py`
**Purpose**: Makes final approval/decline decisions based on all agent results
**Processing**: Uses LLM analysis with comprehensive decision framework

**How it Works**:
1. **Data Aggregation**: Collects results from all previous agents
2. **Decision Matrix**: Uses weighted scoring across multiple factors:
   - Market qualification results
   - Document processing confidence
   - Risk assessment scores
   - Compliance verification status
   - Data validation results

3. **LLM Decision Analysis**: Uses advanced prompting for nuanced decisions
4. **Credit Limit Calculation**: Determines appropriate credit limits based on risk
5. **Approval Conditions**: Sets specific terms and conditions

**External APIs**: None (uses aggregated data from other agents)
**Fallback**: Rule-based decision matrix if LLM fails
**Output**: Final decision, credit limit, approval conditions, reasoning

---

### **8. Exception Routing Agent**
**File**: `agents/exception-routing/src/agent.py`
**Purpose**: Analyzes exceptions and determines optimal routing strategy
**Processing**: Uses LLM analysis for intelligent exception handling

**How it Works**:
1. **Exception Analysis**: Identifies exceptions from all previous agents:
   - Market qualification failures
   - Document review requirements
   - High-risk assessments
   - Data validation discrepancies

2. **Routing Strategy**: Uses LLM to determine:
   - Appropriate specialist queue assignment
   - Priority level (CRITICAL/HIGH/MEDIUM/LOW)
   - Estimated resolution time
   - Required specialist skills
   - Escalation conditions

3. **Workload Distribution**: Considers specialist availability and expertise

**External APIs**: None (internal routing logic)
**Fallback**: Rule-based routing if LLM fails
**Output**: Routing queue, priority level, exception types, resolution estimates

---

### **9. Communication Agent**
**File**: `agents/communication/src/agent.py`
**Purpose**: Manages merchant communications and notifications
**Processing**: Uses LLM for personalized communication strategy

**How it Works**:
1. **Communication Strategy**: Uses LLM to determine:
   - Message type (confirmation, status update, approval, decline)
   - Communication channels (email, SMS, phone, portal)
   - Message content and tone
   - Follow-up schedule
   - Personalization based on merchant profile

2. **Status-Based Messaging**: Generates appropriate communications based on application status
3. **Multi-Channel Coordination**: Manages communications across different channels

**External APIs**: 
- **Email services** (SendGrid, AWS SES)
- **SMS services** (Twilio)
- **Push notification services**

**Fallback**: Template-based communications if LLM fails
**Output**: Messages to send, communication strategy, follow-up schedule

---

### **10. Multi-Jurisdiction Compliance Agent**
**File**: `agents/multi-jurisdiction-compliance/src/agent.py`
**Purpose**: Ensures regulatory compliance across jurisdictions
**Processing**: Uses jurisdiction-specific compliance rules and external regulatory APIs

**How it Works**:
1. **Jurisdiction Detection**: Automatically detects merchant jurisdiction (US/UK/EU/CA)
2. **Compliance Framework Selection**: Applies appropriate regulatory requirements
3. **External API Integrations**:
   - **OFAC (US)**: Sanctions and prohibited persons screening
   - **FCA (UK)**: Financial Conduct Authority compliance
   - **GDPR (EU)**: Data protection compliance verification
   - **FINTRAC (Canada)**: Anti-money laundering compliance

4. **Compliance Checks**:
   - Performs jurisdiction-specific regulatory verification
   - Validates required licenses and registrations
   - Screens against sanctions and prohibited lists
   - Verifies data protection compliance

**3-Layer Fallback System**:
1. **Primary**: Real regulatory API integrations
2. **Secondary**: Mock compliance checks with simulated results
3. **Tertiary**: Basic compliance rule validation

**Output**: Compliance status, jurisdiction-specific results, violation flags

---

### **11. Account Provisioning Agent**
**File**: `agents/account-provisioning/src/agent.py`
**Purpose**: Creates merchant accounts and provisions services
**Processing**: Direct integration with payment processors and internal systems

**How it Works**:
1. **Account Creation**: Creates merchant account in GlobalPayments system
2. **Service Provisioning**: Sets up multiple services:
   - Payment processing configuration
   - API credentials generation
   - Database access provisioning
   - Dashboard access setup

3. **External API Integrations**:
   - **GlobalPayments API**: Primary payment processor integration
   - **Database provisioning APIs**: Internal system access
   - **Identity provider APIs**: Authentication setup

4. **Configuration Management**: Sets processing fees, credit limits, settlement schedules

**3-Layer Fallback System**:
1. **Primary**: Real GlobalPayments integration
2. **Secondary**: Mock provisioning with simulated accounts
3. **Tertiary**: Basic account creation for development

**Output**: Account creation status, merchant ID, service provisioning results

---

### **12. Monitoring Agent**
**File**: `agents/monitoring/src/agent.py`
**Purpose**: Tracks workflow performance and generates metrics
**Processing**: Direct metrics calculation and performance analysis

**How it Works**:
1. **Metrics Collection**: Calculates processing metrics:
   - Total processing time across all agents
   - Number of agents executed
   - Exception counts and types
   - Automation rate achievement
   - SLA compliance

2. **Performance Analysis**: Evaluates workflow efficiency
3. **Alert Generation**: Identifies performance issues:
   - SLA breaches (>300 seconds)
   - High exception counts (>3)
   - Quality score degradation

4. **Real-time Monitoring**: Provides live performance dashboard data

**External APIs**: None (internal metrics)
**Fallback**: Built-in performance calculations
**Output**: Performance metrics, alerts, efficiency scores

---

### **13. Optimization Agent**
**File**: `agents/optimization/src/agent.py`
**Purpose**: Analyzes workflow performance and identifies improvements
**Processing**: Uses LLM for comprehensive optimization analysis

**How it Works**:
1. **Performance Analysis**: Uses LLM to analyze:
   - Processing time bottlenecks
   - Exception patterns and root causes
   - Agent performance and accuracy metrics
   - Resource utilization patterns

2. **Optimization Recommendations**: Generates actionable improvements:
   - Immediate performance enhancements
   - Process automation opportunities
   - Model tuning suggestions
   - Infrastructure optimizations
   - SLA and threshold adjustments

3. **Predictive Insights**: Identifies future improvement opportunities

**External APIs**: None (internal analysis)
**Fallback**: Rule-based optimization analysis if LLM fails
**Output**: Bottleneck identification, optimization recommendations, performance scores

---

### **14. Onboarding Support Agent**
**File**: `agents/onboarding-support/src/agent.py`
**Purpose**: Creates personalized onboarding plans for approved merchants
**Processing**: Uses LLM for customized onboarding strategy

**How it Works**:
1. **Merchant Profile Analysis**: Uses LLM to analyze:
   - Technical sophistication level
   - Integration complexity requirements
   - Business size and transaction volume expectations
   - Industry-specific onboarding needs
   - Risk profile considerations

2. **Onboarding Plan Generation**: Creates customized plans:
   - Prioritized onboarding checklist
   - Support level assignment (basic/standard/premium/enterprise)
   - Follow-up schedule based on merchant needs
   - Integration timeline and milestones
   - Training recommendations
   - Success metrics and checkpoints

3. **Support Level Assignment**: Determines appropriate support tier based on merchant profile

**External APIs**: None (internal onboarding logic)
**Fallback**: Template-based onboarding plans if LLM fails
**Output**: Onboarding checklist, support level, follow-up schedule, training plan

---

## 🔧 **Tool Calling Architecture**

### **Agents with Tool Calling (4 out of 14)**

#### **1. Compliance Verification Agent** ✅
- **Tools:** OFAC Sanctions, PEP Screening, AML Risk Assessment, KYC Verification
- **LLM Decision:** Chooses compliance checks based on merchant profile and risk factors
- **External Services:** Mock regulatory databases (OFAC, PEP lists, AML systems)

#### **2. Data Validation Agent** ✅
- **Tools:** Business Registry Lookup, Tax ID Validation, Address Verification
- **LLM Decision:** Selects validation checks based on data quality and completeness
- **External Services:** Mock government databases (Secretary of State, IRS, USPS)

#### **3. Document Processing Agent** ✅
- **Tools:** OCR Processing, Document Classification, Fraud Detection
- **LLM Decision:** Determines document analysis workflow based on document types
- **External Services:** Google Document AI (real) + mock fraud detection

#### **4. Risk Assessment Agent** ✅
- **Tools:** Financial Risk Assessment, Industry Risk Assessment, Credit Risk Scoring
- **LLM Decision:** Combines multiple risk dimensions for comprehensive analysis
- **External Services:** Mock financial and credit scoring systems

### **Tool Categories**

#### **Compliance Tools (4 tools)**
1. **OFACSanctionsTool** - Sanctions list screening
2. **PEPScreeningTool** - Politically exposed persons check
3. **AMLRiskAssessmentTool** - Anti-money laundering analysis
4. **KYCVerificationTool** - Identity verification

#### **Validation Tools (3 tools)**
1. **BusinessRegistryTool** - Business registration verification
2. **TaxIdValidationTool** - Tax ID/EIN validation
3. **AddressVerificationTool** - Address standardization

#### **Document Tools (3 tools)**
1. **OCRProcessingTool** - Text extraction via Google Document AI
2. **DocumentClassificationTool** - Document type identification
3. **FraudDetectionTool** - Fraud indicator detection

#### **Risk Tools (3 tools)**
1. **FinancialRiskTool** - Financial stability assessment
2. **IndustryRiskTool** - Sector-specific risk analysis
3. **CreditRiskTool** - Credit scoring and limit determination

### **How Tool Calling Works**

```python
# 1. Agent receives merchant application
# 2. LLM analyzes requirements
# 3. LLM selects appropriate tools
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)

# 4. Agent executes tools dynamically
result = await agent_executor.ainvoke(input_data)

# 5. LLM processes tool results and makes decisions
```

---

## 🏗️ **System Architecture Overview**

### **Agent Processing Types**

#### **LLM Reasoning Only (6 agents)**
- **Market Qualification** - Market analysis and eligibility
- **Decision Making** - Final approval/decline decisions
- **Exception Routing** - Intelligent routing and prioritization
- **Communication** - Personalized message generation
- **Optimization** - Performance analysis and recommendations
- **Onboarding Support** - Personalized onboarding plans

#### **Tool-Calling Agents (4 agents)**
- **Document Processing** - Uses document analysis tools
- **Data Validation** - Uses validation and verification tools
- **Risk Assessment** - Uses risk analysis tools
- **Compliance Verification** - Uses compliance checking tools

#### **Rule-Based Logic (2 agents)**
- **Application Assistant** - Field validation and completeness
- **Monitoring** - Performance metrics and alerting

#### **API Integration (2 agents)**
- **Lead Qualification** - CRM and marketing platform integration
- **Account Provisioning** - Payment processor and system integration

---

## 🔄 **Fallback System Architecture**

### **3-Layer Fallback Strategy**

#### **Layer 1: Primary Processing**
- Real external API integrations
- Full LLM reasoning capabilities
- Complete tool calling functionality
- Real-time data processing

#### **Layer 2: Secondary Processing**
- Mock API responses with realistic data
- Simplified LLM processing
- Direct tool usage without agent orchestration
- Cached data processing

#### **Layer 3: Tertiary Processing**
- Rule-based processing
- Static data responses
- Basic validation logic
- Minimal functionality to maintain workflow

### **Fallback Triggers**
- API timeout or failure
- LLM service unavailability
- Tool execution errors
- Data quality issues
- System performance degradation

---

## 📊 **Integration Architecture**

### **External Service Integration**
- **Credit Bureaus**: Experian, Equifax APIs
- **Identity Verification**: Jumio, Onfido APIs
- **Government Databases**: OFAC, Secretary of State, IRS APIs
- **Payment Processing**: GlobalPayments API
- **Communication**: SendGrid, Twilio APIs
- **Document Processing**: Google Document AI, Vision API

### **Internal System Integration**
- **Workflow Engine**: Agent orchestration and routing
- **Data Pipeline**: Real-time data processing and storage
- **Monitoring System**: Performance tracking and alerting
- **Configuration Management**: Dynamic parameter adjustment
- **Audit System**: Compliance tracking and reporting

### **Cloud Platform Integration**
- **Google Cloud Platform**: Primary AI/ML services
- **Vertex AI**: LLM hosting and model management
- **BigQuery**: Data warehousing and analytics
- **Cloud Functions**: Serverless agent execution
- **Cloud Storage**: Document and data storage

---

## 🔒 **Security Architecture**

### **Data Protection**
- **Encryption**: End-to-end encryption for all data
- **Access Control**: Role-based access control (RBAC)
- **Audit Logging**: Comprehensive activity tracking
- **Data Masking**: PII protection in logs and monitoring

### **API Security**
- **Authentication**: OAuth 2.0 and API key management
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive data sanitization
- **Error Handling**: Secure error responses

### **Compliance**
- **PCI DSS**: Payment card industry compliance
- **SOC 2**: Security and availability controls
- **GDPR**: Data protection regulation compliance
- **SOX**: Financial reporting controls

This architecture provides a robust, scalable, and secure foundation for AI-powered merchant onboarding with comprehensive fallback mechanisms and enterprise-grade reliability.