#!/usr/bin/env python3
"""
Simple WebSocket client to test the connection to the WebSocket server.
"""
import asyncio
import websockets
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test the connection to the WebSocket server."""
    try:
        # Connect to the WebSocket server
        logger.info("Connecting to WebSocket server...")
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            logger.info("Connected to WebSocket server!")
            
            # Send a simple message
            message = {
                "type": "ping",
                "payload": {"message": "Hello, WebSocket server!"}
            }
            logger.info(f"Sending message: {message}")
            await websocket.send(json.dumps(message))
            
            # Wait for a response
            logger.info("Waiting for response...")
            response = await websocket.recv()
            logger.info(f"Received response: {response}")
            
            # Parse the response
            response_data = json.loads(response)
            logger.info(f"Response type: {response_data.get('type')}")
            logger.info(f"Response payload: {response_data.get('payload')}")
            
            logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
