"""
Test Bob Speaks Quote Aloud

This script sends a test quote via WebSocket using `client_tool_result` and checks if Bob speaks
the price and carrier clearly. It provides guidance on adjusting the tool prompt in Agent Studio if needed.
"""
import asyncio
import json
import logging
import os
import sys
import time
import websockets
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Test configuration
WS_SERVER_URL = os.environ.get("WS_SERVER_URL", "ws://localhost:8000/ws")
API_SERVER_URL = os.environ.get("API_SERVER_URL", "http://localhost:8000")

# Test data - This is the client_tool_result message that will be sent to Bob
TEST_QUOTE_RESULT = {
    "type": "client_tool_result",
    "tool_call_id": f"test-quotes-{int(time.time())}",
    "result": [
        {
            "carrier": "UPS",
            "service": "Ground",
            "price": 12.99,
            "eta": "3-5 business days"
        },
        {
            "carrier": "USPS",
            "service": "Priority Mail",
            "price": 9.99,
            "eta": "2-3 business days"
        },
        {
            "carrier": "FedEx",
            "service": "Express Saver",
            "price": 14.99,
            "eta": "1-2 business days"
        }
    ],
    "is_error": false,
    "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": f"test-quotes-{int(time.time())}",
        "parameters": {
            "from_zip": "90210",
            "to_zip": "10001",
            "weight": 5.0,
            "dimensions": "12x10x8"
        }
    }
}

async def get_auth_token() -> str:
    """Get an authentication token from the API server."""
    try:
        response = requests.post(
            f"{API_SERVER_URL}/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        raise

async def test_bob_speaks_quote():
    """
    Test that Bob speaks the quote aloud when receiving a client_tool_result message.
    
    This test:
    1. Connects to the WebSocket server
    2. Sends a client_tool_result message with shipping quotes
    3. Waits for any responses (for logging purposes)
    4. Provides instructions for manual verification
    """
    try:
        # Get authentication token
        token = await get_auth_token()
        logger.info(f"Obtained auth token: {token[:10]}...")
        
        # Connect to WebSocket server
        logger.info(f"Connecting to WebSocket server at {WS_SERVER_URL}")
        async with websockets.connect(f"{WS_SERVER_URL}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Fix the tool_call_id to be the same in both places
            tool_call_id = f"test-quotes-{int(time.time())}"
            TEST_QUOTE_RESULT["tool_call_id"] = tool_call_id
            TEST_QUOTE_RESULT["client_tool_call"]["tool_call_id"] = tool_call_id
            
            # Send the client_tool_result message
            logger.info(f"Sending client_tool_result message with quotes...")
            await websocket.send(json.dumps(TEST_QUOTE_RESULT))
            
            # Print the expected response from Bob
            logger.info("\n=== EXPECTED BOB RESPONSE ===")
            logger.info("Bob should speak something like:")
            logger.info("I've found some shipping options for you. The most affordable option is USPS Priority Mail at $9.99, which would arrive in 2-3 business days.")
            logger.info("Other options include UPS Ground at $12.99 with delivery in 3-5 business days, and FedEx Express Saver at $14.99 with delivery in 1-2 business days.")
            logger.info("Which option would you prefer?")
            logger.info("===========================\n")
            
            # Wait for any responses (for logging purposes)
            logger.info("Waiting for any responses (for 10 seconds)...")
            start_time = time.time()
            
            while time.time() - start_time < 10:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    logger.info(f"Received response: {response}")
                except asyncio.TimeoutError:
                    # This is expected, we'll try again until the timeout
                    continue
                except Exception as e:
                    logger.error(f"Error receiving response: {str(e)}")
            
            # Provide instructions for manual verification
            logger.info("\n=== MANUAL VERIFICATION INSTRUCTIONS ===")
            logger.info("1. Did Bob speak the quote aloud?")
            logger.info("2. Did Bob clearly mention the carrier names (UPS, USPS, FedEx)?")
            logger.info("3. Did Bob clearly mention the prices ($9.99, $12.99, $14.99)?")
            logger.info("4. Did Bob mention the delivery times?")
            logger.info("5. Did Bob ask which option the user would prefer?")
            logger.info("=======================================\n")
            
            # Provide guidance on adjusting the tool prompt in Agent Studio
            logger.info("\n=== ADJUSTING TOOL PROMPT IN AGENT STUDIO ===")
            logger.info("If Bob did not speak the quote clearly, you may need to adjust the tool prompt in Agent Studio:")
            logger.info("1. Go to Agent Studio and find the 'get_shipping_quotes' tool")
            logger.info("2. Edit the tool description to be more explicit about how to present the quotes")
            logger.info("3. Add examples of good responses in the tool description")
            logger.info("4. Consider adding instructions like:")
            logger.info("   - 'Always mention the carrier name, service type, price, and delivery time for each option'")
            logger.info("   - 'Present the cheapest option first, then list other options'")
            logger.info("   - 'Ask the user which option they prefer after presenting the quotes'")
            logger.info("5. Save the changes and test again")
            logger.info("===========================================\n")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

async def main():
    """Run the test."""
    logger.info("Starting test to verify Bob speaks quote aloud")
    
    try:
        await test_bob_speaks_quote()
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
