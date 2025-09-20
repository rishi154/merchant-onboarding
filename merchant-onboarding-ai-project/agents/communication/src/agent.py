from typing import Dict, Any
import json
from langchain_core.output_parsers import JsonOutputParser

async def communication_agent(state) -> Dict[str, Any]:
    """Agent 9: Communication AI Agent"""
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
    from llm_config import get_llm, create_agent_prompt
    
    llm = get_llm()
    
    prompt = create_agent_prompt(
        "Communication Agent",
        "merchant communication and notification management",
        """Generate appropriate communications based on application status and results.
        
        Determine communication strategy:
        1. Message type (confirmation, status update, approval, decline, info request)
        2. Communication channels (email, SMS, phone, portal)
        3. Message content and tone
        4. Follow-up schedule
        5. Personalization based on merchant profile
        
        Return JSON with: messages_to_send (array), communication_strategy, follow_up_schedule, personalization_notes"""
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = await chain.ainvoke({
            "application_data": json.dumps(state.application_data),
            "documents": json.dumps(state.documents),
            "previous_results": json.dumps({
                "status": str(state.status),
                "decision": state.decision,
                "exceptions": state.exceptions
            })
        })
        
        result.setdefault("processing_time", 0.2)
        
        # Add messages to state
        messages_sent = result.get("messages_to_send", [])
        state.communications_sent.extend(messages_sent)
        
        state.communication = result
        return {"communication": result}
        
    except Exception as e:
        # Fallback communication
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
        from state import ApplicationStatus
        
        messages = []
        if state.status == ApplicationStatus.APPROVED:
            messages.append({
                "type": "approval",
                "channel": "email",
                "template": "approval_notification"
            })
        elif state.status == ApplicationStatus.DECLINED:
            messages.append({
                "type": "decline", 
                "channel": "email",
                "template": "decline_notification"
            })
        
        result = {
            "messages_sent": len(messages),
            "messages_to_send": messages,
            "error": str(e),
            "processing_time": 0.2
        }
        
        state.communication = result
        return {"communication": result}