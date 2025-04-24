#!/usr/bin/env python3
"""
Command-line tool to send a message to a WebSocket server with authentication.
"""
import asyncio
import websockets
import json
import argparse
import sys

async def send_message(url, token, message_type, message_payload):
    """Send a message to a WebSocket server with authentication."""
    # Add token to URL if provided
    full_url = f"{url}?token={token}" if token else url
    
    try:
        print(f"Connecting to {full_url}...")
        async with websockets.connect(full_url) as websocket:
            print("✅ Connection successful!")
            
            # Create the message
            message = {
                "type": message_type,
                "payload": json.loads(message_payload) if message_payload.startswith('{') else {"message": message_payload}
            }
            
            # Send the message
            await websocket.send(json.dumps(message))
            print(f"✅ Sent message: {json.dumps(message, indent=2)}")
            
            # Wait for a response
            print("Waiting for response...")
            response = await websocket.recv()
            print(f"✅ Received response: {response}")
            
            # Close the connection
            await websocket.close()
            print("Connection closed.")
            
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed with code {e.code}: {e.reason}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def main():
    """Parse arguments and run the WebSocket client."""
    parser = argparse.ArgumentParser(description="Send a message to a WebSocket server with authentication.")
    parser.add_argument("--url", default="ws://localhost:8000/ws", help="WebSocket server URL (default: ws://localhost:8000/ws)")
    parser.add_argument("--token", default="your-secure-token-here", help="Authentication token (default: your-secure-token-here)")
    parser.add_argument("--type", default="test", help="Message type (default: test)")
    parser.add_argument("--payload", default='{"message": "Hello from command line"}', help="Message payload as JSON string or simple text (default: {\"message\": \"Hello from command line\"})")
    
    args = parser.parse_args()
    
    return asyncio.run(send_message(args.url, args.token, args.type, args.payload))

if __name__ == "__main__":
    sys.exit(main())
