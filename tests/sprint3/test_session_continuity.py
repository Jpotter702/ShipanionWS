"""
Test Session Continuity

This script tests session continuity features, including:
1. Adding session_id to all messages
2. Reconnecting and resuming a session
3. ElevenLabs session resumption
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
SHIPPING_DETAILS = {
    "type": "get_rates",
    "payload": {
        "origin_zip": "90210",
        "destination_zip": "10001",
        "weight": 5.0,
        "dimensions": "12x10x8",
        "pickup_requested": False
    }
}

TOOL_CALL = {
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
    }
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

async def test_session_id_in_messages():
    """
    Test that session_id is added to all messages.
    
    This test:
    1. Connects to the WebSocket server
    2. Sends a message
    3. Verifies that the response includes a session_id
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        logger.info(f"Obtained auth token: {token[:10]}...")
        
        # Connect to WebSocket server
        logger.info(f"Connecting to WebSocket server at {WS_SERVER_URL}")
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send a message
            logger.info(f"Sending message: {json.dumps(SHIPPING_DETAILS)}")
            await websocket.send(json.dumps(SHIPPING_DETAILS))
            
            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            response_data = json.loads(response)
            
            # Verify that the response includes a session_id
            assert "session_id" in response_data, "Response does not include session_id"
            session_id = response_data["session_id"]
            logger.info(f"Received session_id: {session_id}")
            
            # Return the session_id for use in other tests
            return session_id
                
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def test_reconnect_resume(session_id: str):
    """
    Test reconnecting and resuming a session.
    
    This test:
    1. Connects to the WebSocket server with a session_id
    2. Verifies that the session is resumed
    3. Sends a message and verifies that it includes the session_id
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        logger.info(f"Obtained auth token: {token[:10]}...")
        
        # Connect to WebSocket server with session_id
        logger.info(f"Connecting to WebSocket server with session_id: {session_id}")
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}&session_id={session_id}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Send a message
            logger.info(f"Sending message: {json.dumps(SHIPPING_DETAILS)}")
            await websocket.send(json.dumps(SHIPPING_DETAILS))
            
            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            response_data = json.loads(response)
            
            # Verify that the response includes the correct session_id
            assert "session_id" in response_data, "Response does not include session_id"
            assert response_data["session_id"] == session_id, f"Response has incorrect session_id: {response_data['session_id']} (expected {session_id})"
            logger.info(f"Session resumed successfully with session_id: {session_id}")
                
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def test_elevenlabs_session_resumption(session_id: str):
    """
    Test ElevenLabs session resumption.
    
    This test:
    1. Connects to the WebSocket server with a session_id
    2. Sends a client_tool_call with the session_id in metadata
    3. Verifies that the response includes the session_id
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        logger.info(f"Obtained auth token: {token[:10]}...")
        
        # Connect to WebSocket server with session_id
        logger.info(f"Connecting to WebSocket server with session_id: {session_id}")
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}&session_id={session_id}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Add session_id to tool call metadata
            tool_call = TOOL_CALL.copy()
            if "metadata" not in tool_call["client_tool_call"]:
                tool_call["client_tool_call"]["metadata"] = {}
            tool_call["client_tool_call"]["metadata"]["session_id"] = session_id
            
            # Send the tool call
            logger.info(f"Sending tool call with session_id in metadata: {json.dumps(tool_call)}")
            await websocket.send(json.dumps(tool_call))
            
            # Wait for response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            response_data = json.loads(response)
            
            # Verify that the response includes the correct session_id
            assert "session_id" in response_data, "Response does not include session_id"
            assert response_data["session_id"] == session_id, f"Response has incorrect session_id: {response_data['session_id']} (expected {session_id})"
            logger.info(f"ElevenLabs session resumption successful with session_id: {session_id}")
                
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def main():
    """Run all tests."""
    logger.info("Starting session continuity tests")
    
    try:
        # Test session_id in messages
        session_id = await test_session_id_in_messages()
        logger.info("Session ID in messages test passed!")
        
        # Test reconnect/resume
        await test_reconnect_resume(session_id)
        logger.info("Reconnect/resume test passed!")
        
        # Test ElevenLabs session resumption
        await test_elevenlabs_session_resumption(session_id)
        logger.info("ElevenLabs session resumption test passed!")
        
        logger.info("All session continuity tests passed!")
    except Exception as e:
        logger.error(f"Tests failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
