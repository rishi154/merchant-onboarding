-- Add jurisdiction support to existing tables
ALTER TABLE merchant_applications ADD COLUMN jurisdiction VARCHAR(10) DEFAULT 'US';
ALTER TABLE merchant_applications ADD COLUMN business_country VARCHAR(10);
ALTER TABLE merchant_applications ADD COLUMN incorporation_country VARCHAR(10);
ALTER TABLE merchant_applications ADD COLUMN processing_sla_hours INTEGER DEFAULT 72;

-- Create jurisdiction-specific tables
CREATE TABLE IF NOT EXISTS jurisdiction_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jurisdiction VARCHAR(10) NOT NULL,
    business_type VARCHAR(50) NOT NULL,
    required_documents TEXT, -- JSON array
    compliance_rules TEXT,   -- JSON array
    processing_sla_hours INTEGER DEFAULT 72,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jurisdiction, business_type)
);

CREATE TABLE IF NOT EXISTS jurisdiction_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jurisdiction VARCHAR(10) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    provider_name VARCHAR(100) NOT NULL,
    api_config TEXT, -- JSON object
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jurisdiction, service_type, provider_name)
);

-- Insert default jurisdiction requirements
INSERT OR REPLACE INTO jurisdiction_requirements (jurisdiction, business_type, required_documents, compliance_rules, processing_sla_hours) VALUES
('US', 'LLC', '["articles_of_organization", "ein_letter", "operating_agreement"]', '["BSA", "OFAC", "FinCEN", "State_Licensing"]', 72),
('US', 'Corporation', '["articles_of_incorporation", "ein_letter", "bylaws"]', '["BSA", "OFAC", "FinCEN", "State_Licensing"]', 72),
('UK', 'Limited', '["certificate_of_incorporation", "memorandum", "articles_of_association"]', '["FCA", "PCI-DSS", "MLR_2017"]', 96),
('UK', 'LLP', '["incorporation_document", "llp_agreement"]', '["FCA", "PCI-DSS", "MLR_2017"]', 96),
('EU', 'GmbH', '["handelsregister", "gesellschaftsvertrag", "vat_certificate"]', '["GDPR", "PSD2", "5AMLD", "MiFID_II"]', 120),
('EU', 'SAS', '["kbis", "statuts", "vat_certificate"]', '["GDPR", "PSD2", "5AMLD", "MiFID_II"]', 120),
('CA', 'Corporation', '["articles_of_incorporation", "business_number", "provincial_registration"]', '["FINTRAC", "PIPEDA", "Provincial_Regs"]', 96);

-- Insert default integration providers
INSERT OR REPLACE INTO jurisdiction_integrations (jurisdiction, service_type, provider_name, api_config, is_active) VALUES
('US', 'credit_bureau', 'experian_us', '{"endpoint": "https://api.experian.com/us", "version": "v1"}', TRUE),
('US', 'bank_verification', 'plaid', '{"endpoint": "https://api.plaid.com", "version": "2020-09-14"}', TRUE),
('US', 'sanctions_screening', 'ofac', '{"endpoint": "https://api.treasury.gov/ofac", "version": "v1"}', TRUE),
('UK', 'credit_bureau', 'experian_uk', '{"endpoint": "https://api.experian.co.uk", "version": "v1"}', TRUE),
('UK', 'bank_verification', 'truelayer', '{"endpoint": "https://api.truelayer.com", "version": "v1"}', TRUE),
('UK', 'business_registry', 'companies_house', '{"endpoint": "https://api.company-information.service.gov.uk", "version": "v0"}', TRUE),
('EU', 'credit_bureau', 'schufa', '{"endpoint": "https://api.schufa.de", "version": "v1"}', TRUE),
('EU', 'bank_verification', 'tink', '{"endpoint": "https://api.tink.com", "version": "v1"}', TRUE),
('EU', 'sanctions_screening', 'eu_sanctions', '{"endpoint": "https://api.ec.europa.eu/sanctions", "version": "v1"}', TRUE),
('CA', 'credit_bureau', 'equifax_ca', '{"endpoint": "https://api.equifax.ca", "version": "v1"}', TRUE),
('CA', 'bank_verification', 'flinks', '{"endpoint": "https://api.flinks.com", "version": "v3"}', TRUE),
('CA', 'business_registry', 'corporations_canada', '{"endpoint": "https://api.ic.gc.ca", "version": "v1"}', TRUE);