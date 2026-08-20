import { test, expect } from '../helpers/test.js';

// Bug caught: a registration-delivery failure advances the visitor into verification as if signup succeeded.
test('keeps the visitor on signup when registration returns a server failure', {
  tag: ['@flow:auth-register', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  const registrationId = Date.now();

  await page.route('**/api/auth/signup/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Registration service unavailable' }),
  }));

  await page.goto('/en/signup');
  await page.getByTestId('signup-username').fill(`e2e_registration_${registrationId}`);
  await page.getByTestId('signup-email').fill(`e2e-registration-${registrationId}@example.com`);
  await page.getByTestId('signup-password').fill('E2E-password-123!');
  await page.getByTestId('signup-confirm-password').fill('E2E-password-123!');

  const signupResponse = page.waitForResponse(
    (response) => response.url().includes('/api/auth/signup/') && response.status() === 500,
  );
  await page.getByTestId('signup-submit').click();

  expect((await signupResponse).status()).toBe(500);
  await expect(page.getByRole('dialog')).toContainText('Sign up failed: Error desconocido');
  await expect(page).toHaveURL(/\/en\/signup$/);
});
