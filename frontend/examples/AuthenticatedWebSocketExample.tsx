import React from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

// In a real application, this would be loaded from environment variables or a secure configuration
const WS_AUTH_TOKEN = 'your-secure-token-here';

export function AuthenticatedWebSocketExample() {
  // Pass the authentication token to the WebSocket hook
  const { status, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws', {
    token: WS_AUTH_TOKEN,
  });

  const handleSendMessage = () => {
    sendMessage({
      type: 'example_message',
      payload: { content: 'Hello, authenticated WebSocket!' },
      timestamp: Date.now(),
      requestId: crypto.randomUUID(),
    });
  };

  return (
    <div>
      <h1>WebSocket Status: {status}</h1>
      <button onClick={handleSendMessage} disabled={status !== 'connected'}>
        Send Message
      </button>
      <div>
        <h2>Messages:</h2>
        <ul>
          {messages.map((msg) => (
            <li key={msg.requestId}>
              {msg.type}: {JSON.stringify(msg.payload)}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
