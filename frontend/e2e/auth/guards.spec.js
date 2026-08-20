import { test, expect } from '../helpers/test.js';

// Bug caught: guests can reach profile or lose the requested destination during login redirect.
test('redirects a guest from profile while preserving the destination', {
  tag: ['@flow:auth-protected-redirect', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Profile', exact: true }).click({ noWaitAfter: true });

  await expect(page).toHaveURL(/\/en\/login\?redirect=\/en\/profile$/);
  await expect.poll(() => new URL(page.url()).searchParams.get('redirect')).toBe('/en/profile');
});

// Bug caught: an authenticated user can return to login instead of being redirected home.
test('redirects an authenticated user away from login', {
  tag: ['@flow:auth-guest-redirect', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL('/en');

  await page.goto('/en/login');

  await expect(page).toHaveURL('/en');
});
