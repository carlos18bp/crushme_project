import { test, expect } from '../helpers/test.js';

async function loginAsE2EUser(page) {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL('/en');
}

// Bug caught: the create modal closes without persisting or rendering a named wishlist.
test('creates a named wishlist through the profile modal', {
  tag: ['@flow:wishlist-create', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  const wishlistName = `The E2E wishlist ${Date.now()}`;
  await loginAsE2EUser(page);
  await page.goto('/en/profile/wishlist');
  await page.getByRole('button', { name: 'Create Wishlist', exact: true }).click();
  await page.getByTestId('wishlist-name-input').fill(wishlistName);
  await page.getByTestId('wishlist-description-input').fill('The deterministic wishlist for E2E testing.');

  const createResponse = page.waitForResponse(
    (response) => response.url().includes('/api/wishlists/create/')
      && response.request().method() === 'POST',
  );
  await page.locator('button').filter({ hasText: /^Create$/ }).click();

  const response = await createResponse;
  const responseBody = await response.json();
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));

  try {
    expect(response.status()).toBe(201);
    await expect(page.getByRole('heading', { name: wishlistName, exact: true })).toHaveText(wishlistName);
  } finally {
    const cleanupResponse = await page.request.delete(
      `/api/wishlists/${responseBody.wishlist.id}/delete/`,
      { headers: { Authorization: `Bearer ${accessToken}` } },
    );
    expect(cleanupResponse.status()).toBe(200);
  }
});
