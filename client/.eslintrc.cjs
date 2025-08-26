/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  root: true,
  extends: [
    'google',
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@vue/eslint-config-typescript'
  ],
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    'comma-dangle': ['error', 'never'],
    'vue/multi-word-component-names': 'off',
    'vue/max-attributes-per-line': ['error', {
      'singleline': 3,
      'multiline': 1
    }]
  }
};
