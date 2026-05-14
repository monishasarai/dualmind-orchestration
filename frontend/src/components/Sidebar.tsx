import { Link } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus, Search, Trash2, Sun, Moon,
  MessageSquare, Pin, X, PenLine, Download, MoreHorizontal
} from 'lucide-react'
import type { Conversation } from '../types'
import { getDateGroup } from '../store/conversationStore'

interface SidebarProps {
  onClearChat?: () => void
  onNewChat?: () => void
  conversations?: Conversation[]
  activeId?: string
  onSelectConversation?: (id: string) => void
  onDeleteConversation?: (id: string) => void
  onPinConversation?: (id: string) => void
  onRenameConversation?: (id: string, title: string) => void
  onExportConversation?: (id: string, format: 'md' | 'json') => void
  isMobileOpen?: boolean
  onMobileClose?: () => void
}

const groupConversations = (convs: Conversation[]) => {
  const groups: Record<string, Conversation[]> = {}
  convs.forEach(c => {
    const g = getDateGroup(c.updatedAt)
    if (!groups[g]) groups[g] = []
    groups[g].push(c)
  })
  return groups
}

const DATE_ORDER = ['Today', 'Yesterday', 'Last 7 Days', 'Older']

const Sidebar = ({
  onNewChat,
  conversations = [],
  activeId,
  onSelectConversation,
  onDeleteConversation,
  onPinConversation,
  onRenameConversation,
  onExportConversation,
  isMobileOpen = true,
  onMobileClose,
}: SidebarProps) => {
  const { theme, toggleTheme } = useTheme()
  const [search, setSearch] = useState('')

  const filtered = conversations.filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase())
  )
  const pinned = filtered.filter(c => c.pinned)
  const unpinned = filtered.filter(c => !c.pinned)
  const groups = groupConversations(unpinned)

  const sidebarContent = (
    <div className="w-64 h-full glass flex flex-col border-r border-dark-border z-20 flex-shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-dark-border flex items-center justify-between">
        <Link to="/" className="text-xl font-extrabold neon-text hover:opacity-90 transition-opacity">
          DualMind
        </Link>
        <div className="flex items-center gap-1">
          <button
            onClick={onNewChat}
            className="p-2 rounded-lg hover:bg-white/10 text-text-secondary hover:text-neon-blue transition-all duration-200"
            title="New chat"
          >
            <Plus size={18} />
          </button>
          {onMobileClose && (
            <button
              onClick={onMobileClose}
              className="p-2 rounded-lg hover:bg-white/10 text-text-secondary transition-colors md:hidden"
            >
              <X size={18} />
            </button>
          )}
        </div>
      </div>

      {/* Search */}
      <div className="px-3 py-3 border-b border-dark-border">
        <div className="flex items-center gap-2 glass rounded-lg px-3 py-2">
          <Search size={14} className="text-text-secondary flex-shrink-0" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search chats…"
            className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-secondary outline-none"
          />
          {search && (
            <button onClick={() => setSearch('')} className="text-text-secondary hover:text-text-primary">
              <X size={12} />
            </button>
          )}
        </div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto py-2 scrollbar-thin">
        {/* Pinned */}
        {pinned.length > 0 && (
          <div className="mb-2">
            <div className="flex items-center gap-2 px-4 py-1.5">
              <Pin size={11} className="text-neon-blue" />
              <span className="text-[11px] font-semibold text-text-secondary uppercase tracking-wider">Pinned</span>
            </div>
            {pinned.map(c => (
              <ConvItem
                key={c.id}
                conv={c}
                active={activeId === c.id}
                onSelect={onSelectConversation}
                onDelete={onDeleteConversation}
                onPin={onPinConversation}
                onRename={onRenameConversation}
                onExport={onExportConversation}
              />
            ))}
            <div className="mx-4 my-2 border-t border-white/5" />
          </div>
        )}

        {/* Grouped by date */}
        {DATE_ORDER.map(date => {
          const items = groups[date]
          if (!items?.length) return null
          return (
            <div key={date} className="mb-2">
              <div className="px-4 py-1.5">
                <span className="text-[11px] font-semibold text-text-secondary uppercase tracking-wider">{date}</span>
              </div>
              {items.map(c => (
                <ConvItem
                  key={c.id}
                  conv={c}
                  active={activeId === c.id}
                  onSelect={onSelectConversation}
                  onDelete={onDeleteConversation}
                  onPin={onPinConversation}
                  onRename={onRenameConversation}
                  onExport={onExportConversation}
                />
              ))}
            </div>
          )
        })}

        {conversations.length === 0 && (
          <div className="px-4 py-10 text-center">
            <MessageSquare size={28} className="mx-auto mb-3 text-text-secondary opacity-40" />
            <p className="text-text-secondary text-sm">No conversations yet</p>
            <p className="text-text-secondary text-xs mt-1 opacity-60">Start a new chat to begin</p>
          </div>
        )}

        {conversations.length > 0 && filtered.length === 0 && (
          <div className="px-4 py-8 text-center text-text-secondary text-sm">
            No results for "{search}"
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-dark-border space-y-1">
        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 text-sm text-text-secondary hover:text-text-primary transition-all duration-200 group"
        >
          {theme === 'dark'
            ? <Sun size={15} className="group-hover:scale-110 transition-transform" />
            : <Moon size={15} className="group-hover:scale-110 transition-transform" />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop */}
      <div className="hidden md:flex h-full">{sidebarContent}</div>

      {/* Mobile drawer */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-30 md:hidden"
              onClick={onMobileClose}
            />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="fixed left-0 top-0 bottom-0 z-40 md:hidden"
            >
              {sidebarContent}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

// ── Conversation item ──────────────────────────────────────────────────────────

interface ConvItemProps {
  conv: Conversation
  active: boolean
  onSelect?: (id: string) => void
  onDelete?: (id: string) => void
  onPin?: (id: string) => void
  onRename?: (id: string, title: string) => void
  onExport?: (id: string, format: 'md' | 'json') => void
}

const ConvItem = ({ conv, active, onSelect, onDelete, onPin, onRename, onExport }: ConvItemProps) => {
  const [menuOpen, setMenuOpen] = useState(false)
  const [renaming, setRenaming] = useState(false)
  const [renameVal, setRenameVal] = useState(conv.title)
  const menuRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (renaming) inputRef.current?.focus()
  }, [renaming])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const commitRename = () => {
    const trimmed = renameVal.trim()
    if (trimmed && trimmed !== conv.title) onRename?.(conv.id, trimmed)
    setRenaming(false)
  }

  return (
    <div
      className={`group relative flex items-center gap-2 mx-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 ${
        active ? 'bg-neon-blue/10 border border-neon-blue/20' : 'hover:bg-white/5'
      }`}
      onClick={() => !renaming && onSelect?.(conv.id)}
    >
      <MessageSquare size={14} className={`flex-shrink-0 ${active ? 'text-neon-blue' : 'text-text-secondary'}`} />

      {renaming ? (
        <input
          ref={inputRef}
          value={renameVal}
          onChange={e => setRenameVal(e.target.value)}
          onBlur={commitRename}
          onKeyDown={e => {
            if (e.key === 'Enter') commitRename()
            if (e.key === 'Escape') { setRenameVal(conv.title); setRenaming(false) }
          }}
          onClick={e => e.stopPropagation()}
          className="flex-1 bg-transparent text-sm text-text-primary outline-none border-b border-neon-blue/50"
        />
      ) : (
        <span className={`flex-1 text-sm truncate ${active ? 'text-neon-blue font-medium' : 'text-text-primary'}`}>
          {conv.title}
        </span>
      )}

      {/* Context menu trigger */}
      <div
        ref={menuRef}
        className="relative flex-shrink-0"
        onClick={e => e.stopPropagation()}
      >
        <button
          onClick={() => setMenuOpen(o => !o)}
          className={`p-1 rounded hover:bg-white/10 text-text-secondary hover:text-text-primary transition-colors ${
            menuOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
          }`}
        >
          <MoreHorizontal size={14} />
        </button>

        <AnimatePresence>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -4 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -4 }}
              transition={{ duration: 0.12 }}
              className="absolute right-0 top-full mt-1 w-44 glass-panel rounded-xl border border-white/10 shadow-lg z-50 overflow-hidden"
            >
              <CtxItem icon={<PenLine size={13} />} label="Rename" onClick={() => { setRenaming(true); setMenuOpen(false) }} />
              <CtxItem icon={<Pin size={13} />} label={conv.pinned ? 'Unpin' : 'Pin'} onClick={() => { onPin?.(conv.id); setMenuOpen(false) }} />
              <CtxItem icon={<Download size={13} />} label="Export as MD" onClick={() => { onExport?.(conv.id, 'md'); setMenuOpen(false) }} />
              <CtxItem icon={<Download size={13} />} label="Export as JSON" onClick={() => { onExport?.(conv.id, 'json'); setMenuOpen(false) }} />
              <div className="border-t border-white/5" />
              <CtxItem icon={<Trash2 size={13} />} label="Delete" onClick={() => { onDelete?.(conv.id); setMenuOpen(false) }} danger />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

const CtxItem = ({ icon, label, onClick, danger = false }: {
  icon: React.ReactNode; label: string; onClick: () => void; danger?: boolean
}) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-2.5 px-3 py-2 text-xs transition-colors ${
      danger ? 'text-red-400 hover:bg-red-400/5' : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
    }`}
  >
    {icon}
    {label}
  </button>
)

export default Sidebar
