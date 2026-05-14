import { useEffect, useRef, useState } from 'react'
import FileUploader from './FileUploader'

export interface ChatInputProps {
  onSend: (payload: { text: string; file?: File }) => Promise<void> | void
  disabled?: boolean
}

const AUTO_EXPAND_MIN_HEIGHT = 56
const AUTO_EXPAND_MAX_HEIGHT = 160

const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [value, setValue] = useState('')
  const [pendingFile, setPendingFile] = useState<File | undefined>()
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    const el = textAreaRef.current
    if (!el) return
    el.style.height = 'auto'
    const next = Math.min(Math.max(el.scrollHeight, AUTO_EXPAND_MIN_HEIGHT), AUTO_EXPAND_MAX_HEIGHT)
    el.style.height = `${next}px`
  }, [value])

  const reset = () => {
    setValue('')
    setPendingFile(undefined)
  }

  const handleSend = async () => {
    const trimmed = value.trim()
    if (!trimmed && !pendingFile) return
    await onSend({ text: trimmed, file: pendingFile })
    reset()
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void handleSend()
    }
  }

  return (
    <div className="w-full glass-panel border-t border-white/10 z-40 relative">
      {pendingFile ? (
        <div className="flex items-center justify-between border-b border-dark-border px-6 py-3 text-sm text-text-secondary">
          <div className="flex items-center gap-3">
            <span className="flex h-7 w-7 items-center justify-center rounded border border-aqua/50 text-aqua text-xs">
              📄
            </span>
            <div className="min-w-0">
              <p className="truncate font-medium text-text-primary">{pendingFile.name}</p>
              <p className="text-xs text-text-secondary">{Math.round(pendingFile.size / 1024)} KB</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setPendingFile(undefined)}
            className="text-xs font-medium text-aqua hover:opacity-80 transition-opacity duration-200"
          >
            Remove
          </button>
        </div>
      ) : null}
      <div className="max-w-4xl mx-auto flex items-end gap-3 px-6 py-4">
        <FileUploader
          onFileSelected={(file) => setPendingFile(file)}
          disabled={disabled}
        />
        <textarea
          ref={textAreaRef}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything, or drop a file here…"
          className="
            flex-1 resize-none rounded-xl border border-white/10 bg-black/20 backdrop-blur-sm px-5 py-4 text-[15px]
            text-text-primary outline-none transition-all duration-300
            focus:border-neon-blue focus:shadow-neon-blue placeholder:text-text-secondary
            disabled:opacity-50 disabled:cursor-not-allowed
          "
          rows={1}
          disabled={disabled}
          aria-label="Message input"
        />
        <button
          type="button"
          onClick={() => void handleSend()}
          disabled={disabled || (!value.trim() && !pendingFile)}
          className={`
            inline-flex h-12 items-center justify-center rounded-xl px-8 text-sm font-bold
            border border-neon-blue text-neon-blue bg-transparent
            transition-all duration-300 ease-in-out
            hover:bg-neon-blue/20 hover:shadow-neon-blue
            focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neon-blue
            ${disabled || (!value.trim() && !pendingFile) ? 'opacity-50 cursor-not-allowed hover:bg-transparent hover:shadow-none' : ''}
          `}
        >
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatInput
