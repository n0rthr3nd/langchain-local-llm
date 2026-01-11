/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gemini: {
          bg: '#131314', // Deep dark background
          surface: '#1E1F20', // Card/Surface background
          hover: '#2D2E30', // Hover state
          border: '#37383A', // Border color
          primary: '#4DA6FF', // Primary Blue
          secondary: '#C58AF9', // Secondary Purple (gradient start)
          text: {
            primary: '#E3E3E3',
            secondary: '#A4A7AE',
          }
        },
        // Keeping legacy names mapped to new palette for backward compat initially, 
        // but we will refactor components to use new names.
        'chat-bg': '#131314',
        'chat-input': '#1E1F20',
        'chat-user': '#2D2E30',
        'chat-assistant': '#131314',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
