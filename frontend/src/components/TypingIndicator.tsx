const TypingIndicator = () => (
  <div className="flex items-center gap-3 mb-3">
    <div className="w-8 h-8 rounded-full glass flex items-center justify-center flex-shrink-0 shadow-neon-blue text-base">
      🧠
    </div>
    <div className="glass-panel rounded-2xl rounded-tl-none px-5 py-4 border border-white/10">
      <div className="flex items-center gap-1.5">
        <span className="typing-dot w-2 h-2 rounded-full bg-neon-blue inline-block" />
        <span className="typing-dot w-2 h-2 rounded-full bg-neon-purple inline-block" />
        <span className="typing-dot w-2 h-2 rounded-full bg-neon-pink inline-block" />
      </div>
    </div>
  </div>
)

export default TypingIndicator
