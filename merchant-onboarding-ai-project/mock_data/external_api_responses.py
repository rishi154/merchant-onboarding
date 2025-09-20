"""Mock external API responses for testing"""

# Business Registry Responses
BUSINESS_REGISTRY_RESPONSES = {
    "TechFlow Solutions LLC": {
        "registry_found": True,
        "business_name": "TechFlow Solutions LLC",
        "registration_state": "CA",
        "status": "active",
        "registration_date": "2020-03-15",
        "entity_type": "LLC",
        "registered_agent": "John Smith"
    },
    "CryptoGaming Ventures": {
        "registry_found": True,
        "business_name": "CryptoGaming Ventures",
        "registration_state": "NV",
        "status": "active",
        "registration_date": "2023-11-01",
        "entity_type": "Corporation",
        "special_licenses": ["gaming_license"]
    },
    "Fake Business Inc": {
        "registry_found": False,
        "error": "No matching business found"
    }
}

# OFAC Sanctions Responses
OFAC_RESPONSES = {
    "clean_business": {
        "sanctions_clear": True,
        "business_name": "TechFlow Solutions LLC",
        "matches_found": 0,
        "risk_score": 0.01,
        "last_updated": "2024-01-15T10:00:00Z"
    },
    "sanctioned_business": {
        "sanctions_clear": False,
        "business_name": "Sanctioned Entity Corp",
        "matches_found": 1,
        "risk_score": 0.95,
        "match_details": ["OFAC SDN List Match"]
    }
}

# GlobalPayments API Responses
GLOBALPAYMENTS_RESPONSES = {
    "create_account_success": {
        "id": "MER_12345678",
        "status": "ACTIVE",
        "name": "TechFlow Solutions LLC",
        "created": "2024-01-15T10:30:00Z",
        "response_code": "00",
        "response_message": "SUCCESS"
    },
    "create_account_failure": {
        "error_code": "40001",
        "error_message": "Invalid merchant data",
        "response_code": "57",
        "response_message": "DECLINED"
    },
    "configure_processing_success": {
        "merchant_id": "MER_12345678",
        "processing_enabled": True,
        "daily_limit": 25000,
        "monthly_limit": 750000,
        "settlement_schedule": "T+1",
        "supported_methods": ["visa", "mastercard", "amex", "discover"]
    }
}

# KYC/AML Responses
KYC_RESPONSES = {
    "verified_identity": {
        "identity_verified": True,
        "verification_method": "document_and_biometric",
        "confidence_score": 0.95,
        "document_authentic": True,
        "biometric_match": True,
        "verification_id": "kyc_abc123def456"
    },
    "failed_verification": {
        "identity_verified": False,
        "verification_method": "document_only",
        "confidence_score": 0.25,
        "document_authentic": False,
        "issues": ["document_quality_poor", "suspicious_alterations"]
    }
}

# Address Verification Responses
ADDRESS_RESPONSES = {
    "valid_address": {
        "address_valid": True,
        "standardized_address": {
            "street": "123 INNOVATION DR",
            "city": "SAN FRANCISCO",
            "state": "CA",
            "zip_code": "94105-1234"
        },
        "delivery_point": "valid",
        "usps_verified": True
    },
    "invalid_address": {
        "address_valid": False,
        "error": "Address not found in USPS database",
        "suggestions": ["123 INNOVATION DR", "123 INNOVATION WAY"]
    }
}

# Email/Phone Validation Responses
CONTACT_VALIDATION_RESPONSES = {
    "valid_email": {
        "email_valid": True,
        "domain": "techflow.com",
        "mx_record_exists": True,
        "disposable_email": False,
        "business_email": True
    },
    "valid_phone": {
        "phone_valid": True,
        "formatted_phone": "(555) 123-4567",
        "carrier": "Verizon",
        "line_type": "mobile",
        "country": "US"
    }
}

# Risk Assessment Data
RISK_ASSESSMENT_DATA = {
    "low_risk_profile": {
        "industry_risk": 0.1,
        "revenue_risk": 0.05,
        "geographic_risk": 0.02,
        "experience_risk": 0.08,
        "overall_risk_score": 0.25,
        "risk_category": "LOW"
    },
    "high_risk_profile": {
        "industry_risk": 0.4,  # Gambling/crypto
        "revenue_risk": 0.3,   # Low revenue
        "geographic_risk": 0.1,
        "experience_risk": 0.25, # New business
        "overall_risk_score": 0.85,
        "risk_category": "HIGH"
    }
}