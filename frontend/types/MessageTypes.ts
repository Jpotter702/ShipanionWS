export type WebSocketMessageType =
  // Rate-related messages
  | "get_rates"
  | "quote_ready"

  // Shipping-related messages
  | "zip_collected"
  | "weight_confirmed"
  | "label_created"
  | "pickup_scheduled"

  // System messages
  | "error"
  | "auth"
  | "contextual_update"
  | "client_tool_call"
  | "client_tool_result";

export interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: any;
  timestamp: number;
  requestId: string;
  user?: string;
}

// Rate request message interface
export interface RateRequestPayload {
  origin_zip: string;
  destination_zip: string;
  weight: number;
  dimensions?: {
    length: number;
    width: number;
    height: number;
  };
  pickup_requested: boolean;
}

// Rate option interface
export interface RateOption {
  carrier: string;
  service_name: string;
  service_tier: string;
  cost: number;
  estimated_delivery: string;
  transit_days: number;
}

// Rate response payload interface
export interface RateResponsePayload {
  cheapest_option: RateOption;
  fastest_option: RateOption | null;
  all_options: RateOption[];
}