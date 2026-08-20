import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { createPinia, setActivePinia } from 'pinia';

import {
  clearTokens,
  get_request,
  isAuthenticated,
  setTokens,
} from '@/services/request_http';

describe('request_http', () => {
  let mock;

  beforeEach(() => {
    setActivePinia(createPinia());
    mock = new MockAdapter(axios);
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(() => {
    mock.restore();
    clearTokens();
    localStorage.clear();
  });

  test('builds the contextual request headers', async () => {
    document.cookie = 'csrftoken=csrf-value; path=/';
    localStorage.setItem('currency', 'COP');
    setTokens('access-value', 'refresh-value');
    mock.onGet('/api/products/?lang=en').reply(200, { results: [] });

    await get_request('products/');

    const request = mock.history.get[0];
    expect(request.headers['Accept-Language']).toBe('en');
    expect(request.headers['X-Currency']).toBe('COP');
    expect(request.headers['X-CSRFToken']).toBe('csrf-value');
    expect(request.headers.Authorization).toBe('Bearer access-value');
  });

  test('shares one refresh request across concurrent 401 responses', async () => {
    setTokens('expired-access', 'valid-refresh');
    const replyAfterRefresh = (config) => (
      config.headers.Authorization === 'Bearer fresh-access'
        ? [200, { ok: true }]
        : [401, { detail: 'expired' }]
    );
    mock.onGet('/api/orders/?lang=en').reply(replyAfterRefresh);
    mock.onGet('/api/profile/?lang=en').reply(replyAfterRefresh);
    mock.onPost('/api/auth/token/refresh/').reply(200, {
      access: 'fresh-access',
      refresh: 'rotated-refresh',
    });

    const responses = await Promise.all([
      get_request('orders/'),
      get_request('profile/'),
    ]);

    expect(responses.map(({ status }) => status)).toEqual([200, 200]);
    expect(mock.history.post).toHaveLength(1);
    expect(localStorage.getItem('access_token')).toBe('fresh-access');
    expect(localStorage.getItem('refresh_token')).toBe('rotated-refresh');
  });

  test('clears the complete local authentication state', () => {
    setTokens('access-value', 'refresh-value');
    localStorage.setItem('user', JSON.stringify({ id: 1 }));

    clearTokens();

    expect(isAuthenticated()).toBe(false);
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });
});
