import {fileURLToPath, URL} from 'node:url';

import {defineConfig} from 'vite';
import vue from '@vitejs/plugin-vue';
// @ts-ignore
import eslint from 'vite-plugin-eslint';
import purgecss from '@fullhuman/postcss-purgecss';

// https://vitejs.dev/config/
export default defineConfig(({mode}) => {
  return {
    plugins: [
      vue(),
      eslint()
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      port: 8010
    },
    css: mode === 'production' ? {
      postcss: {
        plugins: [
          purgecss({
            content: [
              './index.html',
              './src/**/*.{vue,js,ts}'
            ],
            variables: true,
            safelist: {
            // Keep leaflet classes
              standard: [/leaflet-/]
            }
          })
        ]
      }
    } : {}
  };
});
