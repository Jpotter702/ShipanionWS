#!/usr/bin/env python3
"""
Test script to verify how the WebSocket server handles unauthenticated connections.
"""
import asyncio
import websockets
import sys

# The WebSocket server URL
WS_URL = "ws://localhost:8000/ws"

async def test_no_token():
    """Test connection without a token."""
    try:
        print(f"Connecting to {WS_URL} without a token...")
        async with websockets.connect(WS_URL) as websocket:
            print("❌ Connection should have failed without token!")
            return False
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"✅ Connection correctly rejected with code {e.code}: {e.reason}")
        return True
    except Exception as e:
        print(f"❓ Unexpected error: {e}")
        return False

async def test_invalid_token():
    """Test connection with an invalid token."""
    try:
        url = f"{WS_URL}?token=invalid-token"
        print(f"Connecting to {url} with invalid token...")
        async with websockets.connect(url) as websocket:
            print("❌ Connection should have failed with invalid token!")
            return False
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"✅ Connection correctly rejected with code {e.code}: {e.reason}")
        return True
    except Exception as e:
        print(f"❓ Unexpected error: {e}")
        return False

async def test_empty_token():
    """Test connection with an empty token."""
    try:
        url = f"{WS_URL}?token="
        print(f"Connecting to {url} with empty token...")
        async with websockets.connect(url) as websocket:
            print("❌ Connection should have failed with empty token!")
            return False
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"✅ Connection correctly rejected with code {e.code}: {e.reason}")
        return True
    except Exception as e:
        print(f"❓ Unexpected error: {e}")
        return False

async def main():
    """Run all tests."""
    print("=== Testing Unauthenticated WebSocket Connections ===\n")
    
    # Make sure the server is running before testing
    print("Make sure the FastAPI server is running before continuing.")
    print("You can start it with: uvicorn backend.main:app --reload\n")
    
    # Test with no token
    no_token_result = await test_no_token()
    print()
    
    # Test with invalid token
    invalid_token_result = await test_invalid_token()
    print()
    
    # Test with empty token
    empty_token_result = await test_empty_token()
    print()
    
    # Summary
    print("=== Test Results ===")
    print(f"No token test: {'PASSED' if no_token_result else 'FAILED'}")
    print(f"Invalid token test: {'PASSED' if invalid_token_result else 'FAILED'}")
    print(f"Empty token test: {'PASSED' if empty_token_result else 'FAILED'}")
    
    if no_token_result and invalid_token_result and empty_token_result:
        print("\n✅ All tests passed! The server correctly handles unauthenticated connections.")
        return 0
    else:
        print("\n❌ Some tests failed. The server may not be handling unauthenticated connections correctly.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
