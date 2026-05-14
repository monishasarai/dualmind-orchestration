/**
 * Conversation store — localStorage, keyed per user.
 * Each user gets their own isolated conversation list.
 */
import type { Conversation, Message } from '../types'

const key = (userId: string) => `dm_convs_${userId}`

function load(userId: string): Conversation[] {
  try {
    return JSON.parse(localStorage.getItem(key(userId)) || '[]')
  } catch {
    return []
  }
}

function save(userId: string, convs: Conversation[]): void {
  localStorage.setItem(key(userId), JSON.stringify(convs))
}

function randomId(): string {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

// ── Date grouping ─────────────────────────────────────────────────────────────

export function getDateGroup(isoDate: string): string {
  const now = new Date()
  const d = new Date(isoDate)
  const diffMs = now.getTime() - d.getTime()
  const diffDays = Math.floor(diffMs / 86_400_000)

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays <= 7) return 'Last 7 Days'
  return 'Older'
}

// ── Public API ────────────────────────────────────────────────────────────────

export function getConversations(userId: string): Conversation[] {
  return load(userId).sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
  )
}

export function getConversation(userId: string, convId: string): Conversation | null {
  return load(userId).find(c => c.id === convId) ?? null
}

export function createConversation(userId: string, firstMessage: string): Conversation {
  const now = new Date().toISOString()
  const conv: Conversation = {
    id: randomId(),
    userId,
    title: firstMessage.slice(0, 60) || 'New Chat',
    pinned: false,
    createdAt: now,
    updatedAt: now,
    messages: [],
  }
  const convs = load(userId)
  convs.unshift(conv)
  save(userId, convs)
  return conv
}

export function appendMessages(userId: string, convId: string, messages: Message[]): void {
  const convs = load(userId)
  const idx = convs.findIndex(c => c.id === convId)
  if (idx === -1) return
  convs[idx].messages = [...convs[idx].messages, ...messages]
  convs[idx].updatedAt = new Date().toISOString()
  save(userId, convs)
}

export function renameConversation(userId: string, convId: string, title: string): void {
  const convs = load(userId)
  const idx = convs.findIndex(c => c.id === convId)
  if (idx === -1) return
  convs[idx].title = title.slice(0, 80)
  save(userId, convs)
}

export function togglePin(userId: string, convId: string): void {
  const convs = load(userId)
  const idx = convs.findIndex(c => c.id === convId)
  if (idx === -1) return
  convs[idx].pinned = !convs[idx].pinned
  save(userId, convs)
}

export function deleteConversation(userId: string, convId: string): void {
  const convs = load(userId).filter(c => c.id !== convId)
  save(userId, convs)
}

export function exportMarkdown(conv: Conversation): string {
  const lines: string[] = [
    `# ${conv.title}`,
    `*Exported from DualMind on ${new Date().toLocaleString()}*`,
    '',
  ]
  conv.messages.forEach(m => {
    const role = m.sender === 'user' ? '**You**' : '**DualMind**'
    const time = new Date(m.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    lines.push(`### ${role} — ${time}`)
    lines.push(m.content)
    lines.push('')
  })
  return lines.join('\n')
}

export function exportJSON(conv: Conversation): string {
  return JSON.stringify(conv, null, 2)
}

export function downloadFile(content: string, filename: string, mime: string): void {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
