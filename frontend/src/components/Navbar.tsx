import { Link } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { Sun, Moon, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const navLinks = [
  { label: 'Features', href: '#features' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

const Navbar = () => {
  const { theme, toggleTheme } = useTheme()
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'glass border-b border-white/10 shadow-lg' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="text-2xl font-extrabold neon-text hover:opacity-90 transition-opacity">
            DualMind
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map(link => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm font-medium text-text-secondary hover:text-neon-blue transition-colors duration-200"
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* Desktop actions */}
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-white/10 text-text-secondary hover:text-text-primary transition-all duration-200"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <Link
              to="/login"
              className="px-5 py-2 rounded-full text-sm font-semibold text-text-secondary border border-white/10 hover:bg-white/5 transition-all duration-200"
            >
              Sign In
            </Link>
            <Link
              to="/signup"
              className="px-5 py-2 rounded-full text-sm font-bold border-2 border-neon-blue text-neon-blue hover:bg-neon-blue/10 hover:shadow-neon-blue transition-all duration-300"
            >
              Try Now
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-white/10 text-text-primary transition-colors"
            onClick={() => setMobileOpen(o => !o)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.2 }}
            className="fixed top-[72px] left-0 right-0 z-40 glass border-b border-white/10 px-6 py-6 flex flex-col gap-4 md:hidden"
          >
            {navLinks.map(link => (
              <a
                key={link.label}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="text-base font-medium text-text-primary hover:text-neon-blue transition-colors"
              >
                {link.label}
              </a>
            ))}
            <div className="flex items-center gap-3 pt-2 border-t border-white/10">
              <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-white/10 text-text-secondary transition-colors">
                {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              <Link to="/chat" onClick={() => setMobileOpen(false)} className="flex-1 text-center py-2 rounded-full border border-white/10 text-sm font-semibold text-text-secondary hover:bg-white/5 transition-colors">
                Sign In
              </Link>
              <Link to="/chat" onClick={() => setMobileOpen(false)} className="flex-1 text-center py-2 rounded-full border-2 border-neon-blue text-sm font-bold text-neon-blue hover:bg-neon-blue/10 transition-colors">
                Try Now
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

export default Navbar
