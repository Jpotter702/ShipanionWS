# ShipVox WebSocket Pack

This pack scaffolds a real-time WebSocket integration for the ShipVox project.

## Contents

### Backend
- `backend/main.py`: FastAPI WebSocket server that handles connection lifecycle and broadcasting messages.

### Frontend
- `frontend/hooks/useWebSocket.ts`: React hook for maintaining a WebSocket connection and receiving messages.
- `frontend/utils/dispatchMessageByType.ts`: Dispatcher to route message types to state setters.
- `frontend/types/MessageTypes.ts`: TypeScript interfaces and enums for WebSocket message structure.

## WebSocket Message Format

All messages follow this format:

```ts
interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: any;
  timestamp: number;
  requestId: string;
}
```

## Common Message Types
- `zip_collected`
- `weight_confirmed`
- `quote_ready`
- `label_created`
- `pickup_scheduled`
- `contextual_update`
- `client_tool_call`
- `client_tool_result`
- `error`
- `auth`

## Authentication

The WebSocket connection is secured with JWT-based authentication:

1. Clients must first obtain a JWT token by authenticating with username/password
2. The JWT token is then passed in the WebSocket URL query string: `ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1...`
3. If the token is missing, invalid, or expired, the server will close the connection with code 1008 (Policy Violation)
4. The JWT token contains user information and has a configurable expiration time

For detailed documentation on the authentication system, see [AUTHENTICATION.md](./AUTHENTICATION.md).

### Obtaining a JWT Token

```bash
# Using curl to authenticate
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}

# Or use the pre-generated test token
curl "http://localhost:8000/test-token"
```

A pre-generated test token is available for quick testing that doesn't expire. For detailed information about using the test token, see [TEST_TOKEN_GUIDE.md](./TEST_TOKEN_GUIDE.md).

### Command Line Usage

A command-line client is provided for testing:

```bash
# Basic usage
./ws_jwt_client.py --type test --payload '{"message":"Hello world"}'

# Interactive mode
./ws_jwt_client.py --interactive
```

### Frontend Usage

```typescript
// First obtain a JWT token through authentication
const token = await authenticateUser(username, password);

// Then pass the JWT token to the WebSocket hook
const { status, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws', {
  token: token,
});
```

## Security Features

- **JWT Authentication**: Secure, stateless authentication with expiration
- **User Context**: Each message includes the authenticated user information
- **Connection Tracking**: Server tracks which user owns each connection
- **Automatic Token Validation**: Tokens are validated for authenticity and expiration
- **Password Hashing**: User passwords are securely hashed using bcrypt
- **Token Signing**: JWT tokens are cryptographically signed to prevent tampering
- **Standard OAuth2 Flow**: Uses industry-standard OAuth2 password flow for authentication

## Next Steps

- Build frontend UI bindings using Tailwind & Radix UI
- Use the dispatcher to populate live components (cards, steppers, etc.)
- Implement HTTPS/WSS for secure connections in production