import asyncio
import websockets
import httpx
import json
import logging
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production server URLs (deployed on Render)
API_URL = "https://shipanionws.onrender.com"
WS_URL = "wss://shipanionws.onrender.com/ws"

async def get_test_token():
    """Get a static test token from the server"""
    try:
        logger.info(f"Getting test token from {API_URL}/test-token")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{API_URL}/test-token")
            resp.raise_for_status()
            token_data = resp.json()
            logger.info("Successfully retrieved test token")
            return token_data["test_token"]
    except Exception as e:
        logger.error(f"Failed to get test token: {str(e)}")
        raise

async def test_message_type(message_type, payload=None):
    """Test a specific message type with the production server"""
    try:
        # Get test token
        token = await get_test_token()
        
        # Connect to WebSocket
        ws_url = f"{WS_URL}?token={token}"
        logger.info(f"Connecting to WebSocket at {ws_url}")
        
        async with websockets.connect(ws_url, open_timeout=30.0) as ws:
            logger.info(f"Successfully connected, testing message type: {message_type}")
            
            # Create the message
            message = {
                "type": message_type
            }
            
            if payload:
                message["payload"] = payload
                
            # Send the message
            await ws.send(json.dumps(message))
            logger.info(f"Sent {message_type} message, waiting for response...")
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=30.0)
            logger.info(f"Received response: {response}")
            
            # Parse the response
            response_data = json.loads(response)
            return response_data
            
    except Exception as e:
        logger.error(f"Error testing message type {message_type}: {type(e).__name__}: {str(e)}")
        return None

async def test_get_rates():
    """Test the get_rates message type"""
    rates_payload = {
        "origin": {
            "name": "Test",
            "street": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210"
        },
        "destination": {
            "name": "Test",
            "street": "456 Test St",
            "city": "Test City",
            "state": "NY",
            "zip_code": "10001"
        },
        "package": {
            "weight": 5.0
        }
    }
    
    return await test_message_type("get_rates", rates_payload)

async def test_client_tool_call():
    """Test a client_tool_call message type"""
    tool_call_payload = {
        "client_tool_call": {
            "tool_name": "hello",
            "tool_call_id": "test-001",
            "parameters": {
                "message": "Hello, production server!"
            }
        }
    }
    
    return await test_message_type("client_tool_call", tool_call_payload)

async def run_tests():
    """Run tests with different message types"""
    logger.info("======== TESTING PRODUCTION SERVER MESSAGE TYPES ========")
    
    # Test simple message types
    test_messages = [
        "echo",
        "hello",
        "test"
    ]
    
    results = {}
    
    # Test simple messages
    for msg_type in test_messages:
        logger.info(f"\n--- Testing message type: {msg_type} ---")
        result = await test_message_type(msg_type)
        results[msg_type] = "SUCCESS" if result else "FAILED"
    
    # Test get_rates
    logger.info("\n--- Testing message type: get_rates ---")
    rates_result = await test_get_rates()
    results["get_rates"] = "SUCCESS" if rates_result else "FAILED"
    
    # Test client_tool_call
    logger.info("\n--- Testing message type: client_tool_call ---")
    tool_result = await test_client_tool_call()
    results["client_tool_call"] = "SUCCESS" if tool_result else "FAILED"
    
    # Print summary
    logger.info("\n======== TEST RESULTS SUMMARY ========")
    for msg_type, result in results.items():
        logger.info(f"Message type '{msg_type}': {result}")
    
if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {type(e).__name__}: {str(e)}")
        sys.exit(1) 