"""
Test WebSocket Rate Request Integration

This module tests the integration between the WebSocket server and the ShipVox rate API.
"""
import asyncio
import json
import pytest
import websockets
import httpx
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
WS_SERVER_URL = os.environ.get("WS_SERVER_URL", "ws://localhost:8000/ws")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8000")

# Test data
VALID_RATE_REQUEST = {
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
        "pickup_requested": False
    },
    "broadcast": False
}

INVALID_RATE_REQUEST = {
    "type": "get_rates",
    "payload": {
        # Missing required fields
        "origin_zip": "90210"
    },
    "broadcast": False
}

async def get_auth_token() -> str:
    """Get an authentication token for testing."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_SERVER_URL}/test-token")
        response.raise_for_status()
        return response.json()["test_token"]

@pytest.mark.asyncio
async def test_valid_rate_request():
    """Test sending a valid rate request through WebSocket."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send rate request
        await websocket.send(json.dumps(VALID_RATE_REQUEST))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify response structure
        assert response_data["type"] == "quote_ready"
        assert "payload" in response_data
        assert "timestamp" in response_data
        assert "requestId" in response_data
        
        # Verify rate data
        payload = response_data["payload"]
        assert "cheapest_option" in payload
        assert "fastest_option" in payload
        assert "all_options" in payload

@pytest.mark.asyncio
async def test_invalid_rate_request():
    """Test sending an invalid rate request through WebSocket."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send invalid rate request
        await websocket.send(json.dumps(INVALID_RATE_REQUEST))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify error response
        assert response_data["type"] == "error"
        assert "payload" in response_data
        assert "message" in response_data["payload"]
        assert "Missing required field" in response_data["payload"]["message"]

@pytest.mark.asyncio
async def test_unauthenticated_rate_request():
    """Test sending a rate request without authentication."""
    try:
        # Connect without token
        async with websockets.connect(WS_SERVER_URL) as websocket:
            # This should fail before we can send anything
            await websocket.send(json.dumps(VALID_RATE_REQUEST))
            assert False, "Connection should have been rejected"
    except websockets.exceptions.ConnectionClosedError as e:
        # Verify connection was closed with policy violation code
        assert e.code == 1008  # Policy violation

if __name__ == "__main__":
    # For manual testing
    async def main():
        token = await get_auth_token()
        logger.info(f"Using token: {token}")
        
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send rate request
            logger.info(f"Sending rate request: {VALID_RATE_REQUEST}")
            await websocket.send(json.dumps(VALID_RATE_REQUEST))
            
            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
    
    asyncio.run(main())
