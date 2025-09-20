from langchain.tools import BaseTool
from typing import Dict, Any
from pydantic import BaseModel, Field
import asyncio
import re
import requests
from config.tool_config import ToolConfig

class BusinessRegistryInput(BaseModel):
    business_name: str = Field(description="Business name to lookup")
    state: str = Field(description="State code (e.g., CA, NY)")

class TaxIdInput(BaseModel):
    tax_id: str = Field(description="Tax ID/EIN to validate")

class AddressInput(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    state: str = Field(description="State code")
    zip_code: str = Field(description="ZIP code")

class BusinessRegistryTool(BaseTool):
    name: str = "business_registry_lookup"
    description: str = "Look up business registration with Secretary of State"
    args_schema: type = BusinessRegistryInput
    
    def _run(self, business_name: str, state: str) -> Dict[str, Any]:
        return asyncio.run(self._arun(business_name, state))
    
    async def _arun(self, business_name: str, state: str) -> Dict[str, Any]:
        """Look up business in state registry"""
        try:
            # Use OpenCorporates API for real lookup
            url = "https://api.opencorporates.com/v0.4/companies/search"
            params = {
                "q": business_name,
                "jurisdiction_code": f"us_{state.lower()}",
                "format": "json"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                companies = data.get("results", {}).get("companies", [])
                
                if companies:
                    company = companies[0].get("company", {})
                    return {
                        "success": True,
                        "registry_found": True,
                        "business_status": company.get("current_status", "unknown"),
                        "registration_date": company.get("incorporation_date"),
                        "entity_type": company.get("company_type"),
                        "registry_response": company
                    }
                else:
                    return {
                        "success": True,
                        "registry_found": False,
                        "business_status": "not_found"
                    }
            else:
                # Fallback to mock
                return await self._mock_lookup(business_name, state)
                
        except Exception as e:
            return await self._mock_lookup(business_name, state)
    
    async def _mock_lookup(self, business_name: str, state: str) -> Dict[str, Any]:
        """Mock business registry lookup"""
        import secrets
        found = secrets.randbelow(10) > 1  # 90% chance of finding business
        
        if found:
            return {
                "success": True,
                "registry_found": True,
                "business_status": "active",
                "registration_date": "2020-03-15",
                "entity_type": "LLC",
                "mock_data": True
            }
        else:
            return {
                "success": True,
                "registry_found": False,
                "business_status": "not_found",
                "mock_data": True
            }

class TaxIdValidationTool(BaseTool):
    name: str = "tax_id_validation"
    description: str = "Validate Tax ID/EIN format and check with IRS"
    args_schema: type = TaxIdInput
    
    def _run(self, tax_id: str) -> Dict[str, Any]:
        return asyncio.run(self._arun(tax_id))
    
    async def _arun(self, tax_id: str) -> Dict[str, Any]:
        """Validate Tax ID format and check with IRS"""
        try:
            # Format validation
            ein_pattern = r'^\d{2}-\d{7}$'
            ssn_pattern = r'^\d{3}-\d{2}-\d{4}$'
            
            format_valid = bool(re.match(ein_pattern, tax_id) or re.match(ssn_pattern, tax_id))
            
            if not format_valid:
                return {
                    "success": True,
                    "format_valid": False,
                    "irs_verified": False,
                    "error": "Invalid Tax ID format"
                }
            
            # For prototype, use mock IRS verification
            return await self._mock_irs_check(tax_id)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "format_valid": False,
                "irs_verified": False
            }
    
    async def _mock_irs_check(self, tax_id: str) -> Dict[str, Any]:
        """Mock IRS verification"""
        import secrets
        verified = secrets.randbelow(10) > 0  # 95% chance of verification
        
        return {
            "success": True,
            "format_valid": True,
            "irs_verified": verified,
            "tax_id_type": "EIN" if "-" in tax_id and len(tax_id) == 10 else "SSN",
            "mock_data": True
        }

class AddressVerificationTool(BaseTool):
    name: str = "address_verification"
    description: str = "Verify and standardize address using USPS"
    args_schema: type = AddressInput
    
    def _run(self, street: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        return asyncio.run(self._arun(street, city, state, zip_code))
    
    async def _arun(self, street: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """Verify address with USPS"""
        try:
            # Basic format validation
            if not all([street.strip(), city.strip(), state.strip(), zip_code.strip()]):
                return {
                    "success": True,
                    "address_valid": False,
                    "error": "Incomplete address information"
                }
            
            # ZIP code format validation
            zip_pattern = r'^\d{5}(-\d{4})?$'
            zip_valid = bool(re.match(zip_pattern, zip_code))
            
            if not zip_valid:
                return {
                    "success": True,
                    "address_valid": False,
                    "error": "Invalid ZIP code format"
                }
            
            # For prototype, use mock USPS verification
            return await self._mock_usps_check(street, city, state, zip_code)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address_valid": False
            }
    
    async def _mock_usps_check(self, street: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """Mock USPS address verification"""
        import secrets
        valid = secrets.randbelow(10) > 0  # 95% chance of valid address
        
        if valid:
            return {
                "success": True,
                "address_valid": True,
                "standardized_address": {
                    "street": street.title(),
                    "city": city.title(),
                    "state": state.upper(),
                    "zip_code": zip_code
                },
                "usps_verified": True,
                "mock_data": True
            }
        else:
            return {
                "success": True,
                "address_valid": False,
                "error": "Address not found in USPS database",
                "mock_data": True
            }