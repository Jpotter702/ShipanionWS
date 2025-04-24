#!/usr/bin/env python3
"""
Test script for the USE_INTERNAL toggle.

This script tests both modes of operation:
1. USE_INTERNAL=False: Using the REST API
2. USE_INTERNAL=True: Using internal function calls
"""
import asyncio
import json
import logging
import sys
import websockets
import httpx
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# WebSocket server URL
WS_URL = "ws://localhost:8001/ws"
API_URL = "http://localhost:8001"

async def get_test_token():
    """Get a test token from the server."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/test-token")
        if response.status_code == 200:
            data = response.json()
            return data.get("test_token")
        else:
            logger.error(f"Failed to get test token: {response.status_code}")
            return None

async def test_rate_request(use_internal=False):
    """Test rate request with the specified toggle setting."""
    # Set the environment variable for the server
    if use_internal:
        logger.info("Testing with USE_INTERNAL=True (using internal function calls)")
    else:
        logger.info("Testing with USE_INTERNAL=False (using REST API)")
    
    # Get a test token
    token = await get_test_token()
    if not token:
        logger.error("Could not get test token. Exiting.")
        return
    
    # Connect to the WebSocket server
    ws_url = f"{WS_URL}?token={token}"
    logger.info(f"Connecting to WebSocket server at {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send a rate request
            logger.info("Sending rate request")
            rate_request = {
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
                "timestamp": int(time.time() * 1000),
                "requestId": "test-toggle-request"
            }
            
            # Send the request
            await websocket.send(json.dumps(rate_request))
            
            # Wait for the response
            logger.info("Waiting for response...")
            start_time = time.time()
            
            response = await websocket.recv()
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            response_data = json.loads(response)
            logger.info(f"Received response after {elapsed_time:.2f} seconds")
            
            # Verify the response is successful
            if (response_data.get("type") == "client_tool_result" and 
                not response_data.get("is_error") and
                isinstance(response_data.get("result"), list) and
                len(response_data.get("result")) > 0):
                logger.info("✅ Test passed: Received valid shipping quotes")
                logger.info(f"First quote: {response_data['result'][0]}")
            else:
                logger.error("❌ Test failed: Did not receive valid shipping quotes")
                logger.error(f"Response: {json.dumps(response_data, indent=2)}")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")

async def main():
    """Run tests for both toggle settings."""
    # Test with USE_INTERNAL=False
    await test_rate_request(use_internal=False)
    
    # Test with USE_INTERNAL=True
    await test_rate_request(use_internal=True)

if __name__ == "__main__":
    asyncio.run(main())
