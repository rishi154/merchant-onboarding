"""
Generate Mermaid diagram for the merchant onboarding workflow
"""

def generate_workflow_diagram():
    """Generate Mermaid diagram for the 14-agent workflow"""
    
    mermaid_code = """
graph TD
    A[Start: Merchant Application] --> B[Market Qualification Agent]
    B --> C[Lead Qualification Agent]
    C --> D[Application Assistant Agent]
    D --> E[Document Processing Agent]
    E --> F[Data Validation Agent]
    F --> G[Risk Assessment Agent]
    G --> H[Compliance Verification Agent]
    H --> I[Decision Making Agent]
    I --> J[Exception Routing Agent]
    J --> K[Communication Agent]
    K --> L[Account Provisioning Agent]
    L --> M[Monitoring Agent]
    M --> N[Optimization Agent]
    N --> O[Onboarding Support Agent]
    O --> P[End: Complete]
    
    %% Tool Connections
    E --> E1[OCR Processing Tool]
    E --> E2[Document Classification Tool]
    E --> E3[Fraud Detection Tool]
    
    F --> F1[Business Registry Tool]
    F --> F2[Tax ID Validation Tool]
    F --> F3[Address Verification Tool]
    
    G --> G1[Financial Risk Tool]
    G --> G2[Industry Risk Tool]
    G --> G3[Credit Risk Tool]
    
    H --> H1[OFAC Sanctions Tool]
    H --> H2[PEP Screening Tool]
    H --> H3[AML Risk Tool]
    H --> H4[KYC Verification Tool]
    
    %% External Integrations
    E1 --> EXT1[Google Document AI]
    E2 --> EXT2[Google Vision API]
    E3 --> EXT2
    
    F1 --> EXT3[Secretary of State APIs]
    F2 --> EXT4[IRS Database]
    F3 --> EXT5[USPS Address API]
    
    G3 --> EXT6[Experian Credit Bureau]
    
    H1 --> EXT7[OFAC Database]
    H4 --> EXT8[Jumio KYC API]
    
    %% Styling
    classDef agent fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef tool fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef external fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class B,C,D,E,F,G,H,I,J,K,L,M,N,O agent
    class E1,E2,E3,F1,F2,F3,G1,G2,G3,H1,H2,H3,H4 tool
    class EXT1,EXT2,EXT3,EXT4,EXT5,EXT6,EXT7,EXT8 external
"""
    
    return mermaid_code

def generate_document_first_diagram():
    """Generate Mermaid diagram for document-first approach"""
    
    mermaid_code = """
graph TD
    A[Merchant Uploads 30 Documents] --> B[Document Processing Engine]
    
    B --> C1[Business License Processing]
    B --> C2[Bank Statement Processing]
    B --> C3[Tax Return Processing]
    B --> C4[Insurance Docs Processing]
    B --> C5[Identity Docs Processing]
    B --> C6[Compliance Docs Processing]
    B --> C7[Other Documents Processing]
    
    C1 --> D1[Extract Business Info]
    C2 --> D2[Extract Financial Data]
    C3 --> D3[Extract Tax Data]
    C4 --> D4[Extract Insurance Data]
    C5 --> D5[Extract Identity Data]
    C6 --> D6[Extract Compliance Data]
    C7 --> D7[Extract Supporting Data]
    
    D1 --> E[Data Consolidation Engine]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    D7 --> E
    
    E --> F[Generate Review Form]
    F --> G[Merchant Reviews Extracted Data]
    G --> H[Fill Missing Fields Only]
    H --> I[Submit Complete Application]
    I --> J[Standard 14-Agent Workflow]
    
    %% Document Types
    subgraph "Document Categories"
        DOC1[Core Business: License, Articles, EIN]
        DOC2[Financial: Bank Statements, Tax Returns]
        DOC3[Identity: Driver License, SSN Card]
        DOC4[Insurance: General Liability, Workers Comp]
        DOC5[Compliance: PCI, OFAC Screening]
        DOC6[Supporting: Business Plan, Lease]
    end
    
    %% Styling
    classDef process fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    classDef document fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef extraction fill:#f1f8e9,stroke:#388e3c,stroke-width:2px
    
    class B,E,F process
    class DOC1,DOC2,DOC3,DOC4,DOC5,DOC6 document
    class D1,D2,D3,D4,D5,D6,D7 extraction
"""
    
    return mermaid_code

def generate_integration_architecture_diagram():
    """Generate Mermaid diagram for integration architecture"""
    
    mermaid_code = """
graph TD
    A[Agent Layer] --> B[Tools Layer]
    B --> C{Mock/Real Decision}
    
    C -->|Mock=true| D[Mock Integrations]
    C -->|Mock=false| E[Real Integrations]
    
    %% Mock Integrations
    D --> D1[Mock Credit Bureau]
    D --> D2[Mock KYC Provider]
    D --> D3[Mock Banking API]
    D --> D4[Mock Government DB]
    D --> D5[Mock Document AI]
    
    %% Real Integrations
    E --> E1[Experian Credit API]
    E --> E2[Jumio KYC API]
    E --> E3[Plaid Banking API]
    E --> E4[OFAC Database API]
    E --> E5[Google Document AI]
    E --> E6[Google Vision API]
    E --> E7[Secretary of State APIs]
    
    %% Environment Configuration
    F[Environment Variables] --> C
    F1[MOCK_CREDIT_BUREAUS=true/false] --> F
    F2[MOCK_KYC_PROVIDERS=true/false] --> F
    F3[MOCK_BANKING_APIS=true/false] --> F
    F4[MOCK_GOVERNMENT_DATABASES=true/false] --> F
    F5[MOCK_DOCUMENT_PROCESSING=true/false] --> F
    
    %% Agent Examples
    A1[Document Processing Agent] --> A
    A2[Risk Assessment Agent] --> A
    A3[Compliance Verification Agent] --> A
    A4[Data Validation Agent] --> A
    
    %% Tool Examples
    B1[OCR Processing Tool] --> B
    B2[Credit Risk Scoring Tool] --> B
    B3[OFAC Sanctions Check Tool] --> B
    B4[Business Registry Tool] --> B
    
    %% Styling
    classDef agent fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px
    classDef tool fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    classDef mock fill:#fff8e1,stroke:#ff8f00,stroke-width:2px
    classDef real fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    classDef config fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class A,A1,A2,A3,A4 agent
    class B,B1,B2,B3,B4 tool
    class D,D1,D2,D3,D4,D5 mock
    class E,E1,E2,E3,E4,E5,E6,E7 real
    class F,F1,F2,F3,F4,F5 config
"""
    
    return mermaid_code

def save_diagrams():
    """Save all Mermaid diagrams to files"""
    
    # Generate workflow diagram
    workflow_diagram = generate_workflow_diagram()
    with open("workflow_diagram.md", "w") as f:
        f.write("# Merchant Onboarding Workflow Diagram\n\n")
        f.write("```mermaid\n")
        f.write(workflow_diagram)
        f.write("\n```\n")
    
    # Generate document-first diagram
    doc_first_diagram = generate_document_first_diagram()
    with open("document_first_diagram.md", "w") as f:
        f.write("# Document-First Onboarding Diagram\n\n")
        f.write("```mermaid\n")
        f.write(doc_first_diagram)
        f.write("\n```\n")
    
    # Generate integration architecture diagram
    integration_diagram = generate_integration_architecture_diagram()
    with open("integration_architecture_diagram.md", "w") as f:
        f.write("# Integration Architecture Diagram\n\n")
        f.write("```mermaid\n")
        f.write(integration_diagram)
        f.write("\n```\n")
    
    print("Generated Mermaid diagrams:")
    print("- workflow_diagram.md")
    print("- document_first_diagram.md") 
    print("- integration_architecture_diagram.md")
    
    return {
        "workflow": workflow_diagram,
        "document_first": doc_first_diagram,
        "integration_architecture": integration_diagram
    }

if __name__ == "__main__":
    diagrams = save_diagrams()
    
    print("\n" + "="*60)
    print("WORKFLOW DIAGRAM")
    print("="*60)
    print("```mermaid")
    print(diagrams["workflow"])
    print("```")
    
    print("\n" + "="*60)
    print("DOCUMENT-FIRST DIAGRAM")
    print("="*60)
    print("```mermaid")
    print(diagrams["document_first"])
    print("```")
    
    print("\n" + "="*60)
    print("INTEGRATION ARCHITECTURE DIAGRAM")
    print("="*60)
    print("```mermaid")
    print(diagrams["integration_architecture"])
    print("```")