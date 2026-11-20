import js from '@eslint/js'
import globals from 'globals'
import hooks from 'eslint-plugin-react-hooks'

export default [
  { linterOptions: { reportUnusedDisableDirectives: false } },
  { ignores: ['dist/**', 'node_modules/**'] },
  {
    files: ['src/**/*.{js,jsx}'],
    languageOptions: { ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } }, globals: { ...globals.browser, global: 'readonly', beforeEach: 'readonly' } },
    plugins: { 'react-hooks': hooks },
    rules: {
      'no-undef': js.configs.recommended.rules['no-undef'],
      'no-unreachable': 'error',
      'no-constant-condition': 'error',
      'react-hooks/rules-of-hooks': 'error',
    },
  },
]
