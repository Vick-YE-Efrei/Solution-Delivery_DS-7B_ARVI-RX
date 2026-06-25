/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        'primary-dark': '#2563eb',
        secondary: '#0f172a',
        surface: '#f8fafc',
        'on-surface': '#1e293b',
        'outline-variant': '#e2e8f0',
        'surface-container-low': '#f1f5f9',
        'surface-container-high': '#e2e8f0',
        'on-surface-variant': '#64748b'
      },
      borderRadius: {
        lg: '12px', xl: '18px', '2xl': '24px', full: '9999px'
      },
      spacing: {
        'section-gap': '48px',
        'container-padding': '32px',
        gutter: '24px',
        base: '8px'
      }
    }
  },
  plugins: []
}
