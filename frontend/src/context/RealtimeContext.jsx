import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

const RealtimeContext = createContext(null);

export const RealtimeProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connectWebSocket = () => {
    try {
      const wsUrl = import.meta.env.VITE_WS_BASE_URL 
        ? `${import.meta.env.VITE_WS_BASE_URL}/api/ws` 
        : `ws://${window.location.host}/ws`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastEvent(data);
          // Trigger refresh for relevant events
          if (['NEW_RESCUE_REQUEST', 'REQUEST_STATUS_CHANGED', 'ZONE_CONFIG_UPDATED', 'ZONES_RECOMPUTED', 'NEW_ALERT'].includes(data.type)) {
            setRefreshTrigger(prev => prev + 1);
          }
        } catch (e) {
          console.warn("Lỗi phân tích WebSocket payload:", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt reconnect after 5s
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      ws.onerror = () => {
        setIsConnected(false);
        ws.close();
      };
    } catch (err) {
      console.warn("Không thể kết nối WebSocket:", err);
    }
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, []);

  return (
    <RealtimeContext.Provider value={{ isConnected, lastEvent, refreshTrigger, triggerManualRefresh: () => setRefreshTrigger(p => p + 1) }}>
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within RealtimeProvider');
  }
  return context;
};
