# ElevenLabs Integration Guide

This guide explains how to integrate the ElevenLabs Conversational AI with the WebSocket server to get shipping rates in real-time using the `get_shipping_quotes` client tool.

## Overview

The ElevenLabs integration allows:
1. The ElevenLabs voice agent to request shipping rates through a client tool
2. The WebSocket server to process the request and fetch rates from the ShipVox API
3. The voice agent to receive and speak the rate information to the user
4. The UI to update in real-time with the same rate information

## Message Flow

```
ElevenLabs Agent                WebSocket Server                ShipVox API
      |                               |                             |
      |--- client_tool_call --------->|                             |
      |                               |--- HTTP Request ----------->|
      |                               |<-- HTTP Response ----------|
      |<-- client_tool_result --------|                             |
      |                               |--- quote_ready (broadcast)->|
      |                               |                             |
```

## Setting Up the ElevenLabs Client Tool

### 1. Create the Client Tool in ElevenLabs Dashboard

1. Navigate to your agent in the ElevenLabs dashboard
2. Go to the **Tools** section and click **Add Tool**
3. Configure the tool:
   - **Tool Type**: Client
   - **Name**: `get_shipping_quotes`
   - **Description**: "Get shipping rates for a package from origin to destination"
   - **Parameters**:
     - `from_zip` (String): "Origin ZIP code (5-digit format)"
     - `to_zip` (String): "Destination ZIP code (5-digit format)"
     - `weight` (Number): "Package weight in pounds"
     - `dimensions` (Object, optional): "Package dimensions in inches"
     - `pickup_requested` (Boolean, optional): "Whether pickup is requested"
   - **Wait for response**: Enabled

### 2. Update the Agent Prompt

Add instructions to your agent prompt to guide the agent on when to use the tool:

```
You can get shipping quotes by using the get_shipping_quotes tool when a user asks about shipping costs.
You need to collect the origin ZIP code, destination ZIP code, and package weight.
Optionally, you can also collect package dimensions (length, width, height) and whether pickup is requested.
After receiving the quotes, present the cheapest option first, followed by the fastest option if different.
```

## Client Tool Call Format

When the ElevenLabs agent calls the `get_shipping_quotes` tool, it sends a message with the following format:

```json
{
  "type": "client_tool_call",
  "client_tool_call": {
    "tool_name": "get_shipping_quotes",
    "tool_call_id": "abc123",
    "parameters": {
      "from_zip": "90210",
      "to_zip": "10001",
      "weight": 5.0,
      "dimensions": {
        "length": 12.0,
        "width": 8.0,
        "height": 6.0
      },
      "pickup_requested": false
    }
  }
}
```

The `dimensions` and `pickup_requested` parameters are optional and can be omitted if not needed.

## Client Tool Result Format

The WebSocket server responds with a message in the following format:

```json
{
  "type": "client_tool_result",
  "tool_call_id": "abc123",
  "result": [
    {
      "carrier": "UPS",
      "service": "Ground",
      "price": 8.44,
      "eta": "3 days"
    },
    {
      "carrier": "FedEx",
      "service": "Express",
      "price": 22.10,
      "eta": "1 day"
    }
  ],
  "is_error": false,
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440001"
}
```

## UI Integration

The WebSocket server also broadcasts a `quote_ready` message to all connected clients, allowing the UI to update in real-time:

```json
{
  "type": "quote_ready",
  "payload": {
    "cheapest_option": {
      "carrier": "UPS",
      "service_name": "Ground",
      "service_tier": "STANDARD",
      "cost": 8.44,
      "estimated_delivery": "2023-05-15T12:00:00Z",
      "transit_days": 3
    },
    "fastest_option": {
      "carrier": "FedEx",
      "service_name": "Express",
      "service_tier": "EXPRESS",
      "cost": 22.10,
      "estimated_delivery": "2023-05-13T12:00:00Z",
      "transit_days": 1
    },
    "all_options": [
      // Array of all available rate options
    ]
  },
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440001",
  "user": "username"
}
```

## Error Handling

If there's an error processing the tool call, the server responds with an error message:

```json
{
  "type": "client_tool_result",
  "tool_call_id": "abc123",
  "result": {
    "error": "Error message describing what went wrong",
    "original_request": {
      // Original request that caused the error
    }
  },
  "is_error": true,
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440002"
}
```

## Testing the Integration

### Using the Test Scripts

You can test the integration using the provided test scripts:

```bash
# Test the general ElevenLabs integration
python -m pytest websocket/tests/sprint2/test_elevenlabs_integration.py -v

# Test the get_shipping_quotes tool specifically
python -m pytest websocket/tests/sprint2/test_get_shipping_quotes.py -v

# Or use the shell script for quick testing
./websocket/test_get_shipping_quotes.sh
```

### Manual Testing

1. Start the WebSocket server and ShipVox backend
2. Use the ElevenLabs dashboard to test the agent
3. Ask for shipping rates (e.g., "I need to ship a 5-pound package from 90210 to 10001")
4. Verify that the agent receives and speaks the rate information
5. Try including package dimensions (e.g., "The package is 12 inches long, 8 inches wide, and 6 inches tall")
6. Verify that the agent includes this information in the request

## Troubleshooting

### Common Issues

- **Tool not being called**: Ensure the tool name and parameters in ElevenLabs match exactly what the WebSocket server expects
- **Missing parameters**: Check that the agent is collecting all required parameters before calling the tool
- **Connection issues**: Verify that the WebSocket server is running and accessible from ElevenLabs

### Debugging

- Check the WebSocket server logs for errors
- Use the test script to verify the WebSocket server is processing tool calls correctly
- Test the ShipVox API directly to ensure it's returning valid responses

## Next Steps

- Add support for more client tools (e.g., `create_label`, `schedule_pickup`)
- Implement session tracking to maintain context across multiple tool calls
- Add authentication for the ElevenLabs integration
- Enhance error handling and retry logic
