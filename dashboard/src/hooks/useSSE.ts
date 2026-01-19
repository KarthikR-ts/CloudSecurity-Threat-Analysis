/**
 * SSE Hook - Server-Sent Events for real-time alert streaming
 * Aurora CSPM Platform
 */

import { useEffect, useState, useCallback, useRef } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface SSEMessage {
    type: 'connected' | 'stats' | 'new_alert';
    data: any;
    timestamp: Date;
}

export interface SSEStats {
    total_alerts: number;
    new_alerts: number;
    timestamp: string;
}

export interface UseSSEOptions {
    onMessage?: (message: SSEMessage) => void;
    onError?: (error: Event) => void;
    onConnect?: () => void;
    autoReconnect?: boolean;
    reconnectDelay?: number;
}

export function useSSE(endpoint: string = '/alerts/stream/live', options: UseSSEOptions = {}) {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState<SSEMessage | null>(null);
    const [stats, setStats] = useState<SSEStats | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const {
        onMessage,
        onError,
        onConnect,
        autoReconnect = true,
        reconnectDelay = 3000
    } = options;

    const connect = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        const url = `${API_BASE_URL}${endpoint}`;
        const eventSource = new EventSource(url);

        eventSource.onopen = () => {
            setIsConnected(true);
            setError(null);
            onConnect?.();
        };

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const message: SSEMessage = {
                    type: data.type,
                    data: data,
                    timestamp: new Date()
                };

                setLastMessage(message);

                if (data.type === 'stats') {
                    setStats(data);
                }

                onMessage?.(message);
            } catch (e) {
                console.error('Failed to parse SSE message:', e);
            }
        };

        eventSource.onerror = (event) => {
            setIsConnected(false);
            setError(new Error('SSE connection failed'));
            onError?.(event);

            if (autoReconnect) {
                reconnectTimeoutRef.current = setTimeout(() => {
                    connect();
                }, reconnectDelay);
            }
        };

        eventSourceRef.current = eventSource;
    }, [endpoint, onMessage, onError, onConnect, autoReconnect, reconnectDelay]);

    const disconnect = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }
        setIsConnected(false);
    }, []);

    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return {
        isConnected,
        lastMessage,
        stats,
        error,
        reconnect: connect,
        disconnect
    };
}
