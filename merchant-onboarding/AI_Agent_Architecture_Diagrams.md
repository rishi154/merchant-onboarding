# AI Agent Architecture Diagrams
## Actual Implementation Architecture

## Multi-Workflow Agent System Overview (As Implemented)

```mermaid
flowchart TD
    A[Document Upload] --> B[Document Processing Agent]
    B --> C[Risk Assessment Agent]
    C --> D{Risk-Based Workflow Routing}
    
    D -->|LOW Risk<br/>Score 0-300| E[Express Workflow<br/>4 Agents - 20 min]
    D -->|MEDIUM Risk<br/>Score 301-700| F[Standard Workflow<br/>8 Agents - 90 min]
    D -->|HIGH Risk<br/>Score 701-1000| G[Comprehensive Workflow<br/>14 Agents - 180 min]
    
    E --> H{Human Review?}
    F --> H
    G --> H
    
    H -->|Required| I[Pause for Review]
    H -->|Not Required| J[Account Setup]
    
    I --> K[Human Reviewer]
    K -->|Approve| J
    K -->|Decline| L[Application Declined]
    
    style D fill:#c8e6c9
    style E fill:#c8e6c9
    style F fill:#fff9c4
    style G fill:#ffcdd2
```

## 14 AI Agents - Actual Implementation

```mermaid
graph TB
    subgraph "Core Agents (All Workflows)"
        A1[Document Processing Agent]
        A2[Risk Assessment Agent]
        A3[Decision Making Agent]
        A4[Account Provisioning Agent]
    end
    
    subgraph "Standard/Comprehensive Agents"
        A5[Data Validation Agent]
        A6[Underwriting Agent]
        A7[Compliance Verification Agent]
        A8[Communication Agent]
    end
    
    subgraph "Comprehensive Only Agents"
        A9[Market Qualification Agent]
        A10[Lead Qualification Agent]
        A11[Exception Routing Agent]
        A12[Monitoring Agent]
        A13[Optimization Agent]
        A14[Onboarding Support Agent]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> A4
    
    A2 --> A5
    A5 --> A6
    A6 --> A7
    A7 --> A3
    A4 --> A8
    
    A2 --> A9
    A9 --> A10
    A10 --> A5
    A3 --> A11
    A11 --> A8
    A4 --> A12
    A12 --> A13
    A13 --> A14
```

## Actual Workflow Implementation (From Code)

```mermaid
graph TB
    subgraph "Express Workflow (4 agents)"
        E1[Document Processing] --> E2[Risk Assessment]
        E2 --> E3[Decision Making] --> E4[Account Provisioning]
    end
    
    subgraph "Standard Workflow (8 agents)"
        S1[Document Processing] --> S3[Risk Assessment]
        S3 --> S2[Data Validation] --> S8[Underwriting]
        S8 --> S4[Compliance Verification]
        S4 --> S5[Decision Making] --> S6[Account Provisioning]
        S6 --> S7[Communication]
    end
    
    subgraph "Comprehensive Workflow (14 agents)"
        C1[Document Processing] --> C2[Risk Assessment]
        C2 --> C3[Market Qualification] --> C4[Lead Qualification]
        C4 --> C5[Data Validation] --> C14[Underwriting]
        C14 --> C6[Compliance Verification]
        C6 --> C7[Decision Making] --> C8[Exception Routing]
        C8 --> C9[Communication] --> C10[Account Provisioning]
        C10 --> C11[Monitoring] --> C12[Optimization]
        C12 --> C13[Onboarding Support]
    end
    
    ROUTE{Risk Score} -->|0-300| E1
    ROUTE -->|301-700| S1
    ROUTE -->|701-1000| C1
    
    style E1 fill:#c8e6c9
    style S1 fill:#fff9c4
    style C1 fill:#ffcdd2
```

## LangGraph State Management (Actual Implementation)

```mermaid
flowchart TB
    subgraph "LangGraph Core"
        LG[StateGraph Engine]
        SM[MerchantOnboardingState]
        AW[Agent Wrapper Functions]
        HR[Human Review System]
    end
    
    subgraph "Agent Configuration"
        AC1[Auto-Approve Agents: 11]
        AC2[Human Review Required: 2]
        AC3[Data Validation]
        AC4[Compliance Verification]
    end
    
    subgraph "State Management"
        SF1[Application ID]
        SF2[Agent Results JSON]
        SF3[Review Status]
        SF4[Workflow Pattern]
        SF5[Progress Tracking]
    end
    
    LG --> SM
    SM --> AW
    AW --> HR
    
    AC1 --> AW
    AC2 --> HR
    AC3 --> HR
    AC4 --> HR
    
    SM --> SF1
    SF1 --> SF2
    SF2 --> SF3
    SF3 --> SF4
    SF4 --> SF5
```

## Tool-Calling Agent Architecture

```mermaid
graph TB
    subgraph "Document Processing Agent"
        DP1[LangGraph Agent] --> DP2[OCR Processing Tool]
        DP1 --> DP3[Document Classification Tool]
        DP1 --> DP4[Fraud Detection Tool]
    end
    
    subgraph "Risk Assessment Agent"
        RA1[LangGraph Agent] --> RA2[Financial Risk Tool]
        RA1 --> RA3[Industry Risk Tool]
        RA1 --> RA4[Credit Risk Tool]
    end
    
    subgraph "Compliance Agent"
        CA1[LangGraph Agent] --> CA2[OFAC Sanctions Tool]
        CA1 --> CA3[PEP Screening Tool]
        CA1 --> CA4[AML Risk Tool]
        CA1 --> CA5[KYC Verification Tool]
    end
    
    subgraph "Data Validation Agent"
        DV1[LangGraph Agent] --> DV2[Business Registry Tool]
        DV1 --> DV3[Tax ID Validation Tool]
        DV1 --> DV4[Address Verification Tool]
    end
```



## Real-Time Progress Tracking

```mermaid
sequenceDiagram
    participant UI as Web UI
    participant WS as WebSocket
    participant WF as Workflow Engine
    participant AG as AI Agents
    participant DB as Database
    
    UI->>WS: Join application room
    WF->>AG: Execute agent
    AG->>AG: Process data
    AG->>DB: Save results
    AG->>WS: Emit progress
    WS->>UI: Real-time update
    
    loop For each agent
        AG->>WS: Agent completed
        WS->>UI: Progress update
    end
    
    AG->>WS: Workflow complete
    WS->>UI: Final results
```

## Integration Architecture with Implementation Status

```mermaid
graph TB
    subgraph "Core Platform"
        CP[LangGraph Workflow Engine]
    end
    
    subgraph "Real Integrations ✅"
        RI1[Google Document AI]
        RI2[Google Vision API]
        RI3[SQLAlchemy Database]
        RI4[Flask Web UI]
    end
    
    subgraph "Mock Integrations ⚠️"
        MI1[Experian Credit API]
        MI2[OFAC Sanctions API]
        MI3[Jumio Identity API]
        MI4[Plaid Banking API]
    end
    
    subgraph "Planned Integrations 📋"
        PI1[Real Credit Bureaus]
        PI2[Real KYC Providers]
        PI3[Real Government DBs]
        PI4[Real Banking APIs]
    end
    
    CP --> RI1
    CP --> RI2
    CP --> RI3
    CP --> RI4
    
    CP -.-> MI1
    CP -.-> MI2
    CP -.-> MI3
    CP -.-> MI4
    
    MI1 -.-> PI1
    MI2 -.-> PI2
    MI3 -.-> PI3
    MI4 -.-> PI4
    
    style RI1 fill:#c8e6c9
    style MI1 fill:#fff9c4
    style PI1 fill:#ffcdd2
```









## Human Review Workflow (Implementation)

```mermaid
sequenceDiagram
    participant A as Agent
    participant W as Workflow
    participant DB as Database
    participant E as Event System
    participant H as Human Reviewer
    
    A->>W: Agent completes processing
    W->>W: Check AGENT_REVIEW_CONFIG
    
    alt Review Required
        W->>DB: Set needs_review = 'true'
        W->>E: Create threading.Event
        W->>W: Pause workflow (await event)
        H->>DB: Review and approve/decline
        H->>E: Set event (resume workflow)
        W->>W: Continue processing
    else Auto-Approve
        W->>W: Continue immediately
    end
```

## File Structure (Actual Implementation)

```
merchant-onboarding-ai-project/
├── src/
│   ├── main.py                    # Entry point with test data
│   ├── multi_workflow.py          # Multi-workflow + human review
│   ├── workflow_router.py         # Risk-based routing logic
│   ├── state.py                   # MerchantOnboardingState class
│   └── document_analyzer.py       # Document processing utilities
├── agents/                        # 13 agent directories
│   ├── document-processing/src/agent.py
│   ├── risk-assessment/src/agent.py
│   ├── compliance-verification/src/agent.py
│   ├── data-validation/src/agent.py
│   └── [9 other agents]/
├── ui/
│   ├── app.py                     # Flask web server
│   ├── review_api.py              # Human review endpoints
│   └── [HTML/CSS/JS files]/
├── tools/                         # Tool functions for agents
│   ├── document_tools.py          # Google Doc AI integration
│   ├── risk_tools.py             # Risk assessment tools
│   ├── compliance_tools.py       # KYC/AML/OFAC tools
│   └── validation_tools.py       # Data validation tools
└── database/
    ├── models.py                  # SQLAlchemy models
    └── merchant_onboarding.db     # SQLite database
```

## System Architecture Components

### High-Level System Architecture

```mermaid
C4Context
    title AI-Powered Merchant Onboarding System

    Person(merchant, "Merchant", "Uploads documents via web interface")
    Person(admin, "System Admin", "Monitors AI agent performance")
    Person(reviewer, "Human Reviewer", "Reviews AI agent decisions")

    System(onboarding, "LangGraph AI Agent Platform", "14 AI agents with multi-workflow routing")

    System_Ext(google_ai, "Google Document AI", "Real OCR and document processing")
    System_Ext(mock_apis, "Mock External APIs", "Simulated credit, KYC, compliance services")
    System_Ext(database, "SQLite Database", "Application and agent results storage")
    System_Ext(websocket, "Real-time Updates", "Live progress tracking via WebSocket")

    Rel(merchant, onboarding, "Uploads documents")
    Rel(admin, onboarding, "Monitors agents")
    Rel(reviewer, onboarding, "Reviews AI decisions")

    Rel(onboarding, google_ai, "Processes documents")
    Rel(onboarding, mock_apis, "Simulates external checks")
    Rel(onboarding, database, "Stores results")
    Rel(onboarding, websocket, "Sends real-time updates")
```

### Current Implementation Architecture

```mermaid
flowchart LR
    subgraph "Web Layer"
        WL1[Flask Web App]
        WL2[WebSocket Server]
        WL3[File Upload]
    end
    
    subgraph "Processing Layer"
        PL1[LangGraph Engine]
        PL2[AI Agents]
        PL3[Tool Functions]
    end
    
    subgraph "Data Layer"
        DL1[(SQLite Database)]
        DL2[Local File Storage]
        DL3[Agent Results Cache]
    end
    
    subgraph "External APIs"
        EA1[Google Document AI]
        EA2[Google Vision API]
        EA3[Mock APIs]
    end
    
    WL1 --> PL1
    WL2 --> PL1
    WL3 --> PL2
    
    PL1 --> PL2
    PL2 --> PL3
    PL3 --> EA1
    PL3 --> EA2
    PL3 --> EA3
    
    PL1 --> DL1
    PL2 --> DL2
    PL2 --> DL3
```



### Current AI Processing (Simplified)

```mermaid
flowchart LR
    subgraph "Input"
        I1[Document Upload]
        I2[Application Data]
    end
    
    subgraph "AI Processing"
        AP1[Google Document AI]
        AP2[Google Vision API]
        AP3[LangGraph Agents]
        AP4[Mock ML Models]
    end
    
    subgraph "Output"
        O1[Risk Scores]
        O2[Compliance Status]
        O3[Processing Results]
    end
    
    I1 --> AP1
    I1 --> AP2
    I2 --> AP3
    AP3 --> AP4
    
    AP1 --> O3
    AP2 --> O3
    AP3 --> O1
    AP4 --> O2
```







