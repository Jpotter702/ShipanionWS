
1. Mirror the Voice Session in UI
	a.   Use `client_tool_call`

>- User: "I need a 2lbs. package sent from 89101 to 10001." 
>- Bob: "Let me check that for you…”
>- client_tool_call is invoked which triggers the following to be sent over Websockets

    {
      "type": "client_tool_call",
      "client_tool_call": {
        "tool_name": "get_shipping_quotes",
        "tool_call_id": "abc123",
        "parameters": {
          "from_zip": "89101",
          "to_zip": "10001",
          "weight": 2
        }
      }
    }

The get_rates listener receives, processes and broadcasts response. CompanionUI subscribes to Websocket broadcasts binding each to `setState()` in components, populating the cards and moving the stepper. The broadcast also carries the client_tool_result, prompting the agent to advise the user with the rate quote, at the same time the UI is updated.

    {
      "type": "client_tool_result",
      "tool_call_id": "abc123",
      "result": [
        {
          "carrier": "UPS",
          "service": "Ground",
          "price": 8.44,
          "eta": "2 days"
        },
        {
          "carrier": "FedEx",
          "service": "Express",
          "price": 22.10,
          "eta": "tomorrow"
        }
      ],
      "is_error": false
    }

2. Use contextual_update

This updates the context of the voice agent as well.
    {
      "type": "contextual_update",
      "text": "quote_ready",
      "data": {
        "from": "Las Vegas, NV",
        "to": "New York, NY",
        "weight_lbs": 2,
        "carrier": "UPS",
        "service": "Ground",
        "price": 8.44,
        "eta": "2 days"
      }
    }


----------




