module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    // Add the Tailwind CSS plugin recommended configuration
    'plugin:tailwindcss/recommended',
    "prettier"
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  settings: {
    react: { version: '18.2' },
    // If you have a custom Tailwind config, add it here
    tailwindcss: {
      config: './tailwind.config.js'
    }
  },
  plugins: [
    'react-refresh',
    // Add the tailwindcss plugin
    'tailwindcss'
  ],
  rules: {
    'react/jsx-no-target-blank': 'off',
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true }
    ],
    // Tailwind CSS rules can go here if you want to customize them
    'tailwindcss/classnames-order': 'warn',
    'tailwindcss/no-custom-classname': 'off',
    'tailwindcss/no-contradicting-classname': 'error',
  },
}
