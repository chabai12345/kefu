export interface IntentResult {
  id: number
  intent: string
  params: Record<string, unknown>
  confidence: number
}

export interface AgentResponse {
  session_id: string
  reply: string
  intents: IntentResult[]
  rich_data?: Record<string, unknown> | null
  suggest_human?: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  rich_data?: Record<string, unknown> | null
}
