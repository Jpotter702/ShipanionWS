"""
Test ElevenLabs Integration

This module tests the integration between the WebSocket server and ElevenLabs client tools.
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
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "test-123",
        "parameters": {
            "from_zip": "90210",
            "to_zip": "10001",
            "weight": 5.0
        }
    },
    "broadcast": False
}

INVALID_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "test-456",
        "parameters": {
            # Missing required fields
            "from_zip": "90210"
        }
    },
    "broadcast": False
}

UNSUPPORTED_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "unsupported_tool",
        "tool_call_id": "test-789",
        "parameters": {}
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
async def test_valid_tool_call():
    """Test sending a valid client_tool_call through WebSocket."""
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
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verify first option
        first_option = result[0]
        assert "carrier" in first_option
        assert "service" in first_option
        assert "price" in first_option
        assert "eta" in first_option

@pytest.mark.asyncio
async def test_invalid_tool_call():
    """Test sending an invalid client_tool_call through WebSocket."""
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

@pytest.mark.asyncio
async def test_unsupported_tool_call():
    """Test sending an unsupported client_tool_call through WebSocket."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send unsupported tool call
        await websocket.send(json.dumps(UNSUPPORTED_TOOL_CALL))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify error response
        assert response_data["type"] == "client_tool_result"
        assert response_data["tool_call_id"] == "test-789"
        assert "result" in response_data
        assert "is_error" in response_data
        assert response_data["is_error"]
        assert "error" in response_data["result"]
        assert "Unsupported tool" in response_data["result"]["error"]

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
    
    asyncio.run(main())
