# Shipanion WebSocket Demo

This repository contains a demonstration of real-time WebSocket communication between the Shipanion backend and UI components.

## Overview

The demo showcases how WebSocket messages can control UI components in real-time, specifically for a shipping application workflow:

1. **Backend (ShipanionWS)**: Sends WebSocket messages with shipping updates
2. **Frontend (ShipanionUI)**: Displays and reacts to these messages in real-time

## Features

- Real-time UI updates via WebSocket
- Shipping workflow demonstration (details, quotes, payment, label)
- Step-by-step visualization with Stepper Accordion
- Performance optimized with throttling and debouncing

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm/yarn
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/Shipanion.git
cd Shipanion
```

### 2. Backend Setup (ShipanionWS)

Create and activate a virtual environment:

```bash
cd ShipanionWS

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt

# If uvicorn is missing, install it explicitly
pip install uvicorn
```

### 3. Frontend Setup (ShipanionUI)

```bash
cd ../ShipanionUI

# Install dependencies
npm install
# or
yarn install
```

## Running the Demo

### 1. Start the WebSocket Backend

In one terminal, navigate to the ShipanionWS directory and run:

```bash
# Make sure your virtual environment is activated
python -m uvicorn backend.main:app --reload --port 8001
```

You should see output indicating the server is running on http://127.0.0.1:8001.

### 2. Start the Frontend Development Server

In another terminal, navigate to the ShipanionUI directory and run:

```bash
npm run dev
# or
yarn dev
```

This will start the Next.js development server, typically on http://localhost:3000.

### 3. Access the WebSocket Demo Page

Open your browser and navigate to:

- Basic WebSocket demo: http://localhost:3000/ws-demo
- Full Shipping WebSocket demo: http://localhost:3000/shipping-ws-demo

### 4. Run the WebSocket Demo Script

In a third terminal, navigate to the ShipanionWS directory and run:

```bash
# Make sure your virtual environment is activated
python ws_ui_demo.py
```

For improved debugging, you can use the fixed version:

```bash
python fixed_ws_ui_demo.py
```

## Demo Workflow

The demo script will send a series of WebSocket messages in sequence:

1. **ZIP code collection**: Origin and destination ZIP codes
2. **Weight confirmation**: Package weight
3. **Shipping quotes**: Available carriers and rates
4. **Notification**: A success notification
5. **Label creation**: Shipping label with tracking number

## Troubleshooting

### WebSocket Connection Issues

- Ensure the WebSocket server is running on port 8001
- Check browser console for connection errors
- Verify that the `NEXT_PUBLIC_WEBSOCKET_URL` is set correctly (defaults to `ws://localhost:8001/ws`)

### High CPU Usage

If you experience high CPU usage:

1. Stop any running instances of the demo
2. Restart your browser
3. Use the optimized version of the code which includes:
   - Throttled message processing
   - Limited WebSocket message history
   - Proper cleanup of event listeners

### Python Module Not Found

If you get "No module named 'uvicorn'" or other module errors:

```bash
pip install uvicorn fastapi websockets python-jose[cryptography] python-multipart
```

## Architecture

The demo consists of these main components:

1. **WebSocket Backend (`backend/main.py`)**: FastAPI server with WebSocket endpoint
2. **Demo Script (`ws_ui_demo.py`)**: Sends messages to simulate a shipping workflow
3. **WebSocket Hook (`hooks/use-web-socket.ts`)**: React hook for WebSocket communication
4. **Shipping Context (`contexts/shipping-context.tsx`)**: React context for shipping state
5. **Demo UI Components**: React components that display shipping workflow

## Performance Optimizations

To prevent high CPU usage and browser crashes, the following optimizations have been implemented:

1. **Throttled Message Processing**: Limits WebSocket message processing rate
2. **Debounced State Updates**: Batches rapid state changes
3. **Memoized Components**: Prevents unnecessary re-renders
4. **Controlled Message History**: Limits stored message history
5. **Proper Resource Cleanup**: Ensures WebSocket connections and timers are properly cleaned up

## License

[Your License Here]

## Contributors

[Your Contributors Here]
