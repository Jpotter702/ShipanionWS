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

async def prod_full_test():
    token = await get_jwt_token()
    ws_url = f"wss://shipanionws.onrender.com/ws?token={token}"
    async with websockets.connect(ws_url) as ws:
        # 1. Send a simple ping message
        await ws.send(json.dumps({"type": "ping"}))
        response = await ws.recv()
        print("Ping response:", response)

        # 2. Send a get_rates message
        get_rates_msg = {
            "type": "get_rates",
            "payload": {
                "origin": {
                    "name": "Test",
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "CA",
                    "zip_code": "90210"
                },
                "destination": {
                    "name": "Test",
                    "street": "456 Test St",
                    "city": "Test City",
                    "state": "NY",
                    "zip_code": "10001"
                },
                "package": {
                    "weight": 5.0
                }
            }
        }
        await ws.send(json.dumps(get_rates_msg))
        response = await ws.recv()
        print("Get rates response:", response)

        # 3. Send a create_label message (production structure)
        create_label_msg = {
            "type": "client_tool_call",
            "client_tool_call": {
                "tool_name": "create_label",
                "tool_call_id": "prod-001",
                "parameters": {
                    "origin": {
                        "name": "Test Sender",
                        "street": "123 Test St",
                        "city": "Test City",
                        "state": "CA",
                        "zip_code": "90210"
                    },
                    "destination": {
                        "name": "Test Receiver",
                        "street": "456 Test St",
                        "city": "Test City",
                        "state": "NY",
                        "zip_code": "10001"
                    },
                    "package": {
                        "weight": 5.0,
                        "length": 10.0,
                        "width": 5.0,
                        "height": 4.0
                    },
                    "service": "ground"
                }
            }
        }
        await ws.send(json.dumps(create_label_msg))
        response = await ws.recv()
        print("Create label response:", response)

if __name__ == "__main__":
    asyncio.run(prod_full_test())
