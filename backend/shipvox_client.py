"""
ShipVox API Client

This module provides a client for interacting with the ShipVox API.
It handles making requests to the ShipVox API endpoints and processing responses.
When USE_INTERNAL is True, it calls internal functions directly instead of making HTTP requests.
"""
import httpx
import json
import logging
from typing import Dict, Any, Optional
import os
from pydantic import BaseModel
from .settings import SHIPVOX_API_URL, USE_INTERNAL

# Import internal service functions if USE_INTERNAL is True
if USE_INTERNAL:
    from .shipping_service import get_shipping_quotes as internal_get_shipping_quotes
    from .shipping_service import create_shipping_label as internal_create_shipping_label

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateRequest(BaseModel):
    """Model for rate request data."""
    origin_zip: str
    destination_zip: str
    weight: float
    dimensions: Optional[Dict[str, float]] = None
    pickup_requested: bool = False

class ShipVoxClient:
    """Client for interacting with the ShipVox API."""

    def __init__(self, base_url: str = SHIPVOX_API_URL):
        """
        Initialize the ShipVox API client.

        Args:
            base_url: Base URL for the ShipVox API
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)  # 30 second timeout
        logger.info(f"ShipVoxClient initialized with base URL: {base_url}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get_rates(self, rate_request: Dict[str, Any], timeout_seconds: float = 10.0) -> Dict[str, Any]:
        """
        Get shipping rates from the ShipVox API or internal service.

        When USE_INTERNAL is True, this method calls the internal get_shipping_quotes function directly.
        When USE_INTERNAL is False, it makes an HTTP request to the ShipVox API.

        Args:
            rate_request: Dictionary containing rate request parameters
            timeout_seconds: Timeout in seconds for this specific request (default: 10.0)
                            Only used when USE_INTERNAL is False

        Returns:
            Dictionary containing rate response data

        Raises:
            httpx.HTTPError: If the request fails (when USE_INTERNAL is False)
            httpx.TimeoutException: If the request times out (when USE_INTERNAL is False)
            TimeoutError: If the internal call times out (when USE_INTERNAL is True)
            ValueError: If required fields are missing
            Exception: For any other errors
        """
        # If USE_INTERNAL is True, call the internal function directly
        if USE_INTERNAL:
            logger.info("Using internal get_shipping_quotes function")
            try:
                # Call the internal function
                result = await internal_get_shipping_quotes(rate_request)
                logger.info("Internal get_shipping_quotes call successful")
                return result
            except TimeoutError as e:
                # Handle timeout from internal function
                logger.error(f"Internal get_shipping_quotes call timed out: {str(e)}")
                # Re-raise with the exact error message
                raise Exception("timeout calling rates endpoint")
            except ValueError as e:
                # Handle validation errors from internal function
                logger.error(f"Internal get_shipping_quotes call failed with validation error: {str(e)}")
                raise Exception(f"Validation error: {str(e)}")
            except Exception as e:
                # Handle any other errors from internal function
                logger.error(f"Unexpected error in internal get_shipping_quotes call: {str(e)}")
                raise
        else:
            # Use the REST API
            url = f"{self.base_url}/get-rates"
            logger.info(f"Sending rate request to {url} with timeout of {timeout_seconds} seconds")

            # Create a specific timeout for this request
            timeout = httpx.Timeout(timeout_seconds)

            try:
                response = await self.client.post(url, json=rate_request, timeout=timeout)
                response.raise_for_status()
                result = response.json()
                logger.info("Rate request successful")
                return result
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

                logger.error(f"Rate request failed with {error_detail}")
                raise Exception(f"API returned error: {error_detail}")
            except httpx.TimeoutException as e:
                logger.error(f"Rate request timed out after {timeout_seconds} seconds: {str(e)}")
                # Use the exact error message specified in the requirements
                raise Exception("timeout calling rates endpoint")
            except httpx.RequestError as e:
                logger.error(f"Rate request network error: {str(e)}")
                raise Exception(f"Network error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error in rate request: {str(e)}")
                raise
