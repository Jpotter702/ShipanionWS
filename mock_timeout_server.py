#!/usr/bin/env python3
"""
Mock server to simulate timeouts for testing.

This script creates a simple FastAPI server that simulates timeouts
for the /get-rates endpoint when a special ZIP code is used.
"""
import asyncio
import logging
import sys
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Mock Timeout Server")

# Special ZIP code that will trigger a timeout
TIMEOUT_ZIP = "99999"

class RateRequest(BaseModel):
    """Model for rate request data."""
    origin_zip: str
    destination_zip: str
    weight: float
    dimensions: Optional[Dict[str, float]] = None
    pickup_requested: bool = False

class ShippingOption(BaseModel):
    """Model for a shipping option."""
    carrier: str
    service_name: str
    cost: float
    transit_days: int

class RateResponse(BaseModel):
    """Model for rate response data."""
    request: RateRequest
    cheapest_option: ShippingOption
    fastest_option: Optional[ShippingOption] = None
    all_options: List[ShippingOption]

@app.post("/api/get-rates")
async def get_rates(request: RateRequest):
    """
    Simulate the get-rates endpoint.
    
    If the origin_zip is the special TIMEOUT_ZIP, sleep for 15 seconds
    to simulate a timeout.
    """
    logger.info(f"Received rate request: {request}")
    
    # Check if this should trigger a timeout
    if request.origin_zip == TIMEOUT_ZIP:
        logger.info(f"Simulating timeout for ZIP code {TIMEOUT_ZIP}")
        # Sleep for 15 seconds (longer than the 10-second timeout in the client)
        await asyncio.sleep(15)
        # This should never be reached if the client times out properly
        return {"error": "This should have timed out"}
    
    # Otherwise, return a normal response
    cheapest_option = ShippingOption(
        carrier="USPS",
        service_name="Priority Mail",
        cost=12.99,
        transit_days=3
    )
    
    fastest_option = ShippingOption(
        carrier="FedEx",
        service_name="Overnight",
        cost=45.99,
        transit_days=1
    )
    
    all_options = [
        cheapest_option,
        fastest_option,
        ShippingOption(
            carrier="UPS",
            service_name="Ground",
            cost=15.99,
            transit_days=4
        )
    ]
    
    return {
        "request": request.dict(),
        "cheapest_option": cheapest_option.dict(),
        "fastest_option": fastest_option.dict(),
        "all_options": [option.dict() for option in all_options]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    # Run the server on port 8002 (different from the main server)
    uvicorn.run(app, host="0.0.0.0", port=8002)
