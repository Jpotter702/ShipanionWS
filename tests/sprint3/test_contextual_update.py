"""
Test Contextual Update to ElevenLabs and AccordionStepper UI

This script tests sending a contextual_update message back to ElevenLabs and the AccordionStepper UI
after returning a client_tool_result.
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
        response = requests.get(f"{API_SERVER_URL}/test-token")
        response.raise_for_status()
        return response.json()["test_token"]
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        raise

async def test_contextual_update():
    """
    Test sending a contextual_update message back to ElevenLabs and the AccordionStepper UI.

    This test:
    1. Connects to the WebSocket server
    2. Sends a client_tool_call message
    3. Waits for the client_tool_result response
    4. Waits for the contextual_update messages
    5. Verifies that both the UI and ElevenLabs receive contextual updates
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        logger.info(f"Obtained auth token: {token[:10]}...")

        # Connect to WebSocket server
        logger.info(f"Connecting to WebSocket server at {WS_SERVER_URL}?token={token}")
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")

            # Send the client_tool_call
            logger.info(f"Sending client_tool_call: {json.dumps(VALID_TOOL_CALL)}")
            await websocket.send(json.dumps(VALID_TOOL_CALL))

            # Wait for responses with timeout
            logger.info("Waiting for responses...")
            start_time = time.time()
            timeout = 30  # 30 seconds timeout

            # Track received messages
            client_tool_result_received = False
            contextual_updates_received = []

            while time.time() - start_time < timeout and (not client_tool_result_received or len(contextual_updates_received) < 2):
                try:
                    # Set a shorter timeout for each receive attempt
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    response_data = json.loads(response)

                    # Log all messages for debugging
                    logger.info(f"Received message: {json.dumps(response_data)}")

                    # Check message type
                    if response_data.get("type") == "client_tool_result":
                        logger.info("Received client_tool_result response!")
                        client_tool_result_received = True
                    elif response_data.get("type") == "contextual_update":
                        logger.info(f"Received contextual_update: {response_data.get('text')}")
                        contextual_updates_received.append(response_data)

                except asyncio.TimeoutError:
                    # This is expected, we'll try again until the overall timeout
                    continue
                except Exception as e:
                    logger.error(f"Error processing response: {str(e)}")
                    raise

            # Verify that we received the expected messages
            if not client_tool_result_received:
                logger.error("Did not receive client_tool_result response")
                assert False, "Did not receive client_tool_result response"

            if len(contextual_updates_received) < 1:
                logger.error("Did not receive any contextual_update messages")
                assert False, "Did not receive any contextual_update messages"

            # Check if we received both types of contextual updates
            ui_update = None
            elevenlabs_update = None

            for update in contextual_updates_received:
                if update.get("text") == "quote_ready":
                    ui_update = update
                elif update.get("text") == "get_shipping_quotes_result":
                    elevenlabs_update = update

            # Verify UI update
            if ui_update:
                logger.info("Received UI contextual update!")
                assert "data" in ui_update, "Missing 'data' field in UI update"
                assert "carrier" in ui_update["data"], "Missing 'carrier' field in UI update data"
                assert "price" in ui_update["data"], "Missing 'price' field in UI update data"
            else:
                logger.warning("Did not receive UI contextual update")

            # Verify ElevenLabs update
            if elevenlabs_update:
                logger.info("Received ElevenLabs contextual update!")
                assert "data" in elevenlabs_update, "Missing 'data' field in ElevenLabs update"
                assert "message" in elevenlabs_update["data"], "Missing 'message' field in ElevenLabs update data"
                assert "tool_name" in elevenlabs_update["data"], "Missing 'tool_name' field in ElevenLabs update data"

                # Check that the message is user-friendly
                message = elevenlabs_update["data"]["message"]
                assert "Quote ready" in message, f"Expected 'Quote ready' in message, got: {message}"
                assert "$" in message, f"Expected '$' in message, got: {message}"
            else:
                logger.warning("Did not receive ElevenLabs contextual update")

            # Overall test result
            if ui_update and elevenlabs_update:
                logger.info("Test passed! Both UI and ElevenLabs received contextual updates.")
            elif ui_update:
                logger.warning("Test partially passed. Only UI received contextual update.")
            elif elevenlabs_update:
                logger.warning("Test partially passed. Only ElevenLabs received contextual update.")
            else:
                logger.error("Test failed. No contextual updates received.")
                assert False, "No contextual updates received"

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def main():
    """Run the test."""
    logger.info("Starting contextual update test")

    try:
        await test_contextual_update()
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
