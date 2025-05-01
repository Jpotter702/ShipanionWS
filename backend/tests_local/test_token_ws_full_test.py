import asyncio
import websockets
import json

WS_URL = "ws://localhost:10000/ws?token=YOUR_TEST_TOKEN"

async def test_token_full():
    async with websockets.connect(WS_URL) as ws:
        # 1. Ping
        await ws.send(json.dumps({"type": "ping"}))
        response = await ws.recv()
        print("Ping response:", response)

        # 2. Get rates
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

        # 3. Create label (correct structure)
        create_label_msg = {
            "type": "client_tool_call",
            "client_tool_call": {
                "tool_name": "create_label",
                "tool_call_id": "test-001",
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
    asyncio.run(test_token_full())
