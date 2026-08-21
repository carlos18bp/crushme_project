import { test, expect } from '../helpers/test.js';

async function fillVerificationCode(page, code = '1234') {
  for (const [index, digit] of [...code].entries()) {
    await page.getByTestId(`verification-code-${index}`).fill(digit);
  }
}

async function loginAsE2EUser(page) {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/\/en\/confirmation\?title=Welcome\+back/);
  await page.goto('/en/profile');
  await expect(page).toHaveURL('/en/profile');
}

async function fillResetPasswordForm(page, password = 'Replacement-password-456!') { // pragma: allowlist secret
  await page.getByRole('textbox', { name: 'New password', exact: true }).fill(password);
  await page.getByRole('textbox', { name: 'Confirm new password', exact: true }).fill(password);
}

// Bug caught: a valid registration does not take a new account to code verification.
test('takes a newly registered account to verification', {
  tag: ['@flow:auth-register', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  const registrationId = Date.now();
  const email = `e2e-register-${registrationId}@example.test`;

  await page.goto('/en/signup');
  await page.getByTestId('signup-username').fill(`e2e_register_${registrationId}`);
  await page.getByTestId('signup-email').fill(email);
  await page.getByTestId('signup-password').fill('E2E-password-123!');
  await page.getByTestId('signup-confirm-password').fill('E2E-password-123!');
  const responsePromise = page.waitForResponse((response) => (
    response.url().includes('/api/auth/signup/') && response.request().method() === 'POST'
  ));

  await page.getByTestId('signup-submit').click();

  expect((await responsePromise).status()).toBe(201);
  await expect(page).toHaveURL(new RegExp(`/en/verification\\?email=${email}$`));
});

// Bug caught: an already-verified email is rejected but the signup form gives the visitor no error state.
test('shows the signup error state for an already registered email', {
  tag: ['@flow:auth-register', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.goto('/en/signup');
  await page.getByTestId('signup-username').fill(`another_user_${Date.now()}`);
  await page.getByTestId('signup-email').fill('e2e-user@example.test');
  await page.getByTestId('signup-password').fill('E2E-password-123!');
  await page.getByTestId('signup-confirm-password').fill('E2E-password-123!');

  await page.getByTestId('signup-submit').click();

  await expect(page.getByRole('dialog')).toContainText('Sign up failed: Error desconocido');
  await expect(page).toHaveURL('/en/signup');
});

// Bug caught: a verified email code does not advance the visitor to the confirmation state.
test('shows verification confirmation after a valid code', {
  tag: ['@flow:auth-verify-email', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.route('**/api/auth/verify-email/', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ access: 'test-access', refresh: 'test-refresh', user: { username: 'verified_user' } }),
  }));
  await page.goto('/en/verification?email=verified@example.test');
  await fillVerificationCode(page);

  await page.getByTestId('verification-submit').click();

  await expect(page).toHaveURL(/\/en\/confirmation\?title=Our\+account\+has\+been\+created\+successfully/);
  await expect(page.getByRole('heading')).toHaveText('Our account has been created successfully. 💖 😍');
});

// Bug caught: a verification-service outage is shown as a successful confirmation instead of an actionable error.
test('shows verification failure feedback after a server error', {
  tag: ['@flow:auth-verify-email', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/verify-email/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Verification service unavailable' }),
  }));
  await page.goto('/en/verification?email=verified@example.test');
  await fillVerificationCode(page);

  await page.getByTestId('verification-submit').click();

  await expect(page.getByRole('dialog')).toContainText('Verification failed: Email verification failed');
  await expect(page.getByTestId('verification-code-0')).toHaveValue('');
});

// Bug caught: a successful resend request does not tell the visitor that a replacement code was sent.
test('confirms that a verification code was resent', {
  tag: ['@flow:auth-resend-verification', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.route('**/api/auth/resend-verification/', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Verification code sent successfully.' }),
  }));
  await page.goto('/en/verification?email=pending@example.test');

  await page.getByTestId('verification-resend').click();

  await expect(page.getByRole('dialog')).toContainText('Verification code sent successfully!');
  await expect(page.getByTestId('verification-resend')).toHaveText('60s');
});

// Bug caught: a rejected resend request omits the address-specific recovery feedback.
test('shows resend rejection feedback for an unknown email', {
  tag: ['@flow:auth-resend-verification', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.route('**/api/auth/resend-verification/', (route) => route.fulfill({
    status: 404,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'User with this email does not exist' }),
  }));
  await page.goto('/en/verification?email=missing@example.test');

  await page.getByTestId('verification-resend').click();

  await expect(page.getByRole('dialog')).toContainText('Failed to resend code: User with this email does not exist');
  await expect(page.getByTestId('verification-resend')).toHaveText('Resend');
});

// Bug caught: a login-service outage is mistaken for a successful session transition.
test('keeps the visitor on login when the login service fails', {
  tag: ['@flow:auth-login', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/login/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Login service unavailable' }),
  }));
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');

  await page.getByTestId('login-submit').click();

  await expect(page.getByRole('dialog')).toContainText('Login failed: Login service unavailable');
  await expect(page).toHaveURL('/en/login');
});

// Bug caught: a valid reset request never advances to the code-entry step.
test('takes a valid password-reset request to code entry', {
  tag: ['@flow:auth-forgot-password', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en/forgot-password');
  await page.getByPlaceholder('Enter your email address').fill('e2e-user@example.test');

  await page.getByRole('button', { name: 'Send instructions', exact: true }).click();

  await expect(page).toHaveURL('/en/reset-code?email=e2e-user@example.test');
});

// Bug caught: an unknown reset email is treated as sent instead of revealing the missing-account error.
test('shows an unknown-account error for password reset', {
  tag: ['@flow:auth-forgot-password', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.goto('/en/forgot-password');
  await page.getByPlaceholder('Enter your email address').fill('missing@example.test');

  await page.getByRole('button', { name: 'Send instructions', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('No account found with this email address');
  await expect(page).toHaveURL('/en/forgot-password');
});

// Bug caught: a password-reset delivery outage redirects the visitor to code entry as though mail was sent.
test('shows password-reset delivery failure feedback', {
  tag: ['@flow:auth-forgot-password', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/forgot-password/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Reset delivery unavailable' }),
  }));
  await page.goto('/en/forgot-password');
  await page.getByPlaceholder('Enter your email address').fill('e2e-user@example.test');

  await page.getByRole('button', { name: 'Send instructions', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Failed to send instructions: Reset delivery unavailable');
  await expect(page).toHaveURL('/en/forgot-password');
});

// Bug caught: entering four reset-code digits does not preserve the entered code when continuing.
test('continues from a complete reset code to password entry', {
  tag: ['@flow:auth-reset-code', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en/reset-code?email=e2e-user@example.test');
  const firstDigit = page.getByRole('textbox', { name: 'Verification code digit 1' });
  const secondDigit = page.getByRole('textbox', { name: 'Verification code digit 2' });
  const thirdDigit = page.getByRole('textbox', { name: 'Verification code digit 3' });
  const fourthDigit = page.getByRole('textbox', { name: 'Verification code digit 4' });
  await firstDigit.fill('1');
  await secondDigit.fill('2');
  await thirdDigit.fill('3');
  await fourthDigit.fill('4');
  await expect(firstDigit).toHaveValue('1');
  await expect(secondDigit).toHaveValue('2');
  await expect(thirdDigit).toHaveValue('3');
  await expect(fourthDigit).toHaveValue('4');

  await page.getByRole('button', { name: 'Verify code', exact: true }).click();

  await expect(page).toHaveURL('/en/reset-password?email=e2e-user@example.test&reset_code=1234');
});

// Bug caught: an incomplete reset code submits instead of giving the visitor the local validation message.
test('shows local validation for an incomplete reset code', {
  tag: ['@flow:auth-reset-code', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.goto('/en/reset-code?email=e2e-user@example.test');
  await page.keyboard.type('12');

  await page.getByRole('button', { name: 'Verify code', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Verification code must be 4 digits');
  await expect(page).toHaveURL('/en/reset-code?email=e2e-user@example.test');
});

// Bug caught: a successful password update never reaches the completion confirmation.
test('shows password-update confirmation after a successful reset', {
  tag: ['@flow:auth-reset-password', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.route('**/api/auth/reset-password/', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Password reset successful. You can now login with your new password.' }),
  }));
  await page.goto('/en/reset-password?email=e2e-user@example.test&reset_code=1234');
  await fillResetPasswordForm(page);

  await page.getByRole('button', { name: 'Update password', exact: true }).click();

  await expect(page).toHaveURL(/\/en\/confirmation\?title=Your\+password\+has\+been\+updated/);
  await expect(page.getByRole('heading')).toHaveText('Your password has been updated. 💋 😍');
});

// Bug caught: an invalid reset code does not expose the expired-session message to the visitor.
test('shows the invalid-code error while resetting a password', {
  tag: ['@flow:auth-reset-password', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.route('**/api/auth/reset-password/', (route) => route.fulfill({
    status: 400,
    contentType: 'application/json',
    body: JSON.stringify({ reset_code: ['Reset code is invalid'] }),
  }));
  await page.goto('/en/reset-password?email=e2e-user@example.test&reset_code=0000');
  await fillResetPasswordForm(page);

  await page.getByRole('button', { name: 'Update password', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Reset session has expired. Please start again.');
  await expect(page).toHaveURL('/en/reset-password?email=e2e-user@example.test&reset_code=0000');
});

// Bug caught: a password-reset service failure appears to complete rather than keeping the visitor on the recovery form.
test('shows password-reset failure feedback after a server error', {
  tag: ['@flow:auth-reset-password', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/reset-password/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Password reset service unavailable' }),
  }));
  await page.goto('/en/reset-password?email=e2e-user@example.test&reset_code=1234');
  await fillResetPasswordForm(page);

  await page.getByRole('button', { name: 'Update password', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Failed to update password: Error desconocido');
  await expect(page).toHaveURL('/en/reset-password?email=e2e-user@example.test&reset_code=1234');
});

// Bug caught: a logout API outage leaves local credentials active after the visitor selects Logout.
test('clears the local session when logout revocation fails', {
  tag: ['@flow:auth-logout', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await loginAsE2EUser(page);
  await page.route('**/api/auth/logout/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ detail: 'Logout service unavailable' }),
  }));

  await page.getByRole('button', { name: 'Logout', exact: true }).click();

  await expect(page).toHaveURL('/en');
  await page.goto('/en/profile');
  await expect(page).toHaveURL('/en/login?redirect=/en/profile');
});
