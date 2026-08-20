import { test, expect } from '../helpers/test.js';

test.describe('authentication login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/en/login');
    await expect(page.getByTestId('login-username')).toBeVisible();
  });

  // Bug caught: valid credentials do not persist a session for protected profile routes.
  test('authenticates a verified user', {
    tag: ['@flow:auth-login', '@role:user', '@outcome:success'],
  }, async ({ page }) => {
    await page.getByTestId('login-username').fill('e2e_user');
    await page.getByTestId('login-password').fill('E2E-password-123!');
    const loginResponse = page.waitForResponse(
      (response) => response.url().includes('/api/auth/login/') && response.status() === 200,
    );

    await page.getByTestId('login-submit').click();
    const response = await loginResponse;

    expect(response.status()).toBe(200);
    await page.goto('/en/profile');

    await expect(page).toHaveURL('/en/profile');
    await expect(
      page.getByRole('heading', { name: 'Hi @e2e_user 💖 ready to spoil a Crush today?' }),
    ).toHaveText('Hi @e2e_user 💖 ready to spoil a Crush today?');
  });

  // Bug caught: rejected credentials navigate as a successful login.
  test('shows an error for invalid credentials', {
    tag: ['@flow:auth-login', '@role:guest', '@outcome:error'],
  }, async ({ page }) => {
    await page.getByTestId('login-username').fill('e2e_user');
    await page.getByTestId('login-password').fill('incorrect-password');
    const loginResponse = page.waitForResponse(
      (response) => response.url().includes('/api/auth/login/') && response.status() === 400,
    );

    await page.getByTestId('login-submit').click();
    const response = await loginResponse;

    expect(response.status()).toBe(400);
    await expect(page.getByRole('dialog')).toContainText('Login failed:');
    await expect(page).toHaveURL(/\/en\/login$/);
  });
});
