import os
from typing import Any

class IntegrationFactory:
    """Factory for creating integration instances with mock/real switching"""
    
    @staticmethod
    def get_credit_bureau_integration(bureau: str) -> Any:
        """Get credit bureau integration (Experian, Equifax, TransUnion, D&B)"""
        use_mock = os.getenv("MOCK_CREDIT_BUREAUS", "true").lower() == "true"
        
        if bureau.lower() == "experian":
            if use_mock:
                from .credit_bureaus.experian import MockExperianIntegration
                return MockExperianIntegration()
            else:
                from .credit_bureaus.experian import ExperianIntegration
                return ExperianIntegration()
                
        elif bureau.lower() == "equifax":
            if use_mock:
                from .credit_bureaus.equifax import MockEquifaxIntegration
                return MockEquifaxIntegration()
            else:
                from .credit_bureaus.equifax import EquifaxIntegration
                return EquifaxIntegration()
                
        elif bureau.lower() == "transunion":
            if use_mock:
                from .credit_bureaus.transunion import MockTransUnionIntegration
                return MockTransUnionIntegration()
            else:
                from .credit_bureaus.transunion import TransUnionIntegration
                return TransUnionIntegration()
                
        elif bureau.lower() == "dun_bradstreet":
            if use_mock:
                from .credit_bureaus.dun_bradstreet import MockDunBradstreetIntegration
                return MockDunBradstreetIntegration()
            else:
                from .credit_bureaus.dun_bradstreet import DunBradstreetIntegration
                return DunBradstreetIntegration()
    
    @staticmethod
    def get_kyc_provider_integration(provider: str) -> Any:
        """Get KYC provider integration (Jumio, Onfido, Trulioo, LexisNexis)"""
        use_mock = os.getenv("MOCK_KYC_PROVIDERS", "true").lower() == "true"
        
        if provider.lower() == "jumio":
            if use_mock:
                from .kyc_providers.jumio import MockJumioIntegration
                return MockJumioIntegration()
            else:
                from .kyc_providers.jumio import JumioIntegration
                return JumioIntegration()
                
        elif provider.lower() == "onfido":
            if use_mock:
                from .kyc_providers.onfido import MockOnfidoIntegration
                return MockOnfidoIntegration()
            else:
                from .kyc_providers.onfido import OnfidoIntegration
                return OnfidoIntegration()
                
        elif provider.lower() == "trulioo":
            if use_mock:
                from .kyc_providers.trulioo import MockTruliooIntegration
                return MockTruliooIntegration()
            else:
                from .kyc_providers.trulioo import TruliooIntegration
                return TruliooIntegration()
                
        elif provider.lower() == "lexisnexis":
            if use_mock:
                from .kyc_providers.lexisnexis import MockLexisNexisIntegration
                return MockLexisNexisIntegration()
            else:
                from .kyc_providers.lexisnexis import LexisNexisIntegration
                return LexisNexisIntegration()
    
    @staticmethod
    def get_banking_api_integration(provider: str) -> Any:
        """Get banking API integration (Plaid, Yodlee, Finicity, MX)"""
        use_mock = os.getenv("MOCK_BANKING_APIS", "true").lower() == "true"
        
        if provider.lower() == "plaid":
            if use_mock:
                from .banking_apis.plaid import MockPlaidIntegration
                return MockPlaidIntegration()
            else:
                from .banking_apis.plaid import PlaidIntegration
                return PlaidIntegration()
                
        elif provider.lower() == "yodlee":
            if use_mock:
                from .banking_apis.yodlee import MockYodleeIntegration
                return MockYodleeIntegration()
            else:
                from .banking_apis.yodlee import YodleeIntegration
                return YodleeIntegration()
                
        elif provider.lower() == "finicity":
            if use_mock:
                from .banking_apis.finicity import MockFinicityIntegration
                return MockFinicityIntegration()
            else:
                from .banking_apis.finicity import FinicityIntegration
                return FinicityIntegration()
                
        elif provider.lower() == "mx":
            if use_mock:
                from .banking_apis.mx import MockMXIntegration
                return MockMXIntegration()
            else:
                from .banking_apis.mx import MXIntegration
                return MXIntegration()
    
    @staticmethod
    def get_government_database_integration(database: str) -> Any:
        """Get government database integration (OFAC, IRS, SOS, FinCEN)"""
        use_mock = os.getenv("MOCK_GOVERNMENT_DATABASES", "true").lower() == "true"
        
        if database.lower() == "ofac":
            if use_mock:
                from .government_databases.ofac import MockOFACIntegration
                return MockOFACIntegration()
            else:
                from .government_databases.ofac import OFACIntegration
                return OFACIntegration()
                
        elif database.lower() == "irs":
            if use_mock:
                from .government_databases.irs import MockIRSIntegration
                return MockIRSIntegration()
            else:
                from .government_databases.irs import IRSIntegration
                return IRSIntegration()
                
        elif database.lower() == "secretary_of_state":
            if use_mock:
                from .government_databases.secretary_of_state import MockSecretaryOfStateIntegration
                return MockSecretaryOfStateIntegration()
            else:
                from .government_databases.secretary_of_state import SecretaryOfStateIntegration
                return SecretaryOfStateIntegration()
                
        elif database.lower() == "fincen":
            if use_mock:
                from .government_databases.fincen import MockFinCENIntegration
                return MockFinCENIntegration()
            else:
                from .government_databases.fincen import FinCENIntegration
                return FinCENIntegration()