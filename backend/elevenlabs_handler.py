"""
ElevenLabs Integration Handler

This module handles integration with ElevenLabs Conversational AI client tools.
It processes client_tool_call messages and returns client_tool_result responses.
"""
import logging
import time
import uuid
import httpx
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
            # Forward the request to the ShipVox API with a 30-second timeout
            logger.info(f"Sending rate request to ShipVox API for tool call: {tool_call_id}")
            rate_response = await shipvox_client.get_rates(rate_request, timeout_seconds=30.0)

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

            # Create a contextual update for the UI and ElevenLabs
            # Extract information for the human-readable message
            cheapest = rate_response.get("cheapest_option", {})
            carrier = cheapest.get("carrier", "")
            price = cheapest.get("cost", 0)
            service = cheapest.get("service_name", "")

            # Create a user-friendly message
            human_message = f"Quote ready from {carrier} {service} for ${price:.2f}"

            contextual_update = create_quote_ready_update(
                rate_response=rate_response,
                user_info=user_info,
                request_id=tool_result["requestId"],
                human_readable_message=human_message
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

        try:
            # Use a 10-second timeout for consistency with get_rates
            response = await shipvox_client.client.post(url, json=label_request, timeout=10.0)
            response.raise_for_status()
            label_response = response.json()
        except httpx.HTTPStatusError as e:
            # Handle non-200 responses
            status_code = e.response.status_code
            error_detail = f"HTTP {status_code}"
            try:
                # Try to extract error details from response
                error_json = e.response.json()
                if isinstance(error_json, dict) and "detail" in error_json:
                    error_detail = f"{error_detail}: {error_json['detail']}"
            except Exception:
                # If we can't parse the response as JSON, use the response text
                if e.response.text:
                    error_detail = f"{error_detail}: {e.response.text[:200]}"

            logger.error(f"Label request failed with {error_detail}")
            return create_tool_error_response(
                tool_call_id=tool_call.get("tool_call_id"),
                error_message=f"API returned error: {error_detail}",
                original_request=tool_call
            ), None
        except httpx.TimeoutException as e:
            logger.error(f"Label request timed out after 10 seconds: {str(e)}")
            return create_tool_error_response(
                tool_call_id=tool_call.get("tool_call_id"),
                error_message="timeout calling labels endpoint",
                original_request=tool_call
            ), None
        except httpx.RequestError as e:
            logger.error(f"Label request network error: {str(e)}")
            return create_tool_error_response(
                tool_call_id=tool_call.get("tool_call_id"),
                error_message=f"Network error: {str(e)}",
                original_request=tool_call
            ), None

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

        # Create a contextual update for the UI and ElevenLabs
        # Extract information for the human-readable message
        tracking_number = label_response.get("tracking_number", "")
        carrier = label_response.get("carrier", "")

        # Create a user-friendly message
        human_message = f"Label created with {carrier} tracking number {tracking_number}"

        contextual_update = create_label_created_update(
            label_response=label_response,
            user_info=user_info,
            request_id=tool_result["requestId"],
            human_readable_message=human_message
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

def create_elevenlabs_contextual_update(
    tool_result: Dict[str, Any],
    tool_name: str,
    user_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a contextual update specifically for ElevenLabs.

    Args:
        tool_result: The client_tool_result message
        tool_name: The name of the tool that was called
        user_info: Information about the authenticated user

    Returns:
        A contextual_update message for ElevenLabs
    """
    # Extract information from the tool result
    is_error = tool_result.get("is_error", False)
    result = tool_result.get("result", {})

    if is_error:
        # Create an error message
        message = f"Error processing {tool_name}: {result.get('error', 'Unknown error')}"
    else:
        # Create a success message based on the tool name
        if tool_name == "get_shipping_quotes":
            # For shipping quotes, extract the cheapest option
            if isinstance(result, list) and len(result) > 0:
                cheapest = min(result, key=lambda x: x.get("price", float("inf")))
                carrier = cheapest.get("carrier", "")
                price = cheapest.get("price", 0)
                message = f"Quote ready from {carrier} for ${price:.2f}"
            else:
                message = "Shipping quotes received"
        elif tool_name == "create_label":
            # For label creation, extract the tracking number
            tracking_number = result.get("tracking_number", "")
            carrier = result.get("carrier", "")
            message = f"Label created with {carrier} tracking number {tracking_number}"
        else:
            # Generic message for other tools
            message = f"{tool_name} completed successfully"

    # Create the contextual update
    return {
        "type": "contextual_update",
        "text": f"{tool_name}_result",
        "data": {
            "message": message,
            "tool_name": tool_name,
            "is_error": is_error
        },
        "timestamp": time.time(),
        "requestId": tool_result.get("requestId", str(uuid.uuid4())),
        "user": user_info.get("username")
    }

async def handle_client_tool_call(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle client tool call messages.
    
    Args:
        message: The WebSocket message containing the client tool call
        user_info: Information about the authenticated user
        
    Returns:
        A tuple of (response, contextual_update) where contextual_update might be None
    """
    logger.info(f"Handling client tool call from user: {user_info.get('username')}")
    request_id = message.get("requestId", str(uuid.uuid4()))
    
    # Extract client tool call details
    try:
        payload = message.get("payload", {})
        client_tool_call = payload.get("client_tool_call", {})
        
        if not client_tool_call:
            logger.warning("Missing client_tool_call in payload")
            return {
                "type": "client_tool_result",
                "tool_call_id": None,
                "result": {
                    "error": "Missing client_tool_call in payload",
                    "original_request": message
                },
                "is_error": True,
                "timestamp": time.time(),
                "requestId": request_id
            }, None
        
        tool_name = client_tool_call.get("tool_name")
        tool_call_id = client_tool_call.get("tool_call_id", str(uuid.uuid4()))
        parameters = client_tool_call.get("parameters", {})
        
        logger.info(f"Client tool call: tool_name={tool_name}, tool_call_id={tool_call_id}, parameters={parameters}")
        
        # Placeholder for actual tool implementation
        # In a real implementation, this would dispatch to specific tool handlers
        
        if tool_name == "hello":
            response_message = parameters.get("message", "Hello, world!")
            result = {
                "message": f"Received: {response_message}",
                "status": "success"
            }
        else:
            # Unsupported tool
            logger.warning(f"Unsupported tool: {tool_name}")
            result = {
                "error": f"Unsupported tool: {tool_name}",
                "original_request": client_tool_call
            }
            is_error = True
            return {
                "type": "client_tool_result",
                "tool_call_id": tool_call_id,
                "result": result,
                "is_error": is_error,
                "timestamp": time.time(),
                "requestId": request_id
            }, None
        
        # Create the response
        response = {
            "type": "client_tool_result",
            "tool_call_id": tool_call_id,
            "result": result,
            "is_error": False,
            "timestamp": time.time(),
            "requestId": request_id
        }
        
        # No contextual update for this handler
        return response, None
        
    except Exception as e:
        logger.error(f"Error handling client tool call: {str(e)}")
        error_response = {
            "type": "client_tool_result",
            "tool_call_id": None,
            "result": {
                "error": f"Error processing client tool call: {str(e)}",
                "original_request": message
            },
            "is_error": True,
            "timestamp": time.time(),
            "requestId": request_id
        }
        return error_response, None
