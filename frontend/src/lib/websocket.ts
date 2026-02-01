import { WS_URL } from './constants'

export type WebSocketMessageType =
  | 'price_update'
  | 'trade_executed'
  | 'portfolio_update'
  | 'strategy_status'
  | 'error'

export interface WebSocketMessage<T = unknown> {
  type: WebSocketMessageType
  data: T
  timestamp: string
}

type MessageHandler<T = unknown> = (message: WebSocketMessage<T>) => void

class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private handlers: Map<WebSocketMessageType, Set<MessageHandler>> = new Map()
  private isConnecting = false

  constructor(url: string) {
    this.url = url
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return
    }

    this.isConnecting = true

    try {
      const token = localStorage.getItem('auth_token')
      const wsUrl = token ? `${this.url}/ws?token=${token}` : `${this.url}/ws`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        this.isConnecting = false
        this.reconnectAttempts = 0
        console.log('WebSocket connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.notifyHandlers(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        this.isConnecting = false
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        this.isConnecting = false
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      this.isConnecting = false
      console.error('Failed to connect WebSocket:', error)
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    setTimeout(() => {
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      this.connect()
    }, delay)
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe<T>(type: WebSocketMessageType, handler: MessageHandler<T>): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set())
    }
    this.handlers.get(type)!.add(handler as MessageHandler)

    return () => {
      this.handlers.get(type)?.delete(handler as MessageHandler)
    }
  }

  private notifyHandlers(message: WebSocketMessage): void {
    const handlers = this.handlers.get(message.type)
    if (handlers) {
      handlers.forEach((handler) => handler(message))
    }
  }

  send(data: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }
}

export const wsClient = new WebSocketClient(WS_URL)
