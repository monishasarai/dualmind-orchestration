import { Link } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { useState } from 'react';
import SignInModal from './SignInModal';

const Sidebar = ({ onClearChat }: { onClearChat: () => void }) => {
  const { theme, toggleTheme } = useTheme();
  const [isSignInOpen, setIsSignInOpen] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState<string | null>(null);
  
  return (
    <>
      <div className="w-64 h-full glass flex flex-col border-r border-dark-border z-20 flex-shrink-0">
        <div className="p-4 border-b border-dark-border">
          <Link
            to="/"
            className="text-2xl font-bold bg-gradient-to-r from-neon-blue to-neon-purple 
                       bg-clip-text text-transparent hover:opacity-90 transition-all duration-200
                       animate-pulse-glow"
          >
            DualMind
          </Link>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin">
          {/* Mock Chat History */}
          <div className="text-xs text-text-secondary uppercase tracking-wider mb-2 font-semibold">
            Recent Sessions
          </div>
          <button className="w-full text-left p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-sm text-text-primary transition-colors">
            Neon UI Design
          </button>
          <button className="w-full text-left p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-sm text-text-primary transition-colors">
            Futuristic Web Dev
          </button>
        </div>
        
        <div className="p-4 border-t border-dark-border space-y-2">
          <button
            onClick={onClearChat}
            className="w-full text-left p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-sm text-text-primary flex items-center gap-2 transition-colors"
          >
            <span>🗑️</span> Clear Chat
          </button>
          <button
            onClick={toggleTheme}
            className="w-full text-left p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-sm text-text-primary flex items-center gap-2 transition-colors"
          >
            <span>{theme === 'dark' ? '☀️' : '🌙'}</span> Toggle Theme
          </button>
          
          <button
            onClick={() => loggedInUser ? setLoggedInUser(null) : setIsSignInOpen(true)}
            className="w-full text-left p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-sm text-neon-blue flex items-center gap-2 transition-colors font-semibold shadow-neon-blue"
          >
            <span>👤</span> {loggedInUser ? `Sign Out (${loggedInUser})` : 'Sign In'}
          </button>
        </div>
      </div>

      <SignInModal 
        isOpen={isSignInOpen} 
        onClose={() => setIsSignInOpen(false)} 
        onSignIn={(provider) => { setLoggedInUser(`User via ${provider}`); setIsSignInOpen(false); }} 
      />
    </>
  );
};

export default Sidebar;
