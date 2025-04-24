#!/bin/bash
# Test script for session tracking

# Set variables
WS_SERVER_URL=${WS_SERVER_URL:-"ws://localhost:8000/ws"}
API_SERVER_URL=${API_SERVER_URL:-"http://localhost:8000"}
SESSION_ID=${SESSION_ID:-""}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --session-id)
      SESSION_ID="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Session Tracking Test ===${NC}"
echo "Server URL: $WS_SERVER_URL"

# Get test token
echo -e "\n${YELLOW}Getting test token...${NC}"
TEST_TOKEN=$(curl -s "$API_SERVER_URL/test-token" | grep -o '"test_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TEST_TOKEN" ]; then
    echo -e "${RED}Failed to get test token${NC}"
    exit 1
fi

echo -e "${GREEN}Got test token: ${TEST_TOKEN:0:15}...${NC}"

# Check if websocat is installed
if ! command -v websocat &> /dev/null; then
    echo -e "${RED}websocat is not installed. Please install it to run this test.${NC}"
    echo "You can install it with: cargo install websocat"
    echo "Or download a binary from: https://github.com/vi/websocat/releases"
    exit 1
fi

# Create WebSocket URL with session ID if provided
WS_URL="$WS_SERVER_URL?token=$TEST_TOKEN"
if [ -n "$SESSION_ID" ]; then
    WS_URL="$WS_URL&session_id=$SESSION_ID"
    echo -e "\n${YELLOW}Connecting to existing session: $SESSION_ID${NC}"
else
    echo -e "\n${YELLOW}Creating a new session${NC}"
fi

# Connect to WebSocket
echo -e "\n${YELLOW}Connecting to WebSocket...${NC}"
echo "URL: $WS_URL"

# Use websocat to connect and capture the session ID from logs
WEBSOCAT_OUTPUT=$(mktemp)
websocat --no-close -n1 "$WS_URL" > "$WEBSOCAT_OUTPUT" 2>&1 &
WEBSOCAT_PID=$!

# Wait for connection to establish
sleep 2

# Check if connection was successful
if ! ps -p $WEBSOCAT_PID > /dev/null; then
    echo -e "${RED}Failed to connect to WebSocket${NC}"
    cat "$WEBSOCAT_OUTPUT"
    rm "$WEBSOCAT_OUTPUT"
    exit 1
fi

echo -e "${GREEN}Connected to WebSocket${NC}"

# Send a test message to get the session ID
echo -e "\n${YELLOW}Sending test message...${NC}"
TEST_MESSAGE='{
    "type": "ping",
    "payload": {
        "message": "Hello, server!"
    },
    "timestamp": '$(date +%s000)',
    "requestId": "test-'$(date +%s)'"
}'

echo "$TEST_MESSAGE" | websocat --no-close -n1 "$WS_URL" > "$WEBSOCAT_OUTPUT" 2>&1 &

# Wait for response
sleep 2

# Display the response
echo -e "\n${GREEN}Response received:${NC}"
cat "$WEBSOCAT_OUTPUT"

# Extract session ID from the response
EXTRACTED_SESSION_ID=$(grep -o '"session_id":"[^"]*' "$WEBSOCAT_OUTPUT" | head -1 | cut -d'"' -f4)

if [ -n "$EXTRACTED_SESSION_ID" ]; then
    echo -e "\n${GREEN}Session ID: $EXTRACTED_SESSION_ID${NC}"
    echo "You can use this session ID to connect multiple clients to the same session:"
    echo "  $WS_URL&session_id=$EXTRACTED_SESSION_ID"
else
    echo -e "\n${YELLOW}No session ID found in response${NC}"
fi

# Clean up
rm "$WEBSOCAT_OUTPUT"
kill $WEBSOCAT_PID 2>/dev/null

echo -e "\n${BLUE}=== Test completed successfully ===${NC}"
