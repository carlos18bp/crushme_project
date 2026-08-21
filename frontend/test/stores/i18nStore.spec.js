import axios from 'axios';
import { createPinia, setActivePinia } from 'pinia';

import { i18n, useI18nStore } from '@/stores/modules/i18nStore';

jest.mock('axios', () => ({ get: jest.fn() }));

describe('i18nStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    Object.defineProperty(navigator, 'language', { configurable: true, value: 'es-CO' });
  });

  test('synchronizes a manual locale with the Vue i18n instance', () => {
    // Fails if switching locale updates Pinia but leaves rendered translations unchanged.
    const store = useI18nStore();

    store.setLocale('es');

    expect(store.locale).toBe('es');
    expect(store.detectedLocale).toBe('es');
    expect(i18n.global.locale.value).toBe('es');
  });

  test('uses browser language when geolocation is unavailable', async () => {
    // Fails if an optional geolocation outage prevents locale initialization.
    axios.get.mockRejectedValue(new Error('Geo unavailable'));
    const store = useI18nStore();

    const locale = await store.detectUserLanguage();

    expect(locale).toBe('es');
    expect(store.locale).toBe('es');
    expect(store.countryCode).toBeNull();
    expect(store.isInitialized).toBe(true);
  });
});
