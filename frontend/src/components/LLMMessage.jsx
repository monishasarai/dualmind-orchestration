import { memo } from 'react'
import ReactMarkdown from 'react-markdown'

/**
 * LLMMessage Component
 * 
 * A specialized component for rendering LLM-generated content with proper markdown formatting.
 * This component uses react-markdown with custom Tailwind styling to display rich content
 * including headings, lists, tables, code blocks, and more.
 * 
 * Features:
 * - Safe markdown rendering with react-markdown
 * - Custom dark theme typography matching the app's design
 * - Responsive layout that works on all screen sizes
 * - Graceful error handling for malformed content
 * - Optimized with React.memo for performance
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The markdown content to render
 * @param {string} [props.className] - Additional CSS classes to apply
 * @returns {JSX.Element} The rendered LLM message component
 */
const LLMMessage = memo(({ content, className = '' }) => {
  // Handle empty or invalid content
  if (!content || typeof content !== 'string') {
    return (
      <div className={`text-text-secondary italic text-sm ${className}`}>
        <em>No content to display</em>
      </div>
    )
  }

  // Handle empty string content
  const trimmedContent = content.trim()
  if (!trimmedContent) {
    return (
      <div className={`text-text-secondary italic text-sm ${className}`}>
        <em>Empty message</em>
      </div>
    )
  }

  return (
    <div 
      className={`
        prose prose-custom-dark max-w-none
        ${className}
      `}
      role="article"
      aria-label="LLM generated content"
    >
      <ReactMarkdown
        components={{
          // Custom component overrides for better control
          h1: ({ children, ...props }) => (
            <h1 
              className="text-text-primary font-semibold text-2xl mt-6 mb-3 first:mt-0 border-b border-dark-border pb-2" 
              {...props}
            >
              {children}
            </h1>
          ),
          h2: ({ children, ...props }) => (
            <h2 
              className="text-text-primary font-semibold text-xl mt-5 mb-3 first:mt-0" 
              {...props}
            >
              {children}
            </h2>
          ),
          h3: ({ children, ...props }) => (
            <h3 
              className="text-text-primary font-semibold text-lg mt-4 mb-2 first:mt-0" 
              {...props}
            >
              {children}
            </h3>
          ),
          // Enhanced code block styling
          code: ({ node, inline, className, children, ...props }) => {
            if (inline) {
              return (
                <code 
                  className="bg-dark-surface text-aqua px-1.5 py-0.5 rounded text-sm font-mono border border-dark-border"
                  {...props}
                >
                  {children}
                </code>
              )
            }
            return (
              <code 
                className={`block bg-dark-surface text-text-primary p-4 rounded-lg border border-dark-border overflow-x-auto font-mono text-sm ${className || ''}`}
                {...props}
              >
                {children}
              </code>
            )
          },
          pre: ({ children, ...props }) => (
            <pre 
              className="bg-dark-surface border border-dark-border rounded-lg p-0 my-4 overflow-hidden"
              {...props}
            >
              {children}
            </pre>
          ),
          // Enhanced table styling
          table: ({ children, ...props }) => (
            <div className="overflow-x-auto my-4">
              <table 
                className="min-w-full border-collapse border border-dark-border rounded-lg overflow-hidden"
                {...props}
              >
                {children}
              </table>
            </div>
          ),
          th: ({ children, ...props }) => (
            <th 
              className="bg-dark-surface border border-dark-border px-3 py-2 text-left font-semibold text-text-primary"
              {...props}
            >
              {children}
            </th>
          ),
          td: ({ children, ...props }) => (
            <td 
              className="border border-dark-border px-3 py-2 text-text-primary"
              {...props}
            >
              {children}
            </td>
          ),
          // Enhanced blockquote styling
          blockquote: ({ children, ...props }) => (
            <blockquote 
              className="border-l-4 border-aqua bg-aqua/5 pl-4 py-2 my-4 text-text-primary italic rounded-r-md"
              {...props}
            >
              {children}
            </blockquote>
          ),
          // Enhanced list styling
          ul: ({ children, ...props }) => (
            <ul 
              className="list-disc pl-6 my-3 space-y-1 text-text-primary marker:text-aqua"
              {...props}
            >
              {children}
            </ul>
          ),
          ol: ({ children, ...props }) => (
            <ol 
              className="list-decimal pl-6 my-3 space-y-1 text-text-primary marker:text-text-secondary"
              {...props}
            >
              {children}
            </ol>
          ),
          li: ({ children, ...props }) => (
            <li 
              className="text-text-primary leading-relaxed"
              {...props}
            >
              {children}
            </li>
          ),
          // Enhanced link styling
          a: ({ children, href, ...props }) => (
            <a 
              href={href}
              className="text-aqua underline decoration-aqua/50 hover:decoration-aqua transition-colors"
              target="_blank"
              rel="noopener noreferrer"
              {...props}
            >
              {children}
            </a>
          ),
          // Enhanced paragraph styling
          p: ({ children, ...props }) => (
            <p 
              className="text-text-primary leading-relaxed my-3 first:mt-0 last:mb-0"
              {...props}
            >
              {children}
            </p>
          ),
          // Horizontal rule styling
          hr: ({ ...props }) => (
            <hr 
              className="border-0 border-t border-dark-border my-6"
              {...props}
            />
          ),
          // Strong and emphasis styling
          strong: ({ children, ...props }) => (
            <strong 
              className="font-semibold text-text-primary"
              {...props}
            >
              {children}
            </strong>
          ),
          em: ({ children, ...props }) => (
            <em 
              className="italic text-text-primary"
              {...props}
            >
              {children}
            </em>
          ),
        }}
      >
        {trimmedContent}
      </ReactMarkdown>
    </div>
  )
})

LLMMessage.displayName = 'LLMMessage'

export default LLMMessage
