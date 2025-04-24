# Timeout Handling for REST Calls

This document explains the timeout handling implementation for REST calls to the ShipVox API.

## Overview

The WebSocket server has been updated to properly handle timeouts when making REST calls to the ShipVox API. When a call to `/get-rates` takes too long, the server now:

1. Logs the timeout error with detailed information
2. Sends a `client_tool_result` back to the client with:
   - `is_error: true`
   - The exact error message `timeout calling rates endpoint`

## Implementation Details

### 1. ShipVox Client

The `ShipVoxClient` class in `shipvox_client.py` has been updated to:

- Accept a `timeout_seconds` parameter in the `get_rates` method (default: 10.0 seconds)
- Create a specific `httpx.Timeout` object for each request
- Catch `httpx.TimeoutException` and raise a new exception with the exact error message `timeout calling rates endpoint`

```python
async def get_rates(self, rate_request: Dict[str, Any], timeout_seconds: float = 10.0) -> Dict[str, Any]:
    # ...
    # Create a specific timeout for this request
    timeout = httpx.Timeout(timeout_seconds)
    
    try:
        response = await self.client.post(url, json=rate_request, timeout=timeout)
        # ...
    except httpx.TimeoutException as e:
        logger.error(f"Rate request timed out after {timeout_seconds} seconds: {str(e)}")
        # Use the exact error message specified in the requirements
        raise Exception("timeout calling rates endpoint")
    # ...
```

### 2. ElevenLabs Handler

The `handle_get_shipping_quotes` function in `elevenlabs_handler.py` has been updated to:

- Call `shipvox_client.get_rates` with a 10-second timeout
- Handle the timeout exception and return a properly formatted error response

### 3. Rate Request Handler

The `handle_rate_request` function in `handlers.py` has been similarly updated to:

- Call `shipvox_client.get_rates` with a 10-second timeout
- Handle the timeout exception and return a properly formatted error response

## Error Response Format

### For Client Tool Calls

```json
{
  "type": "client_tool_result",
  "tool_call_id": "<tool_call_id>",
  "result": {
    "error": "timeout calling rates endpoint",
    "original_request": { ... }
  },
  "is_error": true,
  "timestamp": 1650000000000,
  "requestId": "<request_id>"
}
```

### For Direct Rate Requests

```json
{
  "type": "error",
  "payload": {
    "message": "Failed to get shipping rates: timeout calling rates endpoint",
    "original_request": { ... },
    "is_error": true
  },
  "timestamp": 1650000000000,
  "requestId": "<request_id>",
  "user": "<username>"
}
```

## Testing

Two test scripts have been provided to verify the timeout handling functionality:

1. `test_timeout_handling.py`: Tests the timeout handling for client tool calls
2. `mock_timeout_server.py`: A mock server that simulates timeouts for testing

### Running the Tests

1. Start the mock timeout server:

```bash
cd /home/jason/Shipanion/websocket
python mock_timeout_server.py
```

2. Update the `SHIPVOX_API_URL` environment variable to point to the mock server:

```bash
export SHIPVOX_API_URL="http://localhost:8002/api"
```

3. Start the WebSocket server in another terminal:

```bash
cd /home/jason/Shipanion/websocket
python -m uvicorn backend.main:app --reload --port 8001
```

4. Run the timeout test:

```bash
cd /home/jason/Shipanion/websocket
python test_timeout_handling.py
```

## Benefits

This improved timeout handling:

1. Ensures that the client receives a clear error message when a request times out
2. Prevents the WebSocket connection from hanging indefinitely
3. Allows the client to gracefully handle timeout scenarios
4. Improves the overall reliability and user experience of the application
