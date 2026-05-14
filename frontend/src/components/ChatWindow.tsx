import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import type { Message } from '../types'

export interface ChatWindowProps {
  messages: Message[]
  isTyping: boolean
  onSuggestedPrompt?: (prompt: string) => void
}

const SUGGESTED_PROMPTS = [
  { icon: '🔬', text: 'Summarise the latest AI research papers' },
  { icon: '💻', text: 'Write a React hook for debounced search' },
  { icon: '📊', text: 'Analyse this data and create a chart' },
  { icon: '🌐', text: 'What are the top news stories today?' },
]

const ChatWindow = ({ messages, isTyping, onSuggestedPrompt }: ChatWindowProps) => {
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isTyping])

  const isEmpty = messages.length === 0

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 md:px-8 py-8 pb-4 scrollbar-thin"
    >
      <div className="max-w-4xl mx-auto">
        {isEmpty ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex min-h-[60vh] flex-col items-center justify-center text-center"
          >
            {/* Animated brain */}
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
              className="w-24 h-24 mx-auto mb-8 flex items-center justify-center glass rounded-full shadow-neon-blue"
            >
              <span className="text-5xl">🧠</span>
            </motion.div>

            <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-3">
              Welcome to <span className="neon-text">DualMind</span>
            </h2>
            <p className="text-text-secondary max-w-md mb-12 leading-relaxed">
              Ask anything. I'll plan, verify, and deliver the best answer using dual-agent reasoning.
            </p>

            {/* Suggested prompts */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
              {SUGGESTED_PROMPTS.map((p, i) => (
                <motion.button
                  key={p.text}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + i * 0.08 }}
                  whileHover={{ scale: 1.02, transition: { duration: 0.15 } }}
                  onClick={() => onSuggestedPrompt?.(p.text)}
                  className="flex items-center gap-3 glass-panel rounded-xl px-4 py-3.5 text-left hover:border-neon-blue/30 hover:shadow-neon-blue transition-all duration-200 group"
                >
                  <span className="text-xl flex-shrink-0">{p.icon}</span>
                  <span className="text-sm text-text-secondary group-hover:text-text-primary transition-colors leading-snug">
                    {p.text}
                  </span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <div className="space-y-1">
            <AnimatePresence initial={false}>
              {messages.map(message => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                >
                  <MessageBubble message={message} />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="pt-2"
          >
            <TypingIndicator />
          </motion.div>
        )}

        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  )
}

export default ChatWindow
