import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Settings, LogOut, Sun, Moon, ChevronDown, Zap } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'

interface ProfileMenuProps {
  displayName?: string
  avatarUrl?: string
  email?: string
  plan?: 'free' | 'pro'
}

const ProfileMenu = ({ displayName = 'User', avatarUrl, email, plan = 'free' }: ProfileMenuProps) => {
  const { theme, toggleTheme } = useTheme()
  const { logout } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const initials = displayName.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()

  const handleLogout = () => {
    logout()
    addToast('info', 'Signed out successfully.')
    navigate('/login')
    setOpen(false)
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 glass rounded-full pl-1 pr-3 py-1 border border-white/10 hover:border-neon-blue/30 transition-all duration-200"
      >
        {avatarUrl ? (
          <img src={avatarUrl} alt={displayName} className="w-8 h-8 rounded-full object-cover" />
        ) : (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white text-xs font-bold">
            {initials}
          </div>
        )}
        <span className="text-sm font-medium text-text-primary hidden sm:block max-w-[120px] truncate">{displayName}</span>
        <ChevronDown size={14} className={`text-text-secondary transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full mt-2 w-56 glass-panel rounded-xl border border-white/10 shadow-xl overflow-hidden z-50"
          >
            {/* User info header */}
            <div className="px-4 py-3 border-b border-white/5">
              <div className="flex items-center gap-3">
                {avatarUrl ? (
                  <img src={avatarUrl} alt={displayName} className="w-10 h-10 rounded-full object-cover" />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                    {initials}
                  </div>
                )}
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-text-primary truncate">{displayName}</p>
                  {email && <p className="text-xs text-text-secondary truncate">{email}</p>}
                </div>
              </div>
              <div className={`mt-2 inline-flex items-center gap-1.5 text-xs px-2 py-0.5 rounded-full ${
                plan === 'pro'
                  ? 'bg-neon-blue/10 text-neon-blue border border-neon-blue/20'
                  : 'bg-white/5 text-text-secondary border border-white/10'
              }`}>
                <Zap size={10} />
                {plan === 'pro' ? 'Pro Plan' : 'Free Plan'}
              </div>
            </div>

            {/* Menu items */}
            <div className="py-1">
              <MenuItem icon={<User size={15} />} label="My Profile" onClick={() => setOpen(false)} />
              <MenuItem icon={<Settings size={15} />} label="Settings" onClick={() => setOpen(false)} />
              <button
                onClick={() => { toggleTheme(); setOpen(false) }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-text-secondary hover:text-text-primary hover:bg-white/5 transition-all duration-150"
              >
                {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </button>
            </div>

            <div className="border-t border-white/5 py-1">
              <MenuItem icon={<LogOut size={15} />} label="Sign Out" onClick={handleLogout} danger />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

const MenuItem = ({
  icon, label, onClick, danger = false
}: {
  icon: React.ReactNode; label: string; onClick: () => void; danger?: boolean
}) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all duration-150 ${
      danger
        ? 'text-red-400 hover:bg-red-400/5'
        : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
    }`}
  >
    {icon}
    {label}
  </button>
)

export default ProfileMenu
