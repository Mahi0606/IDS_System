/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ids-dark': '#0f172a',
        'ids-darker': '#020617',
        'ids-accent': '#3b82f6',
      },
    },
  },
  plugins: [],
}

