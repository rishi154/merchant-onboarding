# System Architecture and Technical Diagrams

## High-Level System Architecture

```mermaid
C4Context
    title Merchant Onboarding System Context

    Person(merchant, "Merchant", "Business applying for payment processing services")
    Person(underwriter, "Underwriter", "Reviews and approves merchant applications")
    Person(compliance, "Compliance Officer", "Ensures regulatory compliance")
    Person(admin, "System Admin", "Manages system configuration")

    System(onboarding, "Merchant Onboarding Platform", "Core platform for merchant application processing")

    System_Ext(kyc, "KYC/AML Services", "Third-party identity verification and compliance services")
    System_Ext(credit, "Credit Bureau APIs", "Credit scoring and financial data services")
    System_Ext(banking, "Banking APIs", "Account verification and banking services")
    System_Ext(govt, "Government Databases", "Business registration and regulatory data")
    System_Ext(ai, "AI/ML Services", "Document processing and risk assessment")

    Rel(merchant, onboarding, "Submits application")
    Rel(underwriter, onboarding, "Reviews applications")
    Rel(compliance, onboarding, "Monitors compliance")
    Rel(admin, onboarding, "Configures system")

    Rel(onboarding, kyc, "Verifies identity")
    Rel(onboarding, credit, "Checks credit")
    Rel(onboarding, banking, "Verifies accounts")
    Rel(onboarding, govt, "Validates business")
    Rel(onboarding, ai, "Processes documents")
```

## Microservices Architecture

```mermaid
flowchart TB
    subgraph "API Gateway Layer"
        AG[API Gateway]
        LB[Load Balancer]
        AUTH[Authentication Service]
    end
    
    subgraph "Application Services"
        AS1[Application Service]
        AS2[Document Service]
        AS3[Risk Service]
        AS4[Decision Service]
        AS5[Notification Service]
        AS6[Audit Service]
    end
    
    subgraph "AI/ML Services"
        ML1[GenAI Service]
        ML2[OCR Service]
        ML3[Risk Model Service]
        ML4[Fraud Detection Service]
        ML5[NLP Service]
    end
    
    subgraph "Integration Services"
        IS1[KYC Integration]
        IS2[Credit Bureau Integration]
        IS3[Banking Integration]
        IS4[Government DB Integration]
    end
    
    subgraph "Data Layer"
        DB1[(Application Database)]
        DB2[(Document Store)]
        DB3[(Analytics Database)]
        DB4[(Audit Database)]
        CACHE[(Redis Cache)]
        QUEUE[(Message Queue)]
    end
    
    subgraph "Infrastructure"
        MON[Monitoring]
        LOG[Logging]
        SEC[Security]
        BACKUP[Backup]
    end
    
    LB --> AG
    AG --> AUTH
    AUTH --> AS1
    AUTH --> AS2
    AUTH --> AS3
    AUTH --> AS4
    AUTH --> AS5
    AUTH --> AS6
    
    AS1 --> ML1
    AS2 --> ML2
    AS3 --> ML3
    AS3 --> ML4
    AS5 --> ML5
    
    AS1 --> IS1
    AS3 --> IS2
    AS1 --> IS3
    AS3 --> IS4
    
    AS1 --> DB1
    AS2 --> DB2
    AS3 --> DB3
    AS6 --> DB4
    AS1 --> CACHE
    AS5 --> QUEUE
    
    MON --> AS1
    LOG --> AS2
    SEC --> AS3
    BACKUP --> DB1
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph "Data Sources"
        DS1[Merchant Portal]
        DS2[Document Upload]
        DS3[External APIs]
        DS4[System Events]
    end
    
    subgraph "Data Ingestion"
        DI1[API Gateway]
        DI2[File Processing]
        DI3[Event Streaming]
        DI4[Batch Processing]
    end
    
    subgraph "Data Processing"
        DP1[Real-time Processing]
        DP2[Batch Processing]
        DP3[ML Pipeline]
        DP4[Validation Engine]
    end
    
    subgraph "Data Storage"
        DST1[(Operational DB)]
        DST2[(Data Warehouse)]
        DST3[(Document Store)]
        DST4[(Cache Layer)]
    end
    
    subgraph "Data Analytics"
        DA1[Real-time Analytics]
        DA2[Batch Analytics]
        DA3[ML Models]
        DA4[Reporting Engine]
    end
    
    subgraph "Data Consumption"
        DC1[Dashboards]
        DC2[APIs]
        DC3[Reports]
        DC4[Alerts]
    end
    
    DS1 --> DI1
    DS2 --> DI2
    DS3 --> DI1
    DS4 --> DI3
    
    DI1 --> DP1
    DI2 --> DP2
    DI3 --> DP1
    DI4 --> DP2
    
    DP1 --> DST1
    DP2 --> DST2
    DP3 --> DST3
    DP4 --> DST4
    
    DST1 --> DA1
    DST2 --> DA2
    DST3 --> DA3
    DST4 --> DA4
    
    DA1 --> DC1
    DA2 --> DC2
    DA3 --> DC3
    DA4 --> DC4
```

## Security Architecture

```mermaid
flowchart TB
    subgraph "External Layer"
        EL1[WAF - Web Application Firewall]
        EL2[DDoS Protection]
        EL3[CDN - Content Delivery Network]
    end
    
    subgraph "Network Security"
        NS1[VPC - Virtual Private Cloud]
        NS2[Subnets - Public/Private]
        NS3[Security Groups]
        NS4[NACLs - Network ACLs]
    end
    
    subgraph "Application Security"
        AS1[API Gateway Security]
        AS2[OAuth 2.0 / JWT]
        AS3[Rate Limiting]
        AS4[Input Validation]
        AS5[HTTPS/TLS Encryption]
    end
    
    subgraph "Data Security"
        DS1[Encryption at Rest]
        DS2[Encryption in Transit]
        DS3[Key Management Service]
        DS4[Data Masking]
        DS5[Access Controls]
    end
    
    subgraph "Identity & Access"
        IA1[Multi-Factor Authentication]
        IA2[Role-Based Access Control]
        IA3[Single Sign-On]
        IA4[Identity Provider Integration]
    end
    
    subgraph "Monitoring & Compliance"
        MC1[Security Information Event Management]
        MC2[Vulnerability Scanning]
        MC3[Compliance Monitoring]
        MC4[Audit Logging]
        MC5[Incident Response]
    end
    
    EL1 --> NS1
    EL2 --> NS1
    EL3 --> NS1
    
    NS1 --> AS1
    NS2 --> AS2
    NS3 --> AS3
    NS4 --> AS4
    
    AS1 --> DS1
    AS2 --> DS2
    AS3 --> DS3
    AS4 --> DS4
    AS5 --> DS5
    
    DS1 --> IA1
    DS2 --> IA2
    DS3 --> IA3
    DS4 --> IA4
    
    IA1 --> MC1
    IA2 --> MC2
    IA3 --> MC3
    IA4 --> MC4
    IA5 --> MC5
```

## AI/ML Pipeline Architecture

```mermaid
flowchart LR
    subgraph "Data Input"
        DI1[Application Data]
        DI2[Document Images]
        DI3[External Data]
        DI4[Historical Data]
    end
    
    subgraph "Data Preprocessing"
        DP1[Data Cleaning]
        DP2[Feature Engineering]
        DP3[Data Validation]
        DP4[Data Transformation]
    end
    
    subgraph "Model Training"
        MT1[Training Pipeline]
        MT2[Model Validation]
        MT3[Hyperparameter Tuning]
        MT4[Model Registry]
    end
    
    subgraph "Model Serving"
        MS1[Model Deployment]
        MS2[A/B Testing]
        MS3[Model Monitoring]
        MS4[Model Versioning]
    end
    
    subgraph "Inference Engine"
        IE1[Real-time Inference]
        IE2[Batch Inference]
        IE3[Model Ensemble]
        IE4[Result Aggregation]
    end
    
    subgraph "Output Processing"
        OP1[Risk Scores]
        OP2[Predictions]
        OP3[Recommendations]
        OP4[Explanations]
    end
    
    DI1 --> DP1
    DI2 --> DP2
    DI3 --> DP3
    DI4 --> DP4
    
    DP1 --> MT1
    DP2 --> MT2
    DP3 --> MT3
    DP4 --> MT4
    
    MT1 --> MS1
    MT2 --> MS2
    MT3 --> MS3
    MT4 --> MS4
    
    MS1 --> IE1
    MS2 --> IE2
    MS3 --> IE3
    MS4 --> IE4
    
    IE1 --> OP1
    IE2 --> OP2
    IE3 --> OP3
    IE4 --> OP4
```

## Database Architecture

```mermaid
erDiagram
    MERCHANT ||--o{ APPLICATION : submits
    APPLICATION ||--o{ DOCUMENT : contains
    APPLICATION ||--o{ RISK_ASSESSMENT : has
    APPLICATION ||--o{ DECISION : receives
    
    MERCHANT {
        string merchant_id PK
        string business_name
        string legal_name
        string tax_id
        string business_type
        string industry_code
        datetime created_at
        datetime updated_at
    }
    
    APPLICATION {
        string application_id PK
        string merchant_id FK
        string status
        json application_data
        datetime submitted_at
        datetime completed_at
        string assigned_underwriter
    }
    
    DOCUMENT {
        string document_id PK
        string application_id FK
        string document_type
        string file_path
        json extracted_data
        string verification_status
        datetime uploaded_at
    }
    
    RISK_ASSESSMENT {
        string assessment_id PK
        string application_id FK
        float credit_score
        float fraud_score
        float overall_risk_score
        string risk_tier
        json risk_factors
        datetime assessed_at
    }
    
    DECISION {
        string decision_id PK
        string application_id FK
        string decision_type
        string decision_reason
        json conditions
        string decided_by
        datetime decided_at
    }
    
    AUDIT_LOG {
        string log_id PK
        string entity_id
        string entity_type
        string action
        json old_values
        json new_values
        string user_id
        datetime timestamp
    }
```

## Integration Architecture

```mermaid
flowchart TB
    subgraph "Core Platform"
        CP[Merchant Onboarding Platform]
    end
    
    subgraph "Identity Verification"
        IV1[Jumio API]
        IV2[Onfido API]
        IV3[Trulioo API]
    end
    
    subgraph "KYC/AML Services"
        KYC1[LexisNexis API]
        KYC2[Thomson Reuters API]
        KYC3[Refinitiv API]
    end
    
    subgraph "Credit & Financial"
        CF1[Experian API]
        CF2[Dun & Bradstreet API]
        CF3[Equifax API]
    end
    
    subgraph "Government & Regulatory"
        GR1[IRS Database]
        GR2[Secretary of State APIs]
        GR3[OFAC Sanctions Lists]
    end
    
    subgraph "Banking & Payments"
        BP1[Plaid API]
        BP2[Yodlee API]
        BP3[ACH Network APIs]
    end
    
    subgraph "AI/ML Services"
        AI1[AWS Textract]
        AI2[Google Vision API]
        AI3[Azure Cognitive Services]
        AI4[OpenAI GPT API]
    end
    
    subgraph "Integration Layer"
        IL1[API Gateway]
        IL2[Message Queue]
        IL3[Event Bus]
        IL4[Circuit Breaker]
        IL5[Rate Limiter]
    end
    
    CP --> IL1
    IL1 --> IV1
    IL1 --> IV2
    IL1 --> IV3
    IL1 --> KYC1
    IL1 --> KYC2
    IL1 --> KYC3
    IL1 --> CF1
    IL1 --> CF2
    IL1 --> CF3
    IL1 --> GR1
    IL1 --> GR2
    IL1 --> GR3
    IL1 --> BP1
    IL1 --> BP2
    IL1 --> BP3
    IL1 --> AI1
    IL1 --> AI2
    IL1 --> AI3
    IL1 --> AI4
    
    IL2 --> IL1
    IL3 --> IL1
    IL4 --> IL1
    IL5 --> IL1
```

## Deployment Architecture

```mermaid
flowchart TB
    subgraph "Production Environment"
        subgraph "Load Balancers"
            LB1[Application Load Balancer]
            LB2[Network Load Balancer]
        end
        
        subgraph "Application Tier"
            APP1[App Server 1]
            APP2[App Server 2]
            APP3[App Server 3]
        end
        
        subgraph "Database Tier"
            DB1[(Primary Database)]
            DB2[(Read Replica 1)]
            DB3[(Read Replica 2)]
        end
        
        subgraph "Cache Tier"
            CACHE1[Redis Cluster 1]
            CACHE2[Redis Cluster 2]
        end
    end
    
    subgraph "Staging Environment"
        STAGE1[Staging App Server]
        STAGE_DB[(Staging Database)]
        STAGE_CACHE[Staging Cache]
    end
    
    subgraph "Development Environment"
        DEV1[Dev App Server]
        DEV_DB[(Dev Database)]
        DEV_CACHE[Dev Cache]
    end
    
    subgraph "CI/CD Pipeline"
        GIT[Git Repository]
        BUILD[Build Server]
        TEST[Test Suite]
        DEPLOY[Deployment Pipeline]
    end
    
    subgraph "Monitoring & Logging"
        MON[Monitoring Dashboard]
        LOG[Log Aggregation]
        ALERT[Alert Manager]
    end
    
    LB1 --> APP1
    LB1 --> APP2
    LB1 --> APP3
    
    APP1 --> DB1
    APP2 --> DB2
    APP3 --> DB3
    
    APP1 --> CACHE1
    APP2 --> CACHE2
    
    GIT --> BUILD
    BUILD --> TEST
    TEST --> DEPLOY
    DEPLOY --> STAGE1
    DEPLOY --> APP1
    
    APP1 --> MON
    APP2 --> LOG
    APP3 --> ALERT
```

## Disaster Recovery Architecture

```mermaid
flowchart LR
    subgraph "Primary Region"
        PR1[Primary Data Center]
        PR_DB[(Primary Database)]
        PR_APP[Application Servers]
        PR_STORAGE[File Storage]
    end
    
    subgraph "Secondary Region"
        SR1[Secondary Data Center]
        SR_DB[(Standby Database)]
        SR_APP[Standby App Servers]
        SR_STORAGE[Replicated Storage]
    end
    
    subgraph "Backup Systems"
        BS1[Automated Backups]
        BS2[Point-in-Time Recovery]
        BS3[Cross-Region Replication]
    end
    
    subgraph "Monitoring & Failover"
        MF1[Health Monitoring]
        MF2[Automatic Failover]
        MF3[Manual Failover]
        MF4[Recovery Procedures]
    end
    
    PR_DB -.->|Replication| SR_DB
    PR_STORAGE -.->|Sync| SR_STORAGE
    
    PR1 --> BS1
    PR_DB --> BS2
    PR_STORAGE --> BS3
    
    MF1 --> PR1
    MF1 --> SR1
    MF2 --> SR_APP
    MF3 --> SR_DB
    MF4 --> SR_STORAGE
```