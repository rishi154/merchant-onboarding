# Human Review System Architecture

## Overview
The human review system provides regulatory-compliant manual oversight for merchant onboarding workflows, ensuring BSA/AML compliance through genuine human decision-making.

## Key Components

### 1. Event-Driven Architecture
- **Threading.Event**: Cross-thread communication between Flask and workflow processes
- **Event Dictionary**: Centralized event management with thread-safe access
- **Event Cleanup**: Automatic memory management to prevent leaks

### 2. Configuration-Driven Review
```python
AGENT_REVIEW_CONFIG = {
    'document_processing': True,    # Requires human review
    'data_validation': False,       # Auto-approved
    'risk_assessment': False,       # Auto-approved
    'compliance_verification': False,
    'decision_making': False,
    'account_provisioning': False,
    'communication': False,
    'market_qualification': True,   # Requires human review
    # ... other agents
}
```

### 3. Workflow Pause/Resume Mechanism
1. **Agent Execution**: Agent completes processing and generates results
2. **Review Check**: System checks AGENT_REVIEW_CONFIG for review requirement
3. **Workflow Pause**: If review required, workflow pauses using asyncio.Event
4. **Human Review**: Manual reviewer approves/rejects via UI
5. **Event Trigger**: API call triggers event to resume workflow
6. **Workflow Resume**: Workflow continues from exact pause point

### 4. Database Integration
- **Agent Results Storage**: Direct database saves ensure results are always stored
- **Review Status Tracking**: Database fields track review state and decisions
- **Progress Persistence**: Agent execution history maintained for audit trail

## API Endpoints

### Review Decision Endpoint
```
POST /api/review_decision
{
    "app_id": "string",
    "agent_name": "string", 
    "decision": "approved|rejected",
    "comments": "string"
}
```

### Progress Tracking
```
GET /api/applications/{app_id}/progress
```

## Compliance Features

### BSA/AML Compliance
- **Genuine Human Oversight**: No automatic bypassing of review requirements
- **Audit Trail**: Complete decision history with timestamps and reviewer identity
- **Regulatory Documentation**: All review decisions logged for compliance reporting

### Thread Safety
- **Threading.Lock**: Protects event dictionary access from race conditions
- **Cross-Thread Events**: asyncio.to_thread enables Flask-workflow communication
- **Memory Management**: Events cleaned up after use to prevent memory leaks

## Configuration Management

### Selective Review Control
Administrators can configure which agents require human review:
- **High-Risk Agents**: Document processing, market qualification typically require review
- **Low-Risk Agents**: Data validation, communication typically auto-approved
- **Dynamic Configuration**: Settings can be updated without code changes

### Fallback Mechanisms
- **Event Not Found**: System triggers latest available event as fallback
- **Database Consistency**: Direct saves ensure agent results are always stored
- **Error Handling**: Comprehensive error logging and recovery procedures

## Performance Considerations

### Efficient Event Management
- **Event Reuse**: Events cleaned up and recreated as needed
- **Memory Optimization**: No persistent event storage
- **Thread Pool**: Efficient resource utilization for concurrent reviews

### Database Optimization
- **Direct Saves**: Agent results saved immediately upon completion
- **Progress Callbacks**: Enhanced with detailed logging and error handling
- **Consistent IDs**: Application ID consistency ensures proper data retrieval

## Security Features

### Access Control
- **Role-Based Access**: Only authorized reviewers can make decisions
- **Audit Logging**: All review actions logged with user identity
- **Data Protection**: Sensitive merchant data protected during review process

### Data Integrity
- **Transaction Safety**: Database operations use proper transaction management
- **Consistency Checks**: Validation ensures data integrity across operations
- **Error Recovery**: Robust error handling prevents data corruption