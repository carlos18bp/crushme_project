import { test, expect } from '../helpers/test.js';

async function loginAsE2EUser(page) {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL('/en');
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

  // Bug caught: logout leaves local tokens that still grant access to protected routes.
  test('clears a local session from the profile sidebar', {
    tag: ['@flow:auth-logout', '@role:user', '@outcome:success'],
  }, async ({ page }) => {
    await loginAsE2EUser(page);
    await page.goto('/en/profile');
    await expect(page).toHaveURL('/en/profile');

    await page.getByRole('button', { name: 'Logout', exact: true }).click();
    await expect(page).toHaveURL('/en');

    await page.goto('/en/profile');
    await expect(page).toHaveURL(/\/en\/login\?redirect=\/en\/profile$/);
  });
});
