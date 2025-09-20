# Google Document AI Setup

## 1. Enable Google Document AI API

```bash
gcloud services enable documentai.googleapis.com
```

## 2. Create Document AI Processor

```bash
# Create a general form processor
gcloud alpha documentai processors create \
  --display-name="Merchant Onboarding Processor" \
  --type="FORM_PARSER_PROCESSOR" \
  --location=us

# Note the processor ID from the output
```

## 3. Set Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us"
export GOOGLE_DOC_AI_PROCESSOR_ID="your-processor-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

## 4. Service Account Permissions

Ensure your service account has these roles:
- `roles/documentai.apiUser`
- `roles/storage.objectViewer` (if documents are in Cloud Storage)

## 5. Test Document Processing

```python
from agents.document_processing.src.google_doc_ai import GoogleDocumentAI

doc_ai = GoogleDocumentAI()
result = await doc_ai.process_document("/path/to/document.pdf")
print(result)
```

## 6. Supported Document Types

- Business licenses
- Bank statements  
- Tax returns
- Articles of incorporation
- Financial statements
- Identity documents

## 7. Fallback Behavior

If Google Document AI is not configured:
- Falls back to mock OCR processing
- Still provides realistic test data
- Allows development without Google Cloud setup