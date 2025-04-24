import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

// In a real application, this would be loaded from environment variables or a secure configuration
const WS_AUTH_TOKEN = 'your-secure-token-here';

interface RateOption {
  carrier: string;
  service_name: string;
  service_tier: string;
  cost: number;
  estimated_delivery: string;
  transit_days: number;
}

interface RateResponse {
  cheapest_option: RateOption;
  fastest_option: RateOption | null;
  all_options: RateOption[];
}

export function RateRequestExample() {
  // State for form inputs
  const [originZip, setOriginZip] = useState('90210');
  const [destinationZip, setDestinationZip] = useState('10001');
  const [weight, setWeight] = useState(5);
  const [length, setLength] = useState(12);
  const [width, setWidth] = useState(8);
  const [height, setHeight] = useState(6);
  
  // State for rate results
  const [rateResponse, setRateResponse] = useState<RateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Connect to WebSocket
  const { status, messages, sendMessage } = useWebSocket('ws://localhost:8000/ws', {
    token: WS_AUTH_TOKEN,
  });

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    // Send rate request via WebSocket
    sendMessage({
      type: 'get_rates',
      payload: {
        origin_zip: originZip,
        destination_zip: destinationZip,
        weight: parseFloat(weight.toString()),
        dimensions: {
          length: parseFloat(length.toString()),
          width: parseFloat(width.toString()),
          height: parseFloat(height.toString()),
        },
        pickup_requested: false,
      },
      timestamp: Date.now(),
      requestId: crypto.randomUUID(),
    });
  };

  // Process incoming messages
  useEffect(() => {
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      
      if (latestMessage.type === 'quote_ready') {
        setRateResponse(latestMessage.payload as RateResponse);
        setIsLoading(false);
      } else if (latestMessage.type === 'error') {
        setError(latestMessage.payload.message);
        setIsLoading(false);
      }
    }
  }, [messages]);

  return (
    <div className="rate-request-container">
      <h1>Get Shipping Rates</h1>
      
      <div className="connection-status">
        WebSocket Status: <span className={`status-${status}`}>{status}</span>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="originZip">Origin ZIP Code:</label>
          <input
            type="text"
            id="originZip"
            value={originZip}
            onChange={(e) => setOriginZip(e.target.value)}
            pattern="[0-9]{5}"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="destinationZip">Destination ZIP Code:</label>
          <input
            type="text"
            id="destinationZip"
            value={destinationZip}
            onChange={(e) => setDestinationZip(e.target.value)}
            pattern="[0-9]{5}"
            required
          />
        </div>
        
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
        
        <button 
          type="submit" 
          disabled={status !== 'connected' || isLoading}
        >
          {isLoading ? 'Getting Rates...' : 'Get Rates'}
        </button>
      </form>
      
      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}
      
      {rateResponse && (
        <div className="rate-results">
          <h2>Shipping Options</h2>
          
          <div className="rate-option cheapest">
            <h3>Cheapest Option</h3>
            <p>Carrier: {rateResponse.cheapest_option.carrier}</p>
            <p>Service: {rateResponse.cheapest_option.service_name}</p>
            <p>Cost: ${rateResponse.cheapest_option.cost.toFixed(2)}</p>
            <p>Transit Days: {rateResponse.cheapest_option.transit_days}</p>
            <p>Estimated Delivery: {new Date(rateResponse.cheapest_option.estimated_delivery).toLocaleDateString()}</p>
          </div>
          
          {rateResponse.fastest_option && (
            <div className="rate-option fastest">
              <h3>Fastest Option</h3>
              <p>Carrier: {rateResponse.fastest_option.carrier}</p>
              <p>Service: {rateResponse.fastest_option.service_name}</p>
              <p>Cost: ${rateResponse.fastest_option.cost.toFixed(2)}</p>
              <p>Transit Days: {rateResponse.fastest_option.transit_days}</p>
              <p>Estimated Delivery: {new Date(rateResponse.fastest_option.estimated_delivery).toLocaleDateString()}</p>
            </div>
          )}
          
          <div className="all-options">
            <h3>All Options ({rateResponse.all_options.length})</h3>
            <table>
              <thead>
                <tr>
                  <th>Carrier</th>
                  <th>Service</th>
                  <th>Cost</th>
                  <th>Transit Days</th>
                  <th>Delivery Date</th>
                </tr>
              </thead>
              <tbody>
                {rateResponse.all_options.map((option, index) => (
                  <tr key={index}>
                    <td>{option.carrier}</td>
                    <td>{option.service_name}</td>
                    <td>${option.cost.toFixed(2)}</td>
                    <td>{option.transit_days}</td>
                    <td>{new Date(option.estimated_delivery).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
