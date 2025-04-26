"""
Test ElevenLabs Full Flow Integration

This module tests the complete flow between ElevenLabs, WebSocket server, and UI:
1. ElevenLabs conversational AI client tool (Bob) triggers the get_rates endpoint
2. The system sends responses both as contextual updates/client tool replies to ElevenLabs
3. The system also sends responses to the UI via parallel WebSocket connections
4. ElevenLabs correctly receives client_tool_result messages and speaks the quote information aloud
"""
import asyncio
import json
import pytest
import websockets
import httpx
import os
import logging
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
WS_SERVER_URL = os.environ.get("WS_SERVER_URL", "ws://localhost:8000/ws")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8000")

# Test data
ELEVENLABS_TOOL_CALL = {
    "type": "client_tool_call",
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "elevenlabs-123",
        "parameters": {
            "from_zip": "90210",
            "to_zip": "10001",
            "weight": 5.0
        }
    },
    "session_id": "test-session-123",
    "broadcast": True
}

async def get_auth_token() -> str:
    """Get an authentication token for testing."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_SERVER_URL}/test-token")
        response.raise_for_status()
        return response.json()["test_token"]

async def connect_client(client_name: str, session_id: str, token: str) -> websockets.WebSocketClientProtocol:
    """Connect a client to the WebSocket server with a session ID."""
    logger.info(f"Connecting {client_name} with session ID: {session_id}")
    websocket = await websockets.connect(f"{WS_SERVER_URL}?token={token}&session_id={session_id}")
    return websocket

async def collect_messages(websocket: websockets.WebSocketClientProtocol, timeout: float = 5.0) -> List[Dict[str, Any]]:
    """Collect all messages from a WebSocket connection for a specified duration."""
    messages = []
    try:
        while True:
            # Set a timeout to avoid waiting indefinitely
            message = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            messages.append(json.loads(message))
            logger.info(f"Received message: {message}")
    except asyncio.TimeoutError:
        # This is expected when no more messages are coming
        pass
    except Exception as e:
        logger.error(f"Error collecting messages: {str(e)}")
    
    return messages

@pytest.mark.asyncio
async def test_elevenlabs_full_flow():
    """Test the complete flow between ElevenLabs, WebSocket server, and UI."""
    token = await get_auth_token()
    session_id = "test-session-123"
    
    # Connect ElevenLabs client (Bob)
    elevenlabs_client = await connect_client("ElevenLabs", session_id, token)
    
    # Connect UI client (simulating the user's browser)
    ui_client = await connect_client("UI", session_id, token)
    
    try:
        # Send tool call from ElevenLabs
        logger.info(f"Sending tool call from ElevenLabs: {ELEVENLABS_TOOL_CALL}")
        await elevenlabs_client.send(json.dumps(ELEVENLABS_TOOL_CALL))
        
        # Collect messages from both clients
        elevenlabs_task = asyncio.create_task(collect_messages(elevenlabs_client))
        ui_task = asyncio.create_task(collect_messages(ui_client))
        
        # Wait for both tasks to complete
        elevenlabs_messages = await elevenlabs_task
        ui_messages = await ui_task
        
        # Verify ElevenLabs received the correct response
        assert len(elevenlabs_messages) >= 1, "ElevenLabs should receive at least one message"
        
        # Find the client_tool_result message
        tool_result_message = next((msg for msg in elevenlabs_messages if msg.get("type") == "client_tool_result"), None)
        assert tool_result_message is not None, "ElevenLabs should receive a client_tool_result message"
        assert tool_result_message["tool_call_id"] == "elevenlabs-123"
        assert not tool_result_message["is_error"]
        assert "result" in tool_result_message
        
        # Find the contextual_update message
        contextual_update = next((msg for msg in elevenlabs_messages if msg.get("type") == "contextual_update"), None)
        assert contextual_update is not None, "ElevenLabs should receive a contextual_update message"
        assert "data" in contextual_update
        assert "message" in contextual_update["data"]
        
        # Verify UI received the contextual update
        assert len(ui_messages) >= 1, "UI should receive at least one message"
        ui_contextual_update = next((msg for msg in ui_messages if msg.get("type") == "contextual_update"), None)
        assert ui_contextual_update is not None, "UI should receive a contextual_update message"
        
        # Verify the contextual update contains the same data for both clients
        assert ui_contextual_update["data"]["message"] == contextual_update["data"]["message"]
        
        # Verify the result contains shipping quotes
        result = tool_result_message["result"]
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verify the first quote has the expected fields
        first_quote = result[0]
        assert "carrier" in first_quote
        assert "service" in first_quote
        assert "price" in first_quote
        assert "eta" in first_quote
        
        logger.info("Test passed successfully!")
        
    finally:
        # Close the WebSocket connections
        await elevenlabs_client.close()
        await ui_client.close()

@pytest.mark.asyncio
async def test_elevenlabs_label_flow():
    """Test the complete flow for label creation between ElevenLabs, WebSocket server, and UI."""
    token = await get_auth_token()
    session_id = "test-session-456"
    
    # Create label tool call
    label_tool_call = {
        "type": "client_tool_call",
        "client_tool_call": {
            "tool_name": "create_label",
            "tool_call_id": "elevenlabs-456",
            "parameters": {
                "carrier": "fedex",
                "service_type": "FEDEX_GROUND",
                "shipper_name": "Test Shipper",
                "shipper_street": "123 Shipper St",
                "shipper_city": "Beverly Hills",
                "shipper_state": "CA",
                "shipper_zip": "90210",
                "shipper_country": "US",
                "recipient_name": "Test Recipient",
                "recipient_street": "456 Recipient St",
                "recipient_city": "New York",
                "recipient_state": "NY",
                "recipient_zip": "10001",
                "recipient_country": "US",
                "weight": 5.0
            }
        },
        "session_id": session_id,
        "broadcast": True
    }
    
    # Connect ElevenLabs client (Bob)
    elevenlabs_client = await connect_client("ElevenLabs", session_id, token)
    
    # Connect UI client (simulating the user's browser)
    ui_client = await connect_client("UI", session_id, token)
    
    try:
        # Send tool call from ElevenLabs
        logger.info(f"Sending label tool call from ElevenLabs")
        await elevenlabs_client.send(json.dumps(label_tool_call))
        
        # Collect messages from both clients
        elevenlabs_task = asyncio.create_task(collect_messages(elevenlabs_client))
        ui_task = asyncio.create_task(collect_messages(ui_client))
        
        # Wait for both tasks to complete
        elevenlabs_messages = await elevenlabs_task
        ui_messages = await ui_task
        
        # Verify ElevenLabs received the correct response
        assert len(elevenlabs_messages) >= 1, "ElevenLabs should receive at least one message"
        
        # Find the client_tool_result message
        tool_result_message = next((msg for msg in elevenlabs_messages if msg.get("type") == "client_tool_result"), None)
        assert tool_result_message is not None, "ElevenLabs should receive a client_tool_result message"
        assert tool_result_message["tool_call_id"] == "elevenlabs-456"
        assert not tool_result_message["is_error"]
        assert "result" in tool_result_message
        
        # Find the contextual_update message
        contextual_update = next((msg for msg in elevenlabs_messages if msg.get("type") == "contextual_update"), None)
        assert contextual_update is not None, "ElevenLabs should receive a contextual_update message"
        assert "data" in contextual_update
        assert "message" in contextual_update["data"]
        
        # Verify UI received the contextual update
        assert len(ui_messages) >= 1, "UI should receive at least one message"
        ui_contextual_update = next((msg for msg in ui_messages if msg.get("type") == "contextual_update"), None)
        assert ui_contextual_update is not None, "UI should receive a contextual_update message"
        
        # Verify the contextual update contains the same data for both clients
        assert ui_contextual_update["data"]["message"] == contextual_update["data"]["message"]
        
        # Verify the result contains label information
        result = tool_result_message["result"]
        assert "tracking_number" in result
        assert "label_url" in result
        assert "carrier" in result
        
        logger.info("Label test passed successfully!")
        
    finally:
        # Close the WebSocket connections
        await elevenlabs_client.close()
        await ui_client.close()

if __name__ == "__main__":
    # For manual testing
    async def main():
        token = await get_auth_token()
        logger.info(f"Using token: {token}")
        session_id = "test-session-123"
        
        # Connect ElevenLabs client (Bob)
        elevenlabs_client = await connect_client("ElevenLabs", session_id, token)
        
        # Connect UI client (simulating the user's browser)
        ui_client = await connect_client("UI", session_id, token)
        
        try:
            # Send tool call from ElevenLabs
            logger.info(f"Sending tool call from ElevenLabs: {ELEVENLABS_TOOL_CALL}")
            await elevenlabs_client.send(json.dumps(ELEVENLABS_TOOL_CALL))
            
            # Collect messages from both clients for 5 seconds
            elevenlabs_task = asyncio.create_task(collect_messages(elevenlabs_client, 5.0))
            ui_task = asyncio.create_task(collect_messages(ui_client, 5.0))
            
            # Wait for both tasks to complete
            elevenlabs_messages = await elevenlabs_task
            ui_messages = await ui_task
            
            # Print all messages
            logger.info(f"ElevenLabs received {len(elevenlabs_messages)} messages:")
            for i, msg in enumerate(elevenlabs_messages):
                logger.info(f"  {i+1}. {json.dumps(msg, indent=2)}")
            
            logger.info(f"UI received {len(ui_messages)} messages:")
            for i, msg in enumerate(ui_messages):
                logger.info(f"  {i+1}. {json.dumps(msg, indent=2)}")
            
        finally:
            # Close the WebSocket connections
            await elevenlabs_client.close()
            await ui_client.close()
    
    asyncio.run(main())
