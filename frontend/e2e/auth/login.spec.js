import { test, expect } from '../helpers/test.js';
import { AUTH_LOGIN } from '../helpers/flow-tags.js';

test.describe('authentication login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/en/login');
    await expect(page.getByTestId('login-username')).toBeVisible();
  });

  test('authenticates a verified user', {
    tag: [...AUTH_LOGIN, '@role:user', '@outcome:success'],
  }, async ({ page }) => {
    await page.getByTestId('login-username').fill('e2e_user');
    await page.getByTestId('login-password').fill('E2E-password-123!');
    const loginResponse = page.waitForResponse(
      (response) => response.url().includes('/api/auth/login/') && response.status() === 200,
    );

    await page.getByTestId('login-submit').click();
    await loginResponse;

    await expect.poll(() => page.evaluate(() => localStorage.getItem('access_token'))).toBeTruthy();
    await expect(page).toHaveURL(/\/en\/(confirmation|profile)/);
  });

  test('shows an error for invalid credentials', {
    tag: [...AUTH_LOGIN, '@role:guest', '@outcome:error'],
  }, async ({ page }) => {
    await page.getByTestId('login-username').fill('e2e_user');
    await page.getByTestId('login-password').fill('incorrect-password');
    const loginResponse = page.waitForResponse(
      (response) => response.url().includes('/api/auth/login/') && response.status() === 400,
    );

    await page.getByTestId('login-submit').click();
    await loginResponse;

    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page).toHaveURL(/\/en\/login/);
  });
});
