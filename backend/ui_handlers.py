"""
UI Message Handlers

This module contains handlers for UI-specific WebSocket messages.
These handlers process messages used by ShipanionUI to update the user interface.
"""
import logging
import time
import uuid
from typing import Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_contextual_update(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle contextual update messages from the UI.
    
    These messages are used to update the UI state based on context.
    
    Args:
        message: The WebSocket message containing the contextual update
        user_info: Information about the authenticated user
        
    Returns:
        A tuple of (response, contextual_update) where contextual_update might be None
    """
    logger.info(f"Handling contextual update from user: {user_info.get('username')}")
    request_id = message.get("requestId", str(uuid.uuid4()))
    update_type = message.get("text")
    
    # Extract the data from the message
    data = message.get("data", {})
    
    # Log the contextual update
    logger.info(f"Contextual update type: {update_type}, data: {data}")
    
    # Create the response
    response = {
        "type": "contextual_update_received",
        "payload": {
            "message": f"Received {update_type} update",
            "update_type": update_type,
            "status": "success"
        },
        "timestamp": time.time(),
        "requestId": request_id,
        "user": user_info.get("username")
    }
    
    # Create a contextual update to broadcast to all clients in the session
    contextual_update = {
        "type": "contextual_update",
        "text": update_type,
        "data": data,
        "timestamp": time.time(),
        "requestId": request_id,
        "user": user_info.get("username")
    }
    
    return response, contextual_update

async def handle_ui_navigation(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle UI navigation messages.
    
    These messages are used to navigate between different UI screens or views.
    
    Args:
        message: The WebSocket message containing navigation data
        user_info: Information about the authenticated user
        
    Returns:
        A tuple of (response, contextual_update) where contextual_update might be None
    """
    logger.info(f"Handling UI navigation from user: {user_info.get('username')}")
    request_id = message.get("requestId", str(uuid.uuid4()))
    
    # Extract navigation target
    target = message.get("payload", {}).get("target")
    
    # Create the response
    response = {
        "type": "navigation_processed",
        "payload": {
            "message": f"Navigation to {target} processed",
            "target": target,
            "status": "success"
        },
        "timestamp": time.time(),
        "requestId": request_id,
        "user": user_info.get("username")
    }
    
    # Create a contextual update to broadcast navigation to all clients in the session
    contextual_update = {
        "type": "navigation_update",
        "payload": {
            "target": target
        },
        "timestamp": time.time(),
        "requestId": request_id,
        "user": user_info.get("username")
    }
    
    return response, contextual_update

async def handle_notification(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle notification messages to the UI.
    
    Args:
        message: The WebSocket message containing notification data
        user_info: Information about the authenticated user
        
    Returns:
        A tuple of (response, contextual_update) where contextual_update might be None
    """
    logger.info(f"Handling notification from user: {user_info.get('username')}")
    request_id = message.get("requestId", str(uuid.uuid4()))
    
    # Extract notification details
    notification_type = message.get("payload", {}).get("type", "info")
    title = message.get("payload", {}).get("title", "Notification")
    notification_message = message.get("payload", {}).get("message", "")
    
    # Create the response
    response = {
        "type": "notification_sent",
        "payload": {
            "message": "Notification delivered",
            "status": "success"
        },
        "timestamp": time.time(),
        "requestId": request_id,
        "user": user_info.get("username")
    }
    
    # Create a contextual update to broadcast the notification to all clients in the session
    contextual_update = {
        "type": "notification",
        "payload": {
            "type": notification_type,
            "title": title,
            "message": notification_message
        },
        "timestamp": time.time(),
        "requestId": request_id,
        "user": user_info.get("username")
    }
    
    return response, contextual_update

async def handle_get_shipping_quotes(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle getting shipping quotes via client tool call.
    
    Args:
        message: The WebSocket message containing the tool call
        user_info: Information about the authenticated user
        
    Returns:
        A tuple of (response, contextual_update) where contextual_update might be None
    """
    logger.info(f"Handling get shipping quotes tool call from user: {user_info.get('username')}")
    
    # Extract client tool call data
    tool_call = message.get("payload", {}).get("client_tool_call", {})
    tool_call_id = tool_call.get("tool_call_id", str(uuid.uuid4()))
    parameters = tool_call.get("parameters", {})
    
    # Log the tool call
    logger.info(f"Get shipping quotes tool call: id={tool_call_id}, parameters={parameters}")
    
    # Simulate getting quotes (in a real implementation, this would call a shipping API)
    # For now, return mock data
    mock_quotes = [
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
    
    # Create the response
    response = {
        "type": "client_tool_result",
        "tool_call_id": tool_call_id,
        "result": {
            "quotes": mock_quotes,
            "origin_zip": parameters.get("origin_zip"),
            "destination_zip": parameters.get("destination_zip"),
            "weight": parameters.get("weight")
        },
        "is_error": False,
        "timestamp": time.time(),
        "requestId": message.get("requestId", str(uuid.uuid4()))
    }
    
    # Create a contextual update to broadcast to all clients in the session
    contextual_update = {
        "type": "quote_ready",
        "payload": {
            "quotes": mock_quotes,
            "origin_zip": parameters.get("origin_zip"),
            "destination_zip": parameters.get("destination_zip"),
            "weight": parameters.get("weight")
        },
        "timestamp": time.time(),
        "requestId": message.get("requestId", str(uuid.uuid4())),
        "user": user_info.get("username")
    }
    
    return response, contextual_update

async def handle_create_label(message: Dict[str, Any], user_info: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Handle creating a shipping label via client tool call.
    
    Args:
        message: The WebSocket message containing the tool call
        user_info: Information about the authenticated user
        
    Returns:
        A tuple of (response, contextual_update) where contextual_update might be None
    """
    logger.info(f"Handling create label tool call from user: {user_info.get('username')}")
    
    # Extract client tool call data
    tool_call = message.get("payload", {}).get("client_tool_call", {})
    tool_call_id = tool_call.get("tool_call_id", str(uuid.uuid4()))
    parameters = tool_call.get("parameters", {})
    
    # Log the tool call
    logger.info(f"Create label tool call: id={tool_call_id}, parameters={parameters}")
    
    # Simulate creating a label (in a real implementation, this would call a shipping API)
    # For now, return mock data
    tracking_number = f"1Z{uuid.uuid4().hex[:12].upper()}"
    
    # Create the response
    response = {
        "type": "client_tool_result",
        "tool_call_id": tool_call_id,
        "result": {
            "tracking_number": tracking_number,
            "label_url": "/placeholder.svg?height=400&width=300",
            "qr_code": "/placeholder.svg?height=200&width=200",
            "carrier": parameters.get("carrier"),
            "service": parameters.get("service"),
            "weight": parameters.get("weight")
        },
        "is_error": False,
        "timestamp": time.time(),
        "requestId": message.get("requestId", str(uuid.uuid4()))
    }
    
    # Create a contextual update to broadcast to all clients in the session
    contextual_update = {
        "type": "label_created",
        "payload": {
            "tracking_number": tracking_number,
            "label_url": "/placeholder.svg?height=400&width=300",
            "qr_code": "/placeholder.svg?height=200&width=200",
            "carrier": parameters.get("carrier"),
            "service": parameters.get("service"),
            "weight": parameters.get("weight")
        },
        "timestamp": time.time(),
        "requestId": message.get("requestId", str(uuid.uuid4())),
        "user": user_info.get("username")
    }
    
    return response, contextual_update 