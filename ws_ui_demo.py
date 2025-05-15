#!/usr/bin/env python3
"""
ShipanionWS UI Control Demo

This script demonstrates how to control the ShipanionUI from the WebSocket backend.
It sends various commands to the UI to update its state and trigger actions.
"""
import asyncio
import json
import logging
import sys
import uuid
import time
import websockets
import jwt
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - modify these settings as needed
WS_SERVER_URL = "ws://localhost:8001/ws"
SECRET_KEY = "your-secret-key-here"  # This should match the key in backend/settings.py

# Use the predefined test token from settings.py
# This is more reliable than creating a new token if you're having auth issues
USE_TEST_TOKEN = True
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko"

# Demo user information
USERNAME = "demo_user"

def create_jwt_token():
    """Create a JWT token for authentication"""
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": USERNAME,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

async def send_ui_commands():
    """Send a series of commands to control the UI"""
    # Create JWT token for authentication
    token = TEST_TOKEN if USE_TEST_TOKEN else create_jwt_token()
    
    # Connect to WebSocket server with token
    ws_url = f"{WS_SERVER_URL}?token={token}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            logger.info(f"Connected to WebSocket server: {WS_SERVER_URL}")
            
            # Generate a session ID
            session_id = str(uuid.uuid4())
            logger.info(f"Using session ID: {session_id}")
            
            # Demo 1: Send a contextual update to trigger ZIP code collection
            await send_zip_collected(websocket, session_id)
            await asyncio.sleep(3)
            
            # Demo 2: Send a contextual update to trigger weight confirmation
            await send_weight_confirmed(websocket, session_id)
            await asyncio.sleep(3)
            
            # Demo 3: Send shipping quotes
            await send_shipping_quotes(websocket, session_id)
            await asyncio.sleep(3)
            
            # Demo 4: Send a notification
            await send_notification(websocket, session_id)
            await asyncio.sleep(3)
            
            # Demo 5: Create a shipping label
            await send_label_created(websocket, session_id)
            await asyncio.sleep(3)
            
            logger.info("Demo completed successfully")
            
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        return False
    
    return True

async def send_message(websocket, message):
    """Send a message to the WebSocket server and wait for a response"""
    await websocket.send(json.dumps(message))
    logger.info(f"Sent: {message['type']}")
    
    # Wait for response
    response = await websocket.recv()
    logger.info(f"Received: {response[:100]}...")
    
    return json.loads(response)

async def send_zip_collected(websocket, session_id):
    """Send a contextual update for ZIP code collection"""
    message = {
        "type": "contextual_update",
        "text": "zip_collected",
        "data": {
            "origin_zip": "10001",
            "destination_zip": "90210",
            "session_id": session_id
        },
        "requestId": str(uuid.uuid4()),
        "timestamp": time.time()
    }
    
    return await send_message(websocket, message)

async def send_weight_confirmed(websocket, session_id):
    """Send a contextual update for weight confirmation"""
    message = {
        "type": "contextual_update",
        "text": "weight_confirmed",
        "data": {
            "weight": 2.5,
            "unit": "lbs",
            "session_id": session_id
        },
        "requestId": str(uuid.uuid4()),
        "timestamp": time.time()
    }
    
    return await send_message(websocket, message)

async def send_shipping_quotes(websocket, session_id):
    """Send shipping quotes to the UI"""
    message = {
        "type": "quote_ready",
        "payload": {
            "quotes": [
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
            ],
            "origin_zip": "10001",
            "destination_zip": "90210",
            "weight": 2.5,
            "session_id": session_id
        },
        "requestId": str(uuid.uuid4()),
        "timestamp": time.time()
    }
    
    return await send_message(websocket, message)

async def send_notification(websocket, session_id):
    """Send a notification to the UI"""
    message = {
        "type": "notification",
        "payload": {
            "type": "success",
            "title": "Demo Notification",
            "message": "This notification was sent from the WebSocket demo script!",
            "session_id": session_id
        },
        "requestId": str(uuid.uuid4()),
        "timestamp": time.time()
    }
    
    return await send_message(websocket, message)

async def send_label_created(websocket, session_id):
    """Send a label created update to the UI"""
    message = {
        "type": "label_created",
        "payload": {
            "tracking_number": "1Z999AA10123456784",
            "carrier": "UPS",
            "service_name": "Ground",
            "cost": 14.99,
            "label_url": "https://example.com/label.pdf",
            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "session_id": session_id
        },
        "requestId": str(uuid.uuid4()),
        "timestamp": time.time()
    }
    
    return await send_message(websocket, message)

if __name__ == "__main__":
    if sys.platform == "win32":
        # Windows specific event loop policy
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the demo
    success = asyncio.run(send_ui_commands())
    
    if success:
        logger.info("Demo completed successfully!")
    else:
        logger.error("Demo failed!")
        sys.exit(1) 