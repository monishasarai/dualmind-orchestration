import type { FC } from 'react'

const TypingIndicator: FC = () => {
  return (
    <div className="flex justify-start mb-4" role="status" aria-live="polite">
      <div className="flex items-center gap-2 rounded-lg border border-aqua bg-dark-surface px-4 py-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <span
            key={index}
            className="h-2 w-2 rounded-full bg-aqua opacity-60"
            style={{ 
              animation: `pulse 1.4s ease-in-out ${index * 0.2}s infinite` 
            }}
          />
        ))}
        <span className="ml-2 text-sm text-text-secondary">DualMind is thinking…</span>
      </div>
    </div>
  )
}

export default TypingIndicator
