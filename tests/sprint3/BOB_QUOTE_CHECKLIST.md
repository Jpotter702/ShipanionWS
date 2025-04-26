# Bob Quote Response Checklist

Use this checklist to verify that Bob correctly speaks shipping quotes aloud when receiving a `client_tool_result` message.

## Test Execution

- [ ] Run the test script: `python tests/sprint3/test_bob_speaks_quote.py`
- [ ] Verify that the script connects to the WebSocket server successfully
- [ ] Verify that the script sends the `client_tool_result` message successfully
- [ ] Listen for Bob's spoken response

## Response Verification

### Content Completeness

- [ ] Bob mentions all carriers (UPS, USPS, FedEx)
- [ ] Bob mentions all prices ($9.99, $12.99, $14.99)
- [ ] Bob mentions all delivery times (1-2, 2-3, 3-5 business days)
- [ ] Bob mentions all service types (Ground, Priority Mail, Express Saver)

### Presentation Quality

- [ ] Bob presents the cheapest option first
- [ ] Bob clearly associates each price with the correct carrier and service
- [ ] Bob's speech is clear and understandable
- [ ] Bob uses a natural, conversational tone

### User Interaction

- [ ] Bob asks which option the user would prefer
- [ ] Bob's question is phrased in a way that invites a response
- [ ] Bob waits for the user's response before continuing

## Troubleshooting

If Bob fails any of the checks above, consider the following troubleshooting steps:

### Bob Doesn't Speak at All

- [ ] Check that the WebSocket connection is established
- [ ] Verify that the `client_tool_result` message has the correct format
- [ ] Check that the `tool_call_id` in the message matches the one in the `client_tool_call`
- [ ] Ensure that `is_error` is set to `false`

### Bob Speaks but Misses Information

- [ ] Check that all required fields are present in the `result` array
- [ ] Verify that the field names match what Bob expects (`carrier`, `service`, `price`, `eta`)
- [ ] Ensure that the values are in the expected format (strings for text, numbers for prices)

### Bob's Response is Unclear or Confusing

- [ ] Adjust the tool prompt in Agent Studio (see `AGENT_STUDIO_PROMPT_GUIDE.md`)
- [ ] Add more explicit instructions about how to present the quotes
- [ ] Provide examples of good responses in the tool description

## Test Results

**Date and Time**: ________________________

**Tester**: ________________________

**Bob's Response**: ________________________

**Issues Identified**: ________________________

**Actions Taken**: ________________________

**Retest Results**: ________________________

## Notes

- Remember that changes to the agent in Agent Studio may take a few minutes to propagate
- If Bob consistently fails to speak the quotes correctly, consider capturing the WebSocket traffic for further analysis
- The expected format for Bob's response is:
  ```
  I've found some shipping options for you. The most affordable option is [CARRIER] [SERVICE] at $[PRICE], which would arrive in [ETA]. Other options include [CARRIER] [SERVICE] at $[PRICE] with delivery in [ETA], and [CARRIER] [SERVICE] at $[PRICE] with delivery in [ETA]. Which option would you prefer?
  ```
