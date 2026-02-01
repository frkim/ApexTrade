'use client'

import { useEffect, useCallback, useRef } from 'react'
import { wsClient, WebSocketMessage, WebSocketMessageType } from '@/lib/websocket'

export function useWebSocket<T = unknown>(
  type: WebSocketMessageType,
  handler: (message: WebSocketMessage<T>) => void
) {
  const handlerRef = useRef(handler)
  handlerRef.current = handler

  useEffect(() => {
    wsClient.connect()

    const unsubscribe = wsClient.subscribe<T>(type, (message) => {
      handlerRef.current(message)
    })

    return () => {
      unsubscribe()
    }
  }, [type])

  const send = useCallback((data: unknown) => {
    wsClient.send(data)
  }, [])

  return { send }
}

export function useWebSocketConnection() {
  useEffect(() => {
    wsClient.connect()

    return () => {
      wsClient.disconnect()
    }
  }, [])
}
