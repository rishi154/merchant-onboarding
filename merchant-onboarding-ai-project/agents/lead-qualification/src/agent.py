"""Lead Qualification Agent with enhanced CRM and marketing attribution capabilities."""
from typing import Dict, Any, List
import json
import sys
import os
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from tools.crm_tools import ConsolidatedCRMTool
from tools.attribution_tools import AttributionAnalysisTool
from llm_config import get_llm

async def lead_qualification_agent(state) -> Dict[str, Any]:
    """Agent 3: Lead Qualification AI Agent with enhanced CRM and attribution capabilities."""
    
    # Initialize tools
    tools = [
        ConsolidatedCRMTool(),
        AttributionAnalysisTool()
    ]

    # Enhanced prompt with CRM and attribution analysis capabilities
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Lead Qualification AI Agent specialized in comprehensive lead analysis.

Your task is to evaluate leads using CRM data and marketing attribution analysis.

Available tools:
- get_consolidated_crm_data: Retrieve and analyze lead data from multiple CRM systems
- analyze_attribution: Analyze marketing attribution and channel performance

For each lead:
1. Get CRM data to understand lead history and engagement
2. Analyze marketing attribution to understand acquisition path
3. Evaluate lead quality using both data sources
4. Generate actionable recommendations

Consider:
- Lead source and attribution path
- Engagement history and interactions
- Marketing channel performance
- Conversion probability
- Lead scoring from multiple systems
- Historical performance of similar leads

Return a comprehensive analysis with:
- Qualification status
- Consolidated lead score
- Marketing channel effectiveness
- Conversion probability
- Priority level
- Next best actions"""),
        ("human", "Analyze this lead for qualification:\n\nApplication Data: {application_data}\n\nPrevious Results: {previous_results}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    # Create tool-calling agent
    llm = get_llm()
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    try:
        # Prepare input data
        merchant_data = state.application_data
        input_data = {
            "application_data": json.dumps(merchant_data),
            "previous_results": json.dumps({
                "market_qualification": state.market_qualification
            })
        }

        # Execute agent with tool calling
        result = await agent_executor.ainvoke(input_data)

        # Process agent's analysis
        final_result = await _process_qualification_result(result, merchant_data)
        
        # Add processing time
        final_result["processing_time"] = 0.3
        
        # Update state
        state.lead_qualification = final_result

        return {"lead_qualification": final_result}

    except Exception as e:
        print(f"[ERROR] Lead Qualification Agent error: {str(e)}")
        # Fallback qualification logic
        return await _fallback_qualification(state)

async def _process_qualification_result(result: Dict[str, Any], merchant_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process and enhance the agent's qualification result."""
    
    # Extract core qualification data
    agent_output = result.get("output", {})
    if isinstance(agent_output, str):
        try:
            agent_output = json.loads(agent_output)
        except json.JSONDecodeError:
            agent_output = {}

    # Get CRM and attribution data from tool results
    crm_data = next(
        (action["output"] for action in result.get("intermediate_steps", [])
         if "get_consolidated_crm_data" in str(action)),
        {}
    )
    
    attribution_data = next(
        (action["output"] for action in result.get("intermediate_steps", [])
         if "analyze_attribution" in str(action)),
        {}
    )

    # Combine all data sources for final analysis
    return {
        "qualified": _determine_qualification_status(agent_output, crm_data, attribution_data),
        "lead_details": {
            "consolidated_score": _calculate_consolidated_score(agent_output, crm_data, attribution_data),
            "conversion_probability": _calculate_conversion_probability(agent_output, crm_data, attribution_data),
            "priority_level": _determine_priority_level(agent_output, crm_data, attribution_data),
            "source_quality": _analyze_source_quality(attribution_data)
        },
        "marketing_insights": {
            "channel_performance": attribution_data.get("channel_performance", {}),
            "attribution_path": attribution_data.get("analysis", {}).get("attribution_path", {}),
            "channel_effectiveness": attribution_data.get("analysis", {}).get("channel_effectiveness", {})
        },
        "crm_data": {
            "engagement_history": crm_data.get("engagement_score"),
            "lead_status": crm_data.get("status"),
            "pipeline_stage": crm_data.get("pipeline_stage")
        },
        "recommendations": _generate_recommendations(agent_output, crm_data, attribution_data),
        "next_actions": _determine_next_actions(agent_output, crm_data, attribution_data)
    }

def _determine_qualification_status(agent_output: Dict[str, Any], crm_data: Dict[str, Any], attribution_data: Dict[str, Any]) -> bool:
    """Determine final qualification status using all available data."""
    # Implement sophisticated qualification logic
    crm_score = float(crm_data.get("lead_score", 0))
    conversion_prob = float(crm_data.get("conversion_probability", 0))
    channel_effectiveness = attribution_data.get("analysis", {}).get("channel_effectiveness", {}).get("effectiveness_score", 0)
    
    # Calculate weighted score
    weighted_score = (
        crm_score * 0.4 +
        conversion_prob * 0.4 +
        channel_effectiveness * 0.2
    )
    
    return weighted_score >= 65.0  # Threshold for qualification

def _calculate_consolidated_score(agent_output: Dict[str, Any], crm_data: Dict[str, Any], attribution_data: Dict[str, Any]) -> float:
    """Calculate consolidated lead score using multiple data sources."""
    weights = {
        "crm_score": 0.4,
        "engagement": 0.2,
        "channel_quality": 0.2,
        "conversion_probability": 0.2
    }
    
    scores = {
        "crm_score": float(crm_data.get("lead_score", 0)),
        "engagement": float(crm_data.get("engagement_score", 0)) * 10,
        "channel_quality": float(attribution_data.get("analysis", {}).get("lead_quality", 0)),
        "conversion_probability": float(crm_data.get("conversion_probability", 0)) * 100
    }
    
    return sum(scores[key] * weight for key, weight in weights.items())

def _calculate_conversion_probability(agent_output: Dict[str, Any], crm_data: Dict[str, Any], attribution_data: Dict[str, Any]) -> float:
    """Calculate lead conversion probability."""
    # Implement conversion probability calculation
    base_probability = float(crm_data.get("conversion_probability", 0))
    channel_effectiveness = attribution_data.get("analysis", {}).get("channel_effectiveness", {}).get("effectiveness_score", 0)
    
    # Adjust based on channel effectiveness
    adjusted_probability = base_probability * (1 + channel_effectiveness)
    
    return min(adjusted_probability, 1.0)

def _determine_priority_level(agent_output: Dict[str, Any], crm_data: Dict[str, Any], attribution_data: Dict[str, Any]) -> str:
    """Determine lead priority level."""
    consolidated_score = _calculate_consolidated_score(agent_output, crm_data, attribution_data)
    
    if consolidated_score >= 85:
        return "HIGH"
    elif consolidated_score >= 65:
        return "MEDIUM"
    else:
        return "LOW"

def _analyze_source_quality(attribution_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the quality of the lead source."""
    channel_performance = attribution_data.get("channel_performance", {})
    current_channel = attribution_data.get("attribution_data", {}).get("channel_group")
    
    if not current_channel:
        return {"quality_score": 0, "confidence": "low"}
    
    channel_metrics = next(
        (c for c in channel_performance.get("channels", []) if c["channel"] == current_channel),
        None
    )
    
    if not channel_metrics:
        return {"quality_score": 0, "confidence": "low"}
    
    quality_score = (
        channel_metrics.get("conversion_rate", 0) * 0.4 +
        (channel_metrics.get("average_lead_score", 0) / 100) * 0.3 +
        (1 / (channel_metrics.get("cost_per_lead", 100) + 1)) * 0.3
    )
    
    return {
        "quality_score": quality_score,
        "confidence": "high" if quality_score > 0.7 else "medium" if quality_score > 0.4 else "low",
        "metrics": channel_metrics
    }

def _generate_recommendations(agent_output: Dict[str, Any], crm_data: Dict[str, Any], attribution_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []
    
    # Add attribution-based recommendations
    attribution_recs = attribution_data.get("analysis", {}).get("recommendations", [])
    recommendations.extend(attribution_recs)
    
    # Add CRM-based recommendations
    if crm_data.get("engagement_score", 0) < 5:
        recommendations.append({
            "type": "engagement",
            "action": "increase_engagement",
            "description": "Low engagement detected. Consider implementing engagement nurturing campaign."
        })
    
    if crm_data.get("lead_score", 0) < 70:
        recommendations.append({
            "type": "nurturing",
            "action": "lead_nurturing",
            "description": "Lead score below threshold. Implement targeted nurturing program."
        })
    
    return recommendations

def _determine_next_actions(agent_output: Dict[str, Any], crm_data: Dict[str, Any], attribution_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Determine next actions based on analysis."""
    priority = _determine_priority_level(agent_output, crm_data, attribution_data)
    conv_prob = _calculate_conversion_probability(agent_output, crm_data, attribution_data)
    
    actions = []
    
    if priority == "HIGH":
        actions.append({
            "action": "expedited_review",
            "owner": "sales_team",
            "timeframe": "24h"
        })
    
    if conv_prob < 0.5:
        actions.append({
            "action": "nurturing_campaign",
            "owner": "marketing_team",
            "timeframe": "48h"
        })
    
    # Add channel-specific actions
    channel_effectiveness = attribution_data.get("analysis", {}).get("channel_effectiveness", {})
    if channel_effectiveness.get("effectiveness_score", 0) < 0.5:
        actions.append({
            "action": "channel_optimization",
            "owner": "marketing_team",
            "timeframe": "1w"
        })
    
    return actions

async def _fallback_qualification(state: Any) -> Dict[str, Any]:
    """Fallback qualification logic when primary qualification fails."""
    merchant_data = state.application_data
    
    # Basic qualification criteria
    revenue_qualified = merchant_data.get("annual_revenue", 0) >= 100000
    geo_qualified = merchant_data.get("country", "").upper() in ["US", "CA", "UK"]
    platform_qualified = merchant_data.get("platform", "").lower() in ["shopify", "woocommerce", "custom"]
    
    is_qualified = all([revenue_qualified, geo_qualified, platform_qualified])
    
    return {
        "lead_qualification": {
            "qualified": is_qualified,
            "lead_details": {
                "consolidated_score": 70 if is_qualified else 40,
                "conversion_probability": 0.6 if is_qualified else 0.3,
                "priority_level": "MEDIUM" if is_qualified else "LOW",
                "source_quality": {"quality_score": 0.5, "confidence": "low"}
            },
            "marketing_insights": {
                "channel_performance": {},
                "attribution_path": {},
                "channel_effectiveness": {"effectiveness_score": 0.5, "confidence": "low"}
            },
            "crm_data": {},
            "recommendations": [{
                "type": "fallback",
                "action": "manual_review",
                "description": "Qualification completed using fallback logic. Manual review recommended."
            }],
            "next_actions": [{
                "action": "manual_review",
                "owner": "underwriting_team",
                "timeframe": "48h"
            }],
            "processing_time": 0.1
        }
    }