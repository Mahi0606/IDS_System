import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { WS_BASE_URL } from '../config';

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const messageHandlersRef = useRef(new Set());

  const connect = useCallback(() => {
    // Don't connect if already connected or connecting
    if (wsRef.current && (
      wsRef.current.readyState === WebSocket.OPEN || 
      wsRef.current.readyState === WebSocket.CONNECTING
    )) {
      return;
    }

    try {
      const wsUrl = WS_BASE_URL.endsWith('/') ? WS_BASE_URL.slice(0, -1) : WS_BASE_URL;
      const ws = new WebSocket(`${wsUrl}/api/live`);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected (global)');
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          // Notify all registered handlers
          messageHandlersRef.current.forEach(handler => {
            try {
              handler(data);
            } catch (error) {
              console.error('Error in WebSocket message handler:', error);
            }
          });
          console.log('WebSocket message received:', data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected (global)');
        // Auto-reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };
    } catch (error) {
      console.error('Error connecting WebSocket:', error);
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const subscribe = useCallback((handler) => {
    messageHandlersRef.current.add(handler);
    return () => {
      messageHandlersRef.current.delete(handler);
    };
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  const value = {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    subscribe,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
}

