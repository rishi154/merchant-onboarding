# Merchant Onboarding Process Diagrams

## Overview Flowchart

```mermaid
flowchart TD
    A[Merchant Interest] --> B[Lead Qualification]
    B --> C{Qualified?}
    C -->|Yes| D[Application Initiation]
    C -->|No| E[Lead Nurturing]
    
    D --> F[Dynamic Data Collection]
    F --> G[Document Upload & Processing]
    G --> H[Identity Verification & KYC/AML]
    H --> I[Data Validation & Enrichment]
    I --> J[Risk Assessment & Scoring]
    J --> K[Underwriting & Decision]
    
    K --> L{Decision}
    L -->|Approve| M[Account Setup & Provisioning]
    L -->|Decline| N[Decision Communication]
    L -->|Hold| O[Exception Handling]
    
    M --> P[Onboarding Completion]
    P --> Q[Post-Onboarding Monitoring]
    Q --> R[Portfolio Management]
    
    O --> S{Resolved?}
    S -->|Yes| K
    S -->|No| N
    
    N --> T[Appeal Process]
    T --> U{Resubmit?}
    U -->|Yes| D
    U -->|No| V[End Process]
    
    R --> W[Continuous Improvement]
    W --> X[Model Updates]
    X --> B
```

## Detailed Phase Flow Diagram

```mermaid
flowchart LR
    subgraph "Phase 1: Pre-Application"
        A1[Lead Generation] --> A2[Lead Scoring]
        A2 --> A3[Qualification]
        A3 --> A4[Initial Engagement]
    end
    
    subgraph "Phase 2: Application"
        B1[Portal Access] --> B2[Adaptive Questionnaire]
        B2 --> B3[Data Collection]
        B3 --> B4[Progress Tracking]
    end
    
    subgraph "Phase 3: Documents"
        C1[Document Upload] --> C2[OCR Processing]
        C2 --> C3[Classification]
        C3 --> C4[Data Extraction]
    end
    
    subgraph "Phase 4: Verification"
        D1[Identity Verification] --> D2[KYC Checks]
        D2 --> D3[AML Screening]
        D3 --> D4[Compliance Validation]
    end
    
    subgraph "Phase 5: Validation"
        E1[Document Authentication] --> E2[Data Enrichment]
        E2 --> E3[Cross-Reference]
        E3 --> E4[GenAI Analysis]
    end
    
    subgraph "Phase 6: Risk Assessment"
        F1[Risk Modeling] --> F2[ML Analytics]
        F2 --> F3[Risk Scoring]
        F3 --> F4[Risk Classification]
    end
    
    subgraph "Phase 7: Underwriting"
        G1[Application Routing] --> G2[Underwriter Review]
        G2 --> G3[Decision Matrix]
        G3 --> G4[Final Decision]
    end
    
    A4 --> B1
    B4 --> C1
    C4 --> D1
    D4 --> E1
    E4 --> F1
    F4 --> G1
```

## Swimlane Diagram - Roles and Responsibilities

```mermaid
flowchart TD
    subgraph "Merchant"
        M1[Submit Application]
        M2[Upload Documents]
        M3[Respond to Clarifications]
        M4[Accept Terms]
    end
    
    subgraph "AI/ML Systems"
        AI1[Lead Scoring]
        AI2[Document Processing]
        AI3[Risk Assessment]
        AI4[Decision Support]
    end
    
    subgraph "Compliance Team"
        C1[KYC/AML Review]
        C2[Regulatory Validation]
        C3[Exception Handling]
    end
    
    subgraph "Underwriters"
        U1[Application Review]
        U2[Risk Analysis]
        U3[Decision Making]
        U4[Approval/Decline]
    end
    
    subgraph "Operations"
        O1[Account Setup]
        O2[System Configuration]
        O3[Go-Live Support]
    end
    
    M1 --> AI1
    AI1 --> M2
    M2 --> AI2
    AI2 --> C1
    C1 --> AI3
    AI3 --> U1
    U1 --> AI4
    AI4 --> U2
    U2 --> U3
    U3 --> U4
    U4 --> O1
    O1 --> O2
    O2 --> M4
    M4 --> O3
```

## Risk Assessment Decision Tree

```mermaid
flowchart TD
    A[Application Received] --> B{Complete Application?}
    B -->|No| C[Request Missing Info]
    B -->|Yes| D[Initial Risk Scoring]
    
    D --> E{Risk Score}
    E -->|Low Risk<br/>Score < 300| F[Auto-Approve Path]
    E -->|Medium Risk<br/>300-700| G[Manual Review Required]
    E -->|High Risk<br/>Score > 700| H[Enhanced Due Diligence]
    
    F --> I{KYC/AML Clear?}
    I -->|Yes| J[Auto-Approve]
    I -->|No| K[Manual Review]
    
    G --> L[Underwriter Assignment]
    L --> M[Detailed Review]
    M --> N{Underwriter Decision}
    N -->|Approve| O[Conditional Approval]
    N -->|Decline| P[Decline with Reason]
    N -->|Hold| Q[Request Additional Info]
    
    H --> R[Senior Underwriter]
    R --> S[Enhanced Verification]
    S --> T{Final Assessment}
    T -->|Approve with Restrictions| U[High-Risk Approval]
    T -->|Decline| V[Decline - High Risk]
    
    C --> W{Info Received?}
    W -->|Yes| D
    W -->|No - Timeout| X[Application Expired]
    
    Q --> Y{Info Provided?}
    Y -->|Yes| M
    Y -->|No| P
```

## Technology Architecture Diagram

```mermaid
flowchart TB
    subgraph "Presentation Layer"
        UI1[Merchant Portal]
        UI2[Underwriter Dashboard]
        UI3[Admin Console]
        UI4[Mobile App]
    end
    
    subgraph "API Gateway"
        API[API Management Layer]
    end
    
    subgraph "Application Services"
        AS1[Application Service]
        AS2[Document Service]
        AS3[Risk Service]
        AS4[Decision Service]
        AS5[Notification Service]
    end
    
    subgraph "AI/ML Services"
        ML1[GenAI Engine]
        ML2[OCR Service]
        ML3[Risk Models]
        ML4[Fraud Detection]
        ML5[NLP Service]
    end
    
    subgraph "External Integrations"
        EXT1[KYC/AML Providers]
        EXT2[Credit Bureaus]
        EXT3[Government DBs]
        EXT4[Banking APIs]
        EXT5[Sanctions Lists]
    end
    
    subgraph "Data Layer"
        DB1[(Application DB)]
        DB2[(Document Store)]
        DB3[(Analytics DB)]
        DB4[(Audit Logs)]
    end
    
    UI1 --> API
    UI2 --> API
    UI3 --> API
    UI4 --> API
    
    API --> AS1
    API --> AS2
    API --> AS3
    API --> AS4
    API --> AS5
    
    AS1 --> ML1
    AS2 --> ML2
    AS3 --> ML3
    AS3 --> ML4
    AS5 --> ML5
    
    AS1 --> EXT1
    AS3 --> EXT2
    AS3 --> EXT3
    AS1 --> EXT4
    AS3 --> EXT5
    
    AS1 --> DB1
    AS2 --> DB2
    AS3 --> DB3
    AS4 --> DB4
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph "Input Sources"
        I1[Merchant Application]
        I2[Uploaded Documents]
        I3[External Data Sources]
        I4[Historical Data]
    end
    
    subgraph "Processing Pipeline"
        P1[Data Ingestion]
        P2[Data Validation]
        P3[Data Enrichment]
        P4[Risk Processing]
        P5[Decision Engine]
    end
    
    subgraph "AI/ML Processing"
        AI1[Document OCR]
        AI2[Data Extraction]
        AI3[Risk Modeling]
        AI4[Fraud Detection]
        AI5[Decision Support]
    end
    
    subgraph "Outputs"
        O1[Risk Scores]
        O2[Compliance Status]
        O3[Decision Recommendation]
        O4[Audit Trail]
        O5[Notifications]
    end
    
    I1 --> P1
    I2 --> AI1
    I3 --> P3
    I4 --> AI3
    
    P1 --> P2
    AI1 --> AI2
    P2 --> P3
    AI2 --> P3
    P3 --> P4
    P4 --> AI3
    AI3 --> AI4
    P4 --> P5
    AI4 --> AI5
    AI5 --> P5
    
    P5 --> O1
    P5 --> O2
    P5 --> O3
    P2 --> O4
    P5 --> O5
```

## Compliance and Audit Flow

```mermaid
flowchart TD
    A[Application Start] --> B[Audit Log Creation]
    B --> C[KYC/AML Initiation]
    
    C --> D{Identity Verified?}
    D -->|Yes| E[Log: ID Verified]
    D -->|No| F[Log: ID Failed]
    F --> G[Exception Process]
    
    E --> H[Sanctions Screening]
    H --> I{Sanctions Clear?}
    I -->|Yes| J[Log: Sanctions Clear]
    I -->|No| K[Log: Sanctions Hit]
    K --> L[Immediate Decline]
    
    J --> M[Document Verification]
    M --> N{Documents Valid?}
    N -->|Yes| O[Log: Docs Verified]
    N -->|No| P[Log: Doc Issues]
    P --> Q[Request Clarification]
    
    O --> R[Risk Assessment]
    R --> S[Log: Risk Score]
    S --> T[Underwriter Assignment]
    T --> U[Log: Assignment]
    
    U --> V[Decision Made]
    V --> W[Log: Decision]
    W --> X{Approved?}
    X -->|Yes| Y[Log: Account Created]
    X -->|No| Z[Log: Decline Reason]
    
    Y --> AA[Compliance Report]
    Z --> AA
    L --> AA
    G --> AA
    Q --> AA
    
    AA --> BB[Regulatory Filing]
    BB --> CC[Audit Trail Complete]
```

## Exception Handling Workflow

```mermaid
flowchart TD
    A[Exception Detected] --> B{Exception Type}
    
    B -->|Missing Documents| C[Document Request]
    B -->|Data Discrepancy| D[Clarification Request]
    B -->|System Error| E[Technical Resolution]
    B -->|Regulatory Hold| F[Compliance Review]
    
    C --> G[Automated Notification]
    D --> H[GenAI Clarification]
    E --> I[IT Support Ticket]
    F --> J[Compliance Team Assignment]
    
    G --> K{Response Received?}
    H --> L{Clarification Provided?}
    I --> M{Issue Resolved?}
    J --> N{Compliance Cleared?}
    
    K -->|Yes| O[Resume Processing]
    K -->|No - Timeout| P[Application Suspension]
    
    L -->|Yes| Q[Data Update]
    L -->|No| R[Escalation]
    
    M -->|Yes| S[Resume Processing]
    M -->|No| T[Escalate to Senior IT]
    
    N -->|Yes| U[Resume Processing]
    N -->|No| V[Regulatory Decline]
    
    O --> W[Continue Workflow]
    Q --> W
    S --> W
    U --> W
    
    P --> X[Merchant Notification]
    R --> Y[Senior Review]
    T --> Z[System Maintenance]
    V --> AA[Compliance Documentation]
```

## Performance Monitoring Dashboard Layout

```mermaid
flowchart LR
    subgraph "Real-Time Metrics"
        RT1[Applications in Progress]
        RT2[Processing Times]
        RT3[System Performance]
        RT4[Exception Rates]
    end
    
    subgraph "Quality Metrics"
        Q1[Approval Accuracy]
        Q2[False Positive Rate]
        Q3[Document Quality]
        Q4[Customer Satisfaction]
    end
    
    subgraph "Compliance Metrics"
        C1[KYC/AML Success Rate]
        C2[Regulatory Adherence]
        C3[Audit Findings]
        C4[Reporting Timeliness]
    end
    
    subgraph "Business Metrics"
        B1[Conversion Rates]
        B2[Revenue Impact]
        B3[Cost per Application]
        B4[Market Share]
    end
    
    subgraph "Alerts & Actions"
        A1[SLA Breaches]
        A2[System Alerts]
        A3[Compliance Issues]
        A4[Performance Degradation]
    end
    
    RT1 --> A1
    RT2 --> A1
    Q2 --> A2
    C2 --> A3
    RT3 --> A4
```

## Integration Architecture

```mermaid
flowchart TB
    subgraph "Core Platform"
        CP[Merchant Onboarding Platform]
    end
    
    subgraph "Identity Verification"
        IV1[Jumio]
        IV2[Onfido]
        IV3[Trulioo]
    end
    
    subgraph "KYC/AML Providers"
        KYC1[LexisNexis]
        KYC2[Thomson Reuters]
        KYC3[Refinitiv]
    end
    
    subgraph "Credit & Financial"
        CF1[Experian]
        CF2[Dun & Bradstreet]
        CF3[Equifax]
    end
    
    subgraph "Government & Regulatory"
        GR1[IRS Database]
        GR2[Secretary of State]
        GR3[OFAC Lists]
    end
    
    subgraph "Banking & Payments"
        BP1[Plaid]
        BP2[Yodlee]
        BP3[ACH Networks]
    end
    
    subgraph "Document Processing"
        DP1[AWS Textract]
        DP2[Google Vision API]
        DP3[Azure Cognitive Services]
    end
    
    CP --> IV1
    CP --> IV2
    CP --> IV3
    CP --> KYC1
    CP --> KYC2
    CP --> KYC3
    CP --> CF1
    CP --> CF2
    CP --> CF3
    CP --> GR1
    CP --> GR2
    CP --> GR3
    CP --> BP1
    CP --> BP2
    CP --> BP3
    CP --> DP1
    CP --> DP2
    CP --> DP3
```

## Timeline and Milestones

```mermaid
gantt
    title Merchant Onboarding Process Timeline
    dateFormat X
    axisFormat %s
    
    section Application Phase
    Lead Qualification     :0, 1
    Application Submission :1, 2
    Document Upload       :2, 4
    
    section Verification Phase
    Identity Verification :4, 6
    KYC/AML Checks      :6, 8
    Document Processing  :4, 8
    
    section Assessment Phase
    Data Validation     :8, 10
    Risk Assessment     :10, 12
    Underwriting Review :12, 15
    
    section Decision Phase
    Decision Making     :15, 16
    Communication      :16, 17
    
    section Setup Phase
    Account Provisioning :17, 19
    Integration Setup   :19, 21
    Go-Live Support    :21, 22
    
    section Monitoring
    Initial Monitoring  :22, 52
    Portfolio Management :52, 365
```