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
  const currentCurrency = ref(localStorage.getItem('currency') || 'USD'); // Default USD until geolocation
  const exchangeRate = ref(null); // Optional: if you want to store the rate
  const isInitialized = ref(false);
  const detectedCountry = ref(null);

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

  function formatPrice(price, includeCurrency = true) {
    if (typeof price !== 'number') {
      return includeCurrency ? `${currencySymbol.value}0.00` : '0.00';
    }

    const formatted = currentCurrency.value === 'COP' 
      ? price.toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
      : price.toFixed(2);

    return includeCurrency ? `${currencySymbol.value}${formatted}` : formatted;
  }

  /**
   * Auto-detect currency based on user's country via IP geolocation
   * COP for Colombia (CO), USD for all other countries
   */
  async function detectCurrency() {
    // If already initialized or user has manually set currency, skip
    if (isInitialized.value) {
      console.log('💱 Currency already initialized:', currentCurrency.value);
      return currentCurrency.value;
    }

    // If user has manually set currency in localStorage, respect it
    const storedCurrency = localStorage.getItem('currency');
    if (storedCurrency) {
      console.log('💱 Using stored currency:', storedCurrency);
      currentCurrency.value = storedCurrency;
      isInitialized.value = true;
      return storedCurrency;
    }

    try {
      console.log('🌍 Detecting currency based on country...');
      const response = await axios.get('https://ipapi.co/json/', {
        timeout: 3000 // 3 seconds timeout
      });
      
      const countryCode = response.data.country_code;
      detectedCountry.value = countryCode;
      
      // COP for Colombia, USD for all other countries
      const detectedCurrency = countryCode === 'CO' ? 'COP' : 'USD';
      
      console.log(`🌍 Country detected: ${countryCode} → Currency: ${detectedCurrency}`);
      
      setCurrency(detectedCurrency);
      isInitialized.value = true;
      
      return detectedCurrency;
    } catch (error) {
      console.warn('⚠️ Failed to detect currency, using default USD:', error.message);
      // Fallback to USD on error
      setCurrency('USD');
      isInitialized.value = true;
      return 'USD';
    }
  }

  /**
   * Initialize currency detection if not already done
   */
  async function initializeIfNeeded() {
    if (!isInitialized.value) {
      await detectCurrency();
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
