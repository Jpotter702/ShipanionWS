"""
WebSocket Message Handlers

This module contains handlers for different types of WebSocket messages.
Each handler processes a specific message type and returns a response.
"""
import logging
import time
import uuid
from typing import Dict, Any, List, Callable, Tuple, Optional
from .shipvox_client import ShipVoxClient
from .elevenlabs_handler import handle_client_tool_call

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the ShipVox client
shipvox_client = ShipVoxClient()

async def handle_rate_request(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle a rate request message.

    Args:
        message: The WebSocket message containing rate request data
        user_info: Information about the authenticated user

    Returns:
        A response message to be sent back through the WebSocket
    """
    logger.info(f"Handling rate request from user: {user_info.get('username')}")

    try:
        # Extract rate request data from the message payload
        rate_request = message.get("payload", {})

        # Validate required fields
        required_fields = ["origin_zip", "destination_zip", "weight"]
        for field in required_fields:
            if field not in rate_request:
                return {
                    "type": "error",
                    "payload": {
                        "message": f"Missing required field: {field}",
                        "original_request": message
                    },
                    "timestamp": time.time(),
                    "requestId": str(uuid.uuid4())
                }

        # Forward the request to the ShipVox API
        rate_response = await shipvox_client.get_rates(rate_request)

        # Create the response
        response = {
            "type": "quote_ready",
            "payload": rate_response,
            "timestamp": time.time(),
            "requestId": str(uuid.uuid4()),
            "user": user_info.get("username")
        }

        # No contextual update for direct rate requests
        return response, None
    except Exception as e:
        logger.error(f"Error handling rate request: {str(e)}")
        error_response = {
            "type": "error",
            "payload": {
                "message": f"Error processing rate request: {str(e)}",
                "original_request": message
            },
            "timestamp": time.time(),
            "requestId": str(uuid.uuid4()),
            "user": user_info.get("username")
        }
        return error_response, None

# Message type to handler mapping
message_handlers: Dict[str, Callable] = {
    "get_rates": handle_rate_request,
    "client_tool_call": handle_client_tool_call,
}

async def dispatch_message(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Dispatch a message to the appropriate handler based on its type.

    Args:
        message: The WebSocket message to handle
        user_info: Information about the authenticated user

    Returns:
        A response message to be sent back through the WebSocket
    """
    message_type = message.get("type")

    if message_type in message_handlers:
        logger.info(f"Dispatching message of type: {message_type}")
        return await message_handlers[message_type](message, user_info)
    else:
        logger.warning(f"No handler found for message type: {message_type}")
        error_response = {
            "type": "error",
            "payload": {
                "message": f"Unsupported message type: {message_type}",
                "original_request": message
            },
            "timestamp": time.time(),
            "requestId": str(uuid.uuid4()),
            "user": user_info.get("username")
        }
        return error_response, None
