"""
Capture WebSocket Messages

This script captures WebSocket messages between the client and server for debugging purposes.
It logs all messages to a file and can filter for specific message types.
"""
import asyncio
import json
import logging
import os
import sys
import time
import websockets
import requests
import argparse
from datetime import datetime
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

# Default configuration
DEFAULT_WS_URL = "ws://localhost:8000/ws"
DEFAULT_API_URL = "http://localhost:8000"

async def get_auth_token(api_url: str) -> str:
    """Get an authentication token from the API server."""
    try:
        response = requests.post(
            f"{api_url}/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        logger.error(f"Failed to get auth token: {str(e)}")
        raise

async def capture_messages(ws_url: str, api_url: str, output_file: str, filter_type: Optional[str] = None, duration: int = 60):
    """
    Capture WebSocket messages for a specified duration.
    
    Args:
        ws_url: The WebSocket server URL
        api_url: The API server URL
        output_file: The file to write captured messages to
        filter_type: Only capture messages of this type (if specified)
        duration: How long to capture messages for (in seconds)
    """
    try:
        # Get authentication token
        token = await get_auth_token(api_url)
        logger.info(f"Obtained auth token: {token[:10]}...")
        
        # Connect to WebSocket server
        logger.info(f"Connecting to WebSocket server at {ws_url}")
        async with websockets.connect(f"{ws_url}?token={token}") as websocket:
            logger.info("Connected to WebSocket server")
            
            # Open output file
            with open(output_file, "w") as f:
                f.write(f"# WebSocket Capture - {datetime.now().isoformat()}\n")
                f.write(f"# Server: {ws_url}\n")
                f.write(f"# Filter: {filter_type or 'None'}\n")
                f.write(f"# Duration: {duration} seconds\n\n")
                
                # Capture messages for the specified duration
                start_time = time.time()
                message_count = 0
                filtered_count = 0
                
                logger.info(f"Capturing messages for {duration} seconds...")
                
                while time.time() - start_time < duration:
                    try:
                        # Set a shorter timeout for each receive attempt
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        message_count += 1
                        
                        try:
                            # Parse the message as JSON
                            message_data = json.loads(response)
                            
                            # Check if we should filter this message
                            if filter_type is None or message_data.get("type") == filter_type:
                                filtered_count += 1
                                
                                # Write the message to the output file
                                f.write(f"--- Message {filtered_count} ({message_data.get('type')}) ---\n")
                                f.write(json.dumps(message_data, indent=2))
                                f.write("\n\n")
                                f.flush()  # Ensure it's written immediately
                                
                                # Log the message
                                logger.info(f"Captured message of type: {message_data.get('type')}")
                        except json.JSONDecodeError:
                            # Not JSON, write as-is
                            if filter_type is None:
                                filtered_count += 1
                                f.write(f"--- Message {filtered_count} (non-JSON) ---\n")
                                f.write(response)
                                f.write("\n\n")
                                f.flush()
                                
                                logger.info("Captured non-JSON message")
                    
                    except asyncio.TimeoutError:
                        # This is expected, we'll try again until the overall timeout
                        continue
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        f.write(f"# Error: {str(e)}\n\n")
                        f.flush()
                
                # Write summary
                f.write(f"# Summary: Captured {filtered_count} of {message_count} messages\n")
                logger.info(f"Capture complete. Captured {filtered_count} of {message_count} messages.")
                
    except Exception as e:
        logger.error(f"Capture failed: {str(e)}")
        raise

def main():
    """Parse command line arguments and capture WebSocket messages."""
    parser = argparse.ArgumentParser(description="Capture WebSocket messages")
    parser.add_argument("--ws-url", default=DEFAULT_WS_URL, help=f"WebSocket server URL (default: {DEFAULT_WS_URL})")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help=f"API server URL (default: {DEFAULT_API_URL})")
    parser.add_argument("--output", default=f"websocket_capture_{int(time.time())}.txt", help="Output file (default: websocket_capture_<timestamp>.txt)")
    parser.add_argument("--filter", help="Only capture messages of this type")
    parser.add_argument("--duration", type=int, default=60, help="Capture duration in seconds (default: 60)")
    args = parser.parse_args()
    
    try:
        # Run the capture
        asyncio.run(capture_messages(args.ws_url, args.api_url, args.output, args.filter, args.duration))
    except Exception as e:
        logger.error(f"Capture failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
