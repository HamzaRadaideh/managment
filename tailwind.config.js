// tailwind.config.js
const colors = require('tailwindcss/colors')

module.exports = {
    content: [
        "./app/templates/**/*.html",
        "./app/static/src/**/*.{ts,js}"
    ],
    theme: {
        extend: {
            colors: {
                primary: colors.indigo,
                secondary: colors.slate,
                success: colors.emerald,
                warning: colors.amber,
                danger: colors.rose,
            }
        }
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
    ],
}
