#!/usr/bin/env python3
"""
Test script for WebSocket authentication.
This script attempts to connect to the WebSocket server with and without a valid token.
"""
import asyncio
import websockets
import json
import sys

# The WebSocket server URL
WS_URL = "ws://localhost:8000/ws"

# The authentication token (should match the one in backend/config.py)
AUTH_TOKEN = "your-secure-token-here"

async def test_with_valid_token():
    """Test connection with a valid token."""
    try:
        url = f"{WS_URL}?token={AUTH_TOKEN}"
        print(f"Connecting to {url} with valid token...")
        
        async with websockets.connect(url) as websocket:
            print("✅ Connection successful with valid token!")
            
            # Send a test message
            message = {
                "type": "test",
                "payload": {"message": "Hello from test script"}
            }
            await websocket.send(json.dumps(message))
            print(f"Sent message: {message}")
            
            # Wait for a response (optional)
            response = await websocket.recv()
            print(f"Received response: {response}")
            
            # Close the connection
            await websocket.close()
            
    except Exception as e:
        print(f"❌ Error with valid token: {e}")
        return False
    
    return True

async def test_with_invalid_token():
    """Test connection with an invalid token."""
    try:
        url = f"{WS_URL}?token=invalid-token"
        print(f"Connecting to {url} with invalid token...")
        
        async with websockets.connect(url) as websocket:
            print("❌ Connection should have failed with invalid token!")
            return False
            
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 1008:  # Policy Violation
            print(f"✅ Connection correctly rejected with code 1008: {e.reason}")
            return True
        else:
            print(f"❓ Connection closed with unexpected code: {e.code}, reason: {e.reason}")
            return False
    except Exception as e:
        print(f"❓ Unexpected error with invalid token: {e}")
        return False

async def test_without_token():
    """Test connection without a token."""
    try:
        print(f"Connecting to {WS_URL} without token...")
        
        async with websockets.connect(WS_URL) as websocket:
            print("❌ Connection should have failed without token!")
            return False
            
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 1008:  # Policy Violation
            print(f"✅ Connection correctly rejected with code 1008: {e.reason}")
            return True
        else:
            print(f"❓ Connection closed with unexpected code: {e.code}, reason: {e.reason}")
            return False
    except Exception as e:
        print(f"❓ Unexpected error without token: {e}")
        return False

async def main():
    """Run all tests."""
    print("=== Testing WebSocket Authentication ===\n")
    
    # Make sure the server is running before testing
    print("Make sure the FastAPI server is running before continuing.")
    print("You can start it with: uvicorn backend.main:app --reload\n")
    
    valid_token_result = await test_with_valid_token()
    print()
    
    invalid_token_result = await test_with_invalid_token()
    print()
    
    no_token_result = await test_without_token()
    print()
    
    # Summary
    print("=== Test Results ===")
    print(f"Valid token test: {'PASSED' if valid_token_result else 'FAILED'}")
    print(f"Invalid token test: {'PASSED' if invalid_token_result else 'FAILED'}")
    print(f"No token test: {'PASSED' if no_token_result else 'FAILED'}")
    
    if valid_token_result and invalid_token_result and no_token_result:
        print("\n✅ All tests passed! WebSocket authentication is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
