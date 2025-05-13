import asyncio
import websockets
import httpx
import json
import logging
import time
import sys
import getpass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production server URLs (deployed on Render)
API_URL = "https://shipanionws.onrender.com"
WS_URL = "wss://shipanionws.onrender.com/ws"

# Prompt for credentials
def get_credentials():
    print("\n--- Production Server Authentication ---")
    print(f"Server: {API_URL}")
    username = input("Enter username (default: user): ") or "user"
    password = getpass.getpass("Enter password (default: password): ") or "password"
    return username, password

USERNAME, PASSWORD = get_credentials()

async def test_server_availability():
    """Test if the production server is reachable"""
    try:
        logger.info(f"Testing if server is reachable at {API_URL}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{API_URL}/docs")
            logger.info(f"Server responded with status code: {resp.status_code}")
            return True
    except Exception as e:
        logger.error(f"Failed to reach server: {str(e)}")
        return False

async def get_jwt_token():
    """Get a JWT token from the production server"""
    logger.info(f"Requesting JWT token from {API_URL}/token")
    
    # Add a retry mechanism as production servers may have more latency
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                logger.info(f"Attempt {attempt}: Authenticating with username/password")
                
                resp = await client.post(
                    f"{API_URL}/token",
                    data={"username": USERNAME, "password": PASSWORD},
                    headers=headers,
                )
                resp.raise_for_status()
                token_data = resp.json()
                logger.info(f"Token received, expires in: {token_data.get('expires_in', 'unknown')} seconds")
                return token_data["access_token"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during authentication: {e.response.status_code} - {e.response.text}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                raise
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                raise
    
    raise Exception("Failed to obtain JWT token after maximum retries")

async def get_test_token():
    """Try to get a static test token from the server"""
    try:
        logger.info(f"Attempting to get test token from {API_URL}/test-token")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{API_URL}/test-token")
            resp.raise_for_status()
            token_data = resp.json()
            logger.info("Successfully retrieved test token")
            return token_data["test_token"]
    except Exception as e:
        logger.error(f"Failed to get test token: {str(e)}")
        return None

async def test_websocket_auth():
    """Test WebSocket authentication against production server"""
    if not await test_server_availability():
        logger.error("Cannot proceed - production server is not reachable")
        return False
    
    try:
        # First try to get a JWT token
        try:
            token = await get_jwt_token()
            logger.info(f"Successfully obtained JWT token: {token[:10]}...")
        except Exception as e:
            logger.warning(f"JWT authentication failed, trying test token")
            token = await get_test_token()
            
            if not token:
                logger.error("Failed to obtain any authentication token")
                return False
        
        # Connect to WebSocket with the token
        ws_url = f"{WS_URL}?token={token}"
        logger.info(f"Connecting to WebSocket at {ws_url}")
        
        # Use longer timeouts for production testing
        async with websockets.connect(ws_url, open_timeout=30.0) as ws:
            logger.info("Successfully connected to WebSocket")
            
            # Send a ping message
            await ws.send(json.dumps({"type": "ping"}))
            logger.info("Sent ping message, waiting for response...")
            
            # Wait for response with timeout
            response = await asyncio.wait_for(ws.recv(), timeout=30.0)
            logger.info(f"Received response: {response}")
            
            # Parse and validate response
            response_data = json.loads(response)
            if response_data.get("type") == "pong":
                logger.info("✅ PRODUCTION AUTH TEST: SUCCESS - Server authenticated and responded to ping")
                return True
            else:
                logger.error(f"❌ PRODUCTION AUTH TEST: FAILED - Unexpected response type: {response_data.get('type')}")
                return False
    except asyncio.TimeoutError:
        logger.error("❌ PRODUCTION AUTH TEST: FAILED - Connection or response timed out")
        return False
    except Exception as e:
        logger.error(f"❌ PRODUCTION AUTH TEST: FAILED - Error: {type(e).__name__}: {str(e)}")
        return False

async def test_invalid_token():
    """Test server rejection of invalid token"""
    if not await test_server_availability():
        logger.error("Cannot proceed - production server is not reachable")
        return False
    
    try:
        invalid_token = "invalid.token.value"
        ws_url = f"{WS_URL}?token={invalid_token}"
        logger.info(f"Testing with invalid token: Connecting to {ws_url}")
        
        try:
            async with websockets.connect(ws_url, open_timeout=30.0) as ws:
                await ws.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                logger.error(f"❌ INVALID TOKEN TEST: FAILED - Server accepted invalid token: {response}")
                return False
        except Exception as e:
            # Check for common authentication rejection errors
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["403", "401", "authentication", "unauthorized", "forbidden", "closed", "rejected"]):
                logger.info(f"✅ INVALID TOKEN TEST: SUCCESS - Server correctly rejected invalid token: {str(e)}")
                return True
            else:
                logger.error(f"❓ INVALID TOKEN TEST: INCONCLUSIVE - Error: {type(e).__name__}: {str(e)}")
                return False
    except Exception as e:
        logger.error(f"❌ INVALID TOKEN TEST: FAILED - Error: {type(e).__name__}: {str(e)}")
        return False

async def run_all_tests():
    """Run all production tests"""
    logger.info("======== PRODUCTION SERVER AUTHENTICATION TESTS ========")
    logger.info(f"Testing server at {API_URL}")
    
    # Test with valid JWT token
    valid_result = await test_websocket_auth()
    
    if valid_result:
        # Only test invalid token if valid token succeeds
        invalid_result = await test_invalid_token()
    else:
        logger.warning("Skipping invalid token test due to failed authentication test")
        invalid_result = False
    
    # Summary
    logger.info("\n======== TEST RESULTS SUMMARY ========")
    logger.info(f"Valid token authentication: {'PASSED' if valid_result else 'FAILED'}")
    logger.info(f"Invalid token rejection: {'PASSED' if invalid_result else 'FAILED or SKIPPED'}")
    
    if valid_result and invalid_result:
        logger.info("✅ ALL TESTS PASSED - Production server authentication is working correctly!")
    else:
        logger.info("❌ SOME TESTS FAILED - Check logs above for details.")

if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {type(e).__name__}: {str(e)}")
        sys.exit(1) 