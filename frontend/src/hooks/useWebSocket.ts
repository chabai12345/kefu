import { useCallback, useRef, useState } from 'react'
import type { AgentResponse, ChatMessage } from '../types'

const WS_URL = `ws://${window.location.hostname}:8001/api/v1/ws`

export function useWebSocket() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const ws = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return

    const socket = new WebSocket(WS_URL)
    socket.onopen = () => setConnected(true)
    socket.onclose = () => setConnected(false)
    socket.onmessage = (event) => {
      const data: AgentResponse = JSON.parse(event.data)
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: data.reply,
          timestamp: Date.now(),
          rich_data: data.rich_data ?? null,
        },
      ])
      setLoading(false)
    }
    ws.current = socket
  }, [])

  const send = useCallback((text: string) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) return

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    ws.current.send(JSON.stringify({ message: text }))
  }, [])

  return { messages, connected, loading, connect, send }
}
