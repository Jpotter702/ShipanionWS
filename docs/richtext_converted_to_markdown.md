Have we achieved the following requirements for this phase?

Frontend Client <— WebSocket — ShipVox Server

↑

POST /send-message

↑

Used by test tools or internal API

FastAPI server up and running

Clients connect to /ws

send-message POST will broadcast to all connected clients

Frontend useWebSocket.ts receives messages and stores them in state

Dispatcher and type interfaces scaffolded