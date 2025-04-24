# Rate Request WebSocket Integration Guide

This guide explains how to use the WebSocket API to request shipping rates in real-time.

## Overview

The rate request integration allows clients to:
1. Send shipping details through a WebSocket connection
2. Receive real-time rate quotes from multiple carriers
3. Get the cheapest and fastest shipping options

## Message Flow

```
Client                                Server
  |                                     |
  |--- get_rates (with shipping info)-->|
  |                                     |--- HTTP Request to ShipVox API --->|
  |                                     |<-- HTTP Response with rates -------|
  |<-- quote_ready (with rate options)--|
  |                                     |
```

## Authentication

All WebSocket connections require authentication with a JWT token. See [AUTHENTICATION.md](./AUTHENTICATION.md) for details on obtaining a token.

## Rate Request Message Format

To request shipping rates, send a message with the following format:

```json
{
  "type": "get_rates",
  "payload": {
    "origin_zip": "90210",
    "destination_zip": "10001",
    "weight": 5.0,
    "dimensions": {
      "length": 12.0,
      "width": 8.0,
      "height": 6.0
    },
    "pickup_requested": false
  },
  "timestamp": 1650000000000,
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "broadcast": false
}
```

### Required Fields

- `origin_zip`: Origin ZIP code (5-digit format)
- `destination_zip`: Destination ZIP code (5-digit format)
- `weight`: Package weight in pounds (must be > 0)

### Optional Fields

- `dimensions`: Package dimensions in inches
  - `length`: Length in inches
  - `width`: Width in inches
  - `height`: Height in inches
- `pickup_requested`: Whether pickup is requested (default: false)
- `broadcast`: Whether to broadcast the response to all connected clients (default: false)

## Rate Response Message Format

When rates are available, you'll receive a message with the following format:

```json
{
  "type": "quote_ready",
  "payload": {
    "cheapest_option": {
      "carrier": "FedEx",
      "service_name": "GROUND",
      "service_tier": "STANDARD",
      "cost": 24.99,
      "estimated_delivery": "2023-05-15T12:00:00Z",
      "transit_days": 3
    },
    "fastest_option": {
      "carrier": "UPS",
      "service_name": "2DA",
      "service_tier": "EXPRESS",
      "cost": 34.99,
      "estimated_delivery": "2023-05-13T12:00:00Z",
      "transit_days": 2
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

### Response Fields

- `cheapest_option`: The lowest cost shipping option
- `fastest_option`: The fastest reasonably priced option (may be null)
- `all_options`: Array of all available shipping options

Each option includes:
- `carrier`: Carrier name (e.g., "FedEx", "UPS")
- `service_name`: Carrier-specific service name
- `service_tier`: Normalized service tier (STANDARD, EXPRESS, PRIORITY)
- `cost`: Shipping cost in USD
- `estimated_delivery`: Estimated delivery date and time (ISO format)
- `transit_days`: Number of transit days

## Error Handling

If there's an error processing the rate request, you'll receive an error message:

```json
{
  "type": "error",
  "payload": {
    "message": "Error message describing what went wrong",
    "original_request": {
      // Original request that caused the error
    }
  },
  "timestamp": 1650000001000,
  "requestId": "550e8400-e29b-41d4-a716-446655440002",
  "user": "username"
}
```

Common errors include:
- Missing required fields
- Invalid ZIP code format
- Weight or dimensions out of acceptable range
- Carrier API connection issues

## Frontend Integration Example

Here's how to integrate with the rate request WebSocket in a React application:

```typescript
import { useWebSocket } from '../hooks/useWebSocket';
import { dispatchMessageByType } from '../utils/dispatchMessageByType';
import { RateResponsePayload } from '../types/MessageTypes';
import { useState } from 'react';

function ShippingRateCalculator() {
  const [rateResponse, setRateResponse] = useState<RateResponsePayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Connect to WebSocket with authentication token
  const { status, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws', {
    token: 'your-auth-token-here',
  });
  
  // Process incoming messages
  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      
      dispatchMessageByType(latestMessage, {
        onRateResponse: (payload) => {
          setRateResponse(payload);
          setError(null);
        },
        onError: (message) => {
          setError(message);
        }
      });
    }
  }, [messages]);
  
  // Send rate request
  const requestRates = () => {
    sendMessage({
      type: 'get_rates',
      payload: {
        origin_zip: '90210',
        destination_zip: '10001',
        weight: 5.0,
        dimensions: {
          length: 12.0,
          width: 8.0,
          height: 6.0
        },
        pickup_requested: false
      },
      timestamp: Date.now(),
      requestId: crypto.randomUUID()
    });
  };
  
  // Render UI with rate information
  return (
    <div>
      <button onClick={requestRates} disabled={status !== 'connected'}>
        Get Shipping Rates
      </button>
      
      {error && <div className="error">{error}</div>}
      
      {rateResponse && (
        <div className="rate-options">
          <h2>Shipping Options</h2>
          <div className="cheapest-option">
            <h3>Cheapest Option</h3>
            <p>Carrier: {rateResponse.cheapest_option.carrier}</p>
            <p>Service: {rateResponse.cheapest_option.service_name}</p>
            <p>Cost: ${rateResponse.cheapest_option.cost.toFixed(2)}</p>
            <p>Transit Days: {rateResponse.cheapest_option.transit_days}</p>
          </div>
          
          {/* Display fastest option and all options */}
        </div>
      )}
    </div>
  );
}
```

## Command Line Testing

You can test the rate request WebSocket API using the provided command-line client:

```bash
# First get a test token
TEST_TOKEN=$(curl -s http://localhost:8000/test-token | jq -r .test_token)

# Send a rate request
./ws_jwt_client.py --token $TEST_TOKEN --type get_rates --payload '{"origin_zip":"90210","destination_zip":"10001","weight":5.0,"dimensions":{"length":12.0,"width":8.0,"height":6.0},"pickup_requested":false}'
```

## Next Steps

- Implement caching for frequently requested rate combinations
- Add support for international shipping rates
- Integrate with label creation workflow
