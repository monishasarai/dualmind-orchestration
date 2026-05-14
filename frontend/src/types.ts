export type Sender = 'user' | 'assistant'

export interface FileAttachment {
  filename: string
  size: number
  contentType: string
  previewUrl?: string
}

export interface ExecutionStep {
  step?: number
  tool?: string
  status?: string
  executionTime?: number
  purpose?: string
  input?: string
  output?: string
  error?: string
}

export interface ExecutionMetadata {
  sessionId?: string
  status?: string
  executionTime?: number
  iterations?: number
  planScore?: number
  planApproved?: boolean
  fallbackUsed?: boolean
  fallbackReason?: string | null
  fallbackSource?: string | null
  timestampUtc?: string
  lightweightMode?: boolean
  fallbackPayloadKeys?: string[]
  [key: string]: unknown
}

export interface ExecutionDetails {
  planOverview?: string | null
  plan_overview?: string | null
  planSummary?: string | null
  plan?: Record<string, unknown> | null
  verification?: string | null
  executionSteps?: Array<ExecutionStep | string>
  execution_steps?: Array<ExecutionStep | string>
  expectedOutput?: string | null
  expected_output?: string | null
  summary?: string | null
  metadata?: ExecutionMetadata
  reasoning?: string | null
  finalVerification?: Record<string, unknown> | null
  fallbacks?: Record<string, unknown>
}

export interface Message {
  id: string
  sender: Sender
  content: string
  createdAt: string
  attachments?: FileAttachment[]
  executionDetails?: ExecutionDetails
  status?: string
  fallbackUsed?: boolean
  fallbackReason?: string | null
  fallbackSource?: string | null
  lightweightMode?: boolean
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string
  email: string
  displayName: string
  avatarUrl?: string
  createdAt: string
  plan: 'free' | 'pro'
}

/** Stored in localStorage — password is hashed with a simple SHA-256 hex */
export interface StoredUser extends User {
  passwordHash: string
}

export interface AuthSession {
  userId: string
  token: string          // random session token
  expiresAt: string      // ISO string
  rememberMe: boolean
}

// ── Conversations ─────────────────────────────────────────────────────────────

export interface Conversation {
  id: string
  userId: string
  title: string
  pinned: boolean
  createdAt: string
  updatedAt: string
  messages: Message[]
  sessionId?: string
}

// ── UI ────────────────────────────────────────────────────────────────────────

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
}
