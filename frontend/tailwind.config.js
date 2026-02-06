/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        x: {
          blue: '#1DA1F2',
          dark: '#14171A',
          grey: '#657786',
          light: '#AAB8C2',
          extralight: '#E1E8ED',
        },
        prism: {
          purple: '#8B5CF6',
          pink: '#EC4899',
          blue: '#3B82F6',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
