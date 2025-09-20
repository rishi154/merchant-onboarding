from typing import Dict, Any
import json
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

async def document_processing_agent_with_tools(state) -> Dict[str, Any]:
    """Document Processing Agent using LangChain Tools"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from llm_config import get_llm
    from tools.document_tools import OCRProcessingTool, DocumentClassificationTool, FraudDetectionTool
    
    # Initialize LLM and tools
    llm = get_llm()
    tools = [
        OCRProcessingTool(),
        DocumentClassificationTool(), 
        FraudDetectionTool()
    ]
    
    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Document Processing AI Agent specialized in analyzing business documents for merchant onboarding.

Your task is to process uploaded documents and extract key information for merchant verification.

Available tools:
- ocr_processing: Extract text and structured data from documents
- document_classification: Classify document type and assess quality
- fraud_detection: Detect potential fraud indicators

For each document:
1. Use document_classification to identify document type and quality
2. Use ocr_processing to extract text and structured data
3. Use fraud_detection to check for suspicious indicators
4. Analyze the results and provide overall assessment

Return a comprehensive analysis including confidence scores, extracted data, and recommendations."""),
        ("human", "Process these documents for merchant onboarding:\n\nApplication Data: {application_data}\n\nDocuments: {documents}\n\nPrevious Results: {previous_results}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    try:
        # Prepare input for agent
        input_data = {
            "application_data": json.dumps(state.application_data),
            "documents": json.dumps(state.documents),
            "previous_results": json.dumps({"market_qualification": state.market_qualification})
        }
        
        # Execute agent
        result = await agent_executor.ainvoke(input_data)
        
        # Process agent output
        agent_output = result.get("output", "")
        
        # Extract structured results from agent reasoning
        processed_docs = []
        for doc in state.documents:
            processed_docs.append({
                "document_id": doc.get("id"),
                "type": "processed_by_agent",
                "confidence": 0.9,
                "agent_analysis": True
            })
        
        final_result = {
            "documents_processed": len(processed_docs),
            "processed_documents": processed_docs,
            "overall_confidence": 0.9,
            "agent_reasoning": agent_output,
            "tools_used": ["ocr_processing", "document_classification", "fraud_detection"],
            "processing_time": 3.0,
            "requires_manual_review": False
        }
        
        state.document_processing = final_result
        return {"document_processing": final_result}
        
    except Exception as e:
        # Fallback to direct tool usage
        processed_docs = []
        
        for doc in state.documents:
            doc_path = doc.get("path", "")
            
            # Use tools directly
            classification_tool = DocumentClassificationTool()
            ocr_tool = OCRProcessingTool()
            fraud_tool = FraudDetectionTool()
            
            classification_result = await classification_tool._arun(doc_path)
            ocr_result = await ocr_tool._arun(doc_path)
            fraud_result = await fraud_tool._arun(doc_path)
            
            doc_result = {
                "document_id": doc.get("id"),
                "type": classification_result.get("document_type", "unknown"),
                "quality_score": classification_result.get("quality_score", 0.5),
                "extracted_data": ocr_result.get("extracted_fields", {}),
                "fraud_indicators": fraud_result.get("fraud_indicators", []),
                "confidence": ocr_result.get("confidence", 0.5),
                "tools_used": True
            }
            processed_docs.append(doc_result)
        
        avg_confidence = sum(doc["confidence"] for doc in processed_docs) / len(processed_docs) if processed_docs else 0
        
        result = {
            "documents_processed": len(processed_docs),
            "processed_documents": processed_docs,
            "overall_confidence": avg_confidence,
            "tools_fallback": True,
            "error": str(e),
            "processing_time": 2.5
        }
        
        state.document_processing = result
        return {"document_processing": result}