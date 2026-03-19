import './assets/style.css';

import {createApp} from 'vue';
import {createI18n} from 'vue-i18n';
import App from './App.vue';
import {createRouter, createWebHistory} from 'vue-router';
import HomeView from './HomeView.vue';
import AboutView from './AboutView.vue';

// Import each language's message strings under its own key
const messages = Object.fromEntries(
    Object.entries(
        import.meta.glob('./i18n/*.json', {eager: true})
    ).map(([key, value]) => {
      const lang = key.substring('./i18n/'.length, './i18n/'.length + 2);
      return [lang, (value as any).default];
    })
);

const routes = [
  {path: '/', component: HomeView},
  {path: '/about', component: AboutView}
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export const i18n = createI18n({
  legacy: false,
  locale: navigator.language,
  fallbackLocale: 'en',
  messages
});

const app = createApp(App);

app.use(router);
app.use(i18n);

app.mount('#app');
