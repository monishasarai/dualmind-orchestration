import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { User } from '../types'
import * as authStore from '../store/authStore'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string, rememberMe: boolean) => Promise<{ ok: boolean; error?: string }>
  register: (email: string, password: string, displayName: string) => Promise<{ ok: boolean; error?: string }>
  logout: () => void
  updateProfile: (patch: Partial<Pick<User, 'displayName' | 'avatarUrl'>>) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Restore session on mount
  useEffect(() => {
    const session = authStore.getCurrentSession()
    if (session) {
      const u = authStore.getUserById(session.userId)
      setUser(u)
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string, rememberMe: boolean) => {
    const result = await authStore.login(email, password, rememberMe)
    if (result.ok && result.user) setUser(result.user)
    return { ok: result.ok, error: result.error }
  }

  const register = async (email: string, password: string, displayName: string) => {
    const result = await authStore.register(email, password, displayName)
    if (result.ok && result.user) setUser(result.user)
    return { ok: result.ok, error: result.error }
  }

  const logout = () => {
    authStore.logout()
    setUser(null)
  }

  const updateProfile = (patch: Partial<Pick<User, 'displayName' | 'avatarUrl'>>) => {
    if (!user) return
    const updated = authStore.updateUser(user.id, patch)
    if (updated) setUser(updated)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
