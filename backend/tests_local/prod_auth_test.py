import asyncio
import websockets
import httpx
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Local server URLs that mimic production behavior
API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
USERNAME = "user"
PASSWORD = "password"

async def get_jwt_token():
    """Get a production-style JWT token through the /token endpoint"""
    logger.info(f"Requesting JWT token from {API_URL}/token")
    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = await client.post(
            f"{API_URL}/token",
            data={"username": USERNAME, "password": PASSWORD},
            headers=headers,
        )
        resp.raise_for_status()
        token_data = resp.json()
        logger.info(f"Token received, expires in: {token_data.get('expires_in')} seconds")
        return token_data["access_token"]

async def test_production_auth():
    """Test WebSocket authentication using a production-style JWT token"""
    # Get a real JWT token
    token = await get_jwt_token()
    logger.info(f"Obtained JWT token: {token[:10]}...")
    
    # Connect to WebSocket with the token
    ws_url = f"{WS_URL}?token={token}"
    logger.info(f"Connecting to WebSocket with JWT token")
    
    async with websockets.connect(ws_url) as ws:
        # Send a simple ping
        await ws.send(json.dumps({"type": "ping"}))
        response = await ws.recv()
        response_data = json.loads(response)
        
        logger.info(f"Received response: {response}")
        
        if response_data.get("type") == "pong":
            logger.info("✅ PRODUCTION AUTH TEST: SUCCESS - Server authenticated with JWT token")
        else:
            logger.error(f"❌ PRODUCTION AUTH TEST: FAILED - Unexpected response: {response}")

if __name__ == "__main__":
    asyncio.run(test_production_auth()) 