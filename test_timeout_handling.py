#!/usr/bin/env python3
"""
Test script for timeout handling in the WebSocket server.

This script tests the timeout handling for the /get-rates endpoint.
"""
import asyncio
import json
import logging
import sys
import websockets
import httpx
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

async def test_timeout_handling():
    """Test timeout handling for the /get-rates endpoint."""
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
            
            # Test: Send a rate request that should trigger a timeout
            # Note: This test assumes that the server has been configured to simulate a timeout
            # or that the actual API endpoint is slow enough to trigger the timeout
            logger.info("Sending rate request that should trigger a timeout")
            
            # Create a request with a special ZIP code that will trigger a simulated timeout
            # (This is just an example - the actual implementation would depend on how you've
            # set up your test environment)
            timeout_request = {
                "type": "client_tool_call",
                "client_tool_call": {
                    "tool_name": "get_shipping_quotes",
                    "tool_call_id": "test-timeout",
                    "parameters": {
                        "from_zip": "99999",  # Special ZIP code to trigger timeout simulation
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
                "requestId": "test-timeout-request"
            }
            
            # Send the request
            await websocket.send(json.dumps(timeout_request))
            
            # Wait for the response (should take at least 10 seconds if timeout is working)
            logger.info("Waiting for response (should take about 10 seconds)...")
            start_time = time.time()
            
            response = await websocket.recv()
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            response_data = json.loads(response)
            logger.info(f"Received response after {elapsed_time:.2f} seconds: {json.dumps(response_data, indent=2)}")
            
            # Verify the response contains the expected timeout error
            if (response_data.get("type") == "client_tool_result" and 
                response_data.get("is_error") == True and
                response_data.get("result", {}).get("error") == "timeout calling rates endpoint"):
                logger.info("✅ Test passed: Received correct timeout error message")
            else:
                logger.error("❌ Test failed: Did not receive the expected timeout error message")
                logger.error(f"Expected: 'timeout calling rates endpoint'")
                logger.error(f"Received: {response_data.get('result', {}).get('error')}")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_timeout_handling())
