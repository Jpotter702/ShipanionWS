"""
Test Timeout Handling for REST Calls

This module tests the timeout handling for REST calls to the /get-rates endpoint.
It verifies that if the call takes too long, a client_tool_result with is_error: true
and message "timeout calling rates endpoint" is returned.
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

async def get_auth_token() -> str:
    """Get an authentication token for testing."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_SERVER_URL}/test-token")
        response.raise_for_status()
        return response.json()["test_token"]

@pytest.mark.asyncio
async def test_timeout_handling():
    """Test that timeouts are properly handled and return the correct error message."""
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
        assert response_data["result"]["error"] == "Failed to get shipping rates: timeout calling rates endpoint"

@pytest.mark.asyncio
async def test_direct_rate_request_timeout():
    """Test that direct rate requests also handle timeouts properly."""
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send a direct rate request that should trigger a timeout
        direct_rate_request = {
            "type": "get_rates",
            "payload": {
                "origin_zip": "99999",  # Special ZIP code that triggers a timeout
                "destination_zip": "10001",
                "weight": 5.0
            },
            "requestId": "test-direct-timeout",
            "broadcast": False
        }
        
        await websocket.send(json.dumps(direct_rate_request))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify error response
        assert response_data["type"] == "error"
        assert response_data["requestId"] == "test-direct-timeout"
        assert "payload" in response_data
        assert "is_error" in response_data["payload"]
        assert response_data["payload"]["is_error"] is True
        assert "message" in response_data["payload"]
        assert "timeout calling rates endpoint" in response_data["payload"]["message"]

if __name__ == "__main__":
    # For manual testing
    async def main():
        token = await get_auth_token()
        logger.info(f"Using token: {token}")
        
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Test timeout handling for client tool call
            logger.info(f"Sending timeout tool call: {TIMEOUT_TOOL_CALL}")
            await websocket.send(json.dumps(TIMEOUT_TOOL_CALL))
            
            # Wait for response
            logger.info("Waiting for timeout response...")
            response = await websocket.recv()
            logger.info(f"Received timeout response: {response}")
            
            # Test timeout handling for direct rate request
            direct_rate_request = {
                "type": "get_rates",
                "payload": {
                    "origin_zip": "99999",  # Special ZIP code that triggers a timeout
                    "destination_zip": "10001",
                    "weight": 5.0
                },
                "requestId": "test-direct-timeout",
                "broadcast": False
            }
            
            logger.info(f"Sending direct rate request: {direct_rate_request}")
            await websocket.send(json.dumps(direct_rate_request))
            
            # Wait for response
            logger.info("Waiting for direct rate request response...")
            response = await websocket.recv()
            logger.info(f"Received direct rate request response: {response}")
    
    asyncio.run(main())
