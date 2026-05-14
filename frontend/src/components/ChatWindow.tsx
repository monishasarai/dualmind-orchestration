import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import type { Message } from '../types'

export interface ChatWindowProps {
  messages: Message[]
  isTyping: boolean
}

const ChatWindow = ({ messages, isTyping }: ChatWindowProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const el = bottomRef.current
    if (!el) return
    el.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isTyping])

  const isEmpty = messages.length === 0

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 md:px-8 py-8 pb-32 scrollbar-thin"
    >
      <div className="max-w-4xl mx-auto">
        {isEmpty ? (
          <div className="flex h-full min-h-[60vh] flex-col items-center justify-center text-center">
            <div className="mb-6 text-6xl">🧠</div>
            <h2 className="text-3xl font-semibold text-text-primary mb-3">
              Welcome to DualMind
            </h2>
            <p className="text-lg text-text-secondary max-w-md">
              Ask me anything, and I'll help you discover, learn, and think smarter.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </div>
        )}

        {isTyping ? (
          <div className="pt-2">
            <TypingIndicator />
          </div>
        ) : null}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}

export default ChatWindow
