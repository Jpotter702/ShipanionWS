# Sprint 3 Backend Tests

This directory contains backend tests for the features implemented in Sprint 3 of the Shipanion project.

## Test Scripts

### 1. ElevenLabs Integration Tests

### `test_bob_quote_response.py`

This script tests a full round-trip where Bob receives a `client_tool_result` and speaks it aloud. If Bob fails to respond or misses the quote, you can use the analysis tools to inspect the JSON payload for formatting issues.

#### Usage

```bash
# Run the test
python tests/sprint3/test_bob_quote_response.py

# Run with custom WebSocket and API URLs
WS_SERVER_URL=ws://localhost:8000/ws API_SERVER_URL=http://localhost:8000 python tests/sprint3/test_bob_quote_response.py
```

### `test_bob_speaks_quote.py`

This script sends a test quote via WebSocket using `client_tool_result` and checks if Bob speaks the price and carrier clearly. It provides guidance on adjusting the tool prompt in Agent Studio if needed.

#### Usage

```bash
# Run the test
python tests/sprint3/test_bob_speaks_quote.py

# Run with custom WebSocket and API URLs
WS_SERVER_URL=ws://localhost:8000/ws API_SERVER_URL=http://localhost:8000 python tests/sprint3/test_bob_speaks_quote.py
```

### `BOB_QUOTE_CHECKLIST.md`

A checklist for verifying that Bob correctly speaks shipping quotes aloud when receiving a `client_tool_result` message. Use this to manually verify Bob's response.

### 2. Contextual Update Tests

### `test_contextual_update.py`

Tests sending a contextual update back to ElevenLabs and the AccordionStepper UI after returning a `client_tool_result`.

#### Usage

```bash
# Run the test
python tests/sprint3/test_contextual_update.py

# Run with custom WebSocket and API URLs
WS_SERVER_URL=ws://localhost:8000/ws API_SERVER_URL=http://localhost:8000 python tests/sprint3/test_contextual_update.py
```

### 3. Session Continuity Tests

### `test_session_continuity.py`

Tests session continuity features, including adding `session_id` to all messages, reconnecting and resuming a session, and ElevenLabs session resumption.

#### Usage

```bash
# Run the test
python tests/sprint3/test_session_continuity.py

# Run with custom WebSocket and API URLs
WS_SERVER_URL=ws://localhost:8000/ws API_SERVER_URL=http://localhost:8000 python tests/sprint3/test_session_continuity.py
```

## Analysis Tools

### `analyze_payload.py`

This tool analyzes a JSON payload to identify formatting issues that might cause Bob to fail to respond or miss the quote.

#### Usage

```bash
# Analyze a JSON file
python tools/analyze_payload.py path/to/payload.json

# Analyze from stdin
cat path/to/payload.json | python tools/analyze_payload.py
```

### `capture_websocket.py`

This tool captures WebSocket messages between the client and server for debugging purposes. It logs all messages to a file and can filter for specific message types.

#### Usage

```bash
# Capture all messages for 60 seconds
python tools/capture_websocket.py

# Capture only client_tool_result messages for 120 seconds
python tools/capture_websocket.py --filter client_tool_result --duration 120

# Specify output file and server URLs
python tools/capture_websocket.py --output quotes.txt --ws-url ws://localhost:8000/ws --api-url http://localhost:8000
```

### `simulate_bob_response.py`

This tool simulates how Bob would respond to a `client_tool_result` message. It helps debug issues with Bob's response to shipping quotes.

#### Usage

```bash
# Simulate Bob's response to a JSON file
python tools/simulate_bob_response.py path/to/payload.json

# Simulate Bob's response from stdin
cat path/to/payload.json | python tools/simulate_bob_response.py
```

### `analyze_bob_response.py`

This tool analyzes Bob's spoken response to a shipping quote and compares it to the expected format. It helps identify issues with Bob's response and provides suggestions for improvement.

#### Usage

```bash
# Analyze Bob's response (will prompt for input)
python tools/analyze_bob_response.py

# Analyze Bob's response from a file
python tools/analyze_bob_response.py --response "I've found some shipping options for you. The most affordable option is USPS Priority Mail at $9.99..."
```

## Troubleshooting

If Bob fails to respond or misses the quote, follow these steps:

1. Run the `test_bob_quote_response.py` script to verify the issue
2. Use `capture_websocket.py` to capture the WebSocket messages
3. Use `analyze_payload.py` to check for formatting issues in the captured messages
4. Use `simulate_bob_response.py` to see how Bob would respond to the message

If Bob speaks the quote but doesn't do it clearly:

1. Run the `test_bob_speaks_quote.py` script to verify the issue
2. Use the `BOB_QUOTE_CHECKLIST.md` to manually verify Bob's response
3. Use `analyze_bob_response.py` to analyze Bob's spoken response
4. Refer to the `AGENT_STUDIO_PROMPT_GUIDE.md` for guidance on adjusting the tool prompt

### Common Issues

1. **Missing Fields**: The `client_tool_result` message might be missing required fields like `tool_call_id` or `result`.
2. **Incorrect Format**: The `result` field might not be an array or might have incorrect field names.
3. **Missing `client_tool_call` Field**: ElevenLabs requires the original `client_tool_call` to be included in the response.
4. **Error Response**: If `is_error` is `true`, Bob will respond with an error message instead of quoting the shipping options.

## Expected Format

The expected format for a `client_tool_result` message that Bob can respond to is:

```json
{
  "type": "client_tool_result",
  "tool_call_id": "test-quotes-123456789",
  "result": [
    {
      "carrier": "UPS",
      "service": "Ground",
      "price": 12.99,
      "eta": "3-5 business days"
    },
    {
      "carrier": "USPS",
      "service": "Priority Mail",
      "price": 9.99,
      "eta": "2-3 business days"
    }
  ],
  "is_error": false,
  "client_tool_call": {
    "tool_name": "get_shipping_quotes",
    "tool_call_id": "test-quotes-123456789",
    "parameters": {
      "from_zip": "90210",
      "to_zip": "10001",
      "weight": 5.0
    }
  }
}
```

## Running All Tests

To run all tests, execute the following commands:

```bash
python -m tests.sprint3.test_bob_quote_response
python -m tests.sprint3.test_bob_speaks_quote
python -m tests.sprint3.test_contextual_update
python -m tests.sprint3.test_session_continuity
```

## Test Results

Document your test results in a test report that includes:

1. Test name
2. Pass/Fail status
3. Any issues encountered
4. Logs or output
5. Recommendations for fixes or improvements
