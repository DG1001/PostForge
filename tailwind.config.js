module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif']
      },
      colors: {
        'linkedin': '#0077B5'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms')
  ],
}