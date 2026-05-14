# LLMMessage Component

## Overview
The `LLMMessage` component is designed to render LLM-generated content with proper markdown formatting. It provides a rich, readable display for assistant messages while maintaining the app's dark theme aesthetic.

## Features
- **Safe Markdown Rendering**: Uses `react-markdown` to safely render markdown content
- **Custom Dark Theme**: Matches the app's aqua/dark color scheme
- **Responsive Design**: Works perfectly on all screen sizes
- **Comprehensive Markdown Support**:
  - Headings (H1-H6)
  - Bullet and numbered lists
  - Tables with proper styling
  - Inline code and code blocks
  - Blockquotes
  - Links (with external targeting)
  - Bold and italic text
  - Horizontal rules
- **Error Handling**: Graceful fallbacks for empty or malformed content
- **Performance Optimized**: Memoized for optimal re-rendering

## Usage

### Basic Usage
```jsx
import LLMMessage from './components/LLMMessage'

function ChatMessage({ content }) {
  return <LLMMessage content={content} />
}
```

### With Custom Styling
```jsx
<LLMMessage 
  content={markdownContent} 
  className="custom-class" 
/>
```

## Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `content` | `string` | Yes | - | The markdown content to render |
| `className` | `string` | No | `''` | Additional CSS classes to apply |

## Styling Architecture

### Scoped Styling
All styling is scoped to the component using:
- Custom `prose-custom-dark` typography class
- Component-specific Tailwind classes
- No global CSS modifications

### Typography Configuration
The component uses a custom Tailwind typography configuration (`prose-custom-dark`) that:
- Uses the app's color palette (aqua, dark-surface, text-primary, etc.)
- Maintains consistent font sizing and spacing
- Provides proper contrast for readability

### Component-Level Overrides
Individual markdown elements have custom components with specific styling:
- **Headers**: Proper hierarchy with aqua accents
- **Code**: Syntax highlighting-ready with dark backgrounds
- **Tables**: Bordered layout with striped rows
- **Lists**: Aqua bullets for unordered, numbered for ordered
- **Links**: Aqua colored with hover effects

## Example Markdown Rendering

When you pass this markdown:
```markdown
# Overview
- Item 1
- Item 2

| Name | Role |
|------|------|
| Alice | Dev |

`console.log("Hello")`
```

It renders as:
- Styled heading with proper spacing
- Aqua-colored bullet points
- Bordered table with dark theme
- Highlighted inline code

## Integration with MessageBubble

The component is automatically used in `MessageBubble.tsx` for assistant messages:
```jsx
{isUser ? (
  <p className="text-[15px] leading-6 whitespace-pre-wrap text-text-primary">
    {message.content}
  </p>
) : (
  <LLMMessage content={message.content} />
)}
```

## Error Handling
The component handles various edge cases:
- **Empty content**: Shows "Empty message" placeholder
- **Null/undefined content**: Shows "No content to display" placeholder
- **Malformed markdown**: react-markdown handles gracefully

## Performance
- Uses `React.memo` to prevent unnecessary re-renders
- Optimized component overrides reduce DOM complexity
- Minimal CSS-in-JS usage for better performance

## Testing
Use the `LLMMessageTest` component to verify functionality with various markdown patterns.
