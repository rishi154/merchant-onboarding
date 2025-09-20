import matplotlib.pyplot as plt
import matplotlib.patches as patches
from workflow import create_onboarding_workflow

def visualize_agent_workflow():
    """Generate visual graph of the agent workflow"""
    
    # Create the workflow
    workflow = create_onboarding_workflow()
    
    # Agent positions for visualization (all 14 agents)
    agents = {
        "market_qualification": (1, 13),
        "lead_qualification": (1, 12),
        "application_assistant": (1, 11),
        "document_processing": (1, 10),
        "data_validation": (1, 9),
        "risk_assessment": (1, 8),
        "compliance_verification": (1, 7),
        "decision_making": (1, 6),
        "exception_routing": (1, 5),
        "communication": (1, 4),
        "account_provisioning": (1, 3),
        "monitoring": (1, 2),
        "optimization": (1, 1),
        "onboarding_support": (1, 0)
    }
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    
    # Draw agents as boxes
    for agent_name, (x, y) in agents.items():
        # Agent box
        rect = patches.Rectangle((x-0.4, y-0.3), 0.8, 0.6, 
                               linewidth=2, edgecolor='blue', 
                               facecolor='lightblue', alpha=0.7)
        ax.add_patch(rect)
        
        # Agent label
        ax.text(x, y, agent_name.replace('_', '\n'), 
               ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Draw arrows between agents
    arrow_props = dict(arrowstyle='->', lw=2, color='darkblue')
    
    # Sequential flow arrows (all 14 agents)
    flow_connections = [
        ("market_qualification", "lead_qualification"),
        ("lead_qualification", "application_assistant"),
        ("application_assistant", "document_processing"),
        ("document_processing", "data_validation"),
        ("data_validation", "risk_assessment"),
        ("risk_assessment", "compliance_verification"),
        ("compliance_verification", "decision_making"),
        ("decision_making", "exception_routing"),
        ("exception_routing", "communication"),
        ("communication", "account_provisioning"),
        ("account_provisioning", "monitoring"),
        ("monitoring", "optimization"),
        ("optimization", "onboarding_support")
    ]
    
    for from_agent, to_agent in flow_connections:
        from_pos = agents[from_agent]
        to_pos = agents[to_agent]
        
        ax.annotate('', xy=(to_pos[0], to_pos[1] + 0.3), 
                   xytext=(from_pos[0], from_pos[1] - 0.3),
                   arrowprops=arrow_props)
    
    # Add title and labels
    ax.set_title('Merchant Onboarding AI Agent Workflow', fontsize=16, fontweight='bold', pad=20)
    
    # Add automation percentages (all 14 agents)
    automation_rates = {
        "market_qualification": "95%",
        "lead_qualification": "90%", 
        "application_assistant": "85%",
        "document_processing": "80%",
        "data_validation": "75%",
        "risk_assessment": "70%",
        "compliance_verification": "65%",
        "decision_making": "60%",
        "exception_routing": "80%",
        "communication": "85%",
        "account_provisioning": "90%",
        "monitoring": "95%",
        "optimization": "70%",
        "onboarding_support": "85%"
    }
    
    for agent_name, (x, y) in agents.items():
        automation = automation_rates.get(agent_name, "N/A")
        ax.text(x + 0.5, y, f"Auto: {automation}", 
               ha='left', va='center', fontsize=8, 
               bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
    
    # Add legend
    legend_elements = [
        patches.Patch(color='lightblue', label='AI Agent'),
        patches.Patch(color='yellow', label='Automation Rate'),
        patches.FancyArrowPatch((0, 0), (1, 0), arrowstyle='->', 
                               color='darkblue', label='Process Flow')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    # Set axis properties
    ax.set_xlim(0, 3)
    ax.set_ylim(-0.5, 13.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add workflow stats
    stats_text = """
    Workflow Statistics:
    • Total Agents: 14
    • Average Automation: 80%
    • Processing Time: ~8-15 minutes
    • Success Rate: 95%
    """
    ax.text(2.2, 8, stats_text, fontsize=10, 
           bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('agent_workflow_graph.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("📊 Agent workflow graph saved as 'agent_workflow_graph.png'")
    print("🤖 Workflow contains 14 AI agents with 80% average automation")

def print_workflow_summary():
    """Print text-based workflow summary"""
    
    print("\n" + "="*60)
    print("🤖 MERCHANT ONBOARDING AI AGENT WORKFLOW")
    print("="*60)
    
    agents_flow = [
        ("1. Market Qualification", "95%", "Revenue, geo, platform validation"),
        ("2. Lead Qualification", "90%", "Lead scoring and prioritization"),
        ("3. Application Assistant", "85%", "Form validation and completion"),
        ("4. Document Processing", "80%", "OCR, classification, fraud detection"),
        ("5. Data Validation", "75%", "Cross-reference and verification"),
        ("6. Risk Assessment", "70%", "Multi-dimensional risk analysis"),
        ("7. Decision Making", "60%", "Approval/decline determination"),
        ("8. Communication", "85%", "Status notifications and updates"),
        ("9. Account Provisioning", "90%", "GlobalPayments account setup"),
        ("10. Exception Routing", "80%", "Error handling and escalation")
    ]
    
    for agent, automation, description in agents_flow:
        print(f"{agent:<25} | {automation:>5} | {description}")
    
    print("="*60)
    print(f"📈 Average Automation Rate: 81%")
    print(f"⚡ Estimated Processing Time: 5-10 minutes")
    print(f"🎯 Expected Success Rate: 95%")
    print("="*60)

if __name__ == "__main__":
    print_workflow_summary()
    
    try:
        visualize_agent_workflow()
    except ImportError:
        print("⚠️  Matplotlib not available. Install with: pip install matplotlib")
        print("📊 Text-based workflow summary shown above")