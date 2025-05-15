# Shipanion WebSocket UI Control Demo

This demo shows how the ShipanionWS backend can control the ShipanionUI frontend via WebSocket messages.

## Overview

The demo consists of two main parts:

1. **Backend Script (ShipanionWS)**: `ws_ui_demo.py` - Sends various commands to the UI
2. **Frontend Component (ShipanionUI)**: `/app/ws-demo` - Displays a UI that responds to WebSocket messages

## How It Works

The WebSocket communication allows real-time bidirectional communication between the backend and frontend:

1. Backend sends messages to the UI with specific message types (contextual updates, notifications, etc.)
2. Frontend listens for these messages and updates its state and UI accordingly
3. This creates a dynamic, real-time user experience where the backend can control what's shown in the UI

## Message Types Demonstrated

The demo shows how to send and handle these types of messages:

- `contextual_update` - Updates about the shipping process (ZIP codes, weight)
- `quote_ready` - Shipping quotes from different carriers
- `notification` - Alerts and notifications to show the user
- `label_created` - Shipping label generation confirmation

## Running the Demo

### Prerequisites

1. Both ShipanionWS and ShipanionUI must be set up and running
2. The JWT secret key in `ws_ui_demo.py` should match the one in `backend/settings.py`
3. WebSocket URL in the UI (default: `ws://localhost:8001/ws`) should point to your WS backend

### Step 1: Start the WebSocket Backend

```bash
# In the ShipanionWS directory
python -m uvicorn backend.main:app --reload --port 8001
```

### Step 2: Start the UI Frontend

```bash
# In the ShipanionUI directory
npm run dev
```

### Step 3: Open the Demo Page

Navigate to http://localhost:3000/ws-demo in your browser.

### Step 4: Run the Demo Script

```bash
# In the ShipanionWS directory
python ws_ui_demo.py
```

## Demo Sequence

The demo script will:

1. Send a ZIP code collection update
2. Send a weight confirmation update
3. Send shipping quotes
4. Send a notification
5. Send a shipping label creation update

## Customizing the Demo

You can modify `ws_ui_demo.py` to send different types of messages or change the timing. The WebSocket message format is documented in the code.

## WebSocket Message Formats

### Contextual Update (ZIP Collection)
```json
{
  "type": "contextual_update",
  "text": "zip_collected",
  "data": {
    "origin_zip": "10001",
    "destination_zip": "90210"
  }
}
```

### Contextual Update (Weight Confirmation)
```json
{
  "type": "contextual_update",
  "text": "weight_confirmed",
  "data": {
    "weight": 2.5,
    "unit": "lbs"
  }
}
```

### Shipping Quotes
```json
{
  "type": "quote_ready",
  "payload": {
    "quotes": [
      {
        "carrier": "FedEx",
        "service_name": "Ground",
        "cost": 12.99,
        "transit_days": 3
      },
      // More quotes...
    ]
  }
}
```

### Notification
```json
{
  "type": "notification",
  "payload": {
    "type": "success",
    "title": "Demo Notification",
    "message": "This notification was sent from the WebSocket demo script!"
  }
}
```

### Label Created
```json
{
  "type": "label_created",
  "payload": {
    "tracking_number": "1Z999AA10123456784",
    "carrier": "UPS",
    "service_name": "Ground",
    "cost": 14.99,
    "label_url": "https://example.com/label.pdf",
    "qr_code": "data:image/png;base64,..."
  }
}
```

## Next Steps

This demo shows the basic concept of WebSocket-controlled UI. For a production system, you should:

1. Implement proper error handling
2. Add authentication and security measures
3. Consider using a more sophisticated state management system
4. Add more interactive features that go beyond simple UI updates 