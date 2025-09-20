"""Marketing attribution tools for lead qualification."""
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel
import aiohttp
import json
import os
from datetime import datetime, timedelta

class AttributionData(BaseModel):
    """Schema for marketing attribution data."""
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    utm_content: Optional[str]
    utm_term: Optional[str]
    referrer: Optional[str]
    landing_page: Optional[str]
    device_type: Optional[str]
    channel_group: Optional[str]

class ChannelPerformanceData(BaseModel):
    """Schema for channel performance data."""
    channel: str
    leads_generated: int
    conversion_rate: float
    cost_per_lead: float
    average_lead_score: float
    roi: float

class AttributionQueryInput(BaseModel):
    """Schema for attribution query input."""
    merchant_id: str
    email: str
    date_range: Optional[str] = "30d"  # Options: 7d, 30d, 90d, all

class GAAttributionTool(BaseTool):
    """Tool for Google Analytics attribution data."""
    name: str = "get_ga_attribution"
    description: str = "Get attribution data from Google Analytics"
    args_schema: type = AttributionQueryInput

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get Google Analytics authentication headers."""
        return {
            "Authorization": f"Bearer {os.getenv('GA_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }

    def _run(self, merchant_id: str, email: str, date_range: str = "30d") -> Dict[str, Any]:
        """Get attribution data from Google Analytics (sync version)."""
        # Return mock data for development
        return {
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "merchant_acquisition_2025",
            "utm_content": "banner_1",
            "utm_term": "payment_processing",
            "referrer": "www.google.com",
            "landing_page": "/merchant-solutions",
            "device_type": "desktop",
            "channel_group": "paid_search",
            "first_touch_timestamp": "2025-09-15T10:30:00Z",
            "last_touch_timestamp": "2025-09-18T14:20:00Z"
        }
    
    async def _arun(self, merchant_id: str, email: str, date_range: str = "30d") -> Dict[str, Any]:
        """Get attribution data from Google Analytics (async version)."""
        if not os.getenv("GA_ACCESS_TOKEN"):
            return self._run(merchant_id, email, date_range)

        # Convert date_range to actual dates
        end_date = datetime.now()
        start_date = end_date - {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90)
        }.get(date_range, timedelta(days=30))

        async with aiohttp.ClientSession() as session:
            headers = self._get_auth_headers()
            url = f"{os.getenv('GA_API_URL')}/v1/attribution"
            
            params = {
                "merchant_id": merchant_id,
                "user_identifier": email,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
                return self._process_ga_data(data)

    def _process_ga_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize Google Analytics data."""
        if not data.get("sessions"):
            return {"error": "No attribution data found"}
        
        latest_session = data["sessions"][-1]
        return {
            "utm_source": latest_session.get("source"),
            "utm_medium": latest_session.get("medium"),
            "utm_campaign": latest_session.get("campaign"),
            "utm_content": latest_session.get("content"),
            "utm_term": latest_session.get("term"),
            "referrer": latest_session.get("referrer"),
            "landing_page": latest_session.get("landing_page"),
            "device_type": latest_session.get("device"),
            "channel_group": latest_session.get("channel_group"),
            "first_touch_timestamp": data["sessions"][0]["timestamp"],
            "last_touch_timestamp": latest_session["timestamp"]
        }

class MarketingChannelTool(BaseTool):
    """Tool for analyzing marketing channel performance."""
    name: str = "analyze_channel_performance"
    description: str = "Analyze marketing channel performance metrics"
    args_schema: type = AttributionQueryInput

    def _run(self, merchant_id: str, email: str, date_range: str = "30d") -> Dict[str, Any]:
        """Analyze marketing channel performance (sync version)."""
        # Return mock data for development
        return {
            "channels": [
                {
                    "channel": "paid_search",
                    "leads_generated": 150,
                    "conversion_rate": 0.12,
                    "cost_per_lead": 45.50,
                    "average_lead_score": 75.5,
                    "roi": 2.8
                },
                {
                    "channel": "organic_search",
                    "leads_generated": 80,
                    "conversion_rate": 0.08,
                    "cost_per_lead": 0.0,
                    "average_lead_score": 68.0,
                    "roi": float('inf')
                },
                {
                    "channel": "referral",
                    "leads_generated": 45,
                    "conversion_rate": 0.15,
                    "cost_per_lead": 25.75,
                    "average_lead_score": 82.5,
                    "roi": 3.2
                }
            ],
            "top_performing_channel": "paid_search",
            "total_leads": 275,
            "average_conversion_rate": 0.11,
            "total_marketing_spend": 7500.0
        }
    
    async def _arun(self, merchant_id: str, email: str, date_range: str = "30d") -> Dict[str, Any]:
        """Analyze marketing channel performance (async version)."""
        if not os.getenv("MARKETING_API_KEY"):
            return self._run(merchant_id, email, date_range)

        # Implementation for actual API call would go here
        return await self._get_channel_performance(merchant_id, email, date_range)

    async def _get_channel_performance(self, merchant_id: str, email: str, date_range: str) -> Dict[str, Any]:
        """Get actual channel performance data from marketing analytics API."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {os.getenv('MARKETING_API_KEY')}",
                "Content-Type": "application/json"
            }
            url = f"{os.getenv('MARKETING_API_URL')}/analytics/channel-performance"
            
            params = {
                "merchant_id": merchant_id,
                "date_range": date_range
            }
            
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
                return self._process_channel_data(data)

    def _process_channel_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize channel performance data."""
        channels = []
        total_leads = 0
        total_conversions = 0
        total_spend = 0
        
        for channel in data.get("channels", []):
            processed_channel = {
                "channel": channel["name"],
                "leads_generated": channel["leads"],
                "conversion_rate": channel["conversions"] / channel["leads"],
                "cost_per_lead": channel["spend"] / channel["leads"] if channel["leads"] > 0 else 0,
                "average_lead_score": channel["average_score"],
                "roi": (channel["revenue"] - channel["spend"]) / channel["spend"] if channel["spend"] > 0 else float('inf')
            }
            channels.append(processed_channel)
            total_leads += channel["leads"]
            total_conversions += channel["conversions"]
            total_spend += channel["spend"]
        
        # Find top performing channel based on ROI
        top_channel = max(channels, key=lambda x: x["roi"])
        
        return {
            "channels": channels,
            "top_performing_channel": top_channel["channel"],
            "total_leads": total_leads,
            "average_conversion_rate": total_conversions / total_leads if total_leads > 0 else 0,
            "total_marketing_spend": total_spend
        }

class AttributionAnalysisTool(BaseTool):
    """Tool for comprehensive attribution analysis."""
    name: str = "analyze_attribution"
    description: str = "Perform comprehensive attribution analysis across all channels"
    args_schema: type = AttributionQueryInput

    def _run(self, merchant_id: str, email: str, date_range: str = "30d") -> Dict[str, Any]:
        """Perform comprehensive attribution analysis (sync version)."""
        # Return mock data for development
        return {
            "attribution_data": {
                "utm_source": "google",
                "utm_medium": "cpc",
                "channel_group": "paid_search"
            },
            "channel_performance": {
                "channels": [{
                    "channel": "paid_search",
                    "leads_generated": 150,
                    "conversion_rate": 0.12,
                    "roi": 2.8
                }]
            },
            "analysis": {
                "lead_quality": 75.0,
                "channel_effectiveness": {"effectiveness_score": 0.8, "confidence": "high"}
            }
        }
    
    async def _arun(self, merchant_id: str, email: str, date_range: str = "30d") -> Dict[str, Any]:
        """Perform comprehensive attribution analysis (async version)."""
        return self._run(merchant_id, email, date_range)

    def _analyze_attribution(self, attribution_data: Dict[str, Any], channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze combined attribution and channel performance data."""
        current_channel = attribution_data.get("channel_group")
        channel_metrics = next(
            (c for c in channel_data.get("channels", []) if c["channel"] == current_channel),
            None
        )
        
        return {
            "lead_quality": self._calculate_lead_quality(attribution_data, channel_metrics),
            "channel_effectiveness": self._analyze_channel_effectiveness(channel_metrics),
            "attribution_path": {
                "first_touch": attribution_data.get("utm_source"),
                "last_touch": attribution_data.get("referrer"),
                "key_touchpoints": [
                    {
                        "channel": attribution_data.get("utm_source"),
                        "medium": attribution_data.get("utm_medium"),
                        "campaign": attribution_data.get("utm_campaign")
                    }
                ]
            },
            "recommendations": self._generate_recommendations(attribution_data, channel_metrics)
        }

    def _calculate_lead_quality(self, attribution_data: Dict[str, Any], channel_metrics: Optional[Dict[str, Any]]) -> float:
        """Calculate lead quality score based on attribution data."""
        if not channel_metrics:
            return 0.0
        
        # Implement sophisticated lead quality scoring
        base_score = channel_metrics.get("average_lead_score", 0)
        conversion_multiplier = channel_metrics.get("conversion_rate", 0) * 100
        
        return min(base_score * (1 + conversion_multiplier), 100)

    def _analyze_channel_effectiveness(self, channel_metrics: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the effectiveness of the current channel."""
        if not channel_metrics:
            return {"effectiveness_score": 0, "confidence": "low"}
        
        effectiveness_score = (
            channel_metrics.get("roi", 0) * 0.4 +
            channel_metrics.get("conversion_rate", 0) * 0.3 +
            (channel_metrics.get("average_lead_score", 0) / 100) * 0.3
        )
        
        return {
            "effectiveness_score": effectiveness_score,
            "confidence": "high" if effectiveness_score > 0.7 else "medium" if effectiveness_score > 0.4 else "low"
        }

    def _generate_recommendations(self, attribution_data: Dict[str, Any], channel_metrics: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations based on attribution analysis."""
        recommendations = []
        
        if channel_metrics:
            if channel_metrics.get("roi", 0) < 2.0:
                recommendations.append({
                    "type": "optimization",
                    "action": "review_channel_spend",
                    "description": "Channel ROI is below target. Consider optimizing spend or reviewing targeting."
                })
            
            if channel_metrics.get("conversion_rate", 0) < 0.1:
                recommendations.append({
                    "type": "conversion",
                    "action": "improve_conversion_path",
                    "description": "Low conversion rate detected. Review landing page and form optimization opportunities."
                })
        
        if attribution_data.get("utm_campaign"):
            recommendations.append({
                "type": "campaign",
                "action": "campaign_tracking",
                "description": "Ensure consistent UTM parameters across all campaign touchpoints."
            })
        
        return recommendations