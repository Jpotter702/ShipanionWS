"""
ElevenLabs Integration Handler

This module handles integration with ElevenLabs Conversational AI client tools.
It processes client_tool_call messages and returns client_tool_result responses.
"""
import logging
import time
import uuid
from typing import Dict, Any, Optional, Tuple
from .shipvox_client import ShipVoxClient
from .contextual_update import create_quote_ready_update, create_label_created_update

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the ShipVox client
shipvox_client = ShipVoxClient()

async def handle_get_shipping_quotes(tool_call: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle a get_shipping_quotes tool call from ElevenLabs.

    Args:
        tool_call: The tool call data from ElevenLabs
        user_info: Information about the authenticated user

    Returns:
        A client_tool_result message to be sent back through the WebSocket
    """
    logger.info(f"Handling get_shipping_quotes from user: {user_info.get('username')}")
    tool_call_id = tool_call.get("tool_call_id", "unknown")

    try:
        # Extract parameters from the tool call
        parameters = tool_call.get("parameters", {})

        # Map ElevenLabs parameters to ShipVox API parameters
        rate_request = {
            "origin_zip": parameters.get("from_zip"),
            "destination_zip": parameters.get("to_zip"),
            "weight": float(parameters.get("weight", 0)),
            "dimensions": parameters.get("dimensions"),
            "pickup_requested": parameters.get("pickup_requested", False)
        }

        # Validate required fields
        required_fields = ["origin_zip", "destination_zip", "weight"]
        for field in required_fields:
            if not rate_request.get(field):
                logger.warning(f"Missing required parameter: {field} for tool call: {tool_call_id}")
                return create_tool_error_response(
                    tool_call_id=tool_call_id,
                    error_message=f"Missing required parameter: {field}",
                    original_request=tool_call
                ), None

        try:
            # Forward the request to the ShipVox API with a 10-second timeout
            logger.info(f"Sending rate request to ShipVox API for tool call: {tool_call_id}")
            rate_response = await shipvox_client.get_rates(rate_request, timeout_seconds=10.0)

            # Format the response for ElevenLabs
            formatted_result = format_rate_response_for_elevenlabs(rate_response)

            # Create the client_tool_result
            tool_result = {
                "type": "client_tool_result",
                "tool_call_id": tool_call_id,
                "result": formatted_result,
                "is_error": False,
                "timestamp": time.time(),
                "requestId": str(uuid.uuid4()),
                "user": user_info.get("username")
            }

            # Create a contextual update for the UI
            contextual_update = create_quote_ready_update(
                rate_response=rate_response,
                user_info=user_info,
                request_id=tool_result["requestId"]
            )

            # Return both the tool result and the contextual update
            logger.info(f"Successfully processed shipping quotes for tool call: {tool_call_id}")
            return tool_result, contextual_update

        except Exception as api_error:
            # Handle API-specific errors (non-200 responses, timeouts, etc.)
            error_message = str(api_error)
            logger.error(f"API error for tool call {tool_call_id}: {error_message}")

            # Create a detailed error response
            error_response = create_tool_error_response(
                tool_call_id=tool_call_id,
                error_message=f"Failed to get shipping rates: {error_message}",
                original_request=tool_call
            )
            return error_response, None

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error handling get_shipping_quotes for tool call {tool_call_id}: {str(e)}")
        error_response = create_tool_error_response(
            tool_call_id=tool_call_id,
            error_message=f"Error processing shipping quotes: {str(e)}",
            original_request=tool_call
        )
        return error_response, None

def format_rate_response_for_elevenlabs(rate_response: Dict[str, Any]) -> list:
    """
    Format the ShipVox rate response for ElevenLabs.

    Args:
        rate_response: The response from the ShipVox API

    Returns:
        A list of shipping options formatted for ElevenLabs
    """
    result = []

    # Add the cheapest option
    if "cheapest_option" in rate_response:
        cheapest = rate_response["cheapest_option"]
        result.append({
            "carrier": cheapest["carrier"],
            "service": cheapest["service_name"],
            "price": cheapest["cost"],
            "eta": f"{cheapest['transit_days']} days"
        })

    # Add the fastest option if different from cheapest
    if "fastest_option" in rate_response and rate_response["fastest_option"]:
        fastest = rate_response["fastest_option"]
        # Check if fastest is different from cheapest
        if not any(opt["carrier"] == fastest["carrier"] and
                  opt["service"] == fastest["service_name"] for opt in result):
            result.append({
                "carrier": fastest["carrier"],
                "service": fastest["service_name"],
                "price": fastest["cost"],
                "eta": f"{fastest['transit_days']} days"
            })

    # Add other options (limited to top 3 for clarity)
    if "all_options" in rate_response:
        for option in rate_response["all_options"][:3]:
            # Check if this option is already in the result
            if not any(opt["carrier"] == option["carrier"] and
                      opt["service"] == option["service_name"] for opt in result):
                result.append({
                    "carrier": option["carrier"],
                    "service": option["service_name"],
                    "price": option["cost"],
                    "eta": f"{option['transit_days']} days"
                })

    return result

def create_tool_error_response(tool_call_id: str, error_message: str, original_request: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create an error response for a tool call.

    Args:
        tool_call_id: The ID of the tool call
        error_message: The error message
        original_request: The original request that caused the error

    Returns:
        A client_tool_result message with error information
    """
    return {
        "type": "client_tool_result",
        "tool_call_id": tool_call_id,
        "result": {
            "error": error_message,
            "original_request": original_request
        },
        "is_error": True,
        "timestamp": time.time(),
        "requestId": str(uuid.uuid4())
    }

async def handle_create_label(tool_call: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle a create_label tool call from ElevenLabs.

    Args:
        tool_call: The tool call data from ElevenLabs
        user_info: Information about the authenticated user

    Returns:
        A client_tool_result message to be sent back through the WebSocket
    """
    logger.info(f"Handling create_label from user: {user_info.get('username')}")

    try:
        # Extract parameters from the tool call
        parameters = tool_call.get("parameters", {})

        # Map ElevenLabs parameters to ShipVox API parameters
        label_request = {
            "carrier": parameters.get("carrier", "").lower(),
            "shipper": {
                "name": parameters.get("shipper_name", ""),
                "street": parameters.get("shipper_street", ""),
                "city": parameters.get("shipper_city", ""),
                "state": parameters.get("shipper_state", ""),
                "zip_code": parameters.get("shipper_zip", ""),
                "country": parameters.get("shipper_country", "US")
            },
            "recipient": {
                "name": parameters.get("recipient_name", ""),
                "street": parameters.get("recipient_street", ""),
                "city": parameters.get("recipient_city", ""),
                "state": parameters.get("recipient_state", ""),
                "zip_code": parameters.get("recipient_zip", ""),
                "country": parameters.get("recipient_country", "US")
            },
            "package": {
                "weight": float(parameters.get("weight", 0)),
                "dimensions": parameters.get("dimensions", None)
            },
            "service_type": parameters.get("service_type", "")
        }

        # Validate required fields
        required_fields = ["carrier", "service_type"]
        for field in required_fields:
            if not label_request.get(field):
                return create_tool_error_response(
                    tool_call_id=tool_call.get("tool_call_id"),
                    error_message=f"Missing required parameter: {field}",
                    original_request=tool_call
                )

        # Validate shipper and recipient addresses
        for address_type in ["shipper", "recipient"]:
            address = label_request.get(address_type, {})
            for field in ["name", "street", "city", "state", "zip_code"]:
                if not address.get(field):
                    return create_tool_error_response(
                        tool_call_id=tool_call.get("tool_call_id"),
                        error_message=f"Missing required {address_type} field: {field}",
                        original_request=tool_call
                    )

        # Validate package
        if not label_request["package"]["weight"] or label_request["package"]["weight"] <= 0:
            return create_tool_error_response(
                tool_call_id=tool_call.get("tool_call_id"),
                error_message=f"Invalid package weight: must be greater than 0",
                original_request=tool_call
            )

        # Forward the request to the ShipVox API
        url = f"{shipvox_client.base_url}/labels"
        logger.info(f"Sending label request to {url}")

        response = await shipvox_client.client.post(url, json=label_request)
        response.raise_for_status()
        label_response = response.json()

        # Format the response for ElevenLabs
        formatted_result = {
            "tracking_number": label_response.get("tracking_number"),
            "label_url": label_response.get("label_url"),
            "qr_code": label_response.get("fallback_qr_code_url") or label_response.get("native_qr_code_base64"),
            "carrier": label_response.get("carrier"),
            "estimated_delivery": label_response.get("estimated_delivery")
        }

        # Create the client_tool_result
        tool_result = {
            "type": "client_tool_result",
            "tool_call_id": tool_call.get("tool_call_id"),
            "result": formatted_result,
            "is_error": False,
            "timestamp": time.time(),
            "requestId": str(uuid.uuid4()),
            "user": user_info.get("username")
        }

        # Create a contextual update for the UI
        contextual_update = create_label_created_update(
            label_response=label_response,
            user_info=user_info,
            request_id=tool_result["requestId"]
        )

        # Return both the tool result and the contextual update
        return tool_result, contextual_update
    except Exception as e:
        logger.error(f"Error handling create_label: {str(e)}")
        error_response = create_tool_error_response(
            tool_call_id=tool_call.get("tool_call_id"),
            error_message=f"Error processing label creation: {str(e)}",
            original_request=tool_call
        )
        return error_response, None

# Map of tool names to handler functions
tool_handlers = {
    "get_shipping_quotes": handle_get_shipping_quotes,
    "create_label": handle_create_label,
}

async def handle_client_tool_call(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle a client_tool_call message from ElevenLabs.

    Args:
        message: The WebSocket message containing the client_tool_call
        user_info: Information about the authenticated user

    Returns:
        A response message to be sent back through the WebSocket
    """
    logger.info(f"Handling client_tool_call from user: {user_info.get('username')}")

    try:
        # Extract the client_tool_call data
        client_tool_call = message.get("client_tool_call", {})
        tool_name = client_tool_call.get("tool_name")

        # Check if we have a handler for this tool
        if tool_name in tool_handlers:
            logger.info(f"Processing tool call for: {tool_name}")
            return await tool_handlers[tool_name](client_tool_call, user_info)
        else:
            logger.warning(f"No handler found for tool: {tool_name}")
            error_response = create_tool_error_response(
                tool_call_id=client_tool_call.get("tool_call_id"),
                error_message=f"Unsupported tool: {tool_name}",
                original_request=client_tool_call
            )
            return error_response, None
    except Exception as e:
        logger.error(f"Error handling client_tool_call: {str(e)}")
        error_response = create_tool_error_response(
            tool_call_id=message.get("client_tool_call", {}).get("tool_call_id", "unknown"),
            error_message=f"Error processing tool call: {str(e)}",
            original_request=message
        )
        return error_response, None
