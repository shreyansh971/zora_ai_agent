/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        body: ['DM Sans', 'sans-serif'],
      },
      colors: {
        zora: {
          bg: '#06040f',
          surface: '#0d0a1a',
          border: '#1e1535',
          purple: '#7c3aed',
          'purple-light': '#a78bfa',
          accent: '#e879f9',
        }
      }
    }
  },
  plugins: []
}
