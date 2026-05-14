import LLMMessage from './LLMMessage'

/**
 * Test component to verify LLMMessage functionality
 * This component demonstrates various markdown features
 */
const LLMMessageTest = () => {
  const testMarkdown = `# Overview
This is a test of the LLMMessage component with various markdown features.

## Lists
Here are some bullet points:
- Item 1 with some text
- Item 2 with **bold text**
- Item 3 with *italic text*

And here's a numbered list:
1. First item
2. Second item
3. Third item

## Table Example
| Name | Role | Experience |
|------|------|------------|
| Alice | Developer | 5 years |
| Bob | Designer | 3 years |
| Carol | Manager | 8 years |

## Code Examples

Inline code: \`const message = "Hello World"\`

Code block:
\`\`\`javascript
function greet(name) {
  return \`Hello, \${name}!\`;
}

console.log(greet("World"));
\`\`\`

## Blockquote
> This is a blockquote with some important information.
> It can span multiple lines and looks great!

## Links
Check out [React](https://reactjs.org) and [Tailwind CSS](https://tailwindcss.com).

---

## Edge Cases
Empty content test:
`

  const emptyContent = ""
  const invalidContent = null

  return (
    <div className="p-6 bg-dark-bg min-h-screen">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="bg-dark-surface border border-aqua rounded-lg p-4">
          <h2 className="text-text-primary text-lg font-semibold mb-4">Full Markdown Test</h2>
          <LLMMessage content={testMarkdown} />
        </div>
        
        <div className="bg-dark-surface border border-aqua rounded-lg p-4">
          <h2 className="text-text-primary text-lg font-semibold mb-4">Empty Content Test</h2>
          <LLMMessage content={emptyContent} />
        </div>
        
        <div className="bg-dark-surface border border-aqua rounded-lg p-4">
          <h2 className="text-text-primary text-lg font-semibold mb-4">Invalid Content Test</h2>
          <LLMMessage content={invalidContent} />
        </div>
      </div>
    </div>
  )
}

export default LLMMessageTest
