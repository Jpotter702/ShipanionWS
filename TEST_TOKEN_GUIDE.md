# Test Token Guide

This document provides a comprehensive guide for using the pre-generated test token for WebSocket authentication.

## What is the Test Token?

The test token is a pre-generated JWT (JSON Web Token) that:
- Is valid for the 'user' account
- Does not expire
- Is hardcoded in the application
- Can be used for quick testing without authentication

## Why Use a Test Token?

The test token simplifies the testing process by:
- Eliminating the need to authenticate with username/password for each test
- Providing a consistent token that doesn't expire
- Making it easier to automate tests
- Allowing quick manual testing with tools like websocat

## How to Get the Test Token

### Option 1: Use the Test Token Endpoint

The application provides a dedicated endpoint to retrieve the test token:

```bash
# Get the test token
curl "http://localhost:8000/test-token"

# Response
{
  "test_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko",
  "note": "This token is for testing only. It is valid for the 'user' account and does not expire."
}
```

### Option 2: Use the Hardcoded Value

You can directly use the hardcoded test token value:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko
```

## How to Use the Test Token

### With websocat

```bash
# Using the test token directly
echo '{"type":"test","payload":{"message":"Hello"}}' | \
  websocat "ws://localhost:8000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko"

# Or store it in a variable first
TEST_TOKEN=$(curl -s "http://localhost:8000/test-token" | grep -o '"test_token":"[^"]*' | cut -d'"' -f4)
echo '{"type":"test","payload":{"message":"Hello"}}' | websocat "ws://localhost:8000/ws?token=$TEST_TOKEN"
```

### With the Provided Test Script

A convenience script is provided to test the WebSocket connection using the test token:

```bash
# Run the test script
./test_token_websocket.sh
```

### In Frontend Applications

```typescript
// Get the test token
async function getTestToken() {
  const response = await fetch('http://localhost:8000/test-token');
  const data = await response.json();
  return data.test_token;
}

// Use the test token for WebSocket connection
const testToken = await getTestToken();
const ws = new WebSocket(`ws://localhost:8000/ws?token=${testToken}`);
```

### With the Python Client

The Python client supports multiple ways to use the test token:

```bash
# Option 1: Use the --use-test-token flag to automatically fetch the test token
./ws_jwt_client.py --use-test-token --type test --payload '{"message":"Hello with test token"}'

# Option 2: Provide the test token directly
./ws_jwt_client.py --token "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko" \
  --type test --payload '{"message":"Hello with test token"}'

# Option 3: Interactive mode with test token
./ws_jwt_client.py --use-test-token --interactive
```

## Customizing the Test Token

You can override the default test token in two ways:

### 1. Using Environment Variables

Set the `WS_TEST_TOKEN` environment variable:

```bash
# Set a custom test token
export WS_TEST_TOKEN="your-custom-test-token"

# Start the server
uvicorn backend.main:app --reload
```

### 2. Using a .env File

Create a `.env` file based on the provided `.env.example`:

```
# .env file
JWT_SECRET_KEY=your_secure_secret_key_here
WS_TEST_TOKEN=your_custom_test_token
```

## Test Token Implementation

The test token is implemented in the following files:

### backend/security.py

```python
# Test token for easy testing (valid for the 'user' account)
# This is a pre-generated token that doesn't expire
# Only use this for testing, never in production
TEST_TOKEN = os.environ.get(
    "WS_TEST_TOKEN",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko"
)
```

### backend/main.py

```python
# Endpoint to get the test token
@app.get("/test-token", response_model=TestToken)
async def get_test_token():
    """Get a pre-generated test token for the 'user' account.
    This is for testing purposes only and should not be used in production.
    """
    return {
        "test_token": TEST_TOKEN,
        "note": "This token is for testing only. It is valid for the 'user' account and does not expire."
    }
```

## Security Considerations

The test token is intended for development and testing purposes only. For production environments:

1. **Disable the Test Token Endpoint**: Remove or disable the `/test-token` endpoint
2. **Remove the Hardcoded Token**: Remove the hardcoded test token from the codebase
3. **Use Proper Authentication**: Always use proper authentication with expiring tokens
4. **Implement HTTPS/WSS**: Use secure connections for all communication

## Troubleshooting

### Token Not Working

If the test token is not working:

1. Make sure the server is running with the same JWT secret key that was used to generate the token
2. Check if you've overridden the test token with an environment variable
3. Verify that you're using the correct token format in the WebSocket URL

### Server Rejecting the Token

If the server rejects the test token with a 1008 error:

1. The token might be malformed or corrupted
2. The JWT secret key might have changed
3. You might be using a different token than expected

## Conclusion

The test token provides a convenient way to test WebSocket authentication without going through the authentication process each time. It's especially useful for development and automated testing scenarios.

Remember that while the test token simplifies testing, it should never be used in production environments where proper security measures are essential.
