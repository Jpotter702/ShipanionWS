import asyncio
import websockets
import json

WS_URL = "ws://localhost:10000/ws?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIn0.dNsYhOKsYlKZzUmOJl8Zpf9SbJ4DJxhd3AU6pO-PWko"

async def simple_test():
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({"type": "ping"}))
        response = await ws.recv()
        print("Ping response:", response)

if __name__ == "__main__":
    asyncio.run(simple_test())
