import { Link } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { useState } from 'react'
import SignInModal from './SignInModal'

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();
  const [isSignInOpen, setIsSignInOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState<string | null>(null);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            to="/"
            className="text-2xl font-bold bg-gradient-to-r from-neon-blue to-neon-purple 
                       bg-clip-text text-transparent hover:opacity-90 transition-all duration-200 animate-pulse-glow"
          >
            DualMind
          </Link>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full hover:bg-white/10 text-text-primary transition-colors text-xl"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>
            <button
              onClick={() => loggedInUser ? setLoggedInUser(null) : setIsSignInOpen(true)}
              className="px-6 py-2 rounded-full border border-neon-blue text-neon-blue font-semibold hover:bg-neon-blue/20 hover:shadow-neon-blue transition-all duration-300"
            >
              {loggedInUser ? `Sign Out (${loggedInUser})` : 'Sign In'}
            </button>
          </div>
        </div>
      </nav>

      <SignInModal 
        isOpen={isSignInOpen} 
        onClose={() => setIsSignInOpen(false)} 
        onSignIn={(provider) => { setLoggedInUser(`User via ${provider}`); setIsSignInOpen(false); }} 
      />
    </>
  )
}

export default Navbar
