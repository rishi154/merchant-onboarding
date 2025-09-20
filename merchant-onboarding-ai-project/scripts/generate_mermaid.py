"""Generate Mermaid diagram for the workflow"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def generate_mermaid_diagram():
    """Generate Mermaid flowchart with working syntax"""
    
    mermaid_code = """
graph TD
    Start --> MQ[Market Qualification]
    MQ --> LQ[Lead Qualification]
    LQ --> AA[Application Assistant]
    AA --> DP[Document Processing]
    DP --> DV[Data Validation]
    DV --> RA[Risk Assessment]
    RA --> CV[Compliance Verification]
    CV --> DM[Decision Making]
    DM --> ER[Exception Routing]
    ER --> COM[Communication]
    COM --> AP[Account Provisioning]
    AP --> MON[Monitoring]
    MON --> OPT[Optimization]
    OPT --> OS[Onboarding Support]
    OS --> End

    DP --> OCR[OCR Tool]
    DP --> DOC[Document Tool]
    DP --> FRAUD[Fraud Tool]
    
    DV --> BIZ[Business Tool]
    DV --> TAX[Tax Tool]
    DV --> ADDR[Address Tool]
    
    CV --> OFAC[OFAC Tool]
    CV --> PEP[PEP Tool]
    CV --> AML[AML Tool]
    CV --> KYC[KYC Tool]
    
    AP --> GP1[Create Account]
    AP --> GP2[Configure Processing]
    AP --> GP3[Generate Credentials]

    OCR --> GDOC[Google Document AI]
    BIZ --> SOS[Secretary of State]
    TAX --> IRS[IRS Validation]
    ADDR --> USPS[USPS Verification]
    OFAC --> TREAS[Treasury OFAC]
    GP1 --> GLOBAL[GlobalPayments API]

    classDef agent fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef tool fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef service fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class MQ,LQ,AA,DP,DV,RA,CV,DM,ER,COM,AP,MON,OPT,OS agent
    class OCR,DOC,FRAUD,BIZ,TAX,ADDR,OFAC,PEP,AML,KYC,GP1,GP2,GP3 tool
    class GDOC,SOS,IRS,USPS,TREAS,GLOBAL service
"""
    
    return mermaid_code.strip()

def generate_langgraph_mermaid():
    """Generate Mermaid from LangGraph workflow"""
    
    try:
        from workflow import create_onboarding_workflow
        
        workflow = create_onboarding_workflow()
        
        # Get the graph
        graph = workflow.get_graph()
        
        # Generate Mermaid (if LangGraph supports it)
        if hasattr(graph, 'draw_mermaid'):
            return graph.draw_mermaid()
        else:
            print("LangGraph Mermaid not available, using custom diagram")
            return generate_mermaid_diagram()
            
    except Exception as e:
        print(f"Error generating from LangGraph: {e}")
        return generate_mermaid_diagram()

def save_mermaid_files():
    """Save Mermaid diagrams to files"""
    
    print("Generating Mermaid Workflow Diagrams")
    print("=" * 40)
    
    # Generate custom Mermaid
    custom_mermaid = generate_mermaid_diagram()
    
    # Save to file
    mermaid_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'workflow.mmd')
    os.makedirs(os.path.dirname(mermaid_file), exist_ok=True)
    
    with open(mermaid_file, 'w') as f:
        f.write(custom_mermaid)
    
    print(f"Saved: {mermaid_file}")
    
    # Generate HTML with Mermaid
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Merchant Onboarding Workflow</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <h1>Merchant Onboarding AI Agent Workflow</h1>
    <div class="mermaid">
{custom_mermaid}
    </div>
    
    <h2>Workflow Information</h2>
    <ul>
        <li>Total Agents: 14</li>
        <li>Sequential Processing Flow</li>
        <li>Real VertexAI Integration</li>
        <li>Mock External Services</li>
    </ul>
    
    <script>
        mermaid.initialize({{ startOnLoad: true }});
    </script>
</body>
</html>
"""
    
    html_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'workflow.html')
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"Saved: {html_file}")
    
    # Try LangGraph Mermaid
    try:
        langgraph_mermaid = generate_langgraph_mermaid()
        if langgraph_mermaid and langgraph_mermaid != custom_mermaid:
            langgraph_file = os.path.join(os.path.dirname(__file__), '..', 'docs', 'langgraph_workflow.mmd')
            with open(langgraph_file, 'w') as f:
                f.write(langgraph_mermaid)
            print(f"Saved: {langgraph_file}")
    except Exception as e:
        print(f"LangGraph Mermaid failed: {e}")
    
    print()
    print("View the workflow:")
    print(f"1. Open {html_file} in browser")
    print("2. Copy .mmd content to https://mermaid.live")
    print("3. Use Mermaid CLI: mmdc -i workflow.mmd -o workflow.png")

if __name__ == "__main__":
    save_mermaid_files()
    
    # Print the Mermaid code
    print("\nMermaid Code:")
    print("-" * 40)
    print(generate_mermaid_diagram())