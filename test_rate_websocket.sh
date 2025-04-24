#!/bin/bash
# Test script for the Rate Request WebSocket integration

# Set variables
WS_SERVER_URL=${WS_SERVER_URL:-"ws://localhost:8000/ws"}
API_SERVER_URL=${API_SERVER_URL:-"http://localhost:8000"}

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Rate Request WebSocket Test ===${NC}"
echo "Server URL: $WS_SERVER_URL"

# Get test token
echo -e "\n${YELLOW}Getting test token...${NC}"
TEST_TOKEN=$(curl -s "$API_SERVER_URL/test-token" | grep -o '"test_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TEST_TOKEN" ]; then
    echo -e "${RED}Failed to get test token${NC}"
    exit 1
fi

echo -e "${GREEN}Got test token: ${TEST_TOKEN:0:15}...${NC}"

# Create a valid rate request payload
VALID_PAYLOAD='{
    "origin_zip": "90210",
    "destination_zip": "10001",
    "weight": 5.0,
    "dimensions": {
        "length": 12.0,
        "width": 8.0,
        "height": 6.0
    },
    "pickup_requested": false
}'

# Create an invalid rate request payload (missing required fields)
INVALID_PAYLOAD='{
    "origin_zip": "90210"
}'

# Test valid rate request
echo -e "\n${YELLOW}Testing valid rate request...${NC}"
echo "Payload: $VALID_PAYLOAD"

# Check if websocat is installed
if ! command -v websocat &> /dev/null; then
    echo -e "${RED}websocat is not installed. Please install it to run this test.${NC}"
    echo "You can install it with: cargo install websocat"
    echo "Or download a binary from: https://github.com/vi/websocat/releases"
    exit 1
fi

# Use websocat to send the request and capture the response
echo -e "\n${YELLOW}Sending request and waiting for response...${NC}"
RESPONSE=$(echo "{\"type\":\"get_rates\",\"payload\":$VALID_PAYLOAD,\"timestamp\":$(date +%s000),\"requestId\":\"test-$(date +%s)\"}" | \
    websocat --no-close -n1 "$WS_SERVER_URL?token=$TEST_TOKEN" 2>/dev/null)

# Check if we got a response
if [ -z "$RESPONSE" ]; then
    echo -e "${RED}No response received${NC}"
    exit 1
fi

# Print the response
echo -e "\n${GREEN}Response received:${NC}"
echo "$RESPONSE" | python3 -m json.tool

# Check if it's a quote_ready response
if echo "$RESPONSE" | grep -q '"type":"quote_ready"'; then
    echo -e "\n${GREEN}✓ Test passed: Received quote_ready response${NC}"
else
    echo -e "\n${RED}✗ Test failed: Did not receive quote_ready response${NC}"
    exit 1
fi

# Test invalid rate request
echo -e "\n${YELLOW}Testing invalid rate request...${NC}"
echo "Payload: $INVALID_PAYLOAD"

# Use websocat to send the invalid request and capture the response
echo -e "\n${YELLOW}Sending request and waiting for response...${NC}"
RESPONSE=$(echo "{\"type\":\"get_rates\",\"payload\":$INVALID_PAYLOAD,\"timestamp\":$(date +%s000),\"requestId\":\"test-$(date +%s)\"}" | \
    websocat --no-close -n1 "$WS_SERVER_URL?token=$TEST_TOKEN" 2>/dev/null)

# Check if we got a response
if [ -z "$RESPONSE" ]; then
    echo -e "${RED}No response received${NC}"
    exit 1
fi

# Print the response
echo -e "\n${GREEN}Response received:${NC}"
echo "$RESPONSE" | python3 -m json.tool

# Check if it's an error response
if echo "$RESPONSE" | grep -q '"type":"error"'; then
    echo -e "\n${GREEN}✓ Test passed: Received error response${NC}"
else
    echo -e "\n${RED}✗ Test failed: Did not receive error response${NC}"
    exit 1
fi

echo -e "\n${BLUE}=== All tests completed ===${NC}"
