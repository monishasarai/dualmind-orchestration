/**
 * Auth store — pure localStorage, no backend required.
 * Stores users, hashed passwords, and session tokens.
 */
import type { AuthSession, StoredUser, User } from '../types'

const USERS_KEY = 'dm_users'
const SESSION_KEY = 'dm_session'

// ── Crypto helpers ────────────────────────────────────────────────────────────

async function sha256(text: string): Promise<string> {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text))
  return Array.from(new Uint8Array(buf))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}

function randomId(): string {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

// ── User storage ──────────────────────────────────────────────────────────────

function loadUsers(): StoredUser[] {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '[]')
  } catch {
    return []
  }
}

function saveUsers(users: StoredUser[]): void {
  localStorage.setItem(USERS_KEY, JSON.stringify(users))
}

// ── Session storage ───────────────────────────────────────────────────────────

function loadSession(): AuthSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    const s: AuthSession = JSON.parse(raw)
    if (new Date(s.expiresAt) < new Date()) {
      clearSession()
      return null
    }
    return s
  } catch {
    return null
  }
}

function saveSession(session: AuthSession): void {
  const raw = JSON.stringify(session)
  if (session.rememberMe) {
    localStorage.setItem(SESSION_KEY, raw)
  } else {
    sessionStorage.setItem(SESSION_KEY, raw)
  }
}

function clearSession(): void {
  localStorage.removeItem(SESSION_KEY)
  sessionStorage.removeItem(SESSION_KEY)
}

// ── Public API ────────────────────────────────────────────────────────────────

export interface RegisterResult {
  ok: boolean
  error?: string
  user?: User
  session?: AuthSession
}

export interface LoginResult {
  ok: boolean
  error?: string
  user?: User
  session?: AuthSession
}

export async function register(
  email: string,
  password: string,
  displayName: string,
): Promise<RegisterResult> {
  const users = loadUsers()
  const normalised = email.trim().toLowerCase()

  if (users.find(u => u.email === normalised)) {
    return { ok: false, error: 'An account with this email already exists.' }
  }
  if (password.length < 8) {
    return { ok: false, error: 'Password must be at least 8 characters.' }
  }

  const passwordHash = await sha256(password)
  const now = new Date().toISOString()
  const newUser: StoredUser = {
    id: randomId(),
    email: normalised,
    displayName: displayName.trim() || normalised.split('@')[0],
    passwordHash,
    createdAt: now,
    plan: 'free',
  }
  users.push(newUser)
  saveUsers(users)

  const session = createSession(newUser.id, false)
  const { passwordHash: _, ...user } = newUser
  return { ok: true, user, session }
}

export async function login(
  email: string,
  password: string,
  rememberMe: boolean,
): Promise<LoginResult> {
  const users = loadUsers()
  const normalised = email.trim().toLowerCase()
  const stored = users.find(u => u.email === normalised)

  if (!stored) {
    return { ok: false, error: 'Invalid email or password.' }
  }

  const hash = await sha256(password)
  if (hash !== stored.passwordHash) {
    return { ok: false, error: 'Invalid email or password.' }
  }

  const session = createSession(stored.id, rememberMe)
  const { passwordHash: _, ...user } = stored
  return { ok: true, user, session }
}

function createSession(userId: string, rememberMe: boolean): AuthSession {
  const days = rememberMe ? 7 : 1
  const expiresAt = new Date(Date.now() + days * 86_400_000).toISOString()
  const session: AuthSession = { userId, token: randomId(), expiresAt, rememberMe }
  saveSession(session)
  return session
}

export function logout(): void {
  clearSession()
}

export function getCurrentSession(): AuthSession | null {
  return loadSession()
}

export function getUserById(id: string): User | null {
  const users = loadUsers()
  const stored = users.find(u => u.id === id)
  if (!stored) return null
  const { passwordHash: _, ...user } = stored
  return user
}

export function updateUser(id: string, patch: Partial<Pick<User, 'displayName' | 'avatarUrl'>>): User | null {
  const users = loadUsers()
  const idx = users.findIndex(u => u.id === id)
  if (idx === -1) return null
  users[idx] = { ...users[idx], ...patch }
  saveUsers(users)
  const { passwordHash: _, ...user } = users[idx]
  return user
}
