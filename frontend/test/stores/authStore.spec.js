import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { createPinia, setActivePinia } from 'pinia';

import { useAuthStore } from '@/stores/modules/authStore';
import { setTokens } from '@/services/request_http';

describe('authStore', () => {
  let mock;

  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    mock = new MockAdapter(axios);
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    mock.restore();
    localStorage.clear();
  });

  test('stores the accepted login session contract', async () => {
    // Fails if a successful login reports success without a usable persisted session.
    const responseData = {
      access: 'access-1',
      refresh: 'refresh-1',
      user: { id: 7, username: 'maya' },
    };
    mock.onPost('/api/auth/login/').reply(200, responseData);
    const store = useAuthStore();

    const result = await store.login({
      username: 'maya',
      password: 'secret-1', // pragma: allowlist secret - deterministic test credential only
    });

    expect(result).toEqual({ success: true, data: responseData });
    expect(store.user).toEqual({ id: 7, username: 'maya' });
    expect(localStorage.getItem('access_token')).toBe('access-1');
    expect(localStorage.getItem('refresh_token')).toBe('refresh-1');
    expect(localStorage.getItem('user')).toBe('{"id":7,"username":"maya"}');
  });

  test('returns the signup verification requirement from the API', async () => {
    // Fails if registration advances without exposing the required email verification step.
    const responseData = { message: 'Check your email', requires_verification: true };
    mock.onPost('/api/auth/signup/').reply(201, responseData);
    const store = useAuthStore();

    const result = await store.register({ email: 'maya@example.com', username: 'maya' });

    expect(result).toEqual({
      success: true,
      data: { message: 'Check your email', requires_verification: true },
      requiresVerification: true,
    });
  });

  test('clears the local session when refresh revocation fails', async () => {
    // Fails if a failed revocation request leaves the browser authenticated.
    setTokens('access-1', 'refresh-1');
    localStorage.setItem('user', '{"id":7,"username":"maya"}');
    mock.onPost('/api/auth/logout/').networkError();
    const store = useAuthStore();

    await store.logout();

    expect(mock.history.post.map((request) => request.url)).toEqual(['/api/auth/logout/']);
    expect(store.user).toBeNull();
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('persists the verified account session', async () => {
    // Fails if email verification succeeds without creating an authenticated browser session.
    const responseData = {
      access: 'verified-access',
      refresh: 'verified-refresh',
      user: { id: 9, username: 'verified-user' },
    };
    mock.onPost('/api/auth/verify-email/').reply(200, responseData);
    const store = useAuthStore();

    const result = await store.verifyEmail({ email: 'verified@example.test', verification_code: '1234' });

    expect(result).toEqual({ success: true, data: responseData });
    expect(store.user).toEqual(responseData.user);
    expect(localStorage.getItem('access_token')).toBe('verified-access');
  });

  test('returns the exact rejected verification message', async () => {
    // Fails if a rejected code is hidden behind a generic verification error.
    mock.onPost('/api/auth/verify-email/').reply(400, {
      verification_code: ['Code expired'],
    });
    const store = useAuthStore();

    const result = await store.verifyEmail({ email: 'verified@example.test', verification_code: '0000' });

    expect(result).toEqual({ success: false, error: 'Code expired' });
    expect(store.error).toBe('Code expired');
    expect(store.user).toBeNull();
  });

  test('exposes the password-reset delivery result', async () => {
    // Fails if password recovery reports success without preserving the server confirmation.
    mock.onPost('/api/auth/forgot-password/').reply(200, { message: 'Reset code sent' });
    const store = useAuthStore();

    const result = await store.forgotPassword('buyer@example.test');

    expect(result).toEqual({ success: true, message: 'Reset code sent' });
    expect(store.isLoading).toBe(false);
  });
});
