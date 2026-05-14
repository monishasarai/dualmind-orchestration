const SignInModal = ({ isOpen, onClose, onSignIn }: { isOpen: boolean; onClose: () => void; onSignIn: (provider: string) => void }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="glass-panel max-w-md w-full rounded-2xl p-8 relative shadow-neon-purple animate-float">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-text-secondary hover:text-text-primary text-xl"
        >
          ✕
        </button>
        
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🔮</div>
          <h2 className="text-2xl font-bold text-text-primary mb-2">Welcome Back</h2>
          <p className="text-text-secondary">Sign in to sync your AI sessions</p>
        </div>

        <div className="space-y-4">
          <button 
            onClick={() => onSignIn('Google')}
            className="w-full py-3 px-4 rounded-lg border border-neon-blue text-neon-blue hover:bg-neon-blue/10 hover:shadow-neon-blue transition-all duration-300 flex items-center justify-center gap-3 font-medium"
          >
            Sign in with Google
          </button>
          <button 
            onClick={() => onSignIn('GitHub')}
            className="w-full py-3 px-4 rounded-lg border border-neon-purple text-neon-purple hover:bg-neon-purple/10 hover:shadow-neon-purple transition-all duration-300 flex items-center justify-center gap-3 font-medium"
          >
            Sign in with GitHub
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignInModal;
