/**
 * Currency selection for the CrushMe storefront.
 *
 * A valid user preference wins over IP detection. Without a preference, the
 * backend recommends COP for Colombia and USD for every other country.
 */
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

import { get_request } from '@/services/request_http';

const SUPPORTED_CURRENCIES = new Set(['COP', 'USD']);

function readStoredCurrency() {
  const storedCurrency = localStorage.getItem('currency');
  return SUPPORTED_CURRENCIES.has(storedCurrency) ? storedCurrency : null;
}

export const useCurrencyStore = defineStore('currency', () => {
  const storedCurrency = readStoredCurrency();
  const currentCurrency = ref(storedCurrency || 'USD');
  const exchangeRate = ref(null);
  const isInitialized = ref(Boolean(storedCurrency));
  const detectedCountry = ref(null);

  const currencySymbol = computed(() => '$');
  const currencyCode = computed(() => currentCurrency.value);

  function setCurrency(currency) {
    if (!SUPPORTED_CURRENCIES.has(currency)) {
      console.error('Invalid currency. Must be COP or USD');
      return false;
    }

    currentCurrency.value = currency;
    localStorage.setItem('currency', currency);
    return true;
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

    if (showCurrencyCode) {
      result += ` ${currentCurrency.value}`;
    }

    return result;
  }

  async function detectCurrency() {
    if (isInitialized.value) {
      return currentCurrency.value;
    }

    try {
      const response = await get_request('geolocation/me/');
      const recommendedCurrency = response.data?.recommended_currency;

      if (!SUPPORTED_CURRENCIES.has(recommendedCurrency)) {
        throw new Error('Geolocation returned an unsupported currency');
      }

      detectedCountry.value = response.data?.country_code || null;
      setCurrency(recommendedCurrency);
      isInitialized.value = true;
      return recommendedCurrency;
    } catch (error) {
      console.error('Currency detection failed:', error);
      detectedCountry.value = null;
      setCurrency('USD');
      isInitialized.value = true;
      return 'USD';
    }
  }

  async function initializeIfNeeded() {
    if (!isInitialized.value) {
      return detectCurrency();
    }

    return currentCurrency.value;
  }

  return {
    currentCurrency,
    exchangeRate,
    isInitialized,
    detectedCountry,
    currencySymbol,
    currencyCode,
    setCurrency,
    toggleCurrency,
    formatPrice,
    detectCurrency,
    initializeIfNeeded,
  };
});
