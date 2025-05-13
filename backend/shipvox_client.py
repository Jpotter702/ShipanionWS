"""
Mock ShipVox API Client

This is a placeholder implementation for the ShipVox API client.
In a production environment, this would be replaced with actual API calls.
"""
import logging
import asyncio
import random
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShipVoxClient:
    """Mock client for the ShipVox API"""
    
    def __init__(self):
        """Initialize the ShipVox client"""
        logger.info("Initializing mock ShipVox client")
        
        # Mock carrier list
        self.carriers = ["FedEx", "UPS", "USPS", "DHL"]
        
        # Mock service types by carrier
        self.service_types = {
            "FedEx": ["Ground", "2Day", "Priority Overnight"],
            "UPS": ["Ground", "3 Day Select", "2nd Day Air", "Next Day Air"],
            "USPS": ["First Class", "Priority Mail", "Priority Mail Express"],
            "DHL": ["Express", "Ground", "eCommerce"]
        }
    
    async def get_rates(self, rate_request: Dict[str, Any], timeout_seconds: float = 10.0) -> Dict[str, Any]:
        """
        Get shipping rates for a given request.
        
        Args:
            rate_request: Dictionary containing rate request parameters
            timeout_seconds: Timeout for the API call
            
        Returns:
            Dictionary containing shipping rate quotes
        """
        # Log the request
        logger.info(f"Mock ShipVox API: Getting rates for request: {rate_request}")
        
        # Simulate API latency (between 0.5 and 1.5 seconds)
        delay = random.uniform(0.5, 1.5)
        logger.info(f"Simulating API latency: {delay:.2f} seconds")
        await asyncio.sleep(delay)
        
        # Extract request parameters
        origin_zip = rate_request.get("origin_zip", "00000")
        destination_zip = rate_request.get("destination_zip", "99999")
        weight = rate_request.get("weight", 1.0)
        
        # Generate mock quotes
        quotes = self._generate_mock_quotes(origin_zip, destination_zip, weight)
        
        # Create response
        response = {
            "quotes": quotes,
            "origin_zip": origin_zip,
            "destination_zip": destination_zip,
            "weight": weight,
            "currency": "USD",
            "request_id": rate_request.get("requestId", "mock-request-id")
        }
        
        return response
    
    def _generate_mock_quotes(self, origin_zip: str, destination_zip: str, weight: float) -> List[Dict[str, Any]]:
        """Generate mock shipping quotes"""
        quotes = []
        
        # Calculate a base distance factor based on ZIP codes
        # This is just for simulation purposes
        distance_factor = abs(int(origin_zip[:1]) - int(destination_zip[:1])) / 10.0 + 0.5
        
        # Generate quotes for each carrier and service type
        for carrier in self.carriers:
            for service in self.service_types[carrier]:
                # Calculate a mock rate based on weight and distance
                base_rate = 5.0 + (weight * 2.0) + (distance_factor * 5.0)
                
                # Add carrier/service specific adjustments
                if carrier == "FedEx":
                    if service == "Ground":
                        rate = base_rate * 1.0
                        transit_days = int(3 + distance_factor * 2)
                    elif service == "2Day":
                        rate = base_rate * 1.5
                        transit_days = 2
                    else:  # Priority Overnight
                        rate = base_rate * 2.2
                        transit_days = 1
                elif carrier == "UPS":
                    if service == "Ground":
                        rate = base_rate * 1.1
                        transit_days = int(3 + distance_factor * 2)
                    elif service == "3 Day Select":
                        rate = base_rate * 1.3
                        transit_days = 3
                    elif service == "2nd Day Air":
                        rate = base_rate * 1.7
                        transit_days = 2
                    else:  # Next Day Air
                        rate = base_rate * 2.3
                        transit_days = 1
                elif carrier == "USPS":
                    if service == "First Class":
                        # USPS First Class has weight limits
                        if weight <= 13.0:
                            rate = base_rate * 0.8
                            transit_days = int(3 + distance_factor * 2)
                        else:
                            # Skip this service for heavy packages
                            continue
                    elif service == "Priority Mail":
                        rate = base_rate * 0.9
                        transit_days = int(2 + distance_factor)
                    else:  # Priority Mail Express
                        rate = base_rate * 1.6
                        transit_days = 1
                else:  # DHL
                    if service == "Express":
                        rate = base_rate * 2.0
                        transit_days = 1
                    elif service == "Ground":
                        rate = base_rate * 1.1
                        transit_days = int(4 + distance_factor * 2)
                    else:  # eCommerce
                        rate = base_rate * 0.85
                        transit_days = int(4 + distance_factor * 3)
                
                # Add some randomness
                rate = rate * random.uniform(0.95, 1.05)
                
                # Format the rate
                rate = round(rate, 2)
                
                # Add the quote
                quotes.append({
                    "carrier": carrier,
                    "service_name": service,
                    "cost": rate,
                    "currency": "USD",
                    "transit_days": transit_days,
                    "delivery_date": f"2025-05-{12 + transit_days}",  # Mock date
                    "package_type": rate_request.get("package_type", "custom_box")
                })
        
        # Sort by cost
        quotes.sort(key=lambda q: q["cost"])
        
        return quotes
