import asyncio
import websockets
import json
import logging
import time
import sys
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Local server URL
SERVER_URL = "ws://localhost:8000/ws"

async def get_test_token():
    """Get a test token from the local server"""
    import httpx
    
    try:
        logger.info("Getting test token from http://localhost:8000/test-token")
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/test-token")
            resp.raise_for_status()
            token_data = resp.json()
            logger.info("Successfully retrieved test token")
            return token_data["test_token"]
    except Exception as e:
        logger.error(f"Failed to get test token: {str(e)}")
        return None

async def authenticate():
    """Get authentication token from local server"""
    import httpx
    
    try:
        logger.info("Authenticating with username/password")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8000/token",
                data={"username": "user", "password": "password"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            resp.raise_for_status()
            token_data = resp.json()
            logger.info(f"Successfully authenticated, token expires in {token_data.get('expires_in')} seconds")
            return token_data["access_token"]
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        return None

async def send_message(ws, message):
    """Send a message over the WebSocket"""
    message_str = json.dumps(message)
    logger.info(f"Sending message: {message_str}")
    await ws.send(message_str)
    
    # Wait for response
    response = await ws.recv()
    logger.info(f"Received response: {response}")
    return json.loads(response)

async def test_ping(ws):
    """Test basic ping message"""
    return await send_message(ws, {"type": "ping"})

async def test_zip_collected(ws, session_id=None):
    """Test ZIP collected contextual update"""
    message = {
        "type": "contextual_update",
        "text": "zip_collected",
        "data": {
            "from": "90210",
            "to": "10001"
        },
        "timestamp": int(time.time() * 1000),
        "requestId": f"req-{int(time.time() * 1000)}"
    }
    
    if session_id:
        message["session_id"] = session_id
        
    return await send_message(ws, message)

async def test_weight_confirmed(ws, session_id=None):
    """Test weight confirmed contextual update"""
    message = {
        "type": "contextual_update",
        "text": "weight_confirmed",
        "data": {
            "weight_lbs": 5.2
        },
        "timestamp": int(time.time() * 1000),
        "requestId": f"req-{int(time.time() * 1000)}"
    }
    
    if session_id:
        message["session_id"] = session_id
        
    return await send_message(ws, message)

async def test_quote_ready(ws, session_id=None):
    """Test quote ready contextual update"""
    message = {
        "type": "contextual_update",
        "text": "quote_ready",
        "data": {
            "all_options": [
                {
                    "carrier": "FedEx",
                    "service_name": "Ground",
                    "cost": 12.99,
                    "transit_days": 3
                },
                {
                    "carrier": "UPS",
                    "service_name": "Ground",
                    "cost": 14.99,
                    "transit_days": 3
                },
                {
                    "carrier": "USPS",
                    "service_name": "Priority Mail",
                    "cost": 9.99,
                    "transit_days": 2
                }
            ]
        },
        "timestamp": int(time.time() * 1000),
        "requestId": f"req-{int(time.time() * 1000)}"
    }
    
    if session_id:
        message["session_id"] = session_id
        
    return await send_message(ws, message)

async def test_label_created(ws, session_id=None):
    """Test label created contextual update"""
    message = {
        "type": "contextual_update",
        "text": "label_created",
        "data": {
            "tracking_number": "1Z999AA1234567890",
            "label_url": "/placeholder.svg?height=400&width=300",
            "qr_code": "/placeholder.svg?height=200&width=200"
        },
        "timestamp": int(time.time() * 1000),
        "requestId": f"req-{int(time.time() * 1000)}"
    }
    
    if session_id:
        message["session_id"] = session_id
        
    return await send_message(ws, message)

async def test_get_shipping_quotes_tool(ws, session_id=None):
    """Test client tool call for getting shipping quotes"""
    message = {
        "type": "client_tool_call",
        "payload": {
            "client_tool_call": {
                "tool_name": "get_shipping_quotes",
                "tool_call_id": f"quotes-{int(time.time() * 1000)}",
                "parameters": {
                    "origin_zip": "90210",
                    "destination_zip": "10001",
                    "weight": 5.2,
                    "package_type": "custom_box"
                }
            }
        },
        "timestamp": int(time.time() * 1000),
        "requestId": f"req-{int(time.time() * 1000)}"
    }
    
    if session_id:
        message["session_id"] = session_id
        
    return await send_message(ws, message)

async def test_create_label_tool(ws, session_id=None):
    """Test client tool call for creating a shipping label"""
    message = {
        "type": "client_tool_call",
        "payload": {
            "client_tool_call": {
                "tool_name": "create_label",
                "tool_call_id": f"label-{int(time.time() * 1000)}",
                "parameters": {
                    "carrier": "USPS",
                    "service": "Priority Mail",
                    "package_type": "custom_box",
                    "weight": 5.2,
                    "origin_zip": "90210",
                    "destination_zip": "10001"
                }
            }
        },
        "timestamp": int(time.time() * 1000),
        "requestId": f"req-{int(time.time() * 1000)}"
    }
    
    if session_id:
        message["session_id"] = session_id
        
    return await send_message(ws, message)

async def ws_client():
    """Main WebSocket client function"""
    # Try to get token from server
    token = await authenticate()
    
    if not token:
        logger.info("Trying test token as fallback")
        token = await get_test_token()
        
    if not token:
        logger.error("Could not obtain authentication token, exiting")
        return False
    
    # Connect to WebSocket with token
    ws_url = f"{SERVER_URL}?token={token}"
    logger.info(f"Connecting to WebSocket at {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as ws:
            logger.info("Successfully connected to WebSocket")
            session_id = None
            
            # Test regular ping
            logger.info("\n--- Testing basic ping ---")
            ping_response = await test_ping(ws)
            
            # Extract session ID from the response if available
            if "session_id" in ping_response:
                session_id = ping_response["session_id"]
                logger.info(f"Session ID: {session_id}")
            
            # Test ZIP collected update
            logger.info("\n--- Testing ZIP collected update ---")
            zip_response = await test_zip_collected(ws, session_id)
            
            # Test weight confirmed update
            logger.info("\n--- Testing weight confirmed update ---")
            weight_response = await test_weight_confirmed(ws, session_id)
            
            # Test quote ready update
            logger.info("\n--- Testing quote ready update ---")
            quote_response = await test_quote_ready(ws, session_id)
            
            # Test label created update
            logger.info("\n--- Testing label created update ---")
            label_response = await test_label_created(ws, session_id)
            
            # Test get shipping quotes tool
            logger.info("\n--- Testing get shipping quotes tool ---")
            quotes_tool_response = await test_get_shipping_quotes_tool(ws, session_id)
            
            # Test create label tool
            logger.info("\n--- Testing create label tool ---")
            label_tool_response = await test_create_label_tool(ws, session_id)
            
            # Give a summary of results
            logger.info("\n=== Test Results Summary ===")
            results = {
                "ping": "SUCCESS" if ping_response.get("type") == "pong" else f"FAILED: {ping_response.get('type')}",
                "zip_collected": "SUCCESS" if not zip_response.get("type") == "error" else f"FAILED: {zip_response.get('payload', {}).get('message')}",
                "weight_confirmed": "SUCCESS" if not weight_response.get("type") == "error" else f"FAILED: {weight_response.get('payload', {}).get('message')}",
                "quote_ready": "SUCCESS" if not quote_response.get("type") == "error" else f"FAILED: {quote_response.get('payload', {}).get('message')}",
                "label_created": "SUCCESS" if not label_response.get("type") == "error" else f"FAILED: {label_response.get('payload', {}).get('message')}",
                "get_shipping_quotes_tool": "SUCCESS" if not quotes_tool_response.get("type") == "error" else f"FAILED: {quotes_tool_response.get('payload', {}).get('message')}",
                "create_label_tool": "SUCCESS" if not label_tool_response.get("type") == "error" else f"FAILED: {label_tool_response.get('payload', {}).get('message')}"
            }
            
            for test, result in results.items():
                logger.info(f"{test}: {result}")
            
            # Check for overall success
            success = all(result.startswith("SUCCESS") for result in results.values())
            
            # If ping succeeded but other methods failed, suggest server handler updates
            if results["ping"].startswith("SUCCESS") and not success:
                logger.warning("\nSome message types are not supported by the server.")
                logger.warning("You may need to update the backend/handlers.py file to handle these message types.")
            
            return success
                
    except Exception as e:
        logger.error(f"WebSocket connection failed: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(ws_client())
        if success:
            logger.info("✅ All UI control tests completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Some UI control tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        sys.exit(1) 