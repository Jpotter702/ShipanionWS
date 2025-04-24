# Using websocat with JWT Authentication

This document provides examples of how to use the `websocat` command-line tool with JWT-based authentication for WebSocket connections.

## Prerequisites

1. Make sure you have `websocat` installed
2. The FastAPI server should be running: `uvicorn backend.main:app --reload`

## Step 1: Obtain a JWT Token

First, you need to obtain a JWT token by authenticating with the server:

```bash
# Using curl to get a JWT token
TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password" | jq -r '.access_token')

# If you don't have jq installed, you can manually copy the token from the response
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password"
```

## Step 2: Connect to WebSocket with JWT Token

Once you have the token, you can use it to connect to the WebSocket server:

```bash
# If you stored the token in a variable
echo '{"type":"test","payload":{"message":"Hello with JWT"}}' | websocat "ws://localhost:8000/ws?token=$TOKEN"

# Or with the token directly
echo '{"type":"test","payload":{"message":"Hello with JWT"}}' | websocat "ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Interactive Mode

You can also use websocat in interactive mode to send multiple messages:

```bash
# Interactive mode
websocat "ws://localhost:8000/ws?token=$TOKEN"
```

Then you can type JSON messages like:
```json
{"type":"test","payload":{"message":"First message"}}
{"type":"contextual_update","payload":{"status":"processing"}}
```

## Testing Invalid Authentication

To test that authentication is working correctly, try connecting with an invalid token:

```bash
# This should fail with a 1008 Policy Violation error
echo '{"type":"test","payload":{"message":"This should fail"}}' | websocat "ws://localhost:8000/ws?token=invalid.token"
```

## Shell Script for Testing

Here's a complete shell script that demonstrates the JWT authentication flow:

```bash
#!/bin/bash

# Get JWT token
echo "Obtaining JWT token..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password")

# Extract token (requires jq)
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')
echo "Token obtained: ${TOKEN:0:20}..."

# Connect to WebSocket with token
echo "Connecting to WebSocket with JWT token..."
echo '{"type":"test","payload":{"message":"Hello with JWT authentication"}}' | \
  websocat "ws://localhost:8000/ws?token=$TOKEN"
```

Save this as `test_jwt_websocket.sh`, make it executable with `chmod +x test_jwt_websocket.sh`, and run it to test the JWT authentication flow.
