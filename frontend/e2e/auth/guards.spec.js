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
