# Sprint 2 WebSocket Endpoint Changes

This document outlines all changes made to the WebSocket endpoint and related components during Sprint 2.

## Overview

During Sprint 2, we implemented several key features:

1. Added support for ElevenLabs client tools (`create_label`)
2. Implemented contextual updates for real-time UI synchronization
3. Added session tracking for multi-device experiences
4. Enhanced error handling and response formatting
5. Created comprehensive test files and documentation

## WebSocket Endpoint Changes

### 1. Return Type Changes

The WebSocket message handlers now return a tuple containing:
- The primary response message
- An optional contextual update message

```python
# Before
async def dispatch_message(message: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]

# After
async def dispatch_message(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]
```

### 2. Session Tracking

Added session tracking to maintain context across multiple connections:

- Created a new `session.py` module for session management
- Added session ID support in the WebSocket connection URL
- Implemented session state storage
- Added session-specific broadcasting

### 3. Message Handling

Updated the message handling flow:

```python
# Process the message using the dispatcher
response, contextual_update = await dispatch_message(data, user_info)

# Send the response back to the client
await websocket.send_json(response)

# If there's a contextual update, broadcast it to the session
if contextual_update and session_id:
    # Add session ID to the contextual update
    contextual_update['session_id'] = session_id
    await manager.broadcast_to_session(session_id, contextual_update)
# If there's a contextual update but no session, broadcast to all
elif contextual_update:
    await manager.broadcast(contextual_update)
```

### 4. Connection Manager

Enhanced the `ConnectionManager` class:

- Added session tracking
- Implemented session-specific broadcasting
- Added methods to get connections by session

```python
async def broadcast_to_session(self, session_id: str, message: dict):
    """Broadcast a message to all connections in a session."""
    for connection in self.active_connections:
        if self.sessions.get(connection) == session_id:
            await connection.send_json(message)
```

## Handler Changes

### 1. Rate Request Handler

Updated the rate request handler to return contextual updates:

```python
async def handle_rate_request(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    # ...
    
    # Create the response
    response = {
        "type": "quote_ready",
        "payload": rate_response,
        "timestamp": time.time(),
        "requestId": str(uuid.uuid4()),
        "user": user_info.get("username")
    }
    
    # No contextual update for direct rate requests
    return response, None
```

### 2. ElevenLabs Client Tool Handler

Added support for ElevenLabs client tools:

- Implemented the `create_label` tool
- Added contextual updates for label creation
- Enhanced error handling for tool calls

## Session Management

Created a new session management module with the following features:

### 1. Session Creation and Retrieval

```python
def create_session(user_info: Dict[str, Any]) -> str:
    """Create a new session for a user."""
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "user_info": user_info,
        "created_at": time.time(),
        "last_active": time.time(),
        "state": {}
    }
    
    return session_id

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a session by ID."""
    session = sessions.get(session_id)
    
    if session:
        # Update last active time
        session["last_active"] = time.time()
    
    return session
```

### 2. Session State Management

```python
def update_session_state(session_id: str, key: str, value: Any) -> bool:
    """Update a value in the session state."""
    session = get_session(session_id)
    
    if not session:
        return False
    
    session["state"][key] = value
    return True

def get_session_state(session_id: str, key: str) -> Optional[Any]:
    """Get a value from the session state."""
    session = get_session(session_id)
    
    if not session:
        return None
    
    return session["state"].get(key)
```

### 3. Session Cleanup

```python
def cleanup_expired_sessions(max_age_seconds: int = 3600) -> int:
    """Clean up expired sessions."""
    now = time.time()
    expired_sessions = [
        session_id for session_id, session in sessions.items()
        if now - session["last_active"] > max_age_seconds
    ]
    
    for session_id in expired_sessions:
        delete_session(session_id)
    
    return len(expired_sessions)
```

## Message Format Changes

### 1. Contextual Update Format

Added a new message type for contextual updates:

```json
{
  "type": "contextual_update",
  "text": "label_created",
  "data": {
    "tracking_number": "794644746986",
    "carrier": "FedEx",
    "label_url": "https://shipvox.com/labels/794644746986.pdf",
    "qr_code": "https://shipvox.com/qr/794644746986.png",
    "estimated_delivery": "2023-05-15T12:00:00Z"
  },
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440001",
  "user": "username",
  "session_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

### 2. Client Tool Result Format

Added support for ElevenLabs client tool results:

```json
{
  "type": "client_tool_result",
  "tool_call_id": "abc123",
  "result": {
    "tracking_number": "794644746986",
    "label_url": "https://shipvox.com/labels/794644746986.pdf",
    "qr_code": "https://shipvox.com/qr/794644746986.png",
    "carrier": "FedEx",
    "estimated_delivery": "2023-05-15T12:00:00Z"
  },
  "is_error": false,
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Test Files

Added comprehensive test files:

1. `test_create_label.py` - Tests for the create_label tool
2. `test_create_label.sh` - Shell script for manual testing
3. `test_session.sh` - Shell script for testing session functionality

## Documentation

Created detailed documentation:

1. `CREATE_LABEL_GUIDE.md` - Guide for the create_label tool
2. `SESSION_TRACKING_GUIDE.md` - Guide for session tracking
3. `elevenlabs_create_label_prompt.md` - Sample ElevenLabs agent prompt

## Frontend Integration

Added example frontend components:

1. `CreateLabelExample.tsx` - Example React component for label creation
2. Enhanced WebSocket hook to support session IDs and contextual updates

## Summary

These changes significantly enhance the WebSocket endpoint's capabilities:

- **Real-time Synchronization**: Contextual updates enable real-time UI synchronization
- **Multi-device Experience**: Session tracking allows for seamless multi-device experiences
- **Voice Integration**: ElevenLabs client tools enable voice-driven shipping operations
- **Robust Error Handling**: Enhanced error handling improves reliability
- **Comprehensive Testing**: Test files ensure functionality works as expected
- **Detailed Documentation**: Documentation makes it easy for developers to understand and use the system
