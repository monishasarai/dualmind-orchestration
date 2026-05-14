/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: 'var(--bg-color)',
          surface: 'var(--surface-color)',
          border: 'var(--border-color)',
        },
        light: {
          bg: 'var(--bg-color)',
          surface: 'var(--surface-color)',
          border: 'var(--border-color)',
        },
        aqua: {
          DEFAULT: '#00FFFF',
          hover: 'rgba(0, 255, 255, 0.2)',
        },
        neon: {
          pink: '#FF00FF',
          purple: '#B200FF',
          blue: '#00D4FF',
          green: '#39FF14',
          cyan: '#00FFFF',
        },
        text: {
          primary: 'var(--text-primary)',
          secondary: 'var(--text-secondary)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'Manrope', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon-blue': '0 0 10px rgba(0, 212, 255, 0.5), 0 0 20px rgba(0, 212, 255, 0.3)',
        'neon-pink': '0 0 10px rgba(255, 0, 255, 0.5), 0 0 20px rgba(255, 0, 255, 0.3)',
        'neon-purple': '0 0 10px rgba(178, 0, 255, 0.5), 0 0 20px rgba(178, 0, 255, 0.3)',
        'neon-green': '0 0 10px rgba(57, 255, 20, 0.5), 0 0 20px rgba(57, 255, 20, 0.3)',
      },
      animation: {
        'gradient-x': 'gradient-x 15s ease infinite',
        'pulse-glow': 'pulse-glow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        'gradient-x': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center',
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center',
          },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: 1, boxShadow: '0 0 20px rgba(0, 212, 255, 0.4)' },
          '50%': { opacity: .7, boxShadow: '0 0 40px rgba(0, 212, 255, 0.8)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      },
      transitionDuration: {
        DEFAULT: '300ms',
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            '--tw-prose-body': 'var(--text-primary)',
            '--tw-prose-headings': 'var(--text-primary)',
            '--tw-prose-lead': 'var(--text-secondary)',
            '--tw-prose-links': theme('colors.neon.blue'),
            '--tw-prose-bold': 'var(--text-primary)',
            '--tw-prose-counters': 'var(--text-secondary)',
            '--tw-prose-bullets': theme('colors.neon.blue'),
            '--tw-prose-hr': 'var(--border-color)',
            '--tw-prose-quotes': 'var(--text-primary)',
            '--tw-prose-quote-borders': theme('colors.neon.blue'),
            '--tw-prose-captions': 'var(--text-secondary)',
            '--tw-prose-code': theme('colors.neon.pink'),
            '--tw-prose-pre-code': 'var(--text-primary)',
            '--tw-prose-pre-bg': 'var(--surface-color)',
            '--tw-prose-th-borders': 'var(--border-color)',
            '--tw-prose-td-borders': 'var(--border-color)',
            maxWidth: 'none',
            color: 'var(--text-primary)',
            lineHeight: '1.6',
            fontSize: '15px',
            a: {
              color: theme('colors.neon.blue'),
              textDecoration: 'none',
              '&:hover': {
                textShadow: '0 0 8px rgba(0, 212, 255, 0.8)',
              },
            },
            code: {
              color: theme('colors.neon.pink'),
              backgroundColor: 'var(--surface-color)',
              borderRadius: '0.25rem',
              padding: '0.125rem 0.25rem',
              fontWeight: '500',
            },
            pre: {
              backgroundColor: 'var(--surface-color)',
              border: '1px solid var(--border-color)',
              boxShadow: 'inset 0 0 10px rgba(0, 0, 0, 0.2)',
            },
            blockquote: {
              borderLeftColor: theme('colors.neon.blue'),
              borderLeftWidth: '4px',
              backgroundColor: 'rgba(0, 212, 255, 0.05)',
              padding: '0.75em 1em',
              borderRadius: '0 0.5rem 0.5rem 0',
            },
          },
        },
      }),
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
