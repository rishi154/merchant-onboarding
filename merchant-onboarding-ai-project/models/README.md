# ML Models Directory

## ML Platform Selection Required

**Choose ML platform before model development:**

### Option 1: AWS SageMaker
- **Training**: SageMaker Training Jobs
- **Deployment**: SageMaker Endpoints  
- **Registry**: SageMaker Model Registry
- **Monitoring**: SageMaker Model Monitor
- **Cost**: $$$

### Option 2: Azure ML
- **Training**: Azure ML Compute
- **Deployment**: Azure ML Endpoints
- **Registry**: Azure ML Model Registry  
- **Monitoring**: Azure ML Monitoring
- **Cost**: $$

### Option 3: Google Vertex AI
- **Training**: Vertex AI Training
- **Deployment**: Vertex AI Endpoints
- **Registry**: Vertex AI Model Registry
- **Monitoring**: Vertex AI Model Monitoring  
- **Cost**: $$

## Model Categories

### Risk Scoring Models
- **credit-risk/**: Financial stability assessment
- **fraud-risk/**: Fraud detection and prevention
- **operational-risk/**: Business model analysis
- **regulatory-risk/**: Compliance risk assessment

### Document Processing Models  
- **document-classification/**: Document type identification
- **ocr-models/**: Text extraction and recognition
- **fraud-detection/**: Document tampering detection

### Identity Verification Models
- **face-matching/**: Biometric verification
- **document-verification/**: ID authenticity
- **behavioral-biometrics/**: Behavioral analysis

### Predictive Analytics Models
- **success-prediction/**: Merchant success forecasting
- **churn-prediction/**: Retention analysis
- **volume-prediction/**: Processing volume forecasting

## Model Structure Template
```
model-name/
├── training/               # Training scripts
├── inference/              # Inference code
├── data/                   # Training data
├── config/                 # Model configuration
├── experiments/            # Experiment tracking
└── deployment/             # Deployment configs
```