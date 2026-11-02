/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: '#002366', deep: '#00163f' },
        turquoise: { DEFAULT: '#00ced1', deep: '#007a7c' },
        gold: '#c5a059',
        sand: { DEFAULT: '#f3e9d2', soft: '#f8f2e7' },
        ivory: '#fdfcf8',
        ink: '#57606f',
        card: '#ffffff',
        destructive: '#c92a2a',
        background: 'hsl(45 55% 98%)',
      },
      fontFamily: {
        heading: ['"Instrument Serif"', 'ui-serif', 'Georgia', 'serif'],
        body: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      keyframes: {
        'rise-in': { '0%': { opacity: 0, transform: 'translateY(20px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
      animation: { 'rise-in': 'rise-in .8s cubic-bezier(.16,1,.3,1) both' },
    },
  },
  plugins: [],
}
