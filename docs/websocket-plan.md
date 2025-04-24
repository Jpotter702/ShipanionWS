# 📡 ShipVox WebSocket Implementation Plan

This document outlines the end-to-end implementation strategy for WebSocket integration within the ShipVox Companion UI, enabling real-time UI updates synced with the voice agent.

---

## ✅ Phase 1: Foundation Setup

- **Create WebSocket Server**
  - [ ] Choose stack (Node.js + ws, or FastAPI + websockets)
  - [ ] Create `server.js` or `main.py` entry point
  - [ ] Handle connect, message, disconnect
  - [ ] Accept messages from voice agent via API or socket

- **Create Message Format Schema**
  - [ ] Standardize message structure: `{ type, payload, timestamp, requestId }`
  - [ ] Define per-step payload structures (`details`, `quotes`, `label`, etc.)

- **Implement Authentication (optional)**
  - [ ] Accept token in message after connection
  - [ ] Validate token and associate session with user/clientId

---

## ✅ Phase 2: Frontend Hook + Integration

- **Finalize `useWebSocket` Hook**
  - [x] Add fallback for preview mode
  - [x] Handle reconnect logic
  - [ ] Expose connection status and parsed messages
  - [ ] Allow message filtering by `type`

- **Add Dispatcher Logic**
  - [ ] Build `dispatchMessageByType()` to hydrate cards by payload type
  - [ ] Push payloads into appropriate state slices (`setQuotes`, `setLabel`, etc.)

- **Improve Typing and Message Handling**
  - [ ] Add TS interfaces for all message types
  - [ ] Add optional logging/debug panel

---

## ✅ Phase 3: UI Consumption + Testing

- **Consume Hook in `ShippingFeedPage`**
  - [ ] Call `useWebSocket()`
  - [ ] Pass state into `ShippingFeed` and children

- **Stepper/Accordion UI Animation**
  - [ ] Animate card reveal based on step
  - [ ] Highlight active step
  - [ ] Show checkmark icons on complete

- **Build Fallback Demo Simulator (Done ✅)**
  - [x] Cycle mock messages with delays
  - [x] Populate all cards step-by-step

---

## ✅ Phase 4: Production & Monitoring

- **Deploy WebSocket Server**
  - [ ] Dockerize and deploy to Render/Fly.io/VPS
  - [ ] Enable TLS (wss://)

- **Monitor & Maintain**
  - [ ] Log all incoming/outgoing messages
  - [ ] Add metrics (message rate, connection count)
  - [ ] Implement rate limiting or abuse prevention

---

## 🧠 Related Work

- [x] CompanionUI fallback mechanism written
- [x] Message format examples defined
- [x] SSR-safe dynamic import implemented
