import './assets/style.css';

import {createApp} from 'vue';
import App from './App.vue';
import {createRouter, createWebHistory} from 'vue-router';
import HomeView from './HomeView.vue';
import AboutView from './AboutView.vue';

const routes = [
  {path: '/', component: HomeView},
  {path: '/about', component: AboutView}
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

const app = createApp(App);

app.use(router);

app.mount('#app');
