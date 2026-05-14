import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { Menu } from 'lucide-react'
import ChatInput from '../components/ChatInput'
import ChatWindow from '../components/ChatWindow'
import Sidebar from '../components/Sidebar'
import ProfileMenu from '../components/ProfileMenu'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import type { Conversation, Message } from '../types'
import { hasExecutionDetailsData } from '../utils/executionDetails'
import * as convStore from '../store/conversationStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

interface MessageOptions
  extends Pick<
    Message,
    | 'attachments'
    | 'executionDetails'
    | 'status'
    | 'fallbackUsed'
    | 'fallbackReason'
    | 'fallbackSource'
    | 'lightweightMode'
  > {}

const createMessage = (
  sender: Message['sender'],
  content: string,
  options: MessageOptions = {},
): Message => ({
  id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
  sender,
  content,
  createdAt: new Date().toISOString(),
  ...options,
})

const Chat = () => {
  const { user, isLoading } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()

  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [activeTitle, setActiveTitle] = useState('New Chat')
  const [isTyping, setIsTyping] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  // Guard: while a send is in flight, don't let the activeConvId effect reload messages
  const isSendingRef = useRef(false)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) navigate('/login')
  }, [user, isLoading, navigate])

  // Load conversations for this user on mount
  useEffect(() => {
    if (!user) return
    setConversations(convStore.getConversations(user.id))
  }, [user])

  // When active conversation changes (user clicks sidebar), load its messages
  // BUT skip if we're mid-send (isSendingRef) to avoid wiping optimistic messages
  useEffect(() => {
    if (isSendingRef.current) return
    if (!user || !activeConvId) {
      setMessages([])
      setActiveTitle('New Chat')
      return
    }
    const conv = convStore.getConversation(user.id, activeConvId)
    if (conv) {
      setMessages(conv.messages)
      setActiveTitle(conv.title)
    }
  }, [activeConvId, user])

  const refreshConversations = useCallback(() => {
    if (!user) return
    setConversations(convStore.getConversations(user.id))
  }, [user])

  const client = useMemo(() => axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
  }), [])

  const handleSend = useCallback(async ({ text, file }: { text: string; file?: File }) => {
    if (!user) return

    const attachments = file
      ? [{ filename: file.name, size: file.size, contentType: file.type }]
      : undefined

    const userMessage = createMessage('user', text || (file ? `Uploaded ${file.name}` : ''), { attachments })

    // Mark as sending BEFORE any state changes so the effect guard is active
    isSendingRef.current = true

    // Create conversation on first message
    let convId = activeConvId
    if (!convId) {
      const conv = convStore.createConversation(user.id, text || file?.name || 'New Chat')
      convId = conv.id
      // Update title immediately
      setActiveTitle(conv.title)
      // Set the active conv id — the useEffect will be blocked by isSendingRef
      setActiveConvId(convId)
    }

    // Show user message immediately (optimistic)
    setMessages(prev => [...prev, userMessage])
    setIsTyping(true)

    try {
      let assistantMessage: Message

      if (file) {
        const formData = new FormData()
        formData.append('file', file)
        if (text) formData.append('message', text)

        const res = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        const opts: MessageOptions = {
          status: res.data.status,
          fallbackUsed: res.data.fallback_used,
          fallbackReason: res.data.fallback_reason,
          fallbackSource: res.data.fallback_source,
          lightweightMode: res.data.lightweight_mode,
        }
        if (hasExecutionDetailsData(res.data.execution_details)) {
          opts.executionDetails = res.data.execution_details
        }

        assistantMessage = res.data?.response
          ? createMessage('assistant', res.data.response, opts)
          : createMessage('assistant', 'Your file has been processed. Ask a question to get insights.')
      } else {
        const res = await client.post('/api/chat', { message: text })
        const opts: MessageOptions = {
          status: res.data.status,
          fallbackUsed: res.data.fallback_used,
          fallbackReason: res.data.fallback_reason,
          fallbackSource: res.data.fallback_source,
          lightweightMode: res.data.lightweight_mode,
        }
        if (hasExecutionDetailsData(res.data.execution_details)) {
          opts.executionDetails = res.data.execution_details
        }
        assistantMessage = createMessage('assistant', res.data.response, opts)
      }

      // Persist both messages to store BEFORE clearing the guard
      convStore.appendMessages(user.id, convId!, [userMessage, assistantMessage])

      // Now safe to clear the guard and update UI
      isSendingRef.current = false
      setMessages(prev => [...prev, assistantMessage])
      refreshConversations()

    } catch (error) {
      const detail = axios.isAxiosError(error)
        ? error.response?.data?.detail || error.message
        : 'Unexpected error occurred.'
      const errMsg = createMessage('assistant', `Sorry, I ran into an issue: ${detail}`, { status: 'error' })
      convStore.appendMessages(user.id, convId!, [userMessage, errMsg])
      isSendingRef.current = false
      setMessages(prev => [...prev, errMsg])
      addToast('error', `Request failed: ${detail}`)
      refreshConversations()
    } finally {
      setIsTyping(false)
    }
  }, [user, activeConvId, client, addToast, refreshConversations])

  const handleNewChat = useCallback(() => {
    isSendingRef.current = false
    setActiveConvId(null)
    setMessages([])
    setActiveTitle('New Chat')
  }, [])

  const handleSelectConversation = useCallback((id: string) => {
    if (isTyping) return          // don't switch mid-response
    isSendingRef.current = false  // allow the effect to load messages
    setActiveConvId(id)
    setMobileSidebarOpen(false)
  }, [isTyping])

  const handleDeleteConversation = useCallback((id: string) => {
    if (!user) return
    convStore.deleteConversation(user.id, id)
    if (activeConvId === id) handleNewChat()
    refreshConversations()
    addToast('success', 'Conversation deleted.')
  }, [user, activeConvId, handleNewChat, refreshConversations, addToast])

  const handlePinConversation = useCallback((id: string) => {
    if (!user) return
    convStore.togglePin(user.id, id)
    refreshConversations()
  }, [user, refreshConversations])

  const handleRenameConversation = useCallback((id: string, title: string) => {
    if (!user) return
    convStore.renameConversation(user.id, id, title)
    if (activeConvId === id) setActiveTitle(title)
    refreshConversations()
  }, [user, activeConvId, refreshConversations])

  const handleExport = useCallback((id: string, format: 'md' | 'json') => {
    if (!user) return
    const conv = convStore.getConversation(user.id, id)
    if (!conv) return
    if (format === 'md') {
      convStore.downloadFile(convStore.exportMarkdown(conv), `${conv.title}.md`, 'text/markdown')
    } else {
      convStore.downloadFile(convStore.exportJSON(conv), `${conv.title}.json`, 'application/json')
    }
    addToast('success', `Exported as ${format.toUpperCase()}`)
  }, [user, addToast])

  const handleStopStreaming = () => {
    abortRef.current?.abort()
    setIsStreaming(false)
    setIsTyping(false)
  }

  const handleSuggestedPrompt = (prompt: string) => {
    void handleSend({ text: prompt })
  }

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="flex gap-2">
          <span className="typing-dot w-2.5 h-2.5 rounded-full bg-neon-blue inline-block" />
          <span className="typing-dot w-2.5 h-2.5 rounded-full bg-neon-purple inline-block" />
          <span className="typing-dot w-2.5 h-2.5 rounded-full bg-neon-pink inline-block" />
        </div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="h-screen bg-transparent flex overflow-hidden">
      <Sidebar
        onClearChat={handleNewChat}
        onNewChat={handleNewChat}
        conversations={conversations}
        activeId={activeConvId ?? undefined}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onPinConversation={handlePinConversation}
        onRenameConversation={handleRenameConversation}
        onExportConversation={handleExport}
        isMobileOpen={mobileSidebarOpen}
        onMobileClose={() => setMobileSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col relative z-10 w-full overflow-hidden">
        <header className="flex items-center justify-between px-4 md:px-6 py-3 glass border-b border-white/10 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              className="md:hidden p-2 rounded-lg hover:bg-white/10 text-text-secondary transition-colors"
              onClick={() => setMobileSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              <Menu size={20} />
            </button>
            <span className="text-sm font-semibold text-text-primary truncate max-w-[200px] md:max-w-xs">
              {activeTitle}
            </span>
          </div>
          <ProfileMenu
            displayName={user.displayName}
            avatarUrl={user.avatarUrl}
            email={user.email}
            plan={user.plan}
          />
        </header>

        <ChatWindow
          messages={messages}
          isTyping={isTyping}
          onSuggestedPrompt={handleSuggestedPrompt}
        />

        <ChatInput
          onSend={handleSend}
          disabled={isTyping}
          isStreaming={isStreaming}
          onStopStreaming={handleStopStreaming}
        />
      </div>
    </div>
  )
}

export default Chat
