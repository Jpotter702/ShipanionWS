---

#  ShipVox WebSocket Integration: Sprint Plan

Each sprint is structured around your current assets, codebase ownership, and realistic engineering flow.  
 Cursor's Wonder Twins = front/back pairing  
 You = lead architect & code reviewer

---

##  Sprint 1: 🔐 Auth, Routing, and the First Tool Call (4–5 Days)

###  Backend (WebSocket + API)
- [ ] Add `?token=abc123` validation on socket connect
- [ ] Reject unauthenticated connections gracefully
- [ ] Add a test token (hardcoded or ENV-based for now)
- [ ] Handle `"tool_name": "get_shipping_quotes"`:
  - Parse parameters
  - `POST` to `/get-rates` (ShipVox backend)
  - Capture response
  - Wrap in `client_tool_result`
  - Broadcast to all clients (including voice + UI)

---

###  Frontend (CompanionUI)
- [ ] Update `useWebSocket.ts` to:
  - Parse message `type`
  - Expose a `onQuoteReady` callback or reducer hook
- [ ] Wire to `ShippingFeedPage`
- [ ] Create visual placeholder for incoming quote data

---

### 🎤 ElevenLabs
- [ ] Define tool in agent studio: `get_shipping_quotes`
- [ ] Set correct path for proxy call to WebSocket server (or gateway function)
- [ ] Confirm LLM speaks quote result clearly

---

### 🔍 Test Path
> Bob voice agent → Socket → ShipVox `/get-rates` → result to Bob + UI  
> ✅ QuoteCard shows info  
> ✅ Bob speaks it  
> ✅ WebSocket broadcast confirms reach

---

### ⏳ Time Block: Unknowns
- [ ] Session ID propagation strategy
- [ ] Delayed message handling (e.g. slow FedEx API)
- [ ] UI fallback testing for dropped WebSocket

---

## 🚀 Sprint 2: 🧠 Step Sync, Create Label, Mirror UI (5 Days)

### Backend
- [ ] Add `"tool_name": "create_label"` logic
  - POST to `/create-label`
  - Return `client_tool_result`
- [ ] Add `"contextual_update"` emitter as optional second response
- [ ] Track `session_id` per client (stubbed via token for now)

---

### Frontend
- [ ] Add reducer for `zip`, `weight`, `quote`, `label` steps
- [ ] Animate QuoteCard with Framer Motion
- [ ] Add checkmark + highlight to active step
- [ ] Receive `"label_created"` and render PDF/QR preview

---

### ElevenLabs
- [ ] Register `create_label` tool
- [ ] LLM voice confirmation: “Label created, downloading now.”
- [ ] UI displays label with 3 buttons: Download, Print, Email

---

### ⏳ Time Block: Message Order + Sync Drift
- [ ] Late-arriving quote after user already picked one
- [ ] Bob speaks quote A, UI shows quote B (race condition logic)
- [ ] UI rehydration after reconnect (browser refresh)

---

## 🔧 Sprint 3: 🛡️ Prod Readiness & Session Sync (5–7 Days)

### Backend
- [ ] Add ping/pong or heartbeat check
- [ ] Rate limit suspicious message frequency
- [ ] Deploy WebSocket as module inside backend project
- [ ] Add TLS for `wss://` deployment (Render or Fly.io)

---

### Frontend
- [ ] Auto-reconnect to WebSocket with `session_id`
- [ ] Display UI banner: “Reconnected to voice session”
- [ ] Add basic dev console/log toggle to show live message flow

---

### ElevenLabs
- [ ] Append `session_id` to all tool call payloads (metadata or custom param)
- [ ] Support “resume session” instruction (“I lost my place”)

---

### Analytics & Monitoring (optional)
- [ ] Add debug endpoint `/status` showing open connections
- [ ] Track session logs by ID
- [ ] Integrate simple logger (stdout + daily roll logs)

---

## ✅ Final Delivery Milestone

> A full shipping flow where:
> - User speaks to Bob
> - CompanionUI updates in real-time (quote → label → confirmation)
> - Session is tracked and resumable
> - Everything is secured, logged, and deterministic

---

Would you like me to export this Sprint Plan as a `SPRINT_PLAN.md` file too? Or integrate it into your Notion or GitHub `projects/` board?

We’re on track to build a production-ready conversational AI logistics engine. Let's roll. 📡🧠📦