import { WebSocketMessage, RateResponsePayload } from '../types/MessageTypes';

/**
 * Message handlers interface
 * Define handlers for different message types
 */
interface MessageHandlers {
  // Rate-related handlers
  onRateResponse?: (payload: RateResponsePayload) => void;

  // Error handler
  onError?: (message: string, originalRequest?: any) => void;

  // Other message type handlers
  [key: string]: ((payload: any) => void) | undefined;
}

/**
 * Dispatches a WebSocket message to the appropriate handler based on its type.
 *
 * @param message The WebSocket message to dispatch
 * @param handlers Object containing handler functions for different message types
 */
export function dispatchMessageByType(message: WebSocketMessage, handlers: MessageHandlers): void {
  // Special handling for specific message types
  switch (message.type) {
    case 'quote_ready':
      if (handlers.onRateResponse) {
        handlers.onRateResponse(message.payload as RateResponsePayload);
        return;
      }
      break;

    case 'error':
      if (handlers.onError) {
        handlers.onError(message.payload.message, message.payload.original_request);
        return;
      }
      break;
  }

  // Generic handling for other message types
  const handlerKey = message.type.replace(/[-_]([a-z])/g, (_, letter) =>
    letter.toUpperCase()
  );

  const handler = handlers[`on${handlerKey.charAt(0).toUpperCase() + handlerKey.slice(1)}`];

  if (handler) {
    handler(message.payload);
  } else {
    console.warn("Unhandled message type:", message.type);
  }
}