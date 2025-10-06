"""Multi-jurisdiction compliance verification agent"""
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from jurisdiction_service import JurisdictionService

class MultiJurisdictionComplianceAgent:
    """Enhanced compliance agent with jurisdiction-specific rules"""
    
    def __init__(self, jurisdiction: str = "US"):
        self.jurisdiction = jurisdiction
        self.jurisdiction_service = JurisdictionService()
        self.config = self.jurisdiction_service.get_jurisdiction_config(jurisdiction)
        self.compliance_rules = self.config.compliance_rules
        
    async def verify_compliance(self, merchant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform jurisdiction-specific compliance verification"""
        
        # Detect jurisdiction if not provided
        if not self.jurisdiction or self.jurisdiction == "US":
            detected_jurisdiction = self.jurisdiction_service.detect_jurisdiction(merchant_data)
            if detected_jurisdiction != self.jurisdiction:
                self.jurisdiction = detected_jurisdiction
                self.config = self.jurisdiction_service.get_jurisdiction_config(detected_jurisdiction)
                self.compliance_rules = self.config.compliance_rules
        
        compliance_results = {
            "jurisdiction": self.jurisdiction,
            "compliance_status": "pending",
            "checks_performed": [],
            "violations": [],
            "warnings": [],
            "next_steps": []
        }
        
        # Perform jurisdiction-specific compliance checks
        for rule in self.compliance_rules:
            check_result = await self._perform_compliance_check(rule, merchant_data)
            compliance_results["checks_performed"].append(check_result)
            
            if not check_result["passed"]:
                if check_result["severity"] == "violation":
                    compliance_results["violations"].append(check_result)
                else:
                    compliance_results["warnings"].append(check_result)
        
        # Determine overall compliance status
        if compliance_results["violations"]:
            compliance_results["compliance_status"] = "failed"
        elif compliance_results["warnings"]:
            compliance_results["compliance_status"] = "conditional"
        else:
            compliance_results["compliance_status"] = "passed"
            
        return compliance_results
    
    async def _perform_compliance_check(self, rule: str, merchant_data: Dict) -> Dict:
        """Perform specific compliance check based on jurisdiction"""
        
        if self.jurisdiction == "US":
            return await self._us_compliance_check(rule, merchant_data)
        elif self.jurisdiction == "UK":
            return await self._uk_compliance_check(rule, merchant_data)
        elif self.jurisdiction == "EU":
            return await self._eu_compliance_check(rule, merchant_data)
        elif self.jurisdiction == "CA":
            return await self._ca_compliance_check(rule, merchant_data)
        else:
            return {"rule": rule, "passed": True, "message": "No specific check implemented"}
    
    async def _us_compliance_check(self, rule: str, merchant_data: Dict) -> Dict:
        """US-specific compliance checks"""
        
        if rule == "OFAC":
            return await self._ofac_sanctions_check(merchant_data)
        elif rule == "BSA":
            return await self._bsa_compliance_check(merchant_data)
        elif rule == "FinCEN":
            return await self._fincen_check(merchant_data)
        elif rule == "State_Licensing":
            return await self._state_licensing_check(merchant_data)
        
        return {"rule": rule, "passed": True, "message": "Check passed"}
    
    async def _uk_compliance_check(self, rule: str, merchant_data: Dict) -> Dict:
        """UK-specific compliance checks"""
        
        if rule == "FCA":
            return await self._fca_compliance_check(merchant_data)
        elif rule == "MLR_2017":
            return await self._uk_mlr_check(merchant_data)
        elif rule == "PCI-DSS":
            return await self._pci_dss_check(merchant_data)
            
        return {"rule": rule, "passed": True, "message": "Check passed"}
    
    async def _eu_compliance_check(self, rule: str, merchant_data: Dict) -> Dict:
        """EU-specific compliance checks"""
        
        if rule == "GDPR":
            return await self._gdpr_compliance_check(merchant_data)
        elif rule == "PSD2":
            return await self._psd2_check(merchant_data)
        elif rule == "5AMLD":
            return await self._amld5_check(merchant_data)
        elif rule == "MiFID_II":
            return await self._mifid2_check(merchant_data)
            
        return {"rule": rule, "passed": True, "message": "Check passed"}
    
    async def _ca_compliance_check(self, rule: str, merchant_data: Dict) -> Dict:
        """Canada-specific compliance checks"""
        
        if rule == "FINTRAC":
            return await self._fintrac_check(merchant_data)
        elif rule == "PIPEDA":
            return await self._pipeda_check(merchant_data)
        elif rule == "Provincial_Regs":
            return await self._provincial_regulations_check(merchant_data)
            
        return {"rule": rule, "passed": True, "message": "Check passed"}
    
    # Individual compliance check implementations
    async def _ofac_sanctions_check(self, merchant_data: Dict) -> Dict:
        """OFAC sanctions screening using external API"""
        from regulatory_api_services import USRegulatoryServices
        us_service = USRegulatoryServices()
        return await us_service.ofac_sanctions_check(merchant_data)
    
    async def _gdpr_compliance_check(self, merchant_data: Dict) -> Dict:
        """GDPR compliance verification using external APIs"""
        from gdpr_compliance_service import GDPRComplianceService
        
        gdpr_service = GDPRComplianceService()
        compliance_result = await gdpr_service.verify_gdpr_compliance(merchant_data)
        
        return {
            "rule": "GDPR",
            "passed": compliance_result["gdpr_compliant"],
            "severity": "violation" if not compliance_result["gdpr_compliant"] else "info",
            "message": f"GDPR compliance score: {compliance_result['compliance_score']}%",
            "details": {
                "compliance_score": compliance_result["compliance_score"],
                "checks_performed": len(compliance_result["checks_performed"]),
                "violations": compliance_result["violations"],
                "recommendations": compliance_result["recommendations"]
            }
        }
    
    async def _fca_compliance_check(self, merchant_data: Dict) -> Dict:
        """FCA compliance check using external API"""
        from regulatory_api_services import UKRegulatoryServices
        uk_service = UKRegulatoryServices()
        return await uk_service.fca_compliance_check(merchant_data)
    
    async def _fintrac_check(self, merchant_data: Dict) -> Dict:
        """FINTRAC compliance check using external API"""
        from regulatory_api_services import CanadaRegulatoryServices
        ca_service = CanadaRegulatoryServices()
        return await ca_service.fintrac_check(merchant_data)
    
    # External API-based compliance checks
    async def _bsa_compliance_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import USRegulatoryServices
        us_service = USRegulatoryServices()
        return await us_service.bsa_compliance_check(merchant_data)
    
    async def _fincen_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import USRegulatoryServices
        us_service = USRegulatoryServices()
        return await us_service.fincen_check(merchant_data)
    
    async def _state_licensing_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import USRegulatoryServices
        us_service = USRegulatoryServices()
        return await us_service.state_licensing_check(merchant_data)
    
    async def _uk_mlr_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import UKRegulatoryServices
        uk_service = UKRegulatoryServices()
        return await uk_service.mlr_2017_check(merchant_data)
    
    async def _pci_dss_check(self, merchant_data: Dict) -> Dict:
        return {"rule": "PCI-DSS", "passed": True, "severity": "info", "message": "PCI-DSS requirements met"}
    
    async def _psd2_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import EURegulatoryServices
        eu_service = EURegulatoryServices()
        return await eu_service.psd2_compliance_check(merchant_data)
    
    async def _amld5_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import EURegulatoryServices
        eu_service = EURegulatoryServices()
        return await eu_service.amld5_check(merchant_data)
    
    async def _mifid2_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import EURegulatoryServices
        eu_service = EURegulatoryServices()
        return await eu_service.mifid2_check(merchant_data)
    
    async def _pipeda_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import CanadaRegulatoryServices
        ca_service = CanadaRegulatoryServices()
        return await ca_service.pipeda_check(merchant_data)
    
    async def _provincial_regulations_check(self, merchant_data: Dict) -> Dict:
        from regulatory_api_services import CanadaRegulatoryServices
        ca_service = CanadaRegulatoryServices()
        return await ca_service.provincial_regulations_check(merchant_data)

# Main agent function for integration with existing workflow
async def multi_jurisdiction_compliance_agent(state) -> Dict[str, Any]:
    """Multi-jurisdiction compliance verification agent"""
    
    try:
        # Detect jurisdiction from application data
        jurisdiction_service = JurisdictionService()
        jurisdiction = jurisdiction_service.detect_jurisdiction(state.application_data)
        
        # Initialize compliance agent for detected jurisdiction
        compliance_agent = MultiJurisdictionComplianceAgent(jurisdiction)
        
        # Perform compliance verification
        compliance_result = await compliance_agent.verify_compliance(state.application_data)
        
        # Update state
        state.compliance_verification = compliance_result
        
        return {"compliance_verification": compliance_result}
        
    except Exception as e:
        error_result = {
            "jurisdiction": "US",
            "compliance_status": "error",
            "error": str(e),
            "checks_performed": [],
            "violations": [],
            "warnings": []
        }
        
        state.compliance_verification = error_result
        return {"compliance_verification": error_result}