/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'chat-bg': '#343541',
        'chat-input': '#40414f',
        'chat-user': '#343541',
        'chat-assistant': '#444654',
      }
    },
  },
  plugins: [],
}
