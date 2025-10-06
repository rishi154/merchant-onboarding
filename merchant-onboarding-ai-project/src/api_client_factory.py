"""API client factory with consistent mock/real API interfaces"""
from typing import Dict, Any, Protocol
import os
import asyncio
import aiohttp

class RegulatoryAPIClient(Protocol):
    """Protocol defining standard interface for all regulatory API clients"""
    async def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]: ...

class MockAPIClient:
    """Base mock client with consistent response format"""
    
    def __init__(self, api_name: str, mock_responses: Dict[str, Any]):
        self.api_name = api_name
        self.mock_responses = mock_responses
    
    async def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.1)  # Simulate API latency
        
        return {
            "success": True,
            "api_provider": self.api_name,
            "mock_mode": True,
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": f"mock_{self.api_name}_{hash(str(data)) % 10000}",
            **self.mock_responses.get("default", {})
        }

class RealAPIClient:
    """Base real API client with consistent interface"""
    
    def __init__(self, api_name: str, base_url: str, api_key: str):
        self.api_name = api_name
        self.base_url = base_url
        self.api_key = api_key
    
    async def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/compliance/check",
                json=data,
                headers=headers
            ) as response:
                result = await response.json()
                
                return {
                    "success": response.status == 200,
                    "api_provider": self.api_name,
                    "mock_mode": False,
                    "timestamp": result.get("timestamp"),
                    "request_id": result.get("request_id"),
                    **result
                }

class APIClientFactory:
    """Factory for creating mock or real API clients"""
    
    # Mock response templates
    MOCK_RESPONSES = {
        "ofac": {
            "default": {
                "sanctions_match": False,
                "confidence_score": 0.95,
                "checked_lists": ["SDN", "Consolidated", "Non-SDN"]
            }
        },
        "fincen_bsa": {
            "default": {
                "compliant": True,
                "status": "BSA requirements met",
                "required_reports": ["CTR", "SAR"]
            }
        },
        "fincen_registration": {
            "default": {
                "registration_compliant": True,
                "status": "Registration not required",
                "msb_registration_needed": False
            }
        },
        "state_licensing": {
            "default": {
                "all_licenses_valid": True,
                "status": "All licenses verified",
                "licenses_checked": []
            }
        },
        "fca_register": {
            "default": {
                "authorized": True,
                "authorization_required": False,
                "status": "No authorization required",
                "firm_reference_number": None
            }
        },
        "companies_house": {
            "default": {
                "company_active": True,
                "status": "Company active",
                "incorporation_date": "2020-01-15",
                "company_status": "active"
            }
        },
        "mlr_compliance": {
            "default": {
                "compliant": True,
                "status": "MLR 2017 requirements met",
                "registration_required": False
            }
        },
        "cookiebot_privacy": {
            "default": {
                "has_privacy_policy": True,
                "gdpr_compliant": True,
                "compliance_score": 85,
                "violations": [],
                "recommendations": []
            }
        },
        "psd2": {
            "default": {
                "compliant": True,
                "status": "PSD2 requirements met",
                "license_required": False
            }
        },
        "amld5": {
            "default": {
                "compliant": True,
                "status": "5AMLD compliance verified",
                "beneficial_owners_disclosed": True
            }
        },
        "mifid2": {
            "default": {
                "compliant": True,
                "status": "MiFID II not applicable",
                "authorization_required": False
            }
        },
        "fintrac": {
            "default": {
                "compliant": True,
                "status": "FINTRAC registration not required",
                "msb_registration_needed": False
            }
        },
        "pipeda": {
            "default": {
                "compliant": True,
                "status": "PIPEDA requirements met",
                "privacy_policy_compliant": True
            }
        },
        "provincial": {
            "default": {
                "all_compliant": True,
                "status": "All provincial requirements met",
                "provinces_checked": []
            }
        }
    }
    
    # Real API configurations
    REAL_API_CONFIGS = {
        "ofac": {
            "base_url": "https://api.treasury.gov/ofac",
            "api_key_env": "OFAC_API_KEY"
        },
        "fincen_bsa": {
            "base_url": "https://api.fincen.gov/bsa",
            "api_key_env": "FINCEN_API_KEY"
        },
        "fincen_registration": {
            "base_url": "https://api.fincen.gov/registration",
            "api_key_env": "FINCEN_API_KEY"
        },
        "state_licensing": {
            "base_url": "https://api.statenet.com/licensing",
            "api_key_env": "STATENET_API_KEY"
        },
        "fca_register": {
            "base_url": "https://api.fca.org.uk/register",
            "api_key_env": "FCA_API_KEY"
        },
        "companies_house": {
            "base_url": "https://api.companieshouse.gov.uk",
            "api_key_env": "COMPANIES_HOUSE_API_KEY"
        },
        "mlr_compliance": {
            "base_url": "https://api.hmrc.gov.uk/mlr",
            "api_key_env": "HMRC_API_KEY"
        },
        "cookiebot_privacy": {
            "base_url": "https://api.cookiebot.com/privacy",
            "api_key_env": "COOKIEBOT_API_KEY"
        },
        "psd2": {
            "base_url": "https://api.eba.europa.eu/psd2",
            "api_key_env": "EBA_API_KEY"
        },
        "amld5": {
            "base_url": "https://api.eu-aml.europa.eu",
            "api_key_env": "EU_AML_API_KEY"
        },
        "mifid2": {
            "base_url": "https://api.esma.europa.eu/mifid2",
            "api_key_env": "ESMA_API_KEY"
        },
        "fintrac": {
            "base_url": "https://api.fintrac-canafe.gc.ca",
            "api_key_env": "FINTRAC_API_KEY"
        },
        "pipeda": {
            "base_url": "https://api.priv.gc.ca/pipeda",
            "api_key_env": "PRIVACY_COMMISSIONER_API_KEY"
        },
        "provincial": {
            "base_url": "https://api.provincial-registries.ca",
            "api_key_env": "PROVINCIAL_API_KEY"
        }
    }
    
    @classmethod
    def create_client(cls, api_name: str, use_mock: bool = None) -> RegulatoryAPIClient:
        """Create API client (mock or real based on environment)"""
        
        if use_mock is None:
            use_mock = os.getenv("USE_MOCK_APIS", "true").lower() == "true"
        
        if use_mock:
            return MockAPIClient(
                api_name=api_name,
                mock_responses=cls.MOCK_RESPONSES.get(api_name, {})
            )
        else:
            config = cls.REAL_API_CONFIGS.get(api_name)
            if not config:
                raise ValueError(f"No configuration found for API: {api_name}")
            
            api_key = os.getenv(config["api_key_env"])
            if not api_key:
                raise ValueError(f"API key not found for {api_name}: {config['api_key_env']}")
            
            return RealAPIClient(
                api_name=api_name,
                base_url=config["base_url"],
                api_key=api_key
            )