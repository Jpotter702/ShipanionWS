import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

// In a real application, this would be loaded from environment variables or a secure configuration
const WS_AUTH_TOKEN = 'your-secure-token-here';

interface ShippingQuote {
  carrier: string;
  service: string;
  price: number;
  eta: string;
}

export function ElevenLabsToolExample() {
  // State for tool call results
  const [quotes, setQuotes] = useState<ShippingQuote[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastToolCallId, setLastToolCallId] = useState<string | null>(null);

  // Connect to WebSocket
  const { status, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws', {
    token: WS_AUTH_TOKEN,
  });

  // Process incoming messages
  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      
      if (latestMessage.type === 'client_tool_result' && latestMessage.tool_call_id === lastToolCallId) {
        if (latestMessage.is_error) {
          setError(latestMessage.result.error);
        } else {
          setQuotes(latestMessage.result);
        }
        setIsLoading(false);
      }
    }
  }, [messages, lastToolCallId]);

  // Simulate an ElevenLabs tool call
  const simulateToolCall = () => {
    setIsLoading(true);
    setError(null);
    
    const toolCallId = `test-${Date.now()}`;
    setLastToolCallId(toolCallId);
    
    // Send client_tool_call message
    sendMessage({
      type: 'client_tool_call',
      client_tool_call: {
        tool_name: 'get_shipping_quotes',
        tool_call_id: toolCallId,
        parameters: {
          from_zip: '90210',
          to_zip: '10001',
          weight: 5.0,
          dimensions: {
            length: 12.0,
            width: 8.0,
            height: 6.0
          },
          pickup_requested: false
        }
      },
      timestamp: Date.now(),
      requestId: crypto.randomUUID()
    });
  };

  return (
    <div className="elevenlabs-tool-container">
      <h1>ElevenLabs Tool Example</h1>
      
      <div className="connection-status">
        WebSocket Status: <span className={`status-${status}`}>{status}</span>
      </div>
      
      <button 
        onClick={simulateToolCall} 
        disabled={status !== 'connected' || isLoading}
      >
        {isLoading ? 'Getting Quotes...' : 'Simulate get_shipping_quotes Tool Call'}
      </button>
      
      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}
      
      {quotes.length > 0 && (
        <div className="quotes-results">
          <h2>Shipping Quotes</h2>
          
          <table>
            <thead>
              <tr>
                <th>Carrier</th>
                <th>Service</th>
                <th>Price</th>
                <th>ETA</th>
              </tr>
            </thead>
            <tbody>
              {quotes.map((quote, index) => (
                <tr key={index} className={index === 0 ? 'cheapest' : ''}>
                  <td>{quote.carrier}</td>
                  <td>{quote.service}</td>
                  <td>${quote.price.toFixed(2)}</td>
                  <td>{quote.eta}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <div className="quote-summary">
            <p>
              <strong>Cheapest Option:</strong> {quotes[0].carrier} {quotes[0].service} - ${quotes[0].price.toFixed(2)} ({quotes[0].eta})
            </p>
            
            {quotes.length > 1 && (
              <p>
                <strong>Alternative Option:</strong> {quotes[1].carrier} {quotes[1].service} - ${quotes[1].price.toFixed(2)} ({quotes[1].eta})
              </p>
            )}
          </div>
        </div>
      )}
      
      <div className="tool-explanation">
        <h3>How This Works</h3>
        <p>This example simulates an ElevenLabs Conversational AI client tool call:</p>
        <ol>
          <li>The button click simulates the ElevenLabs agent calling the <code>get_shipping_quotes</code> tool</li>
          <li>A WebSocket message with type <code>client_tool_call</code> is sent to the server</li>
          <li>The server processes the request and calls the ShipVox API</li>
          <li>The server returns a <code>client_tool_result</code> message with the shipping quotes</li>
          <li>The UI displays the quotes in a table</li>
        </ol>
        <p>In a real application, the ElevenLabs agent would make this call based on user voice input.</p>
      </div>
    </div>
  );
}
