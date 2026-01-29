/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cream': '#faf9f7',
        'text-main': '#1a1a1a',
        'openai': '#10a37f',
        'anthropic': '#d4a574',
        'deepmind': '#4285f4',
        'meta': '#0081fb',
      },
      fontFamily: {
        serif: ['Lora', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
