"""
Test Create Label Tool Integration

This module tests the integration between the WebSocket server and ElevenLabs client tool
for the create_label functionality.
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
VALID_TOOL_CALL = {
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
}

INVALID_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "create_label",
        "tool_call_id": "test-456",
        "parameters": {
            # Missing required fields
            "carrier": "fedex"
        }
    }
}

async def get_auth_token() -> str:
    """Get an authentication token for testing."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_SERVER_URL}/test-token")
        response.raise_for_status()
        return response.json()["test_token"]

@pytest.mark.asyncio
async def test_valid_tool_call():
    """Test sending a valid create_label tool call."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send tool call
        await websocket.send(json.dumps(VALID_TOOL_CALL))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify response structure
        assert response_data["type"] == "client_tool_result"
        assert response_data["tool_call_id"] == "test-123"
        assert "result" in response_data
        assert "is_error" in response_data
        assert not response_data["is_error"]
        
        # Verify result data
        result = response_data["result"]
        assert "tracking_number" in result
        assert "label_url" in result
        assert "qr_code" in result
        assert "carrier" in result
        
        # Wait for contextual update
        contextual_update = await websocket.recv()
        update_data = json.loads(contextual_update)
        
        # Verify contextual update
        assert update_data["type"] == "contextual_update"
        assert update_data["text"] == "label_created"
        assert "data" in update_data
        assert "tracking_number" in update_data["data"]

@pytest.mark.asyncio
async def test_invalid_tool_call():
    """Test sending an invalid create_label tool call."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send invalid tool call
        await websocket.send(json.dumps(INVALID_TOOL_CALL))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify error response
        assert response_data["type"] == "client_tool_result"
        assert response_data["tool_call_id"] == "test-456"
        assert "result" in response_data
        assert "is_error" in response_data
        assert response_data["is_error"]
        assert "error" in response_data["result"]
        assert "Missing required parameter" in response_data["result"]["error"]

if __name__ == "__main__":
    # For manual testing
    async def main():
        token = await get_auth_token()
        logger.info(f"Using token: {token}")
        
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send tool call
            logger.info(f"Sending tool call: {VALID_TOOL_CALL}")
            await websocket.send(json.dumps(VALID_TOOL_CALL))
            
            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
            
            # Wait for contextual update
            logger.info("Waiting for contextual update...")
            update = await websocket.recv()
            logger.info(f"Received update: {update}")
    
    asyncio.run(main())
