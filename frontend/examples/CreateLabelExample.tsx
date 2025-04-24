import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

// In a real application, this would be loaded from environment variables or a secure configuration
const WS_AUTH_TOKEN = 'your-secure-token-here';

interface LabelResult {
  tracking_number: string;
  label_url: string;
  qr_code: string;
  carrier: string;
  estimated_delivery: string;
}

export function CreateLabelExample() {
  // State for form inputs - Shipper
  const [shipperName, setShipperName] = useState('John Doe');
  const [shipperStreet, setShipperStreet] = useState('123 Main St');
  const [shipperCity, setShipperCity] = useState('Beverly Hills');
  const [shipperState, setShipperState] = useState('CA');
  const [shipperZip, setShipperZip] = useState('90210');
  
  // State for form inputs - Recipient
  const [recipientName, setRecipientName] = useState('Jane Smith');
  const [recipientStreet, setRecipientStreet] = useState('456 Park Ave');
  const [recipientCity, setRecipientCity] = useState('New York');
  const [recipientState, setRecipientState] = useState('NY');
  const [recipientZip, setRecipientZip] = useState('10001');
  
  // State for form inputs - Package
  const [carrier, setCarrier] = useState('fedex');
  const [serviceType, setServiceType] = useState('FEDEX_GROUND');
  const [weight, setWeight] = useState(5);
  const [length, setLength] = useState(12);
  const [width, setWidth] = useState(8);
  const [height, setHeight] = useState(6);
  
  // State for label results
  const [labelResult, setLabelResult] = useState<LabelResult | null>(null);
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
        setIsLoading(false);
        
        if (latestMessage.is_error) {
          setError(latestMessage.result.error);
        } else {
          setLabelResult(latestMessage.result);
        }
      } else if (latestMessage.type === 'contextual_update' && latestMessage.text === 'label_created') {
        // Handle contextual update if needed
        console.log('Received contextual update:', latestMessage);
      }
    }
  }, [messages, lastToolCallId]);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    const toolCallId = `label-${Date.now()}`;
    setLastToolCallId(toolCallId);
    
    // Send create_label tool call
    sendMessage({
      type: 'client_tool_call',
      client_tool_call: {
        tool_name: 'create_label',
        tool_call_id: toolCallId,
        parameters: {
          carrier,
          service_type: serviceType,
          shipper_name: shipperName,
          shipper_street: shipperStreet,
          shipper_city: shipperCity,
          shipper_state: shipperState,
          shipper_zip: shipperZip,
          recipient_name: recipientName,
          recipient_street: recipientStreet,
          recipient_city: recipientCity,
          recipient_state: recipientState,
          recipient_zip: recipientZip,
          weight: parseFloat(weight.toString()),
          dimensions: {
            length: parseFloat(length.toString()),
            width: parseFloat(width.toString()),
            height: parseFloat(height.toString()),
          }
        }
      },
      timestamp: Date.now(),
      requestId: crypto.randomUUID()
    });
  };

  return (
    <div className="create-label-container">
      <h1>Create Shipping Label</h1>
      
      <div className="connection-status">
        WebSocket Status: <span className={`status-${status}`}>{status}</span>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h2>Carrier Information</h2>
          <div className="form-group">
            <label htmlFor="carrier">Carrier:</label>
            <select
              id="carrier"
              value={carrier}
              onChange={(e) => setCarrier(e.target.value)}
              required
            >
              <option value="fedex">FedEx</option>
              <option value="ups">UPS</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="serviceType">Service Type:</label>
            <select
              id="serviceType"
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              required
            >
              <option value="FEDEX_GROUND">FedEx Ground</option>
              <option value="FEDEX_2_DAY">FedEx 2Day</option>
              <option value="FEDEX_PRIORITY_OVERNIGHT">FedEx Priority Overnight</option>
              <option value="UPS_GROUND">UPS Ground</option>
              <option value="UPS_3_DAY_SELECT">UPS 3 Day Select</option>
              <option value="UPS_2ND_DAY_AIR">UPS 2nd Day Air</option>
            </select>
          </div>
        </div>
        
        <div className="form-section">
          <h2>Shipper Information</h2>
          <div className="form-group">
            <label htmlFor="shipperName">Name:</label>
            <input
              type="text"
              id="shipperName"
              value={shipperName}
              onChange={(e) => setShipperName(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="shipperStreet">Street:</label>
            <input
              type="text"
              id="shipperStreet"
              value={shipperStreet}
              onChange={(e) => setShipperStreet(e.target.value)}
              required
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="shipperCity">City:</label>
              <input
                type="text"
                id="shipperCity"
                value={shipperCity}
                onChange={(e) => setShipperCity(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="shipperState">State:</label>
              <input
                type="text"
                id="shipperState"
                value={shipperState}
                onChange={(e) => setShipperState(e.target.value)}
                maxLength={2}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="shipperZip">ZIP:</label>
              <input
                type="text"
                id="shipperZip"
                value={shipperZip}
                onChange={(e) => setShipperZip(e.target.value)}
                pattern="[0-9]{5}"
                required
              />
            </div>
          </div>
        </div>
        
        <div className="form-section">
          <h2>Recipient Information</h2>
          <div className="form-group">
            <label htmlFor="recipientName">Name:</label>
            <input
              type="text"
              id="recipientName"
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="recipientStreet">Street:</label>
            <input
              type="text"
              id="recipientStreet"
              value={recipientStreet}
              onChange={(e) => setRecipientStreet(e.target.value)}
              required
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="recipientCity">City:</label>
              <input
                type="text"
                id="recipientCity"
                value={recipientCity}
                onChange={(e) => setRecipientCity(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="recipientState">State:</label>
              <input
                type="text"
                id="recipientState"
                value={recipientState}
                onChange={(e) => setRecipientState(e.target.value)}
                maxLength={2}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="recipientZip">ZIP:</label>
              <input
                type="text"
                id="recipientZip"
                value={recipientZip}
                onChange={(e) => setRecipientZip(e.target.value)}
                pattern="[0-9]{5}"
                required
              />
            </div>
          </div>
        </div>
        
        <div className="form-section">
          <h2>Package Information</h2>
          <div className="form-group">
            <label htmlFor="weight">Weight (lbs):</label>
            <input
              type="number"
              id="weight"
              value={weight}
              onChange={(e) => setWeight(Number(e.target.value))}
              min="0.1"
              step="0.1"
              required
            />
          </div>
          
          <div className="dimensions-group">
            <h3>Package Dimensions (inches)</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="length">Length:</label>
                <input
                  type="number"
                  id="length"
                  value={length}
                  onChange={(e) => setLength(Number(e.target.value))}
                  min="0.1"
                  step="0.1"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="width">Width:</label>
                <input
                  type="number"
                  id="width"
                  value={width}
                  onChange={(e) => setWidth(Number(e.target.value))}
                  min="0.1"
                  step="0.1"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="height">Height:</label>
                <input
                  type="number"
                  id="height"
                  value={height}
                  onChange={(e) => setHeight(Number(e.target.value))}
                  min="0.1"
                  step="0.1"
                  required
                />
              </div>
            </div>
          </div>
        </div>
        
        <button 
          type="submit" 
          disabled={status !== 'connected' || isLoading}
          className="create-label-button"
        >
          {isLoading ? 'Creating Label...' : 'Create Shipping Label'}
        </button>
      </form>
      
      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}
      
      {labelResult && (
        <div className="label-result">
          <h2>Label Created Successfully!</h2>
          
          <div className="label-details">
            <p><strong>Tracking Number:</strong> {labelResult.tracking_number}</p>
            <p><strong>Carrier:</strong> {labelResult.carrier}</p>
            <p><strong>Estimated Delivery:</strong> {new Date(labelResult.estimated_delivery).toLocaleDateString()}</p>
          </div>
          
          <div className="label-actions">
            <a 
              href={labelResult.label_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="button"
            >
              Download Label
            </a>
            
            <button className="button">Print Label</button>
            <button className="button">Email Label</button>
          </div>
          
          {labelResult.qr_code && (
            <div className="qr-code">
              <h3>QR Code</h3>
              <img src={labelResult.qr_code} alt="Tracking QR Code" />
            </div>
          )}
        </div>
      )}
      
      <div className="tool-explanation">
        <h3>How This Works</h3>
        <p>This example demonstrates the ElevenLabs Conversational AI client tool for creating shipping labels:</p>
        <ol>
          <li>Fill out the form with shipping details</li>
          <li>Click "Create Shipping Label" to send a WebSocket message with type <code>client_tool_call</code></li>
          <li>The server processes the request and calls the ShipVox API</li>
          <li>The server returns a <code>client_tool_result</code> message with the label details</li>
          <li>The server also broadcasts a <code>contextual_update</code> message to all clients</li>
          <li>The UI displays the label details and download options</li>
        </ol>
        <p>In a real application, the ElevenLabs agent would collect this information through voice conversation.</p>
      </div>
    </div>
  );
}
