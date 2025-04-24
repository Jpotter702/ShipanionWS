# Using websocat with JWT Authentication

This guide provides step-by-step instructions for using the `websocat` command-line tool to test WebSocket connections with JWT authentication.

## Prerequisites

- `websocat` installed on your system
- `curl` for obtaining JWT tokens
- `jq` (optional) for parsing JSON responses
- The FastAPI server running (`uvicorn backend.main:app --reload`)

## Step 1: Obtain a JWT Token

Before connecting to the WebSocket, you need to authenticate and obtain a JWT token. You have two options:

### Option 1: Authenticate with username/password

```bash
# Basic authentication request
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password"
```

### Option 2: Use the pre-generated test token

For quick testing, you can use the pre-generated test token that doesn't expire:

```bash
# Get the test token
curl "http://localhost:8000/test-token"
```

For comprehensive documentation on using the test token, see [TEST_TOKEN_GUIDE.md](./TEST_TOKEN_GUIDE.md).

This will return a response like:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

If you have `jq` installed, you can extract just the token:

```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password" | jq -r '.access_token')

echo "Token: $TOKEN"
```

## Step 2: Connect to WebSocket with JWT Token

Once you have the token, you can use it to connect to the WebSocket:

### Send a Single Message

```bash
# Using the token variable
echo '{"type":"test","payload":{"message":"Hello with JWT"}}' | websocat "ws://localhost:8000/ws?token=$TOKEN"

# Or with the token directly
echo '{"type":"test","payload":{"message":"Hello with JWT"}}' | websocat "ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Interactive Mode

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

### Listen-Only Mode

To just listen for messages without sending anything:

```bash
websocat --no-send "ws://localhost:8000/ws?token=$TOKEN"
```

## Step 3: Test Invalid Authentication

To verify that authentication is working correctly, try connecting with an invalid token:

```bash
# This should fail with a 1008 Policy Violation error
echo '{"type":"test","payload":{"message":"This should fail"}}' | websocat "ws://localhost:8000/ws?token=invalid.token"
```

Or without a token:

```bash
# This should also fail
echo '{"type":"test","payload":{"message":"This should fail too"}}' | websocat "ws://localhost:8000/ws"
```

## Complete Shell Script Example

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

## Common Message Types

Here are some example messages you can send:

```json
{"type":"test","payload":{"message":"Test message"}}
{"type":"zip_collected","payload":{"zipCode":"12345"}}
{"type":"weight_confirmed","payload":{"weight":2.5,"unit":"kg"}}
{"type":"quote_ready","payload":{"price":15.99,"currency":"USD"}}
```

## Troubleshooting

### Connection Closed with Code 1008

If you receive a "Connection closed with code 1008" error, it means your token is invalid or expired. Try obtaining a new token.

### Invalid JSON

Make sure your messages are valid JSON. Common issues include:
- Missing quotes around property names
- Using single quotes instead of double quotes
- Missing commas between properties

### Token Expiration

JWT tokens expire after 30 minutes by default. If your token expires, you'll need to obtain a new one.

## Advanced Usage

### Custom Headers

You can add custom headers to your WebSocket connection:

```bash
websocat "ws://localhost:8000/ws?token=$TOKEN" \
  --header "X-Custom-Header: value"
```

### Binary Messages

For binary messages:

```bash
echo -e '\x01\x02\x03\x04' | websocat --binary "ws://localhost:8000/ws?token=$TOKEN"
```

### Connecting to Secure WebSockets (WSS)

For secure WebSocket connections:

```bash
websocat "wss://example.com/ws?token=$TOKEN"
```
