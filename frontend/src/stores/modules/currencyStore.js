/**
 * Currency Store for CrushMe e-commerce application
 * Manages currency selection (COP/USD) and sends X-Currency header to backend
 * Auto-detects currency based on user's country (COP for Colombia, USD for others)
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useCurrencyStore = defineStore('currency', () => {
  // State
  const currentCurrency = ref('USD'); // Default USD, will be set by detectCurrency
  const exchangeRate = ref(null); // Optional: if you want to store the rate
  const isInitialized = ref(false);
  const detectedCountry = ref(null);
  
  // Inicializar desde localStorage si existe
  const storedCurrency = localStorage.getItem('currency');
  if (storedCurrency) {
    console.log('💱 [currencyStore] Inicializando desde localStorage:', storedCurrency);
    currentCurrency.value = storedCurrency;
  }

  // Getters
  const currencySymbol = computed(() => {
    return currentCurrency.value === 'COP' ? '$' : '$';
  });

  const currencyCode = computed(() => currentCurrency.value);

  // Actions
  function setCurrency(currency) {
    if (currency !== 'COP' && currency !== 'USD') {
      console.error('Invalid currency. Must be COP or USD');
      return;
    }
    
    currentCurrency.value = currency;
    localStorage.setItem('currency', currency);
    console.log(`💱 Currency set to: ${currency}`);
  }

  function toggleCurrency() {
    const newCurrency = currentCurrency.value === 'COP' ? 'USD' : 'COP';
    setCurrency(newCurrency);
  }

  function formatPrice(price, includeCurrency = true, showCurrencyCode = false) {
    if (typeof price !== 'number') {
      const zero = includeCurrency ? `${currencySymbol.value}0.00` : '0.00';
      return showCurrencyCode ? `${zero} ${currentCurrency.value}` : zero;
    }

    const formatted = currentCurrency.value === 'COP' 
      ? price.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
      : price.toFixed(2);

    let result = includeCurrency ? `${currencySymbol.value}${formatted}` : formatted;
    
    // Add currency code if requested (e.g., "$10,000 COP" or "$2.50 USD")
    if (showCurrencyCode) {
      result += ` ${currentCurrency.value}`;
    }
    
    return result;
  }

  /**
   * Auto-detect currency based on user's country via IP geolocation
   * COP for Colombia (CO), USD for all other countries
   */
  async function detectCurrency() {
    console.log('💱 [currencyStore] Iniciando detección de currency por IP...')
    console.log('💱 [currencyStore] Estado inicial:', {
      isInitialized: isInitialized.value,
      currentCurrency: currentCurrency.value,
      detectedCountry: detectedCountry.value,
      localStorage: localStorage.getItem('currency')
    })
    
    // If already initialized AND has detectedCountry, skip
    if (isInitialized.value && detectedCountry.value) {
      console.log('💱 [currencyStore] Currency ya inicializada con país detectado:', {
        currency: currentCurrency.value,
        country: detectedCountry.value
      });
      return currentCurrency.value;
    }

    // Si está inicializado pero NO tiene detectedCountry, forzar re-detección
    if (isInitialized.value && !detectedCountry.value) {
      console.log('⚠️ [currencyStore] Inicializado pero sin país detectado, forzando re-detección...')
      isInitialized.value = false
    }

    // If user has manually set currency AND we have detectedCountry, respect it
    const storedCurrency = localStorage.getItem('currency');
    if (storedCurrency && detectedCountry.value) {
      console.log('💱 [currencyStore] Usando currency guardada con país conocido:', {
        storedCurrency,
        detectedCountry: detectedCountry.value
      });
      currentCurrency.value = storedCurrency;
      isInitialized.value = true;
      return storedCurrency;
    }

    try {
      console.log('🌍 [currencyStore] Consultando API de geolocalización...');
      // Usar ip-api.com (sin restricciones CORS, gratis, sin registro)
      const response = await axios.get('http://ip-api.com/json/', {
        timeout: 5000 // 5 seconds timeout (aumentado para producción)
      });
      
      console.log('🌍 [currencyStore] Respuesta de API:', {
        country: response.data.country,
        countryCode: response.data.countryCode,
        city: response.data.city,
        ip: response.data.query,
        fullResponse: response.data
      })
      
      // ip-api.com usa "countryCode" en lugar de "country_code"
      const countryCode = response.data.countryCode;
      detectedCountry.value = countryCode;
      
      // COP for Colombia, USD for all other countries
      const detectedCurrency = countryCode === 'CO' ? 'COP' : 'USD';
      
      console.log('🌍 [currencyStore] Currency detectada:', {
        countryCode: countryCode,
        isColombia: countryCode === 'CO',
        detectedCurrency: detectedCurrency
      });
      
      setCurrency(detectedCurrency);
      isInitialized.value = true;
      
      console.log('✅ [currencyStore] Currency configurada:', {
        currency: currentCurrency.value,
        savedToLocalStorage: localStorage.getItem('currency'),
        isInitialized: isInitialized.value
      })
      
      return detectedCurrency;
    } catch (error) {
      console.error('❌ [currencyStore] Error detectando currency:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        stack: error.stack
      });
      // Fallback to USD on error
      console.warn('⚠️ [currencyStore] Usando USD por defecto debido al error');
      setCurrency('USD');
      isInitialized.value = true;
      return 'USD';
    }
  }

  /**
   * Initialize currency detection if not already done
   */
  async function initializeIfNeeded() {
    console.log('🔄 [currencyStore] initializeIfNeeded llamado. Estado:', {
      isInitialized: isInitialized.value,
      currentCurrency: currentCurrency.value,
      detectedCountry: detectedCountry.value,
      localStorage: localStorage.getItem('currency')
    })
    
    // Si está inicializado pero no tiene detectedCountry, forzar re-detección
    if (isInitialized.value && !detectedCountry.value) {
      console.log('⚠️ [currencyStore] Inicializado pero sin país detectado, forzando re-detección...')
      isInitialized.value = false
    }
    
    if (!isInitialized.value) {
      console.log('🔄 [currencyStore] No está inicializado, detectando currency...')
      await detectCurrency();
    } else {
      console.log('✅ [currencyStore] Ya está inicializado, usando currency actual:', currentCurrency.value)
    }
  }

  return {
    // State
    currentCurrency,
    exchangeRate,
    isInitialized,
    detectedCountry,
    
    // Getters
    currencySymbol,
    currencyCode,
    
    // Actions
    setCurrency,
    toggleCurrency,
    formatPrice,
    detectCurrency,
    initializeIfNeeded
  };
});
