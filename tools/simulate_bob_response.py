"""
Simulate Bob's Response

This script simulates Bob's response to a client_tool_result message.
It helps debug issues with Bob's response to shipping quotes.
"""
import json
import sys
import argparse
import logging
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

def format_quotes_for_speech(quotes: List[Dict[str, Any]]) -> str:
    """
    Format shipping quotes for speech.
    
    Args:
        quotes: List of shipping quotes
        
    Returns:
        A formatted string that Bob would likely say
    """
    if not quotes:
        return "I don't have any shipping options available at the moment."
    
    # Start with an introduction
    speech = "I've found some shipping options for you. "
    
    # Add the cheapest option first
    cheapest = min(quotes, key=lambda x: x.get("price", float("inf")))
    speech += f"The most affordable option is {cheapest['carrier']} {cheapest['service']} at ${cheapest['price']:.2f}, which would arrive in {cheapest['eta']}. "
    
    # Add other options (limit to 3 total for brevity)
    other_options = [q for q in quotes if q != cheapest][:2]  # Limit to 2 additional options
    
    if other_options:
        speech += "Other options include "
        
        for i, option in enumerate(other_options):
            speech += f"{option['carrier']} {option['service']} at ${option['price']:.2f} with delivery in {option['eta']}"
            
            if i < len(other_options) - 1:
                speech += ", and "
            else:
                speech += ". "
    
    # Add a question to prompt the user
    speech += "Which option would you prefer?"
    
    return speech

def simulate_bob_response(payload: Dict[str, Any]) -> Optional[str]:
    """
    Simulate how Bob would respond to a client_tool_result message.
    
    Args:
        payload: The client_tool_result message
        
    Returns:
        The simulated response from Bob, or None if Bob would not respond
    """
    # Check if this is a client_tool_result message
    if payload.get("type") != "client_tool_result":
        logger.warning(f"Not a client_tool_result message: {payload.get('type')}")
        return None
    
    # Check if this is an error
    if payload.get("is_error", False):
        error_message = payload.get("result", {}).get("error", "Unknown error")
        logger.warning(f"Error in client_tool_result: {error_message}")
        return f"I'm sorry, but I encountered an error while trying to get shipping quotes: {error_message}. Could you please try again with different information?"
    
    # Check if this is a shipping quotes result
    if "client_tool_call" in payload and payload["client_tool_call"].get("tool_name") == "get_shipping_quotes":
        # Get the quotes from the result
        quotes = payload.get("result", [])
        
        if not isinstance(quotes, list):
            logger.warning(f"Result is not a list: {type(quotes).__name__}")
            return "I'm sorry, but I received an unexpected format for the shipping quotes. Could you please try again?"
        
        # Format the quotes for speech
        return format_quotes_for_speech(quotes)
    
    # If we get here, Bob probably wouldn't respond
    logger.warning("Bob would not respond to this message")
    return None

def main():
    """Parse command line arguments and simulate Bob's response."""
    parser = argparse.ArgumentParser(description="Simulate Bob's response to a client_tool_result message")
    parser.add_argument("file", nargs="?", help="JSON file containing the client_tool_result message (if not provided, reads from stdin)")
    args = parser.parse_args()
    
    try:
        # Read JSON from file or stdin
        if args.file:
            with open(args.file, "r") as f:
                payload = json.load(f)
        else:
            payload = json.load(sys.stdin)
        
        # Simulate Bob's response
        response = simulate_bob_response(payload)
        
        # Print the response
        if response:
            print("\n=== BOB'S SIMULATED RESPONSE ===")
            print(response)
            print("================================\n")
        else:
            print("\nBob would not respond to this message.\n")
            sys.exit(1)
    
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
