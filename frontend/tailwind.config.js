/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0A0A0A',
          surface: '#111111',
          border: '#1A1A1A',
        },
        aqua: {
          DEFAULT: '#00FFFF',
          hover: 'rgba(0, 255, 255, 0.1)',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#B0B0B0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'Manrope', 'system-ui', 'sans-serif'],
      },
      transitionDuration: {
        DEFAULT: '200ms',
      },
      typography: (theme) => ({
        'custom-dark': {
          css: {
            '--tw-prose-body': theme('colors.text.primary'),
            '--tw-prose-headings': theme('colors.text.primary'),
            '--tw-prose-lead': theme('colors.text.secondary'),
            '--tw-prose-links': theme('colors.aqua.DEFAULT'),
            '--tw-prose-bold': theme('colors.text.primary'),
            '--tw-prose-counters': theme('colors.text.secondary'),
            '--tw-prose-bullets': theme('colors.aqua.DEFAULT'),
            '--tw-prose-hr': theme('colors.dark.border'),
            '--tw-prose-quotes': theme('colors.text.primary'),
            '--tw-prose-quote-borders': theme('colors.aqua.DEFAULT'),
            '--tw-prose-captions': theme('colors.text.secondary'),
            '--tw-prose-code': theme('colors.aqua.DEFAULT'),
            '--tw-prose-pre-code': theme('colors.text.primary'),
            '--tw-prose-pre-bg': theme('colors.dark.surface'),
            '--tw-prose-th-borders': theme('colors.dark.border'),
            '--tw-prose-td-borders': theme('colors.dark.border'),
            maxWidth: 'none',
            color: theme('colors.text.primary'),
            lineHeight: '1.6',
            fontSize: '15px',
            h1: {
              fontSize: '1.5em',
              fontWeight: '600',
              marginTop: '1.5em',
              marginBottom: '0.75em',
              color: theme('colors.text.primary'),
            },
            h2: {
              fontSize: '1.25em',
              fontWeight: '600',
              marginTop: '1.25em',
              marginBottom: '0.625em',
              color: theme('colors.text.primary'),
            },
            h3: {
              fontSize: '1.125em',
              fontWeight: '600',
              marginTop: '1.125em',
              marginBottom: '0.5em',
              color: theme('colors.text.primary'),
            },
            'h4, h5, h6': {
              fontSize: '1em',
              fontWeight: '600',
              marginTop: '1em',
              marginBottom: '0.5em',
              color: theme('colors.text.primary'),
            },
            p: {
              marginTop: '0.75em',
              marginBottom: '0.75em',
            },
            'ul, ol': {
              marginTop: '0.75em',
              marginBottom: '0.75em',
              paddingLeft: '1.25em',
            },
            li: {
              marginTop: '0.25em',
              marginBottom: '0.25em',
            },
            'li > p': {
              marginTop: '0.5em',
              marginBottom: '0.5em',
            },
            'ol > li::marker': {
              color: theme('colors.text.secondary'),
            },
            'ul > li::marker': {
              color: theme('colors.aqua.DEFAULT'),
            },
            blockquote: {
              borderLeftColor: theme('colors.aqua.DEFAULT'),
              borderLeftWidth: '3px',
              paddingLeft: '1em',
              fontStyle: 'normal',
              color: theme('colors.text.primary'),
              backgroundColor: 'rgba(0, 255, 255, 0.05)',
              borderRadius: '0.375rem',
              padding: '0.75em 1em',
              margin: '1em 0',
            },
            table: {
              width: '100%',
              marginTop: '1em',
              marginBottom: '1em',
              borderCollapse: 'collapse',
            },
            'thead th': {
              borderBottom: `1px solid ${theme('colors.dark.border')}`,
              paddingBottom: '0.5em',
              paddingLeft: '0.75em',
              paddingRight: '0.75em',
              textAlign: 'left',
              fontWeight: '600',
              color: theme('colors.text.primary'),
              backgroundColor: theme('colors.dark.surface'),
            },
            'tbody td': {
              borderBottom: `1px solid ${theme('colors.dark.border')}`,
              paddingTop: '0.5em',
              paddingBottom: '0.5em',
              paddingLeft: '0.75em',
              paddingRight: '0.75em',
              color: theme('colors.text.primary'),
            },
            'tbody tr:nth-child(even)': {
              backgroundColor: 'rgba(255, 255, 255, 0.02)',
            },
            code: {
              color: theme('colors.aqua.DEFAULT'),
              backgroundColor: theme('colors.dark.surface'),
              borderRadius: '0.25rem',
              padding: '0.125rem 0.25rem',
              fontSize: '0.875em',
              fontWeight: '500',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            pre: {
              backgroundColor: theme('colors.dark.surface'),
              borderRadius: '0.5rem',
              padding: '1rem',
              marginTop: '1em',
              marginBottom: '1em',
              border: `1px solid ${theme('colors.dark.border')}`,
              overflowX: 'auto',
            },
            'pre code': {
              backgroundColor: 'transparent',
              borderRadius: '0',
              padding: '0',
              color: theme('colors.text.primary'),
              fontSize: 'inherit',
              fontWeight: 'inherit',
            },
            a: {
              color: theme('colors.aqua.DEFAULT'),
              textDecoration: 'underline',
              textDecorationColor: 'rgba(0, 255, 255, 0.5)',
              '&:hover': {
                textDecorationColor: theme('colors.aqua.DEFAULT'),
              },
            },
            strong: {
              color: theme('colors.text.primary'),
              fontWeight: '600',
            },
            em: {
              color: theme('colors.text.primary'),
              fontStyle: 'italic',
            },
            hr: {
              borderColor: theme('colors.dark.border'),
              marginTop: '2em',
              marginBottom: '2em',
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
