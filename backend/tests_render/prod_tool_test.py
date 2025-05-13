import asyncio
import websockets
import httpx
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Production server URLs (deployed on Render)
API_URL = "https://shipanionws.onrender.com"
WS_URL = "wss://shipanionws.onrender.com/ws"

async def get_test_token():
    """Get a static test token from the server"""
    try:
        logger.info(f"Getting test token from {API_URL}/test-token")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{API_URL}/test-token")
            resp.raise_for_status()
            token_data = resp.json()
            logger.info("Successfully retrieved test token")
            return token_data["test_token"]
    except Exception as e:
        logger.error(f"Failed to get test token: {str(e)}")
        raise

async def test_elevenlabs_tool():
    """Test the ElevenLabs integration with a client_tool_call"""
    try:
        # Get test token
        token = await get_test_token()
        
        # Connect to WebSocket
        ws_url = f"{WS_URL}?token={token}"
        logger.info(f"Connecting to WebSocket at {ws_url}")
        
        # Generate a session ID for tracking
        session_id = "test-session-001"
        
        # Connect with session ID
        async with websockets.connect(f"{ws_url}&session_id={session_id}", open_timeout=30.0) as ws:
            logger.info(f"Successfully connected with session ID: {session_id}")
            
            # Create a client_tool_call message for text-to-speech
            elevenlabs_tool_call = {
                "type": "client_tool_call",
                "client_tool_call": {
                    "tool_name": "elevenlabs_text_to_speech",
                    "tool_call_id": "test-tts-001",
                    "parameters": {
                        "text": "Hello from production testing. Testing the ElevenLabs integration.",
                        "voice_id": "21m00Tcm4TlvDq8ikWAM"  # Default voice ID
                    }
                },
                "session_id": session_id
            }
            
            # Send the message
            logger.info("Sending ElevenLabs TTS tool call...")
            await ws.send(json.dumps(elevenlabs_tool_call))
            
            # Wait for response with a longer timeout
            logger.info("Waiting for response (this may take up to 30 seconds)...")
            response = await asyncio.wait_for(ws.recv(), timeout=30.0)
            
            # Parse and log response
            response_data = json.loads(response)
            
            if response_data.get("type") == "error":
                logger.error(f"Server returned error: {response_data.get('payload', {}).get('message')}")
                return False
            else:
                logger.info(f"Received response of type: {response_data.get('type')}")
                return True
                
    except Exception as e:
        logger.error(f"Error testing ElevenLabs integration: {type(e).__name__}: {str(e)}")
        return False

async def test_contextual_update():
    """Test sending a contextual update"""
    try:
        # Get test token
        token = await get_test_token()
        
        # Connect to WebSocket
        ws_url = f"{WS_URL}?token={token}"
        logger.info(f"Connecting to WebSocket at {ws_url}")
        
        async with websockets.connect(ws_url, open_timeout=30.0) as ws:
            logger.info("Successfully connected, testing contextual_update")
            
            # Create the contextual update message
            contextual_update = {
                "type": "contextual_update",
                "payload": {
                    "message": "This is a test contextual update from production testing"
                }
            }
            
            # Send the message
            await ws.send(json.dumps(contextual_update))
            logger.info("Sent contextual_update message, waiting for response...")
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=30.0)
            logger.info(f"Received response: {response}")
            
            # Parse the response
            response_data = json.loads(response)
            
            if response_data.get("type") == "error":
                logger.error(f"Server returned error: {response_data.get('payload', {}).get('message')}")
                return False
            else:
                logger.info(f"Received response of type: {response_data.get('type')}")
                return True
                
    except Exception as e:
        logger.error(f"Error testing contextual_update: {type(e).__name__}: {str(e)}")
        return False

async def run_tests():
    """Run focused tests on production API"""
    logger.info("======== TESTING PRODUCTION SERVER TOOLS ========")
    
    # Test results dictionary
    results = {}
    
    # Test ElevenLabs integration
    logger.info("\n--- Testing ElevenLabs integration ---")
    elevenlabs_result = await test_elevenlabs_tool()
    results["elevenlabs_tool"] = "SUCCESS" if elevenlabs_result else "FAILED"
    
    # Test contextual update
    logger.info("\n--- Testing contextual update ---")
    contextual_result = await test_contextual_update()
    results["contextual_update"] = "SUCCESS" if contextual_result else "FAILED"
    
    # Print summary
    logger.info("\n======== TEST RESULTS SUMMARY ========")
    for test_name, result in results.items():
        logger.info(f"Test '{test_name}': {result}")

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed with error: {type(e).__name__}: {str(e)}")
        sys.exit(1) 