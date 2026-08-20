import { test, expect } from '../helpers/test.js';

async function loginAsE2EUser(page) {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  const loginResponse = page.waitForResponse(
    (response) => response.url().includes('/api/auth/login/')
      && response.request().method() === 'POST',
  );
  await page.getByTestId('login-submit').click();
  expect((await loginResponse).status()).toBe(200);
  await page.goto('/en/profile');
  await expect(page).toHaveURL('/en/profile');
}

test.describe('critical authentication journeys', () => {
  // Bug caught: an invalid code activates or redirects an account as verified.
  test('rejects an invalid email verification code', {
    tag: ['@flow:auth-verify-email', '@role:guest', '@outcome:error'],
  }, async ({ page }) => {
    await page.goto('/en/verification?email=e2e-user@example.test');

    await page.getByTestId('verification-code-0').fill('0');
    await page.getByTestId('verification-code-1').fill('0');
    await page.getByTestId('verification-code-2').fill('0');
    await page.getByTestId('verification-code-3').fill('0');

    const verificationResponse = page.waitForResponse(
      (response) => response.url().includes('/api/auth/verify-email/')
        && response.request().method() === 'POST',
    );
    await page.getByTestId('verification-submit').click();

    expect((await verificationResponse).status()).toBe(400);
    await expect(page.getByRole('dialog')).toContainText('Invalid verification code');
  });

  // Bug caught: a failed resend starts the cooldown and permanently blocks recovery.
  test('reenables verification resend after a delivery failure', {
    tag: ['@flow:auth-resend-verification', '@role:guest', '@outcome:failure'],
  }, async ({ page }) => {
    await page.route('**/api/auth/resend-verification/', (route) => route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Delivery unavailable' }),
    }));

    await page.goto('/en/verification?email=e2e-user@example.test');
    const resendButton = page.getByTestId('verification-resend');
    const resendResponse = page.waitForResponse(
      (response) => response.url().includes('/api/auth/resend-verification/')
        && response.request().method() === 'POST'
        && response.status() === 500,
    );
    await resendButton.click();

    expect((await resendResponse).status()).toBe(500);
    await expect(page.getByRole('dialog')).toContainText('Failed to resend code: Delivery unavailable');
    await expect(resendButton).toHaveText('Resend');
    await expect(resendButton).toBeEnabled();
  });

  // Bug caught: logout leaves local tokens that still grant access to protected routes.
  test('clears a local session from the profile sidebar', {
    tag: ['@flow:auth-logout', '@role:user', '@outcome:success'],
  }, async ({ page }) => {
    await loginAsE2EUser(page);

    await page.getByRole('button', { name: 'Logout', exact: true }).click();
    await expect(page).toHaveURL('/en');

    await page.goto('/en/profile');
    await expect(page).toHaveURL(/\/en\/login\?redirect=\/en\/profile$/);
  });
});
