"""
Shipping Service Module

This module contains the internal implementation of shipping service functions.
These functions can be called directly when USE_INTERNAL is set to True.
"""
import logging
import time
import uuid
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_shipping_quotes(rate_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get shipping quotes directly (internal implementation).
    
    This function is called directly when USE_INTERNAL is True.
    It implements the same logic as the /get-rates endpoint.
    
    Args:
        rate_request: Dictionary containing rate request parameters
        
    Returns:
        Dictionary containing rate response data
    """
    logger.info("Getting shipping quotes using internal function")
    
    # Validate required fields
    required_fields = ["origin_zip", "destination_zip", "weight"]
    for field in required_fields:
        if field not in rate_request or not rate_request[field]:
            raise ValueError(f"Missing required field: {field}")
    
    # Check for special test ZIP codes
    if rate_request["origin_zip"] == "99999":
        # Simulate a timeout
        logger.info("Simulating a timeout for test ZIP code 99999")
        raise TimeoutError("timeout calling rates endpoint")
    
    # Generate mock shipping options
    cheapest_option = {
        "carrier": "USPS",
        "service_name": "Priority Mail",
        "cost": 12.99,
        "transit_days": 3
    }
    
    fastest_option = {
        "carrier": "FedEx",
        "service_name": "Overnight",
        "cost": 45.99,
        "transit_days": 1
    }
    
    all_options = [
        cheapest_option,
        fastest_option,
        {
            "carrier": "UPS",
            "service_name": "Ground",
            "cost": 15.99,
            "transit_days": 4
        }
    ]
    
    # Create the response
    response = {
        "request": rate_request,
        "cheapest_option": cheapest_option,
        "fastest_option": fastest_option,
        "all_options": all_options
    }
    
    logger.info("Successfully generated shipping quotes")
    return response

async def create_shipping_label(label_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a shipping label directly (internal implementation).
    
    This function is called directly when USE_INTERNAL is True.
    It implements the same logic as the /labels endpoint.
    
    Args:
        label_request: Dictionary containing label request parameters
        
    Returns:
        Dictionary containing label response data
    """
    logger.info("Creating shipping label using internal function")
    
    # Validate carrier and service type
    if not label_request.get("carrier") or not label_request.get("service_type"):
        raise ValueError("Missing required fields: carrier and service_type")
    
    # Validate shipper and recipient addresses
    for address_type in ["shipper", "recipient"]:
        if address_type not in label_request:
            raise ValueError(f"Missing {address_type} information")
        
        address = label_request[address_type]
        for field in ["name", "street", "city", "state", "zip_code"]:
            if field not in address or not address[field]:
                raise ValueError(f"Missing required {address_type} field: {field}")
    
    # Validate package
    if "package" not in label_request:
        raise ValueError("Missing package information")
    
    package = label_request["package"]
    if "weight" not in package or not package["weight"] or package["weight"] <= 0:
        raise ValueError("Invalid package weight: must be greater than 0")
    
    # Generate a mock tracking number
    tracking_number = f"{label_request['carrier'].upper()}-{uuid.uuid4().hex[:12].upper()}"
    
    # Create a mock label URL
    label_url = f"https://shipvox.example.com/labels/{tracking_number}.pdf"
    
    # Create a mock QR code URL
    qr_code_url = f"https://shipvox.example.com/qr/{tracking_number}.png"
    
    # Calculate a mock estimated delivery date (7 days from now)
    current_time = int(time.time())
    estimated_delivery = current_time + (7 * 24 * 60 * 60)  # 7 days in seconds
    
    # Create the response
    response = {
        "tracking_number": tracking_number,
        "carrier": label_request["carrier"],
        "service": label_request["service_type"],
        "label_url": label_url,
        "fallback_qr_code_url": qr_code_url,
        "estimated_delivery": estimated_delivery
    }
    
    logger.info(f"Successfully created shipping label with tracking number: {tracking_number}")
    return response
