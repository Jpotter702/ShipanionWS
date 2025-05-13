import asyncio
import websockets
import httpx
import json

API_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"
USERNAME = "user"
PASSWORD = "password"

async def get_jwt_token():
    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = await client.post(
            f"{API_URL}/token",
            data={"username": USERNAME, "password": PASSWORD},
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

async def test_ws_auth():
    # Test with valid token
    try:
        token = await get_jwt_token()
        ws_url = f"{WS_URL}?token={token}"
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"type": "ping"}))
            response = await ws.recv()
            print("[VALID TOKEN] Success! Ping response:", response)
    except Exception as e:
        print("[VALID TOKEN] Failed:", e)

    # Test with invalid token
    try:
        ws_url = f"{WS_URL}?token=invalidtoken"
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"type": "ping"}))
            response = await ws.recv()
            print("[INVALID TOKEN] Unexpected success! Response:", response)
    except Exception as e:
        print("[INVALID TOKEN] Correctly failed:", e)

if __name__ == "__main__":
    asyncio.run(test_ws_auth()) 
