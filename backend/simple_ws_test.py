import asyncio
import websockets
import json

WS_URL = "wss://shipanionws.onrender.com/ws?token=YOUR_TEST_TOKEN"

async def simple_test():
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"type": "ping"}))
        response = await ws.recv()
        print("Ping response:", response)

if __name__ == "__main__":
    asyncio.run(simple_test())
