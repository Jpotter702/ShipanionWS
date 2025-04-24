# WebSocket Authentication Documentation

This document provides detailed information about the JWT-based authentication system implemented for WebSocket connections in the ShipVox WebSocket Pack.

## Table of Contents

1. [Authentication Overview](#authentication-overview)
2. [JWT Authentication Flow](#jwt-authentication-flow)
3. [Implementation Details](#implementation-details)
   - [Token Endpoint](#token-endpoint)
   - [User Authentication](#user-authentication)
   - [Token Generation](#token-generation)
   - [Token Validation](#token-validation)
   - [WebSocket Authentication](#websocket-authentication)
4. [Security Considerations](#security-considerations)
5. [Client Integration](#client-integration)
   - [Command Line](#command-line)
   - [Frontend Applications](#frontend-applications)
   - [Testing Tools](#testing-tools)
6. [Configuration](#configuration)
7. [Production Recommendations](#production-recommendations)

## Authentication Overview

The WebSocket server uses JWT (JSON Web Token) based authentication to secure connections. This approach provides several benefits:

- **Stateless**: The server doesn't need to store session information
- **Expiration**: Tokens automatically expire after a configurable time
- **User Context**: Tokens contain user information for authorization
- **Security**: Passwords are only transmitted during initial authentication

## JWT Authentication Flow

The authentication process follows these steps:

1. **Client Authentication**:
   - Client sends username and password to the `/token` endpoint
   - Server validates credentials and returns a JWT token

2. **WebSocket Connection**:
   - Client connects to the WebSocket endpoint with the JWT token in the query string
   - Server validates the token before accepting the connection
   - If the token is invalid or expired, the server rejects the connection with code 1008

3. **Message Exchange**:
   - After successful authentication, the client and server can exchange messages
   - Each message is associated with the authenticated user

## Implementation Details

### Token Endpoint

The `/token` endpoint in `backend/main.py` implements the OAuth2 password flow:

```python
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }
```

### User Authentication

User authentication is handled in `backend/security.py`:

```python
def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by username and password."""
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

For demonstration purposes, a mock user database is included:

```python
# Mock user database - in production, use a real database
fake_users_db = {
    "user": {
        "username": "user",
        # Hashed password for "password"
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    }
}
```

### Token Generation

JWT tokens are generated with the `create_access_token` function:

```python
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

The token includes:
- User information (username in the "sub" claim)
- Expiration time ("exp" claim)
- Is signed with a secret key

### Token Validation

Tokens are validated with the `verify_token` function:

```python
def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return its payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

This function:
- Verifies the token signature using the secret key
- Checks if the token has expired
- Returns the token payload if valid

### WebSocket Authentication

The WebSocket endpoint in `backend/main.py` authenticates connections:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Extract token from query parameters
    token = websocket.query_params.get("token")

    # Validate the token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
        return

    # Verify JWT token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
        return

    # Extract user information from token
    username = payload.get("sub")
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token payload")
        return

    # Store user information
    user_info = {"username": username}

    # If token is valid, proceed with connection
    await manager.connect(websocket, user_info)
    try:
        while True:
            data = await websocket.receive_json()
            # Add user information and metadata
            data['user'] = username
            data['timestamp'] = time.time()
            data['requestId'] = str(uuid.uuid4())
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

This endpoint:
1. Extracts the token from the query string
2. Validates the token
3. Extracts user information from the token
4. Rejects invalid connections with code 1008
5. Adds user context to messages

## Security Considerations

The JWT authentication system includes several security features:

1. **Password Hashing**: Passwords are hashed using bcrypt, a secure hashing algorithm
2. **Token Expiration**: Tokens expire after a configurable time (default: 30 minutes)
3. **Token Signing**: Tokens are cryptographically signed to prevent tampering
4. **Connection Validation**: WebSocket connections are validated before being accepted
5. **User Context**: Each message includes the authenticated user for accountability

## Client Integration

### Command Line

#### Obtaining a Token

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password"
```

#### Using the Test Token

For testing purposes, a pre-generated test token is available that doesn't expire:

```bash
# Get the test token
curl "http://localhost:8000/test-token"

# Response
{
  "test_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko",
  "note": "This token is for testing only. It is valid for the 'user' account and does not expire."
}

# Use the test token directly
echo '{"type":"test","payload":{"message":"Hello"}}' | websocat "ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko"
```

This test token is hardcoded in the application and can be overridden with the `WS_TEST_TOKEN` environment variable. For comprehensive documentation on using the test token, see [TEST_TOKEN_GUIDE.md](./TEST_TOKEN_GUIDE.md).

#### Connecting with a Token using websocat

```bash
# Store the token in a variable
TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password" | jq -r '.access_token')

# Connect with the token
echo '{"type":"test","payload":{"message":"Hello"}}' | websocat "ws://localhost:8000/ws?token=$TOKEN"
```

### Frontend Applications

#### Authentication Flow

```typescript
// Login function
async function login(username: string, password: string) {
  const response = await fetch('http://localhost:8000/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      username,
      password,
    }),
  });

  if (response.ok) {
    const data = await response.json();
    return data.access_token;
  } else {
    throw new Error('Authentication failed');
  }
}

// WebSocket connection with token
const token = await login('user', 'password');
const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
```

#### React Hook Usage

```typescript
// First obtain a JWT token through authentication
const token = await authenticateUser(username, password);

// Then pass the JWT token to the WebSocket hook
const { status, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws', {
  token: token,
});
```

### Testing Tools

The project includes several tools for testing the authentication system:

1. **test_jwt_auth.py**: Automated test script for JWT authentication
2. **ws_jwt_client.py**: Command-line client for WebSocket communication with JWT
3. **websocat_jwt_examples.md**: Examples for using websocat with JWT

## Configuration

The authentication system can be configured in `backend/security.py`:

```python
# Generate a secure secret key if not provided in environment variables
# In production, always set this via environment variable
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

Key configuration options:
- **SECRET_KEY**: The secret key used to sign JWT tokens
- **ALGORITHM**: The algorithm used for token signing
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Token expiration time in minutes

## Production Recommendations

For production environments, consider these additional security measures:

1. **Environment Variables**:
   - Store the JWT secret key in environment variables
   - Use a strong, randomly generated secret key

2. **HTTPS/WSS**:
   - Use HTTPS for the token endpoint
   - Use WSS (WebSocket Secure) for WebSocket connections

3. **Database Integration**:
   - Replace the mock user database with a real database
   - Implement proper user management

4. **Token Security**:
   - Implement token refresh mechanisms for longer sessions
   - Consider using shorter token expiration times

5. **Rate Limiting**:
   - Add rate limiting to the token endpoint to prevent brute force attacks
   - Implement connection limits per user

6. **Monitoring and Logging**:
   - Log authentication attempts and failures
   - Set up monitoring for suspicious activities

7. **Token Storage**:
   - Store tokens securely in frontend applications
   - Consider using HTTP-only cookies for web applications

By following these recommendations, you can enhance the security of the JWT authentication system for production use.
