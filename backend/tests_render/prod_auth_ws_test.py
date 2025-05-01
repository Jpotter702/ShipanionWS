import asyncio
import websockets
import httpx
import json

API_URL = "https://shipanionws.onrender.com"
USERNAME = "user"         # Replace with your production username
PASSWORD = "password"     # Replace with your production password

async def get_jwt_token():
    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = await client.post(
            f"{API_URL}/token",
            data=f"username={USERNAME}&password={PASSWORD}",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

async def prod_simple_test():
    token = await get_jwt_token()
    ws_url = f"wss://shipanionws.onrender.com/ws?token={token}"
    async with websockets.connect(ws_url) as ws:
        await ws.send(json.dumps({"type": "ping"}))
        response = await ws.recv()
        print("Ping response:", response)

if __name__ == "__main__":
    asyncio.run(prod_simple_test())
