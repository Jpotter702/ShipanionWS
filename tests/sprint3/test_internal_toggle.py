"""
Test REST/Internal Call Toggle

This module tests the USE_INTERNAL toggle that switches between making HTTP requests
and calling internal functions directly.
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
RATE_REQUEST = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "test-toggle",
        "parameters": {
            "from_zip": "90210",
            "to_zip": "10001",
            "weight": 5.0,
            "dimensions": {
                "length": 12.0,
                "width": 8.0,
                "height": 6.0
            }
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
async def test_toggle_functionality():
    """
    Test that the USE_INTERNAL toggle works correctly.
    
    This test should be run twice:
    1. With USE_INTERNAL=False (default) to test REST API calls
    2. With USE_INTERNAL=True to test internal function calls
    
    The test verifies that in both cases, the response contains valid shipping quotes.
    """
    token = await get_auth_token()
    
    async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
        # Send rate request
        await websocket.send(json.dumps(RATE_REQUEST))
        
        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        
        # Verify response structure
        assert response_data["type"] == "client_tool_result"
        assert response_data["tool_call_id"] == "test-toggle"
        assert "result" in response_data
        assert not response_data.get("is_error", False)
        
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

if __name__ == "__main__":
    # For manual testing
    async def main():
        token = await get_auth_token()
        logger.info(f"Using token: {token}")
        
        # Get the current USE_INTERNAL setting
        use_internal = os.environ.get("USE_INTERNAL", "False").lower() == "true"
        logger.info(f"Current USE_INTERNAL setting: {use_internal}")
        
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send rate request
            logger.info(f"Sending rate request: {RATE_REQUEST}")
            await websocket.send(json.dumps(RATE_REQUEST))
            
            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
    
    asyncio.run(main())
