import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, Send, X, Square } from 'lucide-react'
import FileUploader from './FileUploader'

export interface ChatInputProps {
  onSend: (payload: { text: string; file?: File }) => Promise<void> | void
  disabled?: boolean
  isStreaming?: boolean
  onStopStreaming?: () => void
}

const MAX_HEIGHT = 200
const MIN_HEIGHT = 56

const ChatInput = ({ onSend, disabled, isStreaming, onStopStreaming }: ChatInputProps) => {
  const [value, setValue] = useState('')
  const [pendingFile, setPendingFile] = useState<File | undefined>()
  const [isListening, setIsListening] = useState(false)
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null)
  const recognitionRef = useRef<any>(null)

  // Auto-expand textarea
  useEffect(() => {
    const el = textAreaRef.current
    if (!el) return
    el.style.height = 'auto'
    const next = Math.min(Math.max(el.scrollHeight, MIN_HEIGHT), MAX_HEIGHT)
    el.style.height = `${next}px`
  }, [value])

  // Ctrl+K / Cmd+K focus shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        textAreaRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const reset = () => {
    setValue('')
    setPendingFile(undefined)
    if (textAreaRef.current) textAreaRef.current.style.height = `${MIN_HEIGHT}px`
  }

  const handleSend = useCallback(async () => {
    const trimmed = value.trim()
    if (!trimmed && !pendingFile) return
    await onSend({ text: trimmed, file: pendingFile })
    reset()
  }, [value, pendingFile, onSend])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSend()
    }
  }

  const handleVoice = () => {
    const SpeechRecognitionAPI =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognitionAPI) return

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
      return
    }

    const recognition = new SpeechRecognitionAPI()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'
    recognition.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript
      setValue(prev => prev ? `${prev} ${transcript}` : transcript)
    }
    recognition.onend = () => setIsListening(false)
    recognition.onerror = () => setIsListening(false)
    recognitionRef.current = recognition
    recognition.start()
    setIsListening(true)
  }

  const canSend = (value.trim() || pendingFile) && !disabled && !isStreaming

  return (
    <div className="w-full glass-panel border-t border-white/10 z-40 relative">
      {/* File preview */}
      <AnimatePresence>
        {pendingFile && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="flex items-center justify-between border-b border-dark-border px-6 py-3 text-sm overflow-hidden"
          >
            <div className="flex items-center gap-3">
              <span className="flex h-7 w-7 items-center justify-center rounded border border-neon-blue/40 text-neon-blue text-xs">📄</span>
              <div className="min-w-0">
                <p className="truncate font-medium text-text-primary">{pendingFile.name}</p>
                <p className="text-xs text-text-secondary">{Math.round(pendingFile.size / 1024)} KB</p>
              </div>
            </div>
            <button onClick={() => setPendingFile(undefined)} className="text-text-secondary hover:text-red-400 transition-colors">
              <X size={16} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-end gap-2 glass rounded-2xl px-4 py-3 border border-white/10 focus-within:border-neon-blue/50 focus-within:shadow-neon-blue transition-all duration-300">
          {/* File upload */}
          <FileUploader onFileSelected={setPendingFile} disabled={disabled} />

          {/* Textarea */}
          <textarea
            ref={textAreaRef}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything… (Ctrl+K to focus)"
            className="flex-1 resize-none bg-transparent text-[15px] text-text-primary outline-none placeholder:text-text-secondary disabled:opacity-50 disabled:cursor-not-allowed leading-relaxed py-1"
            style={{ minHeight: `${MIN_HEIGHT - 24}px`, maxHeight: `${MAX_HEIGHT}px` }}
            rows={1}
            disabled={disabled && !isStreaming}
            aria-label="Message input"
          />

          {/* Voice */}
          <button
            type="button"
            onClick={handleVoice}
            className={`p-2 rounded-lg transition-all duration-200 flex-shrink-0 ${
              isListening
                ? 'text-red-400 bg-red-400/10 animate-pulse'
                : 'text-text-secondary hover:text-neon-blue hover:bg-neon-blue/10'
            }`}
            title={isListening ? 'Stop listening' : 'Voice input'}
          >
            {isListening ? <MicOff size={18} /> : <Mic size={18} />}
          </button>

          {/* Send / Stop */}
          {isStreaming ? (
            <button
              type="button"
              onClick={onStopStreaming}
              className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-xl bg-red-500/10 border border-red-500/40 text-red-400 hover:bg-red-500/20 transition-all duration-200"
              title="Stop generating"
            >
              <Square size={16} />
            </button>
          ) : (
            <button
              type="button"
              onClick={() => void handleSend()}
              disabled={!canSend}
              className={`flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-xl transition-all duration-300 ${
                canSend
                  ? 'bg-neon-blue/10 border border-neon-blue text-neon-blue hover:bg-neon-blue/20 hover:shadow-neon-blue'
                  : 'border border-white/10 text-text-secondary opacity-40 cursor-not-allowed'
              }`}
              title="Send (Enter)"
            >
              <Send size={16} />
            </button>
          )}
        </div>

        <p className="text-center text-[11px] text-text-secondary mt-2 opacity-60">
          Shift+Enter for new line · Ctrl+K to focus
        </p>
      </div>
    </div>
  )
}

export default ChatInput
