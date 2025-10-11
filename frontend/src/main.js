import { createApp } from 'vue'
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import './style.css'
import App from './App.vue'
import router from './router';
import { i18n, useI18nStore } from './stores/modules/i18nStore';

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(i18n);

// Initialize i18n before mounting the app
const i18nStore = useI18nStore();
i18nStore.initializeIfNeeded().then(() => {
  app.mount('#app');
});
