#!/usr/bin/env python3
"""
Test script for JWT-based WebSocket authentication.
This script obtains a JWT token and then connects to the WebSocket server.
"""
import asyncio
import websockets
import json
import sys
import requests
import time

# The server base URL
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

# Test credentials (should match those in backend/security.py)
USERNAME = "user"
PASSWORD = "password"

async def get_token():
    """Obtain a JWT token from the server."""
    try:
        print(f"Obtaining JWT token for user '{USERNAME}'...")
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": USERNAME, "password": PASSWORD},
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

async def test_with_valid_token(token):
    """Test connection with a valid JWT token."""
    try:
        url = f"{WS_URL}?token={token}"
        print(f"Connecting to WebSocket with valid JWT token...")
        
        async with websockets.connect(url) as websocket:
            print("✅ Connection successful with valid JWT token!")
            
            # Send a test message
            message = {
                "type": "test",
                "payload": {"message": "Hello with JWT authentication"}
            }
            await websocket.send(json.dumps(message))
            print(f"Sent message: {message}")
            
            # Wait for a response
            response = await websocket.recv()
            print(f"Received response: {response}")
            
            # Close the connection
            await websocket.close()
            
    except Exception as e:
        print(f"❌ Error with valid token: {e}")
        return False
    
    return True

async def test_with_invalid_token():
    """Test connection with an invalid JWT token."""
    try:
        url = f"{WS_URL}?token=invalid.jwt.token"
        print(f"Connecting to WebSocket with invalid JWT token...")
        
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

async def test_with_expired_token():
    """Test connection with an expired JWT token (simulated)."""
    print("Note: This test would require waiting for token expiration or manipulating the token.")
    print("Skipping actual test, but in a real scenario, the server should reject expired tokens.")
    return True

async def main():
    """Run all tests."""
    print("=== Testing JWT-based WebSocket Authentication ===\n")
    
    # Make sure the server is running before testing
    print("Make sure the FastAPI server is running before continuing.")
    print("You can start it with: uvicorn backend.main:app --reload\n")
    
    # Get a valid token
    token = await get_token()
    if not token:
        print("❌ Cannot proceed with tests without a valid token.")
        return 1
    
    print()
    
    # Test with valid token
    valid_token_result = await test_with_valid_token(token)
    print()
    
    # Test with invalid token
    invalid_token_result = await test_with_invalid_token()
    print()
    
    # Test with expired token (simulated)
    expired_token_result = await test_with_expired_token()
    print()
    
    # Summary
    print("=== Test Results ===")
    print(f"Valid JWT token test: {'PASSED' if valid_token_result else 'FAILED'}")
    print(f"Invalid JWT token test: {'PASSED' if invalid_token_result else 'FAILED'}")
    print(f"Expired JWT token test: {'SIMULATED' if expired_token_result else 'FAILED'}")
    
    if valid_token_result and invalid_token_result:
        print("\n✅ Tests passed! JWT-based WebSocket authentication is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
