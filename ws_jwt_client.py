#!/usr/bin/env python3
"""
Command-line tool to send messages to a WebSocket server with JWT authentication.
"""
import asyncio
import websockets
import json
import argparse
import sys
import requests

async def get_test_token(url):
    """Get the pre-generated test token from the server."""
    try:
        print(f"Getting test token from {url}/test-token...")
        response = requests.get(f"{url}/test-token")

        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Test token obtained successfully!")
            return token_data["test_token"]
        else:
            print(f"❌ Failed to obtain test token: {response.status_code} {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error obtaining test token: {e}")
        return None

async def get_token(url, username, password):
    """Obtain a JWT token from the server."""
    try:
        print(f"Obtaining JWT token for user '{username}'...")
        response = requests.post(
            f"{url}/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token obtained successfully! Expires in {token_data['expires_in']} seconds.")
            return token_data["access_token"]
        else:
            print(f"❌ Failed to obtain token: {response.status_code} {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error obtaining token: {e}")
        return None

async def send_message(ws_url, token, message_type, message_payload, interactive=False):
    """Send a message to a WebSocket server with JWT authentication."""
    # Add token to URL
    full_url = f"{ws_url}?token={token}"

    try:
        print(f"Connecting to {full_url}...")
        async with websockets.connect(full_url) as websocket:
            print("✅ Connection successful!")

            if interactive:
                print("\n=== Interactive Mode ===")
                print("Type JSON messages and press Enter to send. Type 'exit' to quit.")
                print("Example: {\"type\":\"test\",\"payload\":{\"message\":\"Hello\"}}")

                while True:
                    user_input = input("\n> ")
                    if user_input.lower() == 'exit':
                        break

                    try:
                        # Try to parse as JSON
                        message = json.loads(user_input)
                        await websocket.send(json.dumps(message))
                        print(f"✅ Sent message: {json.dumps(message, indent=2)}")

                        # Wait for a response
                        print("Waiting for response...")
                        response = await websocket.recv()
                        print(f"✅ Received: {response}")
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON. Please try again.")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        break
            else:
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
    parser = argparse.ArgumentParser(description="Send messages to a WebSocket server with JWT authentication.")
    parser.add_argument("--server", default="http://localhost:8000", help="Server base URL (default: http://localhost:8000)")
    parser.add_argument("--ws", default="ws://localhost:8000/ws", help="WebSocket URL (default: ws://localhost:8000/ws)")
    parser.add_argument("--username", default="user", help="Username for authentication (default: user)")
    parser.add_argument("--password", default="password", help="Password for authentication (default: password)")
    parser.add_argument("--token", help="Use a specific token instead of authenticating")
    parser.add_argument("--use-test-token", action="store_true", help="Use the pre-generated test token")
    parser.add_argument("--type", default="test", help="Message type (default: test)")
    parser.add_argument("--payload", default='{"message": "Hello from JWT client"}', help="Message payload as JSON string or simple text")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    # Get token based on provided options
    token = None

    if args.token:
        # Use the provided token
        print(f"Using provided token: {args.token[:20]}...")
        token = args.token
    elif args.use_test_token:
        # Get the test token
        token = asyncio.run(get_test_token(args.server))
    else:
        # Authenticate to get a token
        token = asyncio.run(get_token(args.server, args.username, args.password))

    if not token:
        return 1

    # Send message with token
    return asyncio.run(send_message(args.ws, token, args.type, args.payload, args.interactive))

if __name__ == "__main__":
    sys.exit(main())
