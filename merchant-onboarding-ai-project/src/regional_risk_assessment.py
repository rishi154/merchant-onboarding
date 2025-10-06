"""Regional risk assessment with jurisdiction-specific models"""
from typing import Dict, Any, List
import json
from jurisdiction_service import JurisdictionService

class RegionalRiskAssessment:
    """Risk assessment with regional models and data sources"""
    
    def __init__(self, jurisdiction: str = "US"):
        self.jurisdiction = jurisdiction
        self.jurisdiction_service = JurisdictionService()
        self.config = self.jurisdiction_service.get_jurisdiction_config(jurisdiction)
        
        # Load jurisdiction-specific risk factors
        self.risk_factors = self._get_risk_factors(jurisdiction)
        self.risk_weights = self._get_risk_weights(jurisdiction)
        
    def _get_risk_factors(self, jurisdiction: str) -> List[str]:
        """Get jurisdiction-specific risk factors"""
        factors = {
            "US": [
                "credit_score", "business_age", "industry_risk", "state_risk",
                "annual_revenue", "debt_to_income", "previous_bankruptcies"
            ],
            "UK": [
                "companies_house_status", "credit_rating", "industry_risk", 
                "vat_status", "business_age", "annual_turnover", "county_risk"
            ],
            "EU": [
                "vat_status", "trade_register_status", "industry_risk",
                "country_risk", "business_age", "annual_revenue", "eu_compliance"
            ],
            "CA": [
                "credit_score", "business_age", "industry_risk", "province_risk",
                "annual_revenue", "cra_status", "previous_insolvencies"
            ]
        }
        
        return factors.get(jurisdiction, factors["US"])
    
    def _get_risk_weights(self, jurisdiction: str) -> Dict[str, float]:
        """Get jurisdiction-specific risk factor weights"""
        weights = {
            "US": {
                "credit_score": 0.25,
                "business_age": 0.15,
                "industry_risk": 0.20,
                "state_risk": 0.10,
                "annual_revenue": 0.15,
                "debt_to_income": 0.10,
                "previous_bankruptcies": 0.05
            },
            "UK": {
                "companies_house_status": 0.20,
                "credit_rating": 0.25,
                "industry_risk": 0.20,
                "vat_status": 0.10,
                "business_age": 0.15,
                "annual_turnover": 0.10
            },
            "EU": {
                "vat_status": 0.15,
                "trade_register_status": 0.20,
                "industry_risk": 0.20,
                "country_risk": 0.15,
                "business_age": 0.15,
                "annual_revenue": 0.10,
                "eu_compliance": 0.05
            },
            "CA": {
                "credit_score": 0.25,
                "business_age": 0.15,
                "industry_risk": 0.20,
                "province_risk": 0.10,
                "annual_revenue": 0.15,
                "cra_status": 0.10,
                "previous_insolvencies": 0.05
            }
        }
        
        return weights.get(jurisdiction, weights["US"])
    
    async def assess_risk(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform jurisdiction-specific risk assessment"""
        
        # Auto-detect jurisdiction if needed
        detected_jurisdiction = self.jurisdiction_service.detect_jurisdiction(merchant_data)
        if detected_jurisdiction != self.jurisdiction:
            self.jurisdiction = detected_jurisdiction
            self.risk_factors = self._get_risk_factors(detected_jurisdiction)
            self.risk_weights = self._get_risk_weights(detected_jurisdiction)
        
        risk_scores = {}
        total_weighted_score = 0.0
        
        # Calculate individual risk factor scores
        for factor in self.risk_factors:
            factor_score = await self._calculate_factor_score(factor, merchant_data)
            risk_scores[factor] = factor_score
            
            weight = self.risk_weights.get(factor, 0.0)
            total_weighted_score += factor_score * weight
        
        # Normalize to 0-100 scale
        final_risk_score = min(100, max(0, total_weighted_score))
        
        # Determine risk category
        risk_category = self._determine_risk_category(final_risk_score)
        
        # Get jurisdiction-specific recommendations
        recommendations = self._get_risk_recommendations(final_risk_score, risk_scores)
        
        return {
            "jurisdiction": self.jurisdiction,
            "overall_risk_score": round(final_risk_score, 2),
            "risk_category": risk_category,
            "individual_scores": risk_scores,
            "risk_factors_used": self.risk_factors,
            "recommendations": recommendations,
            "processing_limits": self._get_processing_limits(risk_category),
            "monitoring_requirements": self._get_monitoring_requirements(risk_category)
        }
    
    async def _calculate_factor_score(self, factor: str, merchant_data: Dict) -> float:
        """Calculate score for individual risk factor"""
        
        if factor == "credit_score":
            return await self._assess_credit_score(merchant_data)
        elif factor == "business_age":
            return await self._assess_business_age(merchant_data)
        elif factor == "industry_risk":
            return await self._assess_industry_risk(merchant_data)
        elif factor == "annual_revenue":
            return await self._assess_revenue_risk(merchant_data)
        elif factor == "companies_house_status":
            return await self._assess_companies_house_status(merchant_data)
        elif factor == "vat_status":
            return await self._assess_vat_status(merchant_data)
        elif factor == "country_risk":
            return await self._assess_country_risk(merchant_data)
        elif factor == "province_risk":
            return await self._assess_province_risk(merchant_data)
        else:
            return 50.0  # Default neutral score
    
    async def _assess_credit_score(self, merchant_data: Dict) -> float:
        """Assess credit score risk"""
        credit_score = merchant_data.get("credit_score", 650)
        
        if credit_score >= 750:
            return 20.0  # Low risk
        elif credit_score >= 650:
            return 40.0  # Medium risk
        elif credit_score >= 550:
            return 70.0  # High risk
        else:
            return 90.0  # Very high risk
    
    async def _assess_business_age(self, merchant_data: Dict) -> float:
        """Assess business age risk"""
        business_age_years = merchant_data.get("business_age_years", 0)
        
        if business_age_years >= 5:
            return 20.0  # Low risk
        elif business_age_years >= 2:
            return 40.0  # Medium risk
        elif business_age_years >= 1:
            return 60.0  # High risk
        else:
            return 80.0  # Very high risk
    
    async def _assess_industry_risk(self, merchant_data: Dict) -> float:
        """Assess industry-specific risk"""
        industry = merchant_data.get("industry", "").lower()
        
        high_risk_industries = [
            "gambling", "adult", "cryptocurrency", "forex", "debt_collection",
            "payday_loans", "telemarketing", "travel", "timeshare"
        ]
        
        medium_risk_industries = [
            "restaurants", "retail", "ecommerce", "professional_services",
            "healthcare", "education", "real_estate"
        ]
        
        if industry in high_risk_industries:
            return 80.0
        elif industry in medium_risk_industries:
            return 40.0
        else:
            return 30.0  # Low risk for standard industries
    
    async def _assess_revenue_risk(self, merchant_data: Dict) -> float:
        """Assess revenue-based risk"""
        annual_revenue = merchant_data.get("annual_revenue", 0)
        
        if annual_revenue >= 1000000:  # $1M+
            return 25.0  # Low risk
        elif annual_revenue >= 500000:  # $500K+
            return 35.0  # Medium-low risk
        elif annual_revenue >= 100000:  # $100K+
            return 50.0  # Medium risk
        elif annual_revenue >= 50000:   # $50K+
            return 65.0  # Medium-high risk
        else:
            return 80.0  # High risk
    
    async def _assess_companies_house_status(self, merchant_data: Dict) -> float:
        """Assess UK Companies House status"""
        companies_house_status = merchant_data.get("companies_house_status", "unknown")
        
        if companies_house_status == "active":
            return 20.0
        elif companies_house_status == "dormant":
            return 40.0
        elif companies_house_status == "liquidation":
            return 90.0
        else:
            return 60.0  # Unknown status
    
    async def _assess_vat_status(self, merchant_data: Dict) -> float:
        """Assess VAT registration status"""
        vat_registered = merchant_data.get("vat_registered", False)
        annual_revenue = merchant_data.get("annual_revenue", 0)
        
        # In EU/UK, businesses above threshold should be VAT registered
        vat_threshold = 85000 if self.jurisdiction == "UK" else 100000  # Simplified
        
        if annual_revenue > vat_threshold and not vat_registered:
            return 70.0  # High risk - should be VAT registered
        elif vat_registered:
            return 25.0  # Low risk - properly registered
        else:
            return 40.0  # Medium risk - below threshold
    
    async def _assess_country_risk(self, merchant_data: Dict) -> float:
        """Assess country-specific risk for EU"""
        country = merchant_data.get("country", "").upper()
        
        low_risk_countries = ["DE", "FR", "NL", "AT", "DK", "SE", "FI"]
        medium_risk_countries = ["IT", "ES", "PT", "IE", "BE", "LU"]
        high_risk_countries = ["BG", "RO", "HR", "HU", "PL", "CZ", "SK"]
        
        if country in low_risk_countries:
            return 25.0
        elif country in medium_risk_countries:
            return 45.0
        elif country in high_risk_countries:
            return 65.0
        else:
            return 50.0  # Unknown country
    
    async def _assess_province_risk(self, merchant_data: Dict) -> float:
        """Assess province-specific risk for Canada"""
        province = merchant_data.get("province", "").upper()
        
        low_risk_provinces = ["ON", "BC", "AB", "QC"]
        medium_risk_provinces = ["MB", "SK", "NS", "NB"]
        
        if province in low_risk_provinces:
            return 30.0
        elif province in medium_risk_provinces:
            return 45.0
        else:
            return 55.0  # Territories or unknown
    
    def _determine_risk_category(self, risk_score: float) -> str:
        """Determine risk category based on score"""
        if risk_score <= 30:
            return "LOW"
        elif risk_score <= 50:
            return "MEDIUM_LOW"
        elif risk_score <= 70:
            return "MEDIUM"
        elif risk_score <= 85:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _get_risk_recommendations(self, risk_score: float, individual_scores: Dict) -> List[str]:
        """Get jurisdiction-specific risk recommendations"""
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("Enhanced due diligence required")
            recommendations.append("Additional documentation needed")
            recommendations.append("Senior underwriter review recommended")
        
        if risk_score > 85:
            recommendations.append("Consider declining application")
            recommendations.append("Manual review by risk committee")
        
        # Factor-specific recommendations
        if individual_scores.get("credit_score", 0) > 70:
            recommendations.append("Verify credit information with additional sources")
        
        if individual_scores.get("business_age", 0) > 60:
            recommendations.append("Request additional business history documentation")
        
        return recommendations
    
    def _get_processing_limits(self, risk_category: str) -> Dict[str, Any]:
        """Get processing limits based on risk category"""
        limits = {
            "LOW": {
                "daily_limit": 50000,
                "monthly_limit": 1000000,
                "single_transaction_limit": 10000
            },
            "MEDIUM_LOW": {
                "daily_limit": 25000,
                "monthly_limit": 500000,
                "single_transaction_limit": 5000
            },
            "MEDIUM": {
                "daily_limit": 10000,
                "monthly_limit": 200000,
                "single_transaction_limit": 2500
            },
            "HIGH": {
                "daily_limit": 5000,
                "monthly_limit": 50000,
                "single_transaction_limit": 1000
            },
            "VERY_HIGH": {
                "daily_limit": 1000,
                "monthly_limit": 10000,
                "single_transaction_limit": 500
            }
        }
        
        return limits.get(risk_category, limits["MEDIUM"])
    
    def _get_monitoring_requirements(self, risk_category: str) -> Dict[str, Any]:
        """Get monitoring requirements based on risk category"""
        monitoring = {
            "LOW": {
                "review_frequency": "quarterly",
                "transaction_monitoring": "standard",
                "reporting_required": False
            },
            "MEDIUM_LOW": {
                "review_frequency": "monthly",
                "transaction_monitoring": "enhanced",
                "reporting_required": False
            },
            "MEDIUM": {
                "review_frequency": "bi_weekly",
                "transaction_monitoring": "enhanced",
                "reporting_required": True
            },
            "HIGH": {
                "review_frequency": "weekly",
                "transaction_monitoring": "intensive",
                "reporting_required": True
            },
            "VERY_HIGH": {
                "review_frequency": "daily",
                "transaction_monitoring": "real_time",
                "reporting_required": True
            }
        }
        
        return monitoring.get(risk_category, monitoring["MEDIUM"])