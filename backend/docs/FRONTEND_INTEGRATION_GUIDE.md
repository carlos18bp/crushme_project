# Frontend Integration Guide - Geolocation API

## Quick Start

Replace the external API calls (ipapi.co, ip-api.com) with the new local geolocation endpoint.

## Update currencyStore.js

### Before (External API):
```javascript
async detectCurrency() {
  try {
    // ❌ External API - slow, rate limited, CORS issues
    const response = await axios.get('http://ip-api.com/json/', { timeout: 3000 });
    const countryCode = response.data.countryCode;
    
    if (countryCode === 'CO') {
      currentCurrency.value = 'COP';
    } else {
      currentCurrency.value = 'USD';
    }
  } catch (error) {
    console.error('Currency detection failed:', error);
    currentCurrency.value = 'USD'; // Fallback
  }
}
```

### After (Local API):
```javascript
async detectCurrency() {
  try {
    // ✅ Local API - fast, no rate limits, no CORS
    const response = await axios.get('/api/geolocation/me/', { timeout: 3000 });
    
    // Use recommended currency from backend
    currentCurrency.value = response.data.recommended_currency;
    detectedCountry.value = response.data.country_code;
    
    console.log(`🌍 Country: ${response.data.country_code}, Currency: ${response.data.recommended_currency}`);
  } catch (error) {
    console.error('Currency detection failed:', error);
    currentCurrency.value = 'USD'; // Fallback
  }
}
```

## Update i18nStore.js (Optional)

You can also use the geolocation API to detect country for language selection:

```javascript
async detectUserLanguage() {
  // MÉTODO 1: Idioma del navegador (PRINCIPAL)
  const browserLanguage = navigator.language || navigator.userLanguage;
  const languageCode = browserLanguage.split('-')[0].toLowerCase();
  const detectedLocale = languageCode === 'es' ? 'es' : 'en';
  
  console.log('🌐 Idioma del navegador:', browserLanguage, '→', detectedLocale);
  
  // MÉTODO 2: País por IP (OPCIONAL, para referencia)
  try {
    // ✅ Use local API instead of external
    const response = await axios.get('/api/geolocation/me/', { timeout: 3000 });
    this.countryCode = response.data.country_code;
    console.log('🌍 País detectado:', response.data.country_code);
  } catch (error) {
    console.warn('⚠️ No se pudo detectar país (no crítico)');
    this.countryCode = null;
  }
  
  // Usar idioma del navegador (más confiable)
  this.setLocale(detectedLocale);
  return detectedLocale;
}
```

## API Endpoints

### 1. Auto-detect Client Country (Recommended)

**Endpoint**: `GET /api/geolocation/me/`

**Usage**:
```javascript
const response = await fetch('/api/geolocation/me/');
const data = await response.json();

console.log(data);
// {
//   "ip": "181.49.176.10",
//   "country_code": "CO",
//   "is_colombia": true,
//   "recommended_currency": "COP"
// }
```

### 2. Check Specific IP (Advanced)

**Endpoint**: `POST /api/geolocation/detect/`

**Usage**:
```javascript
const response = await fetch('/api/geolocation/detect/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ip: '8.8.8.8' // Optional - omit to auto-detect
  })
});
const data = await response.json();

console.log(data);
// {
//   "ip": "8.8.8.8",
//   "country_code": "US",
//   "is_colombia": false,
//   "recommended_currency": "USD"
// }
```

## Complete Integration Example

### src/stores/modules/currencyStore.js

```javascript
import { ref } from 'vue';
import { defineStore } from 'pinia';
import axios from 'axios';

export const useCurrencyStore = defineStore('currency', () => {
  const currentCurrency = ref('USD');
  const detectedCountry = ref(null);
  const isInitialized = ref(false);

  async function detectCurrency() {
    // Skip if already initialized
    if (isInitialized.value && detectedCountry.value) {
      console.log('✅ Currency already detected:', currentCurrency.value);
      return currentCurrency.value;
    }

    try {
      console.log('🌍 Detecting country and currency...');
      
      // Call local geolocation API
      const response = await axios.get('/api/geolocation/me/', { 
        timeout: 3000 
      });
      
      // Extract data
      const { country_code, recommended_currency, is_colombia } = response.data;
      
      // Update store
      detectedCountry.value = country_code;
      currentCurrency.value = recommended_currency;
      isInitialized.value = true;
      
      console.log(`✅ Detected: ${country_code} → ${recommended_currency}`);
      console.log(`🇨🇴 Is Colombia: ${is_colombia}`);
      
      return recommended_currency;
      
    } catch (error) {
      console.error('❌ Currency detection failed:', error);
      
      // Fallback to USD
      currentCurrency.value = 'USD';
      isInitialized.value = true;
      
      return 'USD';
    }
  }

  async function initializeIfNeeded() {
    if (!isInitialized.value) {
      await detectCurrency();
    }
  }

  function setCurrency(currency) {
    currentCurrency.value = currency;
    console.log(`💱 Currency set to: ${currency}`);
  }

  return {
    currentCurrency,
    detectedCountry,
    isInitialized,
    detectCurrency,
    initializeIfNeeded,
    setCurrency
  };
}, {
  persist: true // Pinia persist plugin
});
```

### src/main.js

```javascript
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import App from './App.vue';
import { useCurrencyStore } from './stores/modules/currencyStore';

const app = createApp(App);

// Setup Pinia
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
app.use(pinia);

// Initialize currency detection
const currencyStore = useCurrencyStore();
currencyStore.initializeIfNeeded().catch(error => {
  console.warn('Currency detection failed, using default USD:', error);
});

app.mount('#app');
```

## Benefits of Migration

### Performance
- **Before**: 200-500ms (external API)
- **After**: < 50ms (local database)

### Reliability
- **Before**: Rate limited, CORS issues, requires internet
- **After**: No limits, no CORS, works offline

### Privacy
- **Before**: User IP sent to third-party
- **After**: IP processed locally, no external calls

### Cost
- **Before**: Free tier limits, may need paid plan
- **After**: Completely free, no external costs

## Testing

### Development
```javascript
// Test in browser console
fetch('/api/geolocation/me/')
  .then(r => r.json())
  .then(data => console.log(data));
```

### Production
```bash
# Test from command line
curl https://crushme.com.co/api/geolocation/me/
```

## Debugging

### Enable Detailed Logs

```javascript
async function detectCurrency() {
  console.log('🔍 [currencyStore] Starting currency detection...');
  
  try {
    const response = await axios.get('/api/geolocation/me/', { timeout: 3000 });
    
    console.log('📡 [currencyStore] API Response:', response.data);
    console.log('🌍 [currencyStore] Country:', response.data.country_code);
    console.log('💱 [currencyStore] Currency:', response.data.recommended_currency);
    console.log('🇨🇴 [currencyStore] Is Colombia:', response.data.is_colombia);
    
    // ... rest of code
  } catch (error) {
    console.error('❌ [currencyStore] Detection failed:', error);
    console.error('📋 [currencyStore] Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    });
  }
}
```

## Migration Checklist

- [ ] Update `currencyStore.js` to use `/api/geolocation/me/`
- [ ] Remove external API dependencies (ipapi.co, ip-api.com)
- [ ] Test in development environment
- [ ] Test in production environment
- [ ] Verify currency detection works correctly
- [ ] Check console logs for errors
- [ ] Test with VPN (should still work)
- [ ] Test offline (should fallback gracefully)
- [ ] Update documentation
- [ ] Remove old debug utilities if any

## Fallback Strategy

Always implement a fallback in case the API fails:

```javascript
async function detectCurrency() {
  try {
    const response = await axios.get('/api/geolocation/me/', { timeout: 3000 });
    return response.data.recommended_currency;
  } catch (error) {
    console.error('Currency detection failed:', error);
    
    // Fallback 1: Check localStorage
    const stored = localStorage.getItem('currency');
    if (stored) {
      console.log('Using stored currency:', stored);
      return stored;
    }
    
    // Fallback 2: Default to USD
    console.log('Using default currency: USD');
    return 'USD';
  }
}
```

## Support

If you encounter any issues:

1. Check browser console for errors
2. Verify API endpoint is accessible: `/api/geolocation/me/`
3. Check network tab in DevTools
4. Verify backend is running
5. Check backend logs for errors

## Summary

**Replace this**:
```javascript
const response = await axios.get('http://ip-api.com/json/');
const currency = response.data.countryCode === 'CO' ? 'COP' : 'USD';
```

**With this**:
```javascript
const response = await axios.get('/api/geolocation/me/');
const currency = response.data.recommended_currency;
```

✅ Faster, more reliable, no external dependencies!
