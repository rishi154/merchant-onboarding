# AI Agent Architecture Diagrams
## Actual Implementation Architecture

## Multi-Workflow Agent System Overview

```mermaid
flowchart TD
    A[Document Upload] --> B[Document Processing Agent]
    B --> C[Risk Assessment Agent]
    C --> D{Risk-Based Workflow Routing}
    
    D -->|LOW Risk<br/>Simple Business| E[Express Workflow<br/>4 Agents - 15-30 min]
    D -->|MEDIUM Risk<br/>Standard Business| F[Standard Workflow<br/>7 Agents - 1-2 hours]
    D -->|HIGH Risk<br/>Complex Business| G[Comprehensive Workflow<br/>14 Agents - 2-4 hours]
    
    D --> G[Auto-Approval Pipeline]
    E --> H[Standard Review Pipeline]
    F --> I[Enhanced Review Pipeline]
    
    G --> J[Account Setup]
    H --> J
    I --> J
    
    style D fill:#c8e6c9
    style E fill:#fff9c4
    style F fill:#ffcdd2
```

## 14 AI Agents - Complete System Architecture

```mermaid
graph TB
    subgraph "Phase 0: Segmentation"
        A0[Merchant Segmentation Agent]
    end
    
    subgraph "Phase 1: Acquisition (Agents 1-2)"
        A1[Lead Qualification Agent]
        A2[Application Assistant Agent]
    end
    
    subgraph "Phase 2: Processing (Agents 3-5)"
        A3[Document Processing Agent]
        A4[Compliance Verification Agent]
        A5[Data Validation Agent]
    end
    
    subgraph "Phase 3: Assessment (Agents 6-8)"
        A6[Risk Assessment Agent]
        A7[Decision Making Agent]
        A8[Exception Routing Agent]
    end
    
    subgraph "Phase 4: Setup (Agents 9-10)"
        A9[Communication Agent]
        A10[Account Provisioning Agent]
    end
    
    subgraph "Phase 5: Support (Agents 11-12)"
        A11[Onboarding Support Agent]
        A12[Monitoring Agent]
    end
    
    subgraph "Phase 6: Optimization (Agent 13)"
        A13[Optimization Agent]
    end
    
    A0 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5
    A5 --> A6
    A6 --> A7
    A7 --> A8
    A8 --> A9
    A9 --> A10
    A10 --> A11
    A11 --> A12
    A12 --> A13
```

## Workflow Pattern Comparison

```mermaid
graph LR
    subgraph "Routing Workflow (All merchants start here)"
        R1[Document Processing] --> R2[Risk Assessment]
        R2 --> R3{Route Based on Risk Tier}
    end
    
    subgraph "Express Workflow (LOW risk - 50% of merchants)"
        E1[Document Processing] --> E2[Risk Assessment]
        E2 --> E3[Decision Making] --> E4[Account Provisioning]
    end
    
    subgraph "Standard Workflow (MEDIUM risk - 30% of merchants)"
        S1[Document Processing] --> S2[Data Validation]
        S2 --> S3[Risk Assessment] --> S4[Compliance Verification]
        S4 --> S5[Decision Making] --> S6[Account Provisioning]
        S6 --> S7[Communication]
    end
    
    subgraph "Comprehensive Workflow (HIGH risk - 20% of merchants)"
        C1[Document Processing] --> C2[Market Qualification]
        C2 --> C3[Lead Qualification] --> C4[Data Validation]
        C4 --> C5[Risk Assessment] --> C6[Compliance Verification]
        C6 --> C7[Decision Making] --> C8[Exception Routing]
        C8 --> C9[Communication] --> C10[Account Provisioning]
        C10 --> C11[Monitoring] --> C12[Optimization]
        C12 --> C13[Onboarding Support]
    end
    
    R3 -->|LOW Risk| E1
    R3 -->|MEDIUM Risk| S1
    R3 -->|HIGH Risk| C1
    
    style E1 fill:#c8e6c9
    style S1 fill:#fff9c4
    style C1 fill:#ffcdd2
```

## LangGraph State Management Architecture

```mermaid
flowchart TB
    subgraph "LangGraph Orchestration"
        LG[StateGraph Engine]
        SM[MerchantOnboardingState]
        TC[Tool Calling Agents]
        FB[Fallback System]
    end
    
    subgraph "Agent Types"
        AT1[LLM Reasoning Only<br/>6 agents]
        AT2[Tool-Calling Agents<br/>4 agents]
        AT3[Rule-Based Logic<br/>2 agents]
        AT4[API Integration<br/>2 agents]
    end
    
    subgraph "State Flow"
        SF1[Application Data] --> SF2[Document Processing]
        SF2 --> SF3[Agent Results] --> SF4[Decision Output]
    end
    
    LG --> SM
    SM --> TC
    TC --> FB
    
    LG --> AT1
    LG --> AT2
    LG --> AT3
    LG --> AT4
    
    SM --> SF1
    SF1 --> SF2
    SF2 --> SF3
    SF3 --> SF4
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

## 3-Layer Fallback System

```mermaid
flowchart TD
    A[Agent Execution] --> B{Primary Layer Available?}
    
    B -->|Yes| C[Layer 1: Real APIs<br/>Google Doc AI, Experian, OFAC]
    B -->|No| D{Secondary Layer Available?}
    
    D -->|Yes| E[Layer 2: Mock APIs<br/>Simulated responses, cached data]
    D -->|No| F[Layer 3: Basic Rules<br/>Hardcoded logic, minimal processing]
    
    C --> G[High Quality Results]
    E --> H[Medium Quality Results]
    F --> I[Basic Results - Workflow Continues]
    
    G --> J[Continue Workflow]
    H --> J
    I --> J
    
    style C fill:#c8e6c9
    style E fill:#fff9c4
    style F fill:#ffcdd2
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

## Performance Metrics by Workflow

```mermaid
xychart-beta
    title "Processing Time by Workflow Pattern"
    x-axis [Express, Standard, Comprehensive]
    y-axis "Hours" 0 --> 120
    bar [4, 24, 72]
```

```mermaid
pie title Automation Rate by Workflow
    "Express (95%)" : 95
    "Standard (80%)" : 80
    "Comprehensive (60%)" : 60
```

## Database Schema - Actual Implementation

```mermaid
erDiagram
    MERCHANT_APPLICATION ||--o{ PROCESSING_STEP : has
    
    MERCHANT_APPLICATION {
        string id PK
        string business_name
        string status
        string current_agent
        int progress_percentage
        int documents_processed
        float extraction_confidence
        int manual_fields_required
        datetime processing_start_time
        datetime processing_end_time
        json application_data
        json extracted_data
        json agent_results
        string workflow_pattern
        datetime created_at
        datetime updated_at
    }
    
    PROCESSING_STEP {
        string id PK
        string application_id FK
        string agent_name
        string status
        json result_data
        datetime started_at
        datetime completed_at
    }
```

## Deployment Architecture - Current Implementation

```mermaid
graph TB
    subgraph "Development Environment"
        DE1[Flask Web Server :5000]
        DE2[SQLite Database]
        DE3[Local File Storage]
        DE4[Mock API Services]
    end
    
    subgraph "Production Ready Components"
        PR1[LangGraph Workflow Engine]
        PR2[14 AI Agents]
        PR3[3-Layer Fallback System]
        PR4[Real-time WebSocket Updates]
        PR5[Multi-Workflow Routing]
    end
    
    subgraph "Scalability Path"
        SP1[Kubernetes Deployment]
        SP2[PostgreSQL Database]
        SP3[Redis Cache]
        SP4[Load Balancers]
        SP5[Real API Integrations]
    end
    
    DE1 --> PR1
    DE2 --> PR2
    DE3 --> PR3
    DE4 --> PR4
    
    PR1 -.-> SP1
    PR2 -.-> SP2
    PR3 -.-> SP3
    PR4 -.-> SP4
    PR5 -.-> SP5
```