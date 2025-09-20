# VertexAI Authentication Setup

## Option 1: Application Default Credentials (Easiest)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login with your Google account
gcloud auth application-default login

# Set project
gcloud config set project your-project-id

# No GOOGLE_APPLICATION_CREDENTIALS needed!
```

## Option 2: Service Account Key

```bash
# Create service account in Google Cloud Console
# Download JSON key file
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

## Option 3: Test Authentication

```bash
# Test if authentication works
python -c "
from google.auth import default
try:
    credentials, project = default()
    print(f'✅ Authentication OK - Project: {project}')
except Exception as e:
    print(f'❌ Authentication failed: {e}')
"
```

## Required Permissions

Your account/service account needs:
- `roles/aiplatform.user` - Use Vertex AI
- `roles/ml.developer` - ML development

## Test VertexAI Connection

```python
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(
    model_name="gemini-pro",
    project="your-project-id",
    location="us-central1"
)

response = llm.invoke("Hello, test message")
print(response.content)
```