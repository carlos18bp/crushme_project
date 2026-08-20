import { createPinia, setActivePinia } from 'pinia';

import { get_request } from '@/services/request_http';
import { useCurrencyStore } from '@/stores/modules/currencyStore';

jest.mock('@/services/request_http', () => ({
  get_request: jest.fn(),
}));

describe('currencyStore', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    get_request.mockReset();
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  test('restores a saved currency without geolocation', async () => {
    localStorage.setItem('currency', 'USD');
    const store = useCurrencyStore();

    await store.initializeIfNeeded();

    expect(store.currentCurrency).toBe('USD');
    expect(get_request).not.toHaveBeenCalled();
  });

  test('persists the geolocation currency recommendation', async () => {
    get_request.mockResolvedValue({
      data: {
        country_code: 'CO',
        recommended_currency: 'COP',
      },
    });
    const store = useCurrencyStore();

    const result = await store.detectCurrency();

    expect(get_request).toHaveBeenCalledWith('geolocation/me/');
    expect(result).toBe('COP');
    expect(store.currentCurrency).toBe('COP');
    expect(store.detectedCountry).toBe('CO');
    expect(localStorage.getItem('currency')).toBe('COP');
  });

  test('falls back to USD when geolocation fails', async () => {
    get_request.mockRejectedValue(new Error('network unavailable'));
    const store = useCurrencyStore();

    const result = await store.detectCurrency();

    expect(result).toBe('USD');
    expect(store.currentCurrency).toBe('USD');
    expect(store.isInitialized).toBe(true);
    expect(localStorage.getItem('currency')).toBe('USD');
  });

  test('ignores an unsupported currency selection', () => {
    const store = useCurrencyStore();

    const result = store.setCurrency('EUR');

    expect(result).toBe(false);
    expect(store.currentCurrency).toBe('USD');
    expect(localStorage.getItem('currency')).toBeNull();
  });
});
