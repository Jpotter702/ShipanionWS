"""
Test Error Handling for REST Calls

This module tests the error handling for failed REST calls to the /get-rates endpoint.
It verifies that non-200 responses and timeouts are properly handled and appropriate
error messages are returned to the client.
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

# Test data for timeout simulation
TIMEOUT_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "test-timeout",
        "parameters": {
            "from_zip": "99999",  # Special ZIP code that triggers a timeout
            "to_zip": "10001",
            "weight": 5.0
        }
    },
    "broadcast": False
}

# Test data for non-200 response simulation
INVALID_ZIP_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "test-invalid-zip",
        "parameters": {
            "from_zip": "00000",  # Invalid ZIP code that should trigger a 400 response
            "to_zip": "10001",
            "weight": 5.0
        }
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
async def test_timeout_handling():
    """Test handling of timeouts from the /get-rates endpoint."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send tool call that should trigger a timeout
        await websocket.send(json.dumps(TIMEOUT_TOOL_CALL))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify error response
        assert response_data["type"] == "client_tool_result"
        assert response_data["tool_call_id"] == "test-timeout"
        assert "result" in response_data
        assert "is_error" in response_data
        assert response_data["is_error"] is True
        assert "error" in response_data["result"]
        assert "timeout" in response_data["result"]["error"].lower()

@pytest.mark.asyncio
async def test_non_200_response_handling():
    """Test handling of non-200 responses from the /get-rates endpoint."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send tool call that should trigger a non-200 response
        await websocket.send(json.dumps(INVALID_ZIP_TOOL_CALL))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify error response
        assert response_data["type"] == "client_tool_result"
        assert response_data["tool_call_id"] == "test-invalid-zip"
        assert "result" in response_data
        assert "is_error" in response_data
        assert response_data["is_error"] is True
        assert "error" in response_data["result"]
        # The exact error message will depend on the API implementation
        # but it should contain some indication of an HTTP error
        assert "API returned error" in response_data["result"]["error"]

if __name__ == "__main__":
    # For manual testing
    async def main():
        token = await get_auth_token()
        logger.info(f"Using token: {token}")
        
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Test timeout handling
            logger.info(f"Sending timeout tool call: {TIMEOUT_TOOL_CALL}")
            await websocket.send(json.dumps(TIMEOUT_TOOL_CALL))
            
            # Wait for response
            logger.info("Waiting for timeout response...")
            response = await websocket.recv()
            logger.info(f"Received timeout response: {response}")
            
            # Test non-200 response handling
            logger.info(f"Sending invalid ZIP tool call: {INVALID_ZIP_TOOL_CALL}")
            await websocket.send(json.dumps(INVALID_ZIP_TOOL_CALL))
            
            # Wait for response
            logger.info("Waiting for invalid ZIP response...")
            response = await websocket.recv()
            logger.info(f"Received invalid ZIP response: {response}")
    
    asyncio.run(main())
