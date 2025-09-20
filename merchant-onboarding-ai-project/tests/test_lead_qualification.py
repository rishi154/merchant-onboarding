"""Integration tests for Lead Qualification Agent with CRM and attribution capabilities."""
import pytest
import asyncio
import os
import sys
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.state import MerchantOnboardingState
from agents.lead-qualification.src.agent import lead_qualification_agent

class TestLeadQualificationAgent:
    """Test suite for Lead Qualification Agent."""

    @pytest.fixture
    def state(self) -> MerchantOnboardingState:
        """Create a test state fixture."""
        return MerchantOnboardingState(
            application_data={
                "business_name": "Test Merchant LLC",
                "email": "test@merchant.com",
                "annual_revenue": 500000,
                "country": "US",
                "platform": "shopify",
                "marketing_source": "google_ads",
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "merchant_acquisition_2025"
            },
            market_qualification={
                "qualified": True,
                "score": 0.85,
                "reasons": ["Revenue above threshold", "Supported geography"]
            }
        )

    @pytest.mark.asyncio
    async def test_lead_qualification_success(self, state: MerchantOnboardingState):
        """Test successful lead qualification with CRM and attribution data."""
        result = await lead_qualification_agent(state)
        
        assert "lead_qualification" in result
        qualification = result["lead_qualification"]
        
        # Verify core qualification
        assert "qualified" in qualification
        assert isinstance(qualification["qualified"], bool)
        
        # Verify lead details
        assert "lead_details" in qualification
        lead_details = qualification["lead_details"]
        assert isinstance(lead_details["consolidated_score"], (int, float))
        assert isinstance(lead_details["conversion_probability"], float)
        assert lead_details["priority_level"] in ["HIGH", "MEDIUM", "LOW"]
        
        # Verify marketing insights
        assert "marketing_insights" in qualification
        insights = qualification["marketing_insights"]
        assert "channel_performance" in insights
        assert "attribution_path" in insights
        assert "channel_effectiveness" in insights
        
        # Verify CRM data
        assert "crm_data" in qualification
        crm_data = qualification["crm_data"]
        assert "engagement_history" in crm_data
        assert "lead_status" in crm_data
        
        # Verify recommendations and actions
        assert "recommendations" in qualification
        assert isinstance(qualification["recommendations"], list)
        assert "next_actions" in qualification
        assert isinstance(qualification["next_actions"], list)

    @pytest.mark.asyncio
    async def test_lead_qualification_low_revenue(self, state: MerchantOnboardingState):
        """Test lead qualification with low revenue merchant."""
        state.application_data["annual_revenue"] = 50000
        result = await lead_qualification_agent(state)
        
        qualification = result["lead_qualification"]
        assert not qualification["qualified"]
        assert qualification["lead_details"]["priority_level"] == "LOW"
        
        # Verify nurturing recommendations
        recommendations = qualification["recommendations"]
        assert any(r["type"] == "nurturing" for r in recommendations)

    @pytest.mark.asyncio
    async def test_lead_qualification_high_engagement(self, state: MerchantOnboardingState):
        """Test lead qualification with high engagement metrics."""
        # Mock high engagement in market qualification
        state.market_qualification["score"] = 0.95
        
        result = await lead_qualification_agent(state)
        qualification = result["lead_qualification"]
        
        assert qualification["qualified"]
        assert qualification["lead_details"]["priority_level"] == "HIGH"
        
        # Verify expedited review action
        actions = qualification["next_actions"]
        assert any(a["action"] == "expedited_review" for a in actions)

    @pytest.mark.asyncio
    async def test_lead_qualification_missing_data(self, state: MerchantOnboardingState):
        """Test lead qualification with missing data fields."""
        # Remove some fields
        del state.application_data["marketing_source"]
        del state.application_data["utm_source"]
        
        result = await lead_qualification_agent(state)
        qualification = result["lead_qualification"]
        
        # Should still work with fallback values
        assert "qualified" in qualification
        assert "lead_details" in qualification
        assert "marketing_insights" in qualification

    @pytest.mark.asyncio
    async def test_lead_qualification_poor_channel_performance(self, state: MerchantOnboardingState):
        """Test lead qualification with poor channel performance."""
        # Set up a scenario with poor channel metrics
        state.application_data.update({
            "marketing_source": "paid_social",
            "utm_source": "facebook",
            "utm_medium": "cpc",
            "utm_campaign": "test_campaign"
        })
        
        result = await lead_qualification_agent(state)
        qualification = result["lead_qualification"]
        
        # Verify channel optimization recommendations
        actions = qualification["next_actions"]
        assert any(
            a["action"] == "channel_optimization" and a["owner"] == "marketing_team"
            for a in actions
        )

    @pytest.mark.asyncio
    async def test_lead_qualification_error_handling(self, state: MerchantOnboardingState):
        """Test lead qualification error handling and fallback."""
        # Simulate an error by providing invalid data
        state.application_data = {"invalid": "data"}
        
        result = await lead_qualification_agent(state)
        qualification = result["lead_qualification"]
        
        # Should return fallback result
        assert "qualified" in qualification
        assert "lead_details" in qualification
        assert qualification["recommendations"][0]["type"] == "fallback"
        assert qualification["processing_time"] == 0.1

if __name__ == "__main__":
    pytest.main([__file__])