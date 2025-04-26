"""
Contextual Update Emitter

This module provides functions for creating and sending contextual updates
to the ElevenLabs agent and UI.
"""
import logging
import time
import uuid
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_contextual_update(
    update_type: str,
    data: Dict[str, Any],
    user_info: Dict[str, Any],
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a contextual update message.

    Args:
        update_type: The type of update (e.g., "quote_ready", "label_created")
        data: The data to include in the update
        user_info: Information about the authenticated user
        request_id: Optional request ID to associate with the update

    Returns:
        A contextual_update message to be sent through the WebSocket
    """
    logger.info(f"Creating contextual update of type: {update_type}")

    return {
        "type": "contextual_update",
        "text": update_type,
        "data": data,
        "timestamp": time.time(),
        "requestId": request_id or str(uuid.uuid4()),
        "user": user_info.get("username")
    }

def create_quote_ready_update(
    rate_response: Dict[str, Any],
    user_info: Dict[str, Any],
    request_id: Optional[str] = None,
    human_readable_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a quote_ready contextual update.

    Args:
        rate_response: The response from the ShipVox API
        user_info: Information about the authenticated user
        request_id: Optional request ID to associate with the update
        human_readable_message: Optional human-readable message for ElevenLabs

    Returns:
        A contextual_update message for quote_ready
    """
    # Extract the cheapest option
    cheapest = rate_response.get("cheapest_option", {})

    # Extract origin and destination from the request
    origin_zip = rate_response.get("request", {}).get("origin_zip", "")
    destination_zip = rate_response.get("request", {}).get("destination_zip", "")  # Fixed typo here
    weight = rate_response.get("request", {}).get("weight", 0)

    # Create the update data
    data = {
        "from": origin_zip,
        "to": destination_zip,
        "weight_lbs": weight,
        "carrier": cheapest.get("carrier", ""),
        "service": cheapest.get("service_name", ""),
        "price": cheapest.get("cost", 0),
        "eta": f"{cheapest.get('transit_days', 0)} days"
    }

    # Add human-readable message if provided
    if human_readable_message:
        data["message"] = human_readable_message
    else:
        # Create a default human-readable message
        carrier = cheapest.get("carrier", "")
        price = cheapest.get("cost", 0)
        data["message"] = f"Quote ready from {carrier} for ${price:.2f}"

    return create_contextual_update("quote_ready", data, user_info, request_id)

def create_label_created_update(
    label_response: Dict[str, Any],
    user_info: Dict[str, Any],
    request_id: Optional[str] = None,
    human_readable_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a label_created contextual update.

    Args:
        label_response: The response from the ShipVox API
        user_info: Information about the authenticated user
        request_id: Optional request ID to associate with the update
        human_readable_message: Optional human-readable message for ElevenLabs

    Returns:
        A contextual_update message for label_created
    """
    # Create the update data
    tracking_number = label_response.get("tracking_number", "")
    carrier = label_response.get("carrier", "")

    data = {
        "tracking_number": tracking_number,
        "carrier": carrier,
        "label_url": label_response.get("label_url", ""),
        "qr_code": label_response.get("fallback_qr_code_url", "") or label_response.get("native_qr_code_base64", ""),
        "estimated_delivery": label_response.get("estimated_delivery", "")
    }

    # Add human-readable message if provided
    if human_readable_message:
        data["message"] = human_readable_message
    else:
        # Create a default human-readable message
        data["message"] = f"Label created with {carrier} tracking number {tracking_number}"

    return create_contextual_update("label_created", data, user_info, request_id)
