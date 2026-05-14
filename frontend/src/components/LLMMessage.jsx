import { memo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Copy, Check } from 'lucide-react'

const CodeBlock = ({ language, value }) => {
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // clipboard unavailable
    }
  }

  return (
    <div className="relative group my-4 rounded-xl overflow-hidden border border-dark-border">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-black/40 border-b border-dark-border">
        <span className="text-xs font-mono text-text-secondary">{language || 'code'}</span>
        <button
          onClick={copy}
          className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg transition-all duration-200 ${
            copied
              ? 'text-neon-green bg-neon-green/10'
              : 'text-text-secondary hover:text-text-primary hover:bg-white/10'
          }`}
        >
          {copied ? <Check size={12} /> : <Copy size={12} />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <SyntaxHighlighter
        language={language || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: '1rem',
          background: 'rgba(0,0,0,0.5)',
          fontSize: '13px',
          lineHeight: '1.6',
        }}
        showLineNumbers={value.split('\n').length > 5}
        wrapLongLines={false}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  )
}

const LLMMessage = memo(({ content, className = '' }) => {
  if (!content || typeof content !== 'string') {
    return <div className="text-text-secondary italic text-sm"><em>No content to display</em></div>
  }

  const trimmed = content.trim()
  if (!trimmed) {
    return <div className="text-text-secondary italic text-sm"><em>Empty message</em></div>
  }

  return (
    <div
      className={`prose-custom-dark max-w-none ${className}`}
      role="article"
      aria-label="AI response"
    >
      <ReactMarkdown
        components={{
          code({ node, inline, className: cls, children, ...props }) {
            const match = /language-(\w+)/.exec(cls || '')
            const lang = match ? match[1] : ''
            const codeStr = String(children).replace(/\n$/, '')

            if (!inline && (match || codeStr.includes('\n'))) {
              return <CodeBlock language={lang} value={codeStr} />
            }
            return (
              <code
                className="bg-black/30 text-neon-pink px-1.5 py-0.5 rounded text-[13px] font-mono border border-white/10"
                {...props}
              >
                {children}
              </code>
            )
          },
          pre({ children }) {
            // pre is handled inside CodeBlock; pass through
            return <>{children}</>
          },
          h1: ({ children }) => (
            <h1 className="text-text-primary font-bold text-2xl mt-6 mb-3 first:mt-0 border-b border-white/10 pb-2">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-text-primary font-semibold text-xl mt-5 mb-3 first:mt-0">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-text-primary font-semibold text-lg mt-4 mb-2 first:mt-0">{children}</h3>
          ),
          p: ({ children }) => (
            <p className="text-text-primary leading-relaxed my-3 first:mt-0 last:mb-0">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="list-disc pl-6 my-3 space-y-1 text-text-primary marker:text-neon-blue">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-6 my-3 space-y-1 text-text-primary marker:text-text-secondary">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="text-text-primary leading-relaxed">{children}</li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-neon-blue bg-neon-blue/5 pl-4 py-2 my-4 text-text-primary italic rounded-r-lg">{children}</blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border-collapse border border-white/10 rounded-lg overflow-hidden">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="bg-black/30 border border-white/10 px-3 py-2 text-left font-semibold text-text-primary text-sm">{children}</th>
          ),
          td: ({ children }) => (
            <td className="border border-white/10 px-3 py-2 text-text-primary text-sm">{children}</td>
          ),
          a: ({ children, href }) => (
            <a href={href} className="text-neon-blue underline decoration-neon-blue/40 hover:decoration-neon-blue transition-colors" target="_blank" rel="noopener noreferrer">{children}</a>
          ),
          hr: () => <hr className="border-0 border-t border-white/10 my-6" />,
          strong: ({ children }) => <strong className="font-semibold text-text-primary">{children}</strong>,
          em: ({ children }) => <em className="italic text-text-primary">{children}</em>,
        }}
      >
        {trimmed}
      </ReactMarkdown>
    </div>
  )
})

LLMMessage.displayName = 'LLMMessage'
export default LLMMessage
