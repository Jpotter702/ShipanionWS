"""
ShipVox API Client

This module provides a client for interacting with the ShipVox API.
It handles making requests to the ShipVox API endpoints and processing responses.
"""
import httpx
import json
import logging
from typing import Dict, Any, Optional
import os
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API URL from environment or use default
SHIPVOX_API_URL = os.environ.get("SHIPVOX_API_URL", "http://localhost:8000/api")

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
    
    async def get_rates(self, rate_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get shipping rates from the ShipVox API.
        
        Args:
            rate_request: Dictionary containing rate request parameters
            
        Returns:
            Dictionary containing rate response data
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.base_url}/get-rates"
        logger.info(f"Sending rate request to {url}")
        
        try:
            response = await self.client.post(url, json=rate_request)
            response.raise_for_status()
            result = response.json()
            logger.info("Rate request successful")
            return result
        except httpx.HTTPError as e:
            logger.error(f"Rate request failed: {str(e)}")
            # Re-raise the exception to be handled by the caller
            raise
