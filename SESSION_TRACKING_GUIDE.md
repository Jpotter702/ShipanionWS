# Session Tracking Guide

This guide explains how to use session tracking in the WebSocket server to maintain context across multiple connections.

## Overview

Session tracking allows:
1. Multiple clients to share the same session context
2. Clients to reconnect to an existing session after disconnection
3. The ElevenLabs voice agent and UI to stay synchronized
4. Messages to be broadcast only to clients in the same session

## How Sessions Work

Each WebSocket connection is associated with a session. Sessions are identified by a unique ID and contain:
- User information
- Creation timestamp
- Last activity timestamp
- Session state (key-value store)

When a client connects to the WebSocket server, it can either:
1. Create a new session (default behavior)
2. Connect to an existing session by providing a session ID

## Connecting to a Session

To connect to an existing session, include the `session_id` query parameter in the WebSocket URL:

```
ws://localhost:8000/ws?token=your-auth-token&session_id=550e8400-e29b-41d4-a716-446655440000
```

The server will validate that the session exists and belongs to the authenticated user before connecting.

## Session-Scoped Broadcasting

Messages can be broadcast to all clients in the same session:

1. **Contextual Updates**: When a client tool call generates a contextual update, it is automatically broadcast to all clients in the same session.

2. **Custom Broadcasting**: The server can broadcast messages to specific sessions using the `broadcast_to_session` method.

## Session State

The session state is a key-value store that can be used to maintain context across multiple connections. For example:

```python
# Store the selected shipping option in the session
update_session_state(session_id, "selected_shipping_option", {
    "carrier": "FedEx",
    "service": "Ground",
    "cost": 12.99
})

# Retrieve the selected shipping option
selected_option = get_session_state(session_id, "selected_shipping_option")
```

## Session Lifecycle

Sessions are created when:
- A client connects without providing a session ID
- A client provides an invalid or expired session ID

Sessions are automatically cleaned up after a period of inactivity (default: 1 hour).

## Example: Voice Agent and UI Synchronization

1. The ElevenLabs voice agent connects to the WebSocket server, creating a new session
2. The session ID is displayed to the user or embedded in a QR code
3. The user opens the CompanionUI and connects to the same session
4. The voice agent and UI now share the same session context
5. When the voice agent triggers a client tool call, the UI receives the contextual update

## Message Format with Session ID

Messages that include a session ID have the following format:

```json
{
  "type": "contextual_update",
  "text": "quote_ready",
  "data": {
    "carrier": "FedEx",
    "service": "Ground",
    "cost": 12.99
  },
  "timestamp": 1650000000000,
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Testing Session Tracking

You can test session tracking using the provided test script:

```bash
# Connect to a new session
./websocket/test_session.sh

# Connect to an existing session
./websocket/test_session.sh --session-id 550e8400-e29b-41d4-a716-446655440000
```

## Troubleshooting

### Common Issues

- **Invalid Session ID**: The session ID provided does not exist or has expired
- **Session Ownership**: The session belongs to a different user
- **Session Expiration**: The session has been cleaned up due to inactivity

### Debugging

- Check the WebSocket server logs for session-related messages
- Use the test script to verify session creation and connection
- Monitor session state using the `/sessions` endpoint (admin only)

## Next Steps

- Add support for session persistence (database storage)
- Implement session sharing between voice agent and UI
- Add session management UI for users
- Enhance security with session-specific tokens
