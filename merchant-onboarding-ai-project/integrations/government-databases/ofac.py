import asyncio
import httpx
import os
import secrets
from typing import Dict, Any, List

class OFACIntegration:
    """Real OFAC Sanctions List API integration"""
    
    def __init__(self):
        self.api_url = os.getenv("OFAC_API_URL", "https://api.trade.gov/consolidated_screening_list/search")
        
    async def sanctions_check(self, business_name: str, owner_name: str = "") -> Dict[str, Any]:
        """Check business and owner against OFAC sanctions list"""
        try:
            # Check business name
            business_result = await self._check_entity(business_name)
            
            # Check owner name if provided
            owner_result = {"matches": []} if not owner_name else await self._check_entity(owner_name)
            
            total_matches = len(business_result.get("matches", [])) + len(owner_result.get("matches", []))
            
            return {
                "success": True,
                "sanctions_clear": total_matches == 0,
                "matches_found": total_matches,
                "business_matches": business_result.get("matches", []),
                "owner_matches": owner_result.get("matches", []),
                "risk_score": 0.01 if total_matches == 0 else 0.95
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sanctions_clear": False,
                "matches_found": -1
            }
    
    async def _check_entity(self, name: str) -> Dict[str, Any]:
        """Check individual entity against OFAC list"""
        try:
            params = {
                "q": name,
                "sources": "SDN,FSE,ISN,PLC,SSI,UVL,DTC",  # OFAC lists
                "size": 10
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.api_url,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Filter for exact or close matches
                    matches = []
                    for item in result.get("results", []):
                        entity_name = item.get("name", "").lower()
                        search_name = name.lower()
                        
                        # Simple fuzzy matching
                        if (search_name in entity_name or 
                            entity_name in search_name or
                            self._calculate_similarity(search_name, entity_name) > 0.8):
                            matches.append({
                                "name": item.get("name"),
                                "source": item.get("source"),
                                "type": item.get("type"),
                                "programs": item.get("programs", []),
                                "addresses": item.get("addresses", [])
                            })
                    
                    return {
                        "success": True,
                        "matches": matches,
                        "total_results": result.get("total", 0)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"OFAC API error: {response.status_code}",
                        "matches": []
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "matches": []
            }
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Simple string similarity calculation"""
        # Basic Jaccard similarity
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

class SecretaryOfStateIntegration:
    """Business registry lookup integration"""
    
    def __init__(self):
        self.api_url = os.getenv("SOS_API_URL", "https://api.opencorporates.com/v0.4")
        
    async def business_registry_lookup(self, state: str, business_name: str) -> Dict[str, Any]:
        """Look up business in state registry"""
        try:
            # Use OpenCorporates API for business lookup
            params = {
                "q": business_name,
                "jurisdiction_code": f"us_{state.lower()}",
                "format": "json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/companies/search",
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    companies = result.get("results", {}).get("companies", [])
                    
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
                            "business_status": "not_found",
                            "registration_date": None,
                            "entity_type": None
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Registry API error: {response.status_code}",
                        "registry_found": False
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "registry_found": False
            }

class MockOFACIntegration:
    """Mock OFAC integration for development/testing"""
    
    async def sanctions_check(self, business_name: str, owner_name: str = "") -> Dict[str, Any]:
        """Mock sanctions check with real API response structure"""
        await asyncio.sleep(0.1)
        
        # Very low chance of sanctions match for testing
        has_business_match = secrets.randbelow(1000) == 0
        has_owner_match = secrets.randbelow(1000) == 0 if owner_name else False
        
        # Mock business matches with real API structure
        business_matches = []
        if has_business_match:
            business_matches.append({
                "name": business_name,
                "source": "SDN",
                "type": "Entity",
                "programs": ["SDNT"],
                "addresses": [{
                    "address": "123 Sanctions St",
                    "city": "Blocked City",
                    "country": "XX"
                }]
            })
        
        # Mock owner matches with real API structure
        owner_matches = []
        if has_owner_match:
            owner_matches.append({
                "name": owner_name,
                "source": "SDN",
                "type": "Individual",
                "programs": ["SDNT"],
                "addresses": []
            })
        
        total_matches = len(business_matches) + len(owner_matches)
        
        return {
            "success": True,
            "sanctions_clear": total_matches == 0,
            "matches_found": total_matches,
            "business_matches": business_matches,
            "owner_matches": owner_matches,
            "risk_score": 0.01 if total_matches == 0 else 0.95
        }

class MockSecretaryOfStateIntegration:
    """Mock Secretary of State integration"""
    
    async def business_registry_lookup(self, state: str, business_name: str) -> Dict[str, Any]:
        """Mock business registry lookup with real API response structure"""
        await asyncio.sleep(0.1)
        
        # 90% chance of finding business
        found = secrets.randbelow(10) > 0
        
        if found:
            # Mock registry response matching real API structure
            mock_registry_response = {
                "company": {
                    "name": business_name,
                    "current_status": "Active",
                    "incorporation_date": "2020-03-15",
                    "company_type": "Limited Liability Company",
                    "jurisdiction_code": f"us_{state.lower()}",
                    "registry_url": f"https://sos.{state.lower()}.gov/business/{secrets.token_hex(8)}"
                }
            }
            
            return {
                "success": True,
                "registry_found": True,
                "business_status": mock_registry_response["company"]["current_status"].lower(),
                "registration_date": mock_registry_response["company"]["incorporation_date"],
                "entity_type": "LLC",
                "registry_response": mock_registry_response["company"]
            }
        else:
            return {
                "success": True,
                "registry_found": False,
                "business_status": "not_found",
                "registration_date": None,
                "entity_type": None
            }

