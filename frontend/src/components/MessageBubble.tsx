import { useState, type FC } from 'react'
import { motion } from 'framer-motion'
import { Copy, Check, RefreshCw } from 'lucide-react'
import type { Message } from '../types'
// @ts-ignore
import MessageTabs from './MessageTabs'
import { hasExecutionDetailsData } from '../utils/executionDetails'
// @ts-ignore
import LLMMessage from './LLMMessage'

interface MessageBubbleProps {
  message: Message
  onRegenerate?: (id: string) => void
}

const formatTime = (iso: string) => {
  const date = new Date(iso)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const CopyButton = ({ text, size = 'sm' }: { text: string; size?: 'sm' | 'xs' }) => {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // clipboard not available
    }
  }
  return (
    <button
      onClick={copy}
      className={`flex items-center gap-1 rounded-lg px-2 py-1 transition-all duration-200 ${
        size === 'xs' ? 'text-[11px]' : 'text-xs'
      } ${
        copied
          ? 'text-neon-green bg-neon-green/10'
          : 'text-text-secondary hover:text-text-primary hover:bg-white/10'
      }`}
      title="Copy"
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

const MessageBubble: FC<MessageBubbleProps> = ({ message, onRegenerate }) => {
  const isUser = message.sender === 'user'
  const [showActions, setShowActions] = useState(false)

  const renderAssistantContent = () => {
    const details = message.executionDetails
    if (hasExecutionDetailsData(details)) {
      return (
        <MessageTabs
          answer={message.content}
          executionDetails={details}
          fallbackUsed={Boolean(message.fallbackUsed)}
          fallbackReason={message.fallbackReason ?? undefined}
          fallbackSource={message.fallbackSource ?? undefined}
        />
      )
    }
    return <LLMMessage content={message.content} />
  }

  return (
    <div
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-3`}
      aria-label={isUser ? 'User message' : 'Assistant message'}
      onMouseEnter={() => !isUser && setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Assistant avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full glass flex items-center justify-center flex-shrink-0 mr-3 mt-1 shadow-neon-blue text-base">
          🧠
        </div>
      )}

      <div className="flex flex-col gap-1 max-w-[85%] md:max-w-[75%]">
        <div
          className={`rounded-2xl px-5 py-4 border transition-all duration-300 backdrop-blur-md ${
            isUser
              ? 'bg-neon-blue/10 border-neon-blue/30 text-text-primary rounded-tr-none'
              : 'glass-panel border-white/10 text-text-primary rounded-tl-none'
          }`}
        >
          {isUser ? (
            <p className="text-[15px] leading-6 whitespace-pre-wrap text-text-primary">{message.content}</p>
          ) : (
            renderAssistantContent()
          )}

          {/* Attachments */}
          {message.attachments?.length ? (
            <ul className="mt-3 space-y-2">
              {message.attachments.map(file => (
                <li key={`${message.id}-${file.filename}`} className="flex items-center gap-2 text-sm text-text-secondary">
                  <span className="inline-flex h-7 w-7 items-center justify-center rounded border border-neon-blue/40 text-neon-blue text-xs">📎</span>
                  <div className="min-w-0">
                    <p className="truncate font-medium text-text-primary">{file.filename}</p>
                    <p className="text-xs text-text-secondary">{Math.round(file.size / 1024)} KB · {file.contentType}</p>
                  </div>
                </li>
              ))}
            </ul>
          ) : null}
        </div>

        {/* Timestamp + actions row */}
        <div className={`flex items-center gap-2 px-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <time className="text-[11px] text-text-secondary">{formatTime(message.createdAt)}</time>

          {!isUser && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: showActions ? 1 : 0 }}
              transition={{ duration: 0.15 }}
              className="flex items-center gap-1"
            >
              <CopyButton text={message.content} size="xs" />
              {onRegenerate && (
                <button
                  onClick={() => onRegenerate(message.id)}
                  className="flex items-center gap-1 text-[11px] rounded-lg px-2 py-1 text-text-secondary hover:text-text-primary hover:bg-white/10 transition-all duration-200"
                  title="Regenerate"
                >
                  <RefreshCw size={11} />
                  Regenerate
                </button>
              )}
            </motion.div>
          )}
        </div>
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center flex-shrink-0 ml-3 mt-1 text-white text-sm font-bold">
          U
        </div>
      )}
    </div>
  )
}

export default MessageBubble
