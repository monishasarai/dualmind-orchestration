import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Mail, Lock, User, ArrowRight, AlertCircle, Check } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'

const passwordRules = [
  { label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
  { label: 'Contains a number', test: (p: string) => /\d/.test(p) },
  { label: 'Contains a letter', test: (p: string) => /[a-zA-Z]/.test(p) },
]

const Signup = () => {
  const { register } = useAuth()
  const { addToast } = useToast()
  const navigate = useNavigate()

  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [touched, setTouched] = useState(false)

  const allRulesPassed = passwordRules.every(r => r.test(password))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setTouched(true)
    setError('')
    if (!email.trim() || !password || !displayName.trim()) {
      setError('Please fill in all fields.')
      return
    }
    if (!allRulesPassed) {
      setError('Password does not meet requirements.')
      return
    }
    setLoading(true)
    const result = await register(email, password, displayName)
    setLoading(false)
    if (result.ok) {
      addToast('success', 'Account created! Welcome to DualMind.')
      navigate('/chat')
    } else {
      setError(result.error || 'Registration failed.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative py-12">
      <div className="absolute w-[500px] h-[500px] rounded-full bg-neon-purple/8 blur-[120px] top-[-100px] right-[-100px] pointer-events-none" />
      <div className="absolute w-[400px] h-[400px] rounded-full bg-neon-blue/8 blur-[120px] bottom-[-80px] left-[-80px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <Link to="/" className="text-3xl font-extrabold neon-text">DualMind</Link>
          <p className="text-text-secondary mt-2 text-sm">Create your free account</p>
        </div>

        <div className="glass-panel rounded-2xl p-8 border border-white/10">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-sm text-red-400"
              >
                <AlertCircle size={15} className="flex-shrink-0" />
                {error}
              </motion.div>
            )}

            {/* Display name */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">Display Name</label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-secondary" />
                <input
                  type="text"
                  value={displayName}
                  onChange={e => setDisplayName(e.target.value)}
                  placeholder="Your name"
                  className="w-full glass rounded-xl pl-10 pr-4 py-3 text-sm text-text-primary placeholder:text-text-secondary outline-none border border-white/10 focus:border-neon-blue/50 focus:shadow-neon-blue transition-all duration-200"
                  autoComplete="name"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">Email</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-secondary" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full glass rounded-xl pl-10 pr-4 py-3 text-sm text-text-primary placeholder:text-text-secondary outline-none border border-white/10 focus:border-neon-blue/50 focus:shadow-neon-blue transition-all duration-200"
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-secondary" />
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => { setPassword(e.target.value); setTouched(true) }}
                  placeholder="••••••••"
                  className="w-full glass rounded-xl pl-10 pr-11 py-3 text-sm text-text-primary placeholder:text-text-secondary outline-none border border-white/10 focus:border-neon-blue/50 focus:shadow-neon-blue transition-all duration-200"
                  autoComplete="new-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPw(v => !v)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>

              {/* Password rules */}
              {touched && password && (
                <motion.ul
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-2 space-y-1"
                >
                  {passwordRules.map(rule => (
                    <li key={rule.label} className={`flex items-center gap-2 text-xs transition-colors ${rule.test(password) ? 'text-neon-green' : 'text-text-secondary'}`}>
                      <Check size={11} className={rule.test(password) ? 'opacity-100' : 'opacity-30'} />
                      {rule.label}
                    </li>
                  ))}
                </motion.ul>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-neon-blue text-neon-blue font-bold text-sm hover:bg-neon-blue/10 hover:shadow-neon-blue transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex gap-1.5">
                  <span className="typing-dot w-2 h-2 rounded-full bg-neon-blue inline-block" />
                  <span className="typing-dot w-2 h-2 rounded-full bg-neon-blue inline-block" />
                  <span className="typing-dot w-2 h-2 rounded-full bg-neon-blue inline-block" />
                </span>
              ) : (
                <>Create Account <ArrowRight size={16} /></>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-text-secondary mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-neon-blue hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}

export default Signup
