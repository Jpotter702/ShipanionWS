#!/bin/bash
# Simple script to test WebSocket connection using the pre-generated test token

# Get the test token
echo "Getting test token..."
TEST_TOKEN_RESPONSE=$(curl -s "http://localhost:8000/test-token")
TEST_TOKEN=$(echo $TEST_TOKEN_RESPONSE | grep -o '"test_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TEST_TOKEN" ]; then
    echo "Failed to get test token. Make sure the server is running."
    exit 1
fi

echo "Test token: ${TEST_TOKEN:0:20}..."
echo "Connecting to WebSocket with test token..."

# Connect to WebSocket with the test token
echo '{"type":"test","payload":{"message":"Hello using test token"}}' | \
    websocat "ws://localhost:8000/ws?token=$TEST_TOKEN"

echo "Done!"
