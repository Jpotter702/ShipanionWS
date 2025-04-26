# ShipanionWS (WebSocket Server)

Real-time communication layer for the Shipanion platform.

## Overview

ShipanionWS serves as the communication bridge between the frontend (ShipanionUI) and middleware (ShipanionMW), enabling real-time updates and voice interactions. It provides:

- WebSocket server for real-time updates
- ElevenLabs voice integration
- Session management
- Event-based communication between UI and middleware
- Authentication via JWT

## Features

### WebSocket Communication

The WebSocket server handles real-time communication between the frontend and middleware, allowing for:

- Real-time shipping rate updates
- Label creation notifications
- Session tracking across devices
- Voice agent integration

### ElevenLabs Integration

The server integrates with ElevenLabs Conversational AI, providing:

- Client tool calls for shipping quotes and label creation
- Contextual updates for UI based on tool call results
- Parallel WebSocket connections for tool results and UI updates

### REST/Internal Call Toggle

The server includes a toggle (`USE_INTERNAL`) that controls how shipping-related functionality is accessed:

- When `USE_INTERNAL = False` (default): The server makes HTTP requests to the ShipVox API endpoints.
- When `USE_INTERNAL = True`: The server calls internal functions directly from the backend service module.

This toggle facilitates the transition after the backend merge, allowing for easy switching between the two modes of operation.

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/Shipanion.git
cd Shipanion/ShipanionWS
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory with the following settings:

```
# API settings
SHIPVOX_API_URL=http://localhost:8000/api

# Authentication settings
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WebSocket settings
ALLOWED_ORIGINS=http://localhost:3000

# Debug settings
DEBUG=True

# Toggle for using internal function calls vs REST API
USE_INTERNAL=False
```

### Running the Server

Start the WebSocket server:

```bash
uvicorn backend.main:app --reload --port 8000
```

The server will be available at:
- HTTP: http://localhost:8000
- WebSocket: ws://localhost:8000/ws

## Documentation

For more detailed information, see the following documentation:

- [TOGGLE_GUIDE.md](../docs/ShipanionWS/TOGGLE_GUIDE.md): Guide for using the REST/internal call toggle
- [ELEVENLABS_INTEGRATION_GUIDE.md](../docs/ShipanionWS/ELEVENLABS_INTEGRATION_GUIDE.md): Guide for integrating with ElevenLabs
- [ERROR_HANDLING_GUIDE.md](../docs/ShipanionWS/ERROR_HANDLING_GUIDE.md): Guide for error handling
- [TIMEOUT_HANDLING_GUIDE.md](../docs/ShipanionWS/TIMEOUT_HANDLING_GUIDE.md): Guide for timeout handling
- [TEST_TOKEN_GUIDE.md](../docs/ShipanionWS/TEST_TOKEN_GUIDE.md): Guide for using the test token

## Testing

Run the tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/sprint3/test_internal_toggle.py

# Run tests with USE_INTERNAL=True
USE_INTERNAL=true pytest tests/sprint3/test_internal_toggle.py
```
