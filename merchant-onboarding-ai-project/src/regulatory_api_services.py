"""External API services for regulatory compliance verification"""
from typing import Dict, Any, List
from api_client_factory import APIClientFactory

class USRegulatoryServices:
    """US regulatory compliance API services"""
    
    async def ofac_sanctions_check(self, merchant_data: Dict) -> Dict:
        """OFAC sanctions screening via Treasury API"""
        business_name = merchant_data.get("business_name", "")
        owner_name = merchant_data.get("owner_name", "")
        
        # Call OFAC Sanctions List API
        result = await self._call_ofac_api({
            "business_name": business_name,
            "owner_name": owner_name,
            "address": merchant_data.get("business_address", "")
        })
        
        return {
            "rule": "OFAC",
            "passed": not result["sanctions_match"],
            "severity": "violation" if result["sanctions_match"] else "info",
            "message": f"OFAC check: {'MATCH FOUND' if result['sanctions_match'] else 'Clear'}",
            "details": result
        }
    
    async def bsa_compliance_check(self, merchant_data: Dict) -> Dict:
        """Bank Secrecy Act compliance verification"""
        business_type = merchant_data.get("business_type", "")
        annual_volume = merchant_data.get("annual_volume", 0)
        
        # Check BSA requirements via FinCEN API
        result = await self._call_fincen_bsa_api({
            "business_type": business_type,
            "annual_volume": annual_volume,
            "cash_transactions": merchant_data.get("cash_transactions", False)
        })
        
        return {
            "rule": "BSA",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"BSA compliance: {result['status']}",
            "details": result
        }
    
    async def fincen_check(self, merchant_data: Dict) -> Dict:
        """FinCEN registration and reporting requirements"""
        business_type = merchant_data.get("business_type", "")
        
        # Check FinCEN registration requirements
        result = await self._call_fincen_registration_api({
            "business_type": business_type,
            "services": merchant_data.get("services", []),
            "states_operating": merchant_data.get("states_operating", [])
        })
        
        return {
            "rule": "FinCEN",
            "passed": result["registration_compliant"],
            "severity": "violation" if not result["registration_compliant"] else "info",
            "message": f"FinCEN: {result['status']}",
            "details": result
        }
    
    async def state_licensing_check(self, merchant_data: Dict) -> Dict:
        """State licensing verification"""
        states = merchant_data.get("states_operating", [])
        business_type = merchant_data.get("business_type", "")
        
        # Check state licensing requirements
        result = await self._call_state_licensing_api({
            "states": states,
            "business_type": business_type,
            "business_name": merchant_data.get("business_name", "")
        })
        
        return {
            "rule": "State_Licensing",
            "passed": result["all_licenses_valid"],
            "severity": "violation" if not result["all_licenses_valid"] else "info",
            "message": f"State licensing: {result['status']}",
            "details": result
        }
    
    # API call implementations
    async def _call_ofac_api(self, data: Dict) -> Dict:
        """Call OFAC Sanctions List API"""
        client = APIClientFactory.create_client("ofac")
        result = await client.check_compliance(data)
        return result
    
    async def _call_fincen_bsa_api(self, data: Dict) -> Dict:
        """Call FinCEN BSA compliance API"""
        client = APIClientFactory.create_client("fincen_bsa")
        result = await client.check_compliance(data)
        return result
    
    async def _call_fincen_registration_api(self, data: Dict) -> Dict:
        """Call FinCEN registration API"""
        client = APIClientFactory.create_client("fincen_registration")
        result = await client.check_compliance(data)
        return result
    
    async def _call_state_licensing_api(self, data: Dict) -> Dict:
        """Call state licensing verification API"""
        client = APIClientFactory.create_client("state_licensing")
        result = await client.check_compliance(data)
        result["licenses_checked"] = data.get("states", [])
        return result

class UKRegulatoryServices:
    """UK regulatory compliance API services"""
    
    async def fca_compliance_check(self, merchant_data: Dict) -> Dict:
        """FCA authorization and compliance check"""
        business_type = merchant_data.get("business_type", "")
        
        # Call FCA Register API
        result = await self._call_fca_register_api({
            "business_name": merchant_data.get("business_name", ""),
            "business_type": business_type,
            "company_number": merchant_data.get("company_number", "")
        })
        
        return {
            "rule": "FCA",
            "passed": result["authorized"] or not result["authorization_required"],
            "severity": "violation" if result["authorization_required"] and not result["authorized"] else "info",
            "message": f"FCA: {result['status']}",
            "details": result
        }
    
    async def companies_house_check(self, merchant_data: Dict) -> Dict:
        """Companies House registration verification"""
        company_number = merchant_data.get("company_number", "")
        
        # Call Companies House API
        result = await self._call_companies_house_api({
            "company_number": company_number,
            "company_name": merchant_data.get("business_name", "")
        })
        
        return {
            "rule": "Companies_House",
            "passed": result["company_active"],
            "severity": "violation" if not result["company_active"] else "info",
            "message": f"Companies House: {result['status']}",
            "details": result
        }
    
    async def mlr_2017_check(self, merchant_data: Dict) -> Dict:
        """Money Laundering Regulations 2017 compliance"""
        business_type = merchant_data.get("business_type", "")
        
        # Check MLR 2017 requirements
        result = await self._call_mlr_compliance_api({
            "business_type": business_type,
            "services": merchant_data.get("services", []),
            "annual_turnover": merchant_data.get("annual_volume", 0)
        })
        
        return {
            "rule": "MLR_2017",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"MLR 2017: {result['status']}",
            "details": result
        }
    
    # API implementations
    async def _call_fca_register_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("fca_register")
        result = await client.check_compliance(data)
        return result
    
    async def _call_companies_house_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("companies_house")
        result = await client.check_compliance(data)
        return result
    
    async def _call_mlr_compliance_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("mlr_compliance")
        result = await client.check_compliance(data)
        return result

class EURegulatoryServices:
    """EU regulatory compliance API services"""
    
    async def psd2_compliance_check(self, merchant_data: Dict) -> Dict:
        """PSD2 compliance verification"""
        business_type = merchant_data.get("business_type", "")
        services = merchant_data.get("services", [])
        
        # Check PSD2 requirements via EBA API
        result = await self._call_psd2_api({
            "business_type": business_type,
            "services": services,
            "country": merchant_data.get("country", "")
        })
        
        return {
            "rule": "PSD2",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"PSD2: {result['status']}",
            "details": result
        }
    
    async def amld5_check(self, merchant_data: Dict) -> Dict:
        """5th Anti-Money Laundering Directive compliance"""
        business_type = merchant_data.get("business_type", "")
        
        # Check 5AMLD requirements
        result = await self._call_amld5_api({
            "business_type": business_type,
            "beneficial_owners": merchant_data.get("beneficial_owners", []),
            "country": merchant_data.get("country", "")
        })
        
        return {
            "rule": "5AMLD",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"5AMLD: {result['status']}",
            "details": result
        }
    
    async def mifid2_check(self, merchant_data: Dict) -> Dict:
        """MiFID II compliance verification"""
        business_type = merchant_data.get("business_type", "")
        
        # Check MiFID II requirements
        result = await self._call_mifid2_api({
            "business_type": business_type,
            "investment_services": merchant_data.get("investment_services", False),
            "country": merchant_data.get("country", "")
        })
        
        return {
            "rule": "MiFID_II",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"MiFID II: {result['status']}",
            "details": result
        }
    
    # API implementations
    async def _call_psd2_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("psd2")
        result = await client.check_compliance(data)
        return result
    
    async def _call_amld5_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("amld5")
        result = await client.check_compliance(data)
        return result
    
    async def _call_mifid2_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("mifid2")
        result = await client.check_compliance(data)
        return result

class CanadaRegulatoryServices:
    """Canada regulatory compliance API services"""
    
    async def fintrac_check(self, merchant_data: Dict) -> Dict:
        """FINTRAC registration and compliance"""
        business_type = merchant_data.get("business_type", "")
        
        # Call FINTRAC API
        result = await self._call_fintrac_api({
            "business_type": business_type,
            "business_name": merchant_data.get("business_name", ""),
            "services": merchant_data.get("services", [])
        })
        
        return {
            "rule": "FINTRAC",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"FINTRAC: {result['status']}",
            "details": result
        }
    
    async def pipeda_check(self, merchant_data: Dict) -> Dict:
        """PIPEDA privacy compliance"""
        # Check PIPEDA requirements
        result = await self._call_pipeda_api({
            "business_type": merchant_data.get("business_type", ""),
            "personal_data_processing": merchant_data.get("processes_personal_data", True),
            "privacy_policy_url": merchant_data.get("privacy_policy_url", "")
        })
        
        return {
            "rule": "PIPEDA",
            "passed": result["compliant"],
            "severity": "violation" if not result["compliant"] else "info",
            "message": f"PIPEDA: {result['status']}",
            "details": result
        }
    
    async def provincial_regulations_check(self, merchant_data: Dict) -> Dict:
        """Provincial regulations compliance"""
        provinces = merchant_data.get("provinces_operating", [])
        
        # Check provincial requirements
        result = await self._call_provincial_api({
            "provinces": provinces,
            "business_type": merchant_data.get("business_type", ""),
            "business_name": merchant_data.get("business_name", "")
        })
        
        return {
            "rule": "Provincial_Regs",
            "passed": result["all_compliant"],
            "severity": "violation" if not result["all_compliant"] else "info",
            "message": f"Provincial: {result['status']}",
            "details": result
        }
    
    # API implementations
    async def _call_fintrac_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("fintrac")
        result = await client.check_compliance(data)
        return result
    
    async def _call_pipeda_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("pipeda")
        result = await client.check_compliance(data)
        return result
    
    async def _call_provincial_api(self, data: Dict) -> Dict:
        client = APIClientFactory.create_client("provincial")
        result = await client.check_compliance(data)
        result["provinces_checked"] = data.get("provinces", [])
        return result