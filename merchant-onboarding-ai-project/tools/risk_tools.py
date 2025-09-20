from langchain.tools import BaseTool
from typing import Dict, Any
from pydantic import BaseModel, Field
import asyncio
from config.tool_config import ToolConfig

class FinancialRiskInput(BaseModel):
    business_data: Dict[str, Any] = Field(description="Business financial data for risk assessment")

class IndustryRiskInput(BaseModel):
    industry: str = Field(description="Industry sector")
    country: str = Field(description="Country of operation", default="US")

class CreditRiskInput(BaseModel):
    business_data: Dict[str, Any] = Field(description="Business data for credit risk scoring")

class FinancialRiskTool(BaseTool):
    name: str = "financial_risk_assessment"
    description: str = "Assess financial risk based on revenue, cash flow, and financial stability"
    args_schema: type = FinancialRiskInput
    
    def _run(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self._arun(business_data))
    
    async def _arun(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess financial risk factors"""
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'risk-assessment', 'src'))
        
        try:
            # Mock financial risk assessment
            revenue = business_data.get("annual_revenue", 0)
            years_in_business = business_data.get("years_in_business", 0)
            
            # Calculate financial risk score
            risk_score = 0.3  # Base risk
            
            if revenue < 100000:
                risk_score += 0.4
            elif revenue < 500000:
                risk_score += 0.2
            
            if years_in_business < 2:
                risk_score += 0.3
            elif years_in_business < 5:
                risk_score += 0.1
            
            return {
                "success": True,
                "financial_risk_score": min(risk_score, 1.0),
                "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low",
                "revenue_stability": "stable" if revenue > 500000 else "unstable",
                "business_maturity": "mature" if years_in_business > 5 else "developing"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "financial_risk_score": 0.8
            }

class IndustryRiskTool(BaseTool):
    name: str = "industry_risk_assessment"
    description: str = "Assess industry-specific risks and regulatory environment"
    args_schema: type = IndustryRiskInput
    
    def _run(self, industry: str, country: str = "US") -> Dict[str, Any]:
        return asyncio.run(self._arun(industry, country))
    
    async def _arun(self, industry: str, country: str = "US") -> Dict[str, Any]:
        """Assess industry risk factors"""
        try:
            # Industry risk mapping
            high_risk_industries = ["gambling", "crypto", "adult", "firearms", "cannabis"]
            medium_risk_industries = ["restaurants", "retail", "travel", "entertainment"]
            
            if industry.lower() in high_risk_industries:
                risk_level = "high"
                risk_score = 0.8
            elif industry.lower() in medium_risk_industries:
                risk_level = "medium"
                risk_score = 0.5
            else:
                risk_level = "low"
                risk_score = 0.2
            
            return {
                "success": True,
                "industry_risk_score": risk_score,
                "risk_level": risk_level,
                "industry": industry,
                "regulatory_complexity": "high" if risk_level == "high" else "medium",
                "compliance_requirements": ["standard"] if risk_level == "low" else ["enhanced", "specialized"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "industry_risk_score": 0.5
            }

class CreditRiskTool(BaseTool):
    name: str = "credit_risk_scoring"
    description: str = "Perform credit risk scoring and determine credit limits"
    args_schema: type = CreditRiskInput
    
    def _run(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self._arun(business_data))
    
    async def _arun(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate credit risk score using real or mock integration"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'integrations', 'credit-bureaus'))
            from experian import ExperianIntegration, MockExperianIntegration
            
            # Decision logic: mock or real
            use_mock = ToolConfig.MOCK_CREDIT_BUREAUS
            
            if use_mock:
                experian_integration = MockExperianIntegration()
            else:
                experian_integration = ExperianIntegration()
                
            return await experian_integration.business_credit_check(business_data)
            
        except Exception as e:
            # Fallback to simple algorithm
            revenue = business_data.get("annual_revenue", 0)
            years_in_business = business_data.get("years_in_business", 0)
            industry = business_data.get("industry", "")
            
            # Credit scoring algorithm
            credit_score = 600  # Base score
            
            # Revenue factor
            if revenue > 1000000:
                credit_score += 100
            elif revenue > 500000:
                credit_score += 50
            elif revenue > 100000:
                credit_score += 25
            
            # Business age factor
            if years_in_business > 5:
                credit_score += 50
            elif years_in_business > 2:
                credit_score += 25
            
            # Industry factor
            if industry.lower() in ["gambling", "crypto"]:
                credit_score -= 100
            
            credit_score = max(ToolConfig.CREDIT_SCORE_MIN, min(ToolConfig.CREDIT_SCORE_MAX, credit_score))
            
            # Determine credit limit
            if credit_score >= 750:
                credit_limit = min(ToolConfig.CREDIT_LIMIT_MAX, revenue * 0.2)
            elif credit_score >= 650:
                credit_limit = min(50000, revenue * 0.1)
            else:
                credit_limit = min(25000, revenue * 0.05)
            
            return {
                "success": True,
                "credit_score": credit_score,
                "credit_limit": int(credit_limit),
                "risk_tier": "low" if credit_score >= 700 else "medium" if credit_score >= 600 else "high",
                "approval_probability": 0.9 if credit_score >= 700 else 0.7 if credit_score >= 600 else 0.3,
                "fallback": True,
                "error": str(e)
            }