/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
        'comfortaa': ['Comfortaa', 'cursive'],
      },
      colors: {
        'brand': {
          'pink-light': '#E9C3CD',
          'pink-lighter': '#FAF3F3',
          'pink-medium': '#D689A2',
          'pink-dark': '#BF5E81',
          'blue-medium': '#406582',
          'blue-light': '#A4C1D0',
          'dark': '#11181E',
        },
      },
    },
  },
  plugins: [],
}
