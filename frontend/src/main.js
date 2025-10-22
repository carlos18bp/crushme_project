import { createApp } from 'vue'
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import './style.css'
import App from './App.vue'
import router from './router';
import { i18n, useI18nStore } from './stores/modules/i18nStore';
import { useCurrencyStore } from './stores/modules/currencyStore';
import './utils/debugGeoLocation'; // Debug helpers

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(i18n);

console.log('🚀 [main.js] Iniciando aplicación CrushMe...')
console.log('🚀 [main.js] Environment:', import.meta.env.MODE)

// Initialize i18n in background (non-blocking)
console.log('🌍 [main.js] Inicializando detección de idioma...')
const i18nStore = useI18nStore();
i18nStore.initializeIfNeeded()
  .then(() => {
    console.log('✅ [main.js] Idioma inicializado:', i18nStore.locale)
  })
  .catch(error => {
    console.error('❌ [main.js] Error inicializando idioma:', error);
  });

// Initialize currency detection in background (non-blocking)
console.log('💱 [main.js] Inicializando detección de currency...')
const currencyStore = useCurrencyStore();
currencyStore.initializeIfNeeded()
  .then(() => {
    console.log('✅ [main.js] Currency inicializada:', currencyStore.currentCurrency)
  })
  .catch(error => {
    console.error('❌ [main.js] Error inicializando currency:', error);
  });

// Mount app immediately
console.log('🎨 [main.js] Montando aplicación...')
app.mount('#app');
console.log('✅ [main.js] Aplicación montada correctamente');
