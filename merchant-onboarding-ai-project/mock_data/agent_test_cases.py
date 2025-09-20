"""Comprehensive test cases for each agent"""

# Market Qualification Test Cases
MARKET_QUALIFICATION_TESTS = {
    "qualified_us_tech": {
        "input": {
            "annual_revenue": 850000,
            "country": "US",
            "platform": "shopify",
            "industry": "technology"
        },
        "expected": {
            "qualified": True,
            "score": 1.0,
            "revenue_check": True,
            "geo_check": True,
            "platform_check": True
        }
    },
    "unqualified_low_revenue": {
        "input": {
            "annual_revenue": 50000,  # Below $100k minimum
            "country": "US",
            "platform": "shopify",
            "industry": "retail"
        },
        "expected": {
            "qualified": False,
            "revenue_check": False
        }
    },
    "unqualified_unsupported_country": {
        "input": {
            "annual_revenue": 500000,
            "country": "XX",  # Unsupported country
            "platform": "shopify",
            "industry": "technology"
        },
        "expected": {
            "qualified": False,
            "geo_check": False
        }
    }
}

# Document Processing Test Cases
DOCUMENT_PROCESSING_TESTS = {
    "high_quality_documents": {
        "input": [
            {"id": "doc1", "type": "business_license", "path": "/uploads/license.pdf"},
            {"id": "doc2", "type": "bank_statement", "path": "/uploads/statement.pdf"}
        ],
        "expected": {
            "documents_processed": 2,
            "overall_confidence": 0.9,
            "fraud_risk": "low",
            "requires_manual_review": False
        }
    },
    "poor_quality_documents": {
        "input": [
            {"id": "doc1", "type": "unknown", "path": "/uploads/blurry.jpg"}
        ],
        "expected": {
            "documents_processed": 1,
            "overall_confidence": 0.3,
            "requires_manual_review": True
        }
    },
    "fraudulent_documents": {
        "input": [
            {"id": "doc1", "type": "business_license", "path": "/uploads/test_fraud.pdf"}
        ],
        "expected": {
            "fraud_risk": "high",
            "requires_manual_review": True
        }
    }
}

# Risk Assessment Test Cases
RISK_ASSESSMENT_TESTS = {
    "low_risk_established_tech": {
        "input": {
            "annual_revenue": 1000000,
            "industry": "technology",
            "years_in_business": 5,
            "country": "US"
        },
        "expected": {
            "risk_category": "LOW",
            "risk_score": 25,  # Should be low
            "requires_manual_review": False
        }
    },
    "high_risk_gambling_startup": {
        "input": {
            "annual_revenue": 100000,
            "industry": "gambling",
            "years_in_business": 1,
            "country": "US"
        },
        "expected": {
            "risk_category": "HIGH",
            "risk_score": 75,  # Should be high
            "requires_manual_review": True
        }
    }
}

# Data Validation Test Cases
DATA_VALIDATION_TESTS = {
    "valid_business_data": {
        "input": {
            "business_name": "TechFlow Solutions LLC",
            "email": "admin@techflow.com",
            "phone": "555-123-4567",
            "tax_id": "12-3456789",
            "street": "123 Innovation Drive",
            "city": "San Francisco",
            "state": "CA"
        },
        "expected": {
            "validation_score": 0.95,
            "requires_manual_review": False
        }
    },
    "invalid_business_data": {
        "input": {
            "business_name": "",
            "email": "invalid-email",
            "phone": "123",
            "tax_id": "invalid"
        },
        "expected": {
            "validation_score": 0.2,
            "requires_manual_review": True
        }
    }
}

# Compliance Verification Test Cases
COMPLIANCE_TESTS = {
    "compliant_business": {
        "input": {
            "business_name": "TechFlow Solutions LLC",
            "owner_name": "John Smith",
            "industry": "technology",
            "country": "US"
        },
        "expected": {
            "compliance_score": 0.95,
            "sanctions_clear": True,
            "pep_clear": True,
            "requires_enhanced_dd": False
        }
    },
    "high_risk_industry": {
        "input": {
            "business_name": "CryptoGaming Ventures",
            "owner_name": "Alex Johnson",
            "industry": "gambling",
            "country": "US"
        },
        "expected": {
            "compliance_score": 0.6,
            "requires_enhanced_dd": True
        }
    }
}

# Decision Making Test Cases
DECISION_MAKING_TESTS = {
    "approve_low_risk": {
        "input": {
            "market_qualified": True,
            "risk_score": 25,
            "compliance_score": 0.95,
            "document_confidence": 0.9
        },
        "expected": {
            "decision": "APPROVED",
            "credit_limit": 25000
        }
    },
    "decline_high_risk": {
        "input": {
            "market_qualified": False,
            "risk_score": 85,
            "compliance_score": 0.4
        },
        "expected": {
            "decision": "DECLINED",
            "credit_limit": 0
        }
    },
    "manual_review_medium_risk": {
        "input": {
            "market_qualified": True,
            "risk_score": 55,
            "compliance_score": 0.7,
            "document_confidence": 0.6
        },
        "expected": {
            "decision": "MANUAL_REVIEW"
        }
    }
}

# Account Provisioning Test Cases
ACCOUNT_PROVISIONING_TESTS = {
    "successful_provisioning": {
        "input": {
            "status": "APPROVED",
            "merchant_data": {
                "business_name": "TechFlow Solutions LLC",
                "email": "admin@techflow.com",
                "credit_limit": 25000
            }
        },
        "expected": {
            "account_created": True,
            "setup_complete": True,
            "services_provisioned": ["globalpayments_processing", "api_access", "dashboard"]
        }
    },
    "skipped_not_approved": {
        "input": {
            "status": "DECLINED"
        },
        "expected": {
            "skipped": True,
            "reason": "not_approved"
        }
    }
}

ALL_TEST_CASES = {
    "market_qualification": MARKET_QUALIFICATION_TESTS,
    "document_processing": DOCUMENT_PROCESSING_TESTS,
    "risk_assessment": RISK_ASSESSMENT_TESTS,
    "data_validation": DATA_VALIDATION_TESTS,
    "compliance": COMPLIANCE_TESTS,
    "decision_making": DECISION_MAKING_TESTS,
    "account_provisioning": ACCOUNT_PROVISIONING_TESTS
}