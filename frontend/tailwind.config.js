/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        philosopher: '#6366f1',
        comedian: '#f59e0b',
        scientist: '#10b981',
      }
    },
  },
  plugins: [],
}