"""
Test Bob's Response to Shipping Quotes

This script tests a full round-trip where Bob receives a `client_tool_result` and speaks it aloud.
If Bob fails to respond or misses the quote, it inspects the JSON payload for formatting issues.
"""
import asyncio
import json
import logging
import os
import sys
import time
import websockets
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Test configuration
WS_SERVER_URL = os.environ.get("WS_SERVER_URL", "ws://localhost:8000/ws")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8000")

# Test data
VALID_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": f"test-quotes-{int(time.time())}",
        "parameters": {
            "from_zip": "90210",
            "to_zip": "10001",
            "weight": 5.0,
            "dimensions": "12x10x8",
            "pickup_requested": False
        }
    },
    "broadcast": True  # Ensure Bob receives this message
}

async def get_auth_token() -> str:
    """Get an authentication token from the API server."""
    try:
        response = requests.post(
            f"{API_SERVER_URL}/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        raise

async def test_bob_quote_response():
    """
    Test a full round-trip where Bob receives a client_tool_result and speaks it aloud.
    
    This test:
    1. Connects to the WebSocket server
    2. Sends a client_tool_call for shipping quotes
    3. Waits for the client_tool_result response
    4. Verifies the response format
    5. Logs the response for manual verification that Bob speaks it aloud
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        logger.info(f"Obtained auth token: {token[:10]}...")
        
        # Connect to WebSocket server
        logger.info(f"Connecting to WebSocket server at {WS_SERVER_URL}")
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send the client_tool_call
            logger.info(f"Sending client_tool_call: {json.dumps(VALID_TOOL_CALL)}")
            await websocket.send(json.dumps(VALID_TOOL_CALL))
            
            # Wait for response with timeout
            logger.info("Waiting for client_tool_result response...")
            response_received = False
            start_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            while time.time() - start_time < timeout and not response_received:
                try:
                    # Set a shorter timeout for each receive attempt
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    response_data = json.loads(response)
                    
                    # Log all messages for debugging
                    logger.info(f"Received message: {json.dumps(response_data)}")
                    
                    # Check if this is the client_tool_result we're waiting for
                    if (response_data.get("type") == "client_tool_result" and 
                        response_data.get("tool_call_id") == VALID_TOOL_CALL["client_tool_call"]["tool_call_id"]):
                        
                        logger.info("Received client_tool_result response!")
                        
                        # Verify response structure
                        assert "result" in response_data, "Missing 'result' field in response"
                        assert "is_error" in response_data, "Missing 'is_error' field in response"
                        
                        if response_data.get("is_error", False):
                            logger.error(f"Error in response: {response_data.get('result', {}).get('error')}")
                            assert False, f"Error in response: {response_data.get('result', {}).get('error')}"
                        
                        # Verify result data
                        result = response_data["result"]
                        assert isinstance(result, list), f"Expected result to be a list, got {type(result)}"
                        assert len(result) > 0, "Expected at least one shipping option"
                        
                        # Verify first option
                        first_option = result[0]
                        assert "carrier" in first_option, "Missing 'carrier' field in first option"
                        assert "service" in first_option, "Missing 'service' field in first option"
                        assert "price" in first_option, "Missing 'price' field in first option"
                        assert "eta" in first_option, "Missing 'eta' field in first option"
                        
                        # Print the result for manual verification that Bob speaks it aloud
                        logger.info("=== SHIPPING QUOTES RESULT ===")
                        for i, option in enumerate(result):
                            logger.info(f"Option {i+1}: {option['carrier']} {option['service']} - ${option['price']} ({option['eta']})")
                        logger.info("==============================")
                        
                        response_received = True
                        logger.info("Test passed! Verify that Bob speaks the quotes aloud.")
                        
                except asyncio.TimeoutError:
                    # This is expected, we'll try again until the overall timeout
                    continue
                except Exception as e:
                    logger.error(f"Error processing response: {str(e)}")
                    raise
            
            if not response_received:
                logger.error(f"Timed out after {timeout} seconds waiting for client_tool_result")
                assert False, f"Timed out after {timeout} seconds waiting for client_tool_result"
                
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def test_invalid_format():
    """
    Test with an invalid format to see how Bob handles it.
    
    This test sends a client_tool_call with missing required parameters
    to see how the system handles it and what error message is returned.
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        
        # Create an invalid tool call (missing required parameters)
        invalid_tool_call = {
            "type": "client_tool_call",
            "client_tool_call": {
                "tool_name": "get_shipping_quotes",
                "tool_call_id": f"test-invalid-{int(time.time())}",
                "parameters": {
                    # Missing required parameters
                    "from_zip": "90210"
                    # Missing to_zip and weight
                }
            },
            "broadcast": True
        }
        
        # Connect to WebSocket server
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send the invalid client_tool_call
            logger.info(f"Sending invalid client_tool_call: {json.dumps(invalid_tool_call)}")
            await websocket.send(json.dumps(invalid_tool_call))
            
            # Wait for response with timeout
            logger.info("Waiting for error response...")
            start_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    response_data = json.loads(response)
                    
                    # Log all messages for debugging
                    logger.info(f"Received message: {json.dumps(response_data)}")
                    
                    # Check if this is the client_tool_result we're waiting for
                    if (response_data.get("type") == "client_tool_result" and 
                        response_data.get("tool_call_id") == invalid_tool_call["client_tool_call"]["tool_call_id"]):
                        
                        logger.info("Received error response!")
                        
                        # Verify it's an error
                        assert response_data.get("is_error", False), "Expected is_error to be True"
                        assert "result" in response_data, "Missing 'result' field in response"
                        assert "error" in response_data["result"], "Missing 'error' field in result"
                        
                        logger.info(f"Error message: {response_data['result']['error']}")
                        return
                        
                except asyncio.TimeoutError:
                    # This is expected, we'll try again until the overall timeout
                    continue
                except Exception as e:
                    logger.error(f"Error processing response: {str(e)}")
                    raise
            
            logger.error(f"Timed out after {timeout} seconds waiting for error response")
            assert False, f"Timed out after {timeout} seconds waiting for error response"
                
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def main():
    """Run the tests."""
    logger.info("Starting Bob quote response test")
    
    try:
        # Test valid format
        await test_bob_quote_response()
        
        # Test invalid format
        await test_invalid_format()
        
        logger.info("All tests completed successfully!")
    except Exception as e:
        logger.error(f"Tests failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
