#!/bin/bash
# Test script for the create_label ElevenLabs client tool

# Set variables
WS_SERVER_URL=${WS_SERVER_URL:-"ws://localhost:8000/ws"}
API_SERVER_URL=${API_SERVER_URL:-"http://localhost:8000"}

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ElevenLabs create_label Test ===${NC}"
echo "Server URL: $WS_SERVER_URL"

# Get test token
echo -e "\n${YELLOW}Getting test token...${NC}"
TEST_TOKEN=$(curl -s "$API_SERVER_URL/test-token" | grep -o '"test_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TEST_TOKEN" ]; then
    echo -e "${RED}Failed to get test token${NC}"
    exit 1
fi

echo -e "${GREEN}Got test token: ${TEST_TOKEN:0:15}...${NC}"

# Create a valid client tool call payload for create_label
VALID_TOOL_CALL='{
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "create_label",
        "tool_call_id": "test-123",
        "parameters": {
            "carrier": "fedex",
            "service_type": "FEDEX_GROUND",
            "shipper_name": "John Doe",
            "shipper_street": "123 Main St",
            "shipper_city": "Beverly Hills",
            "shipper_state": "CA",
            "shipper_zip": "90210",
            "recipient_name": "Jane Smith",
            "recipient_street": "456 Park Ave",
            "recipient_city": "New York",
            "recipient_state": "NY",
            "recipient_zip": "10001",
            "weight": 5.0,
            "dimensions": {
                "length": 12.0,
                "width": 8.0,
                "height": 6.0
            }
        }
    }
}'

# Check if websocat is installed
if ! command -v websocat &> /dev/null; then
    echo -e "${RED}websocat is not installed. Please install it to run this test.${NC}"
    echo "You can install it with: cargo install websocat"
    echo "Or download a binary from: https://github.com/vi/websocat/releases"
    exit 1
fi

# Test valid tool call
echo -e "\n${YELLOW}Testing create_label tool call...${NC}"
echo "Payload: $VALID_TOOL_CALL"

# Use websocat to send the request and capture the response
echo -e "\n${YELLOW}Sending request and waiting for response...${NC}"
RESPONSE=$(echo "$VALID_TOOL_CALL" | \
    websocat --no-close -n1 "$WS_SERVER_URL?token=$TEST_TOKEN" 2>/dev/null)

# Check if we got a response
if [ -z "$RESPONSE" ]; then
    echo -e "${RED}No response received${NC}"
    exit 1
fi

# Print the response
echo -e "\n${GREEN}Response received:${NC}"
echo "$RESPONSE" | python3 -m json.tool

# Check if it's a client_tool_result response
if echo "$RESPONSE" | grep -q '"type":"client_tool_result"'; then
    echo -e "\n${GREEN}✓ Test passed: Received client_tool_result response${NC}"
else
    echo -e "\n${RED}✗ Test failed: Did not receive client_tool_result response${NC}"
    exit 1
fi

# Check if the result is not an error
if echo "$RESPONSE" | grep -q '"is_error":false'; then
    echo -e "${GREEN}✓ Test passed: Result is not an error${NC}"
else
    echo -e "${RED}✗ Test failed: Result is an error${NC}"
    exit 1
fi

# Wait for contextual update
echo -e "\n${YELLOW}Waiting for contextual update...${NC}"
UPDATE=$(websocat --no-close -n1 "$WS_SERVER_URL?token=$TEST_TOKEN" 2>/dev/null)

# Check if we got an update
if [ -z "$UPDATE" ]; then
    echo -e "${RED}No contextual update received${NC}"
    exit 1
fi

# Print the update
echo -e "\n${GREEN}Contextual update received:${NC}"
echo "$UPDATE" | python3 -m json.tool

# Check if it's a contextual_update message
if echo "$UPDATE" | grep -q '"type":"contextual_update"'; then
    echo -e "\n${GREEN}✓ Test passed: Received contextual_update message${NC}"
else
    echo -e "\n${RED}✗ Test failed: Did not receive contextual_update message${NC}"
    exit 1
fi

# Check if it's a label_created update
if echo "$UPDATE" | grep -q '"text":"label_created"'; then
    echo -e "${GREEN}✓ Test passed: Received label_created update${NC}"
else
    echo -e "${RED}✗ Test failed: Did not receive label_created update${NC}"
    exit 1
fi

echo -e "\n${BLUE}=== Test completed successfully ===${NC}"
