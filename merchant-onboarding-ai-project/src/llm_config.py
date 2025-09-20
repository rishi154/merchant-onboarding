from langchain_core.prompts import ChatPromptTemplate
import os
from pathlib import Path

# Load environment variables from .env file
def load_env():
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Initialize LLM with fallback
def get_llm():
    load_env()  # Load .env file
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if project:
        try:
            from langchain_google_vertexai import ChatVertexAI
            return ChatVertexAI(
                model_name="gemini-2.0-flash-001",
                project=project,
                location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
                temperature=0.1
            )
        except Exception as e:
            print(f"[WARNING] VertexAI not available: {e}")
    
    # Fallback to mock LLM for testing
    from langchain_core.language_models.fake import FakeListLLM
    return FakeListLLM(responses=[
        '{"qualified": false, "score": 0.3, "reasoning": "LLM not available - using fallback"}'
    ])

# Base agent prompt template
def create_agent_prompt(agent_name: str, role: str, task: str):
    return ChatPromptTemplate.from_messages([
        ("system", f"""You are {agent_name}, an AI agent specialized in {role}.
        
Your task: {task}

You must analyze the provided data and return a JSON response with your assessment.
Be precise, analytical, and provide reasoning for your decisions.
Consider risk factors, compliance requirements, and business logic.

Always include:
- Your analysis
- Decision/recommendation
- Confidence score (0-1)
- Risk factors identified
- Next steps if applicable"""),
        ("human", "Application Data: {application_data}\n\nDocuments: {documents}\n\nPrevious Agent Results: {previous_results}")
    ])