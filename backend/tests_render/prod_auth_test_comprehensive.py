import asyncio
import websockets
import httpx
import json
import logging
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production API URL
API_URL = "https://shipanionws.onrender.com"
WS_URL = "wss://shipanionws.onrender.com/ws"
USERNAME = "user"
PASSWORD = "password"

# Set timeout values
HTTP_TIMEOUT = 10.0  # seconds
WS_TIMEOUT = 10.0    # seconds

async def check_server_availability():
    """Check if the server is reachable"""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            # Try to reach the server root endpoint
            resp = await client.get(API_URL)
            if resp.status_code == 200 or resp.status_code == 404:  # 404 is OK - endpoint exists but not found
                logger.info(f"✅ Server is reachable (status: {resp.status_code})")
                return True
            else:
                logger.warning(f"⚠️ Server returned status code {resp.status_code}")
                return False
    except Exception as e:
        logger.error(f"❌ Server is not reachable: {str(e)}")
        return False

async def get_jwt_token():
    """Get a valid JWT token by authenticating with username/password"""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            logger.info(f"Requesting JWT token from {API_URL}/token")
            resp = await client.post(
                f"{API_URL}/token",
                data={"username": USERNAME, "password": PASSWORD},
                headers=headers,
            )
            resp.raise_for_status()
            token_data = resp.json()
            logger.info(f"Token expires in: {token_data.get('expires_in')} seconds")
            return token_data["access_token"]
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to get JWT token - HTTP Error: {e.response.status_code} {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Failed to get JWT token - Request Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to get JWT token - Unexpected Error: {str(e)}")
        raise

async def get_test_token():
    """Get the static test token from the /test-token endpoint"""
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            logger.info(f"Requesting test token from {API_URL}/test-token")
            resp = await client.get(f"{API_URL}/test-token")
            resp.raise_for_status()
            return resp.json()["test_token"]
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to get test token - HTTP Error: {e.response.status_code} {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Failed to get test token - Request Error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to get test token - Unexpected Error: {str(e)}")
        raise

async def test_valid_token():
    """Test authentication with a valid JWT token"""
    try:
        token = await get_jwt_token()
        logger.info("Obtained valid JWT token")
        
        ws_url = f"{WS_URL}?token={token}"
        logger.info(f"Connecting to WebSocket with valid token")
        
        # Use a timeout for the WebSocket connection
        async with websockets.connect(ws_url, open_timeout=WS_TIMEOUT) as ws:
            await ws.send(json.dumps({"type": "ping"}))
            response = await asyncio.wait_for(ws.recv(), timeout=WS_TIMEOUT)
            response_data = json.loads(response)
            
            logger.info(f"Received response: {response}")
            
            if response_data.get("type") == "pong":
                logger.info("✅ VALID TOKEN TEST: SUCCESS - Server authenticated and responded to ping")
                return True
            else:
                logger.error(f"❌ VALID TOKEN TEST: FAILED - Unexpected response type: {response_data.get('type')}")
                return False
                
    except asyncio.TimeoutError:
        logger.error(f"❌ VALID TOKEN TEST: FAILED - Connection or response timed out")
        return False
    except Exception as e:
        logger.error(f"❌ VALID TOKEN TEST: FAILED - {type(e).__name__}: {str(e)}")
        return False

async def test_invalid_token():
    """Test authentication with an invalid token"""
    try:
        invalid_token = "invalid.token.value"
        ws_url = f"{WS_URL}?token={invalid_token}"
        logger.info(f"Connecting to WebSocket with invalid token")
        
        try:
            # Use a timeout for the WebSocket connection
            async with websockets.connect(ws_url, open_timeout=WS_TIMEOUT) as ws:
                await ws.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(ws.recv(), timeout=WS_TIMEOUT)
                logger.error(f"❌ INVALID TOKEN TEST: FAILED - Server accepted invalid token: {response}")
                return False
        except websockets.exceptions.ConnectionClosedError as e:
            logger.info(f"✅ INVALID TOKEN TEST: SUCCESS - Server correctly rejected invalid token: {str(e)}")
            return True
        except asyncio.TimeoutError:
            logger.error(f"❌ INVALID TOKEN TEST: FAILED - Connection or response timed out")
            return False
            
    except Exception as e:
        if "403" in str(e) or "401" in str(e) or "authentication" in str(e).lower():
            logger.info(f"✅ INVALID TOKEN TEST: SUCCESS - Server correctly rejected invalid token: {str(e)}")
            return True
        else:
            logger.error(f"❓ INVALID TOKEN TEST: INCONCLUSIVE - {type(e).__name__}: {str(e)}")
            return False

async def test_test_token():
    """Test authentication with the static test token"""
    try:
        test_token = await get_test_token()
        logger.info("Obtained test token")
        
        ws_url = f"{WS_URL}?token={test_token}"
        logger.info(f"Connecting to WebSocket with test token")
        
        # Use a timeout for the WebSocket connection
        async with websockets.connect(ws_url, open_timeout=WS_TIMEOUT) as ws:
            await ws.send(json.dumps({"type": "ping"}))
            response = await asyncio.wait_for(ws.recv(), timeout=WS_TIMEOUT)
            response_data = json.loads(response)
            
            logger.info(f"Received response: {response}")
            
            if response_data.get("type") == "pong":
                logger.info("✅ TEST TOKEN TEST: SUCCESS - Server authenticated and responded to ping")
                return True
            else:
                logger.error(f"❌ TEST TOKEN TEST: FAILED - Unexpected response type: {response_data.get('type')}")
                return False
                
    except asyncio.TimeoutError:
        logger.error(f"❌ TEST TOKEN TEST: FAILED - Connection or response timed out")
        return False
    except Exception as e:
        logger.error(f"❌ TEST TOKEN TEST: FAILED - {type(e).__name__}: {str(e)}")
        return False

async def run_all_tests():
    """Run all authentication tests"""
    logger.info("======== STARTING PRODUCTION AUTHENTICATION TESTS ========")
    
    # First, check if the server is reachable
    server_available = await check_server_availability()
    if not server_available:
        logger.error("❌ SERVER NOT REACHABLE - Cannot proceed with tests")
        return
    
    # Test with valid JWT token
    valid_result = await test_valid_token()
    
    # Test with invalid token
    invalid_result = await test_invalid_token()
    
    # Test with test token
    test_token_result = await test_test_token()
    
    # Summary
    logger.info("\n======== TEST RESULTS SUMMARY ========")
    logger.info(f"Valid JWT token test: {'PASSED' if valid_result else 'FAILED'}")
    logger.info(f"Invalid token test: {'PASSED' if invalid_result else 'FAILED'}")
    logger.info(f"Test token test: {'PASSED' if test_token_result else 'FAILED'}")
    
    if valid_result and invalid_result and test_token_result:
        logger.info("✅ ALL TESTS PASSED - Production authentication is working correctly!")
    else:
        logger.info("❌ SOME TESTS FAILED - Check logs above for details.")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 