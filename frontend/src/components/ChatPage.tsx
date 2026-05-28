import React, { useEffect } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import MessageBubble from './MessageBubble'
import InputBox from './InputBox'
import SidePanel from './SidePanel'

export default function ChatPage() {
  const { messages, connected, loading, connect, send } = useWebSocket()

  useEffect(() => {
    connect()
  }, [connect])

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
            <h1 className="text-lg font-semibold text-gray-800">电商客服</h1>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-20">
                <p className="text-lg">您好！请问有什么可以帮您的？</p>
              </div>
            )}
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {loading && (
              <div className="flex justify-start mb-4">
                <div className="bg-white rounded-2xl rounded-bl-md px-4 py-3 shadow-sm border border-gray-100">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:0.1s]" />
                    <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce [animation-delay:0.2s]" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input */}
        <InputBox onSend={send} disabled={!connected} />
      </div>

      {/* Side panel */}
      <SidePanel connected={connected} messageCount={messages.length} />
    </div>
  )
}
