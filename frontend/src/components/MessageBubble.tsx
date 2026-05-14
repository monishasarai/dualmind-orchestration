import type { FC } from 'react'
import type { Message } from '../types'
// @ts-ignore - consuming shared tabs component authored in JS
import MessageTabs from './MessageTabs'
import { hasExecutionDetailsData } from '../utils/executionDetails'
// @ts-ignore - LLMMessage is a JSX component with proper typing
import LLMMessage from './LLMMessage'

interface MessageBubbleProps {
  message: Message
}

const formatTime = (iso: string) => {
  const date = new Date(iso)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
const MessageBubble: FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user'

  const renderAssistantContent = () => {
    const details = message.executionDetails
    const showTabs = hasExecutionDetailsData(details)

    if (!showTabs) {
      return <LLMMessage content={message.content} />
    }

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

  return (
    <div
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      aria-label={isUser ? 'User message' : 'Assistant message'}
    >
      <div
        className={`
          max-w-[85%] md:max-w-[75%] rounded-lg px-4 py-3 border transition-all duration-200
          ${
            isUser
              ? 'bg-dark-surface border-aqua text-text-primary'
              : 'bg-dark-surface border-aqua text-text-primary'
          }
        `}
      >
        {isUser ? (
          <p className="text-[15px] leading-6 whitespace-pre-wrap text-text-primary">{message.content}</p>
        ) : (
          renderAssistantContent()
        )}

        {message.attachments?.length ? (
          <ul className="mt-3 space-y-2">
            {message.attachments.map((file) => (
              <li
                key={`${message.id}-${file.filename}`}
                className="flex items-center gap-2 text-sm text-text-secondary"
              >
                <span className="inline-flex h-7 w-7 items-center justify-center rounded border border-aqua/50 text-aqua text-xs">
                  📎
                </span>
                <div className="min-w-0">
                  <p className="truncate font-medium text-text-primary">{file.filename}</p>
                  <p className="text-xs text-text-secondary">
                    {Math.round(file.size / 1024)} KB · {file.contentType}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        ) : null}

        <time className="mt-2 block text-xs text-text-secondary">
          {formatTime(message.createdAt)}
        </time>
      </div>
    </div>
  )
}

export default MessageBubble
