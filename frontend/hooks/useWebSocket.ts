import { useEffect, useRef, useState } from "react";

type WebSocketMessage = {
  type: string;
  payload: any;
  timestamp: number;
  requestId: string;
};

interface UseWebSocketOptions {
  token?: string;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [status, setStatus] = useState<"connected" | "disconnected" | "connecting">("connecting");
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Add token to URL if provided
    const wsUrl = options.token ? `${url}?token=${options.token}` : url;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setStatus("connected");
    ws.onclose = () => setStatus("disconnected");
    ws.onerror = () => setStatus("disconnected");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    return () => ws.close();
  }, [url]);

  const sendMessage = (msg: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  };

  return { status, messages, sendMessage };
}