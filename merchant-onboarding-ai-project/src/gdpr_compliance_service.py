"""GDPR compliance verification service with external API integrations"""
from typing import Dict, Any, List
import asyncio
import aiohttp
from datetime import datetime

class GDPRComplianceService:
    """External API-based GDPR compliance verification"""
    
    GDPR_APIS = {
        "privacy_policy_analyzer": {
            "primary": "cookiebot_api",
            "secondary": "onetrust_api", 
            "tertiary": "trustarc_api"
        },
        "consent_management": {
            "primary": "cookiebot_cmp",
            "secondary": "onetrust_cmp",
            "tertiary": "quantcast_cmp"
        },
        "data_mapping": {
            "primary": "privacera_api",
            "secondary": "collibra_api",
            "tertiary": "informatica_api"
        },
        "breach_notification": {
            "primary": "gdpr_breach_api",
            "secondary": "compliance_ai_api"
        }
    }
    
    async def verify_gdpr_compliance(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive GDPR compliance verification using external APIs"""
        
        website_url = merchant_data.get("website_url", "")
        business_type = merchant_data.get("business_type", "")
        
        compliance_results = {
            "gdpr_compliant": False,
            "compliance_score": 0,
            "checks_performed": [],
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # 1. Privacy Policy Analysis
        privacy_check = await self._analyze_privacy_policy(website_url)
        compliance_results["checks_performed"].append(privacy_check)
        
        # 2. Cookie Consent Verification  
        consent_check = await self._verify_consent_mechanism(website_url)
        compliance_results["checks_performed"].append(consent_check)
        
        # 3. Data Processing Lawfulness
        lawfulness_check = await self._verify_processing_lawfulness(merchant_data)
        compliance_results["checks_performed"].append(lawfulness_check)
        
        # 4. Data Subject Rights Implementation
        rights_check = await self._verify_data_subject_rights(website_url)
        compliance_results["checks_performed"].append(rights_check)
        
        # 5. Data Protection Officer (DPO) Requirement
        dpo_check = await self._verify_dpo_requirement(merchant_data)
        compliance_results["checks_performed"].append(dpo_check)
        
        # Calculate compliance score and status
        compliance_results = self._calculate_compliance_score(compliance_results)
        
        return compliance_results
    
    async def _analyze_privacy_policy(self, website_url: str) -> Dict[str, Any]:
        """Analyze privacy policy using external API"""
        
        try:
            # Use Cookiebot API to analyze privacy policy
            analysis_result = await self._call_cookiebot_privacy_analyzer(website_url)
            
            if analysis_result["success"]:
                policy_data = analysis_result["data"]
                
                return {
                    "check_name": "privacy_policy_analysis",
                    "passed": policy_data.get("gdpr_compliant", False),
                    "score": policy_data.get("compliance_score", 0),
                    "details": {
                        "has_privacy_policy": policy_data.get("has_privacy_policy", False),
                        "gdpr_compliant": policy_data.get("gdpr_compliant", False),
                        "data_categories_disclosed": policy_data.get("data_categories", []),
                        "legal_basis_specified": policy_data.get("legal_basis_specified", False),
                        "retention_periods_specified": policy_data.get("retention_periods", False),
                        "third_party_sharing_disclosed": policy_data.get("third_party_sharing", False)
                    },
                    "violations": policy_data.get("violations", []),
                    "recommendations": policy_data.get("recommendations", [])
                }
            else:
                return self._fallback_privacy_policy_check(website_url)
                
        except Exception as e:
            return self._fallback_privacy_policy_check(website_url)
    
    async def _verify_consent_mechanism(self, website_url: str) -> Dict[str, Any]:
        """Verify cookie consent mechanism using external API"""
        
        try:
            # Use Cookiebot CMP API to verify consent mechanism
            consent_result = await self._call_cookiebot_cmp_scanner(website_url)
            
            if consent_result["success"]:
                consent_data = consent_result["data"]
                
                return {
                    "check_name": "consent_mechanism",
                    "passed": consent_data.get("compliant_consent", False),
                    "score": consent_data.get("consent_score", 0),
                    "details": {
                        "has_consent_banner": consent_data.get("has_banner", False),
                        "granular_consent": consent_data.get("granular_consent", False),
                        "withdraw_consent_option": consent_data.get("withdraw_option", False),
                        "pre_ticked_boxes": consent_data.get("pre_ticked", True),  # Violation if True
                        "consent_before_processing": consent_data.get("consent_first", False)
                    },
                    "violations": consent_data.get("violations", []),
                    "recommendations": consent_data.get("recommendations", [])
                }
            else:
                return self._fallback_consent_check(website_url)
                
        except Exception as e:
            return self._fallback_consent_check(website_url)
    
    async def _verify_processing_lawfulness(self, merchant_data: Dict) -> Dict[str, Any]:
        """Verify lawful basis for data processing"""
        
        business_type = merchant_data.get("business_type", "")
        processing_purposes = merchant_data.get("data_processing_purposes", [])
        
        # Determine required lawful basis based on business type
        required_basis = self._determine_lawful_basis(business_type, processing_purposes)
        
        declared_basis = merchant_data.get("lawful_basis", [])
        
        has_valid_basis = bool(set(required_basis).intersection(set(declared_basis)))
        
        return {
            "check_name": "processing_lawfulness",
            "passed": has_valid_basis,
            "score": 100 if has_valid_basis else 0,
            "details": {
                "required_basis": required_basis,
                "declared_basis": declared_basis,
                "processing_purposes": processing_purposes
            },
            "violations": [] if has_valid_basis else ["Missing valid lawful basis for processing"],
            "recommendations": [] if has_valid_basis else ["Specify appropriate lawful basis under GDPR Article 6"]
        }
    
    async def _verify_data_subject_rights(self, website_url: str) -> Dict[str, Any]:
        """Verify implementation of data subject rights"""
        
        try:
            # Check for data subject rights implementation
            rights_result = await self._scan_data_subject_rights(website_url)
            
            required_rights = [
                "right_to_access", "right_to_rectification", "right_to_erasure",
                "right_to_restrict_processing", "right_to_data_portability", 
                "right_to_object", "rights_related_to_automated_decision_making"
            ]
            
            implemented_rights = rights_result.get("implemented_rights", [])
            missing_rights = [right for right in required_rights if right not in implemented_rights]
            
            compliance_score = (len(implemented_rights) / len(required_rights)) * 100
            
            return {
                "check_name": "data_subject_rights",
                "passed": len(missing_rights) == 0,
                "score": compliance_score,
                "details": {
                    "implemented_rights": implemented_rights,
                    "missing_rights": missing_rights,
                    "rights_contact_method": rights_result.get("contact_method", "")
                },
                "violations": [f"Missing implementation: {right}" for right in missing_rights],
                "recommendations": ["Implement all GDPR data subject rights"] if missing_rights else []
            }
            
        except Exception as e:
            return self._fallback_rights_check()
    
    async def _verify_dpo_requirement(self, merchant_data: Dict) -> Dict[str, Any]:
        """Verify Data Protection Officer requirement"""
        
        business_type = merchant_data.get("business_type", "")
        employee_count = merchant_data.get("employee_count", 0)
        processing_scale = merchant_data.get("data_processing_scale", "small")
        
        # Determine if DPO is required
        dpo_required = self._is_dpo_required(business_type, employee_count, processing_scale)
        has_dpo = merchant_data.get("has_dpo", False)
        dpo_contact = merchant_data.get("dpo_contact", "")
        
        compliant = not dpo_required or (dpo_required and has_dpo and dpo_contact)
        
        return {
            "check_name": "dpo_requirement",
            "passed": compliant,
            "score": 100 if compliant else 0,
            "details": {
                "dpo_required": dpo_required,
                "has_dpo": has_dpo,
                "dpo_contact": dpo_contact,
                "business_type": business_type
            },
            "violations": [] if compliant else ["DPO required but not designated"],
            "recommendations": [] if compliant else ["Designate a Data Protection Officer"]
        }
    
    # External API calls
    async def _call_cookiebot_privacy_analyzer(self, website_url: str) -> Dict:
        """Call Cookiebot Privacy Policy Analyzer API"""
        from api_client_factory import APIClientFactory
        
        client = APIClientFactory.create_client("cookiebot_privacy")
        result = await client.check_compliance({"website_url": website_url})
        
        return {
            "success": result["success"],
            "data": result
        }
    
    async def _call_cookiebot_cmp_scanner(self, website_url: str) -> Dict:
        """Call Cookiebot CMP Scanner API"""
        # Mock implementation - replace with real API call
        await asyncio.sleep(0.2)
        
        return {
            "success": True,
            "data": {
                "has_banner": True,
                "compliant_consent": True,
                "consent_score": 90,
                "granular_consent": True,
                "withdraw_option": True,
                "pre_ticked": False,
                "consent_first": True,
                "violations": [],
                "recommendations": []
            }
        }
    
    async def _scan_data_subject_rights(self, website_url: str) -> Dict:
        """Scan website for data subject rights implementation"""
        # Mock implementation - replace with real scanning logic
        await asyncio.sleep(0.1)
        
        return {
            "implemented_rights": [
                "right_to_access", "right_to_rectification", "right_to_erasure",
                "right_to_restrict_processing", "right_to_data_portability"
            ],
            "contact_method": "privacy@merchant.com"
        }
    
    # Helper methods
    def _determine_lawful_basis(self, business_type: str, purposes: List[str]) -> List[str]:
        """Determine required lawful basis based on business type and purposes"""
        
        basis_mapping = {
            "e_commerce": ["contract", "legitimate_interest"],
            "financial_services": ["contract", "legal_obligation"],
            "healthcare": ["consent", "vital_interests"],
            "marketing": ["consent", "legitimate_interest"],
            "default": ["consent", "contract"]
        }
        
        return basis_mapping.get(business_type.lower(), basis_mapping["default"])
    
    def _is_dpo_required(self, business_type: str, employee_count: int, processing_scale: str) -> bool:
        """Determine if DPO is required"""
        
        # DPO required for public authorities, large scale processing, or special categories
        if business_type.lower() in ["public_authority", "government"]:
            return True
        
        if processing_scale in ["large", "systematic"]:
            return True
            
        if employee_count > 250:  # Generally considered large scale
            return True
            
        return False
    
    def _calculate_compliance_score(self, results: Dict) -> Dict:
        """Calculate overall GDPR compliance score"""
        
        checks = results["checks_performed"]
        if not checks:
            results["compliance_score"] = 0
            results["gdpr_compliant"] = False
            return results
        
        total_score = sum(check.get("score", 0) for check in checks)
        average_score = total_score / len(checks)
        
        results["compliance_score"] = round(average_score, 2)
        results["gdpr_compliant"] = average_score >= 80  # 80% threshold
        
        # Collect violations and recommendations
        for check in checks:
            results["violations"].extend(check.get("violations", []))
            results["recommendations"].extend(check.get("recommendations", []))
        
        return results
    
    # Fallback methods when APIs fail
    def _fallback_privacy_policy_check(self, website_url: str) -> Dict:
        return {
            "check_name": "privacy_policy_analysis",
            "passed": False,
            "score": 0,
            "details": {"error": "Could not analyze privacy policy"},
            "violations": ["Privacy policy analysis failed"],
            "recommendations": ["Manual privacy policy review required"]
        }
    
    def _fallback_consent_check(self, website_url: str) -> Dict:
        return {
            "check_name": "consent_mechanism", 
            "passed": False,
            "score": 0,
            "details": {"error": "Could not verify consent mechanism"},
            "violations": ["Consent mechanism verification failed"],
            "recommendations": ["Manual consent mechanism review required"]
        }
    
    def _fallback_rights_check(self) -> Dict:
        return {
            "check_name": "data_subject_rights",
            "passed": False,
            "score": 0,
            "details": {"error": "Could not verify data subject rights"},
            "violations": ["Data subject rights verification failed"],
            "recommendations": ["Manual data subject rights review required"]
        }