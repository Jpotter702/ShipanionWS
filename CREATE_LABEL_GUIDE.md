# Create Label Tool Integration Guide

This guide explains how to integrate the ElevenLabs Conversational AI with the WebSocket server to create shipping labels in real-time.

## Overview

The create_label integration allows:
1. The ElevenLabs voice agent to create shipping labels through a client tool
2. The WebSocket server to process the request and create labels via the ShipVox API
3. The voice agent to receive and speak the label information to the user
4. The UI to update in real-time with the same label information

## Message Flow

```
ElevenLabs Agent                WebSocket Server                ShipVox API
      |                               |                             |
      |--- client_tool_call --------->|                             |
      |                               |--- HTTP Request ----------->|
      |                               |<-- HTTP Response ----------|
      |<-- client_tool_result --------|                             |
      |                               |--- contextual_update ------>|
      |                               |                             |
```

## Setting Up the ElevenLabs Client Tool

### 1. Create the Client Tool in ElevenLabs Dashboard

1. Navigate to your agent in the ElevenLabs dashboard
2. Go to the **Tools** section and click **Add Tool**
3. Configure the tool:
   - **Tool Type**: Client
   - **Name**: `create_label`
   - **Description**: "Create a shipping label for a package"
   - **Parameters**:
     - `carrier` (String): "Carrier name (fedex, ups)"
     - `service_type` (String): "Service type code (e.g., FEDEX_GROUND)"
     - `shipper_name` (String): "Shipper's full name"
     - `shipper_street` (String): "Shipper's street address"
     - `shipper_city` (String): "Shipper's city"
     - `shipper_state` (String): "Shipper's state (2-letter code)"
     - `shipper_zip` (String): "Shipper's ZIP code"
     - `recipient_name` (String): "Recipient's full name"
     - `recipient_street` (String): "Recipient's street address"
     - `recipient_city` (String): "Recipient's city"
     - `recipient_state` (String): "Recipient's state (2-letter code)"
     - `recipient_zip` (String): "Recipient's ZIP code"
     - `weight` (Number): "Package weight in pounds"
     - `dimensions` (Object, optional): "Package dimensions in inches"
   - **Wait for response**: Enabled

### 2. Update the Agent Prompt

Add instructions to your agent prompt to guide the agent on when to use the tool:

```
You can create shipping labels by using the create_label tool when a user wants to ship a package.
You need to collect all the required information:
- Carrier preference (FedEx or UPS)
- Service type (Ground, Express, etc.)
- Shipper's full address
- Recipient's full address
- Package weight
- Package dimensions (optional)

After creating the label, inform the user that the label has been created and is available for download.
```

## Client Tool Call Format

When the ElevenLabs agent calls the `create_label` tool, it sends a message with the following format:

```json
{
  "type": "client_tool_call",
  "client_tool_call": {
    "tool_name": "create_label",
    "tool_call_id": "abc123",
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
}
```

## Client Tool Result Format

The WebSocket server responds with a message in the following format:

```json
{
  "type": "client_tool_result",
  "tool_call_id": "abc123",
  "result": {
    "tracking_number": "794644746986",
    "label_url": "https://shipvox.com/labels/794644746986.pdf",
    "qr_code": "https://shipvox.com/qr/794644746986.png",
    "carrier": "FedEx",
    "estimated_delivery": "2023-05-15T12:00:00Z"
  },
  "is_error": false,
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Contextual Update Format

The WebSocket server also broadcasts a `contextual_update` message to all connected clients, allowing the UI to update in real-time:

```json
{
  "type": "contextual_update",
  "text": "label_created",
  "data": {
    "tracking_number": "794644746986",
    "carrier": "FedEx",
    "label_url": "https://shipvox.com/labels/794644746986.pdf",
    "qr_code": "https://shipvox.com/qr/794644746986.png",
    "estimated_delivery": "2023-05-15T12:00:00Z"
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

Common errors include:
- Missing required fields
- Invalid ZIP code format
- Invalid carrier or service type
- Weight or dimensions out of acceptable range
- Carrier API connection issues

## Testing the Integration

### Using the Test Scripts

You can test the integration using the provided test scripts:

```bash
# Test the create_label tool specifically
python -m pytest websocket/tests/sprint2/test_create_label.py -v

# Or use the shell script for quick testing
./websocket/test_create_label.sh
```

### Manual Testing

1. Start the WebSocket server and ShipVox backend
2. Use the ElevenLabs dashboard to test the agent
3. Ask to create a shipping label (e.g., "I need to create a shipping label for a package from Beverly Hills to New York")
4. Provide all the required information when prompted
5. Verify that the agent receives and speaks the label information
6. Verify that the UI updates with the label information

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

- Add support for more client tools (e.g., `schedule_pickup`)
- Implement session tracking to maintain context across multiple tool calls
- Add authentication for the ElevenLabs integration
- Enhance error handling and retry logic
