import { test, expect } from '../helpers/test.js';

async function loginAndOpenDashboard(page) {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Sign In', exact: true }).click();
  await expect(page).toHaveURL('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/\/en\/confirmation\?title=Welcome\+back/);

  // The confirmation screen has no action. Return to the authenticated home view,
  // then enter the profile through the navbar like a user.
  await page.goto('/en');
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  await expect(page).toHaveURL('/en/profile');
}

async function openProfileSection(page, name, expectedUrl) {
  await page.getByRole('link', { name, exact: true }).click();
  await expect(page).toHaveURL(expectedUrl);
}

async function confirmCrushRequest(page) {
  await page.getByRole('button', { name: /Request Verification/ }).click();
  await page.getByRole('button', { name: 'Yes, continue', exact: true }).click();
}

// Bug caught: the dashboard loses the authenticated user's fixture-backed identity or received-gift count.
test('shows the seeded dashboard summary', {
  tag: ['@flow:profile-dashboard', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  await loginAndOpenDashboard(page);

  await expect(page.getByRole('heading', { name: 'Hi @e2e_user 💖 ready to spoil a Crush today?' }))
    .toHaveText('Hi @e2e_user 💖 ready to spoil a Crush today?');
  await expect(page.getByText('1', { exact: true })).toHaveCount(1);
});

// Bug caught: saving an edited profile reports success even though the update request was not accepted.
test('confirms a successful profile update', {
  tag: ['@flow:profile-update', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await page.route('**/api/auth/update_profile/', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ username: 'e2e_user' }),
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Profile', '/en/profile/my-profile');
  await page.getByLabel('First Name').fill('E2E Updated');

  await page.getByRole('button', { name: 'Save Changes', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Perfil actualizado correctamente');
});

// Bug caught: a rejected profile field update leaves the user without the server validation message.
test('shows a rejected profile-update message', {
  tag: ['@flow:profile-update', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await page.route('**/api/auth/update_profile/', (route) => route.fulfill({
    status: 400,
    contentType: 'text/plain',
    body: 'Profile validation rejected',
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Profile', '/en/profile/my-profile');
  await page.getByLabel('First Name').fill('E2E Invalid');

  await page.getByRole('button', { name: 'Save Changes', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Profile validation rejected');
});

// Bug caught: a profile service outage is presented as a saved profile.
test('shows a profile-update service failure', {
  tag: ['@flow:profile-update', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/update_profile/', (route) => route.fulfill({
    status: 500,
    contentType: 'text/plain',
    body: 'Profile service unavailable',
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Profile', '/en/profile/my-profile');
  await page.getByLabel('First Name').fill('E2E Retry');

  await page.getByRole('button', { name: 'Save Changes', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Profile service unavailable');
});

// Bug caught: requesting verification does not give the user the queued-request confirmation.
test('confirms a crush-verification request', {
  tag: ['@flow:profile-crush-verification', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await page.route('**/api/auth/crush/request-verification/', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      crush_verification_status: 'pending',
      crush_requested_at: '2026-08-21T00:00:00Z',
      message: 'Verification request queued',
    }),
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Profile', '/en/profile/my-profile');

  await confirmCrushRequest(page);

  await expect(page.getByRole('dialog')).toContainText('Verification request queued');
});

// Bug caught: a duplicate verification request does not disclose its rejected state.
test('shows a rejected crush-verification request', {
  tag: ['@flow:profile-crush-verification', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await page.route('**/api/auth/crush/request-verification/', (route) => route.fulfill({
    status: 400,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Verification request already exists' }),
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Profile', '/en/profile/my-profile');

  await confirmCrushRequest(page);

  await expect(page.getByRole('dialog')).toContainText('Verification request already exists');
});

// Bug caught: a verification-service outage is mistaken for a submitted request.
test('shows a crush-verification service failure', {
  tag: ['@flow:profile-crush-verification', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/crush/request-verification/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Verification service unavailable' }),
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Profile', '/en/profile/my-profile');

  await confirmCrushRequest(page);

  await expect(page.getByRole('dialog')).toContainText('Verification service unavailable');
});

// Bug caught: the favorites screen omits the deterministic favorite product after profile navigation.
test('shows the seeded favorite product', {
  tag: ['@flow:profile-favorites', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'Favorites', '/en/profile/favorites');

  await expect(page.getByText('1 favorite product', { exact: true })).toHaveText('1 favorite product');
  await expect(page.getByTestId('product-card-900001')).toContainText('E2E Rose Quartz Wand');
});

// Bug caught: removing a favorite leaves the product in the visible favorites list.
test('removes the selected favorite product', {
  tag: ['@flow:profile-favorites', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await page.route('**/api/favorites/products/900001/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Favorite removed' }),
  }));
  page.once('dialog', (dialog) => dialog.accept());
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'Favorites', '/en/profile/favorites');

  await page.getByRole('button', { name: 'Remove from favorites', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'You don\'t have any favorite products' }))
    .toHaveText('You don\'t have any favorite products');
});

// Bug caught: a failed favorite deletion hides the service error from the user.
test('shows a favorite-removal service failure', {
  tag: ['@flow:profile-favorites', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/favorites/products/900001/**', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Favorites service unavailable' }),
  }));
  page.once('dialog', (dialog) => dialog.accept());
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'Favorites', '/en/profile/favorites');

  await page.getByRole('button', { name: 'Remove from favorites', exact: true }).click();

  await expect(page.getByTestId('favorite-removal-error'))
    .toHaveText('Favorites service unavailable');
});

// Bug caught: purchase history does not expose the seeded purchase after sidebar navigation.
test('shows the seeded purchase history', {
  tag: ['@flow:profile-order-history', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'Purchase History', '/en/profile/history');

  await expect(page.getByText('Order #E2E-ORDER-0001', { exact: true }))
    .toHaveText('Order #E2E-ORDER-0001');
});

// Bug caught: a purchase-history outage is rendered as an empty order list instead of a recoverable error.
test('shows a purchase-history service failure', {
  tag: ['@flow:profile-order-history', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/orders/history/**', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'History service unavailable' }),
  }));
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'Purchase History', '/en/profile/history');

  await expect(page.getByRole('heading', { name: 'Error loading orders' })).toHaveText('Error loading orders');
  await expect(page.getByText('History service unavailable', { exact: true }))
    .toHaveText('History service unavailable');
});

// Bug caught: the received-gifts view drops the deterministic gift record after sidebar navigation.
test('shows the seeded received gift', {
  tag: ['@flow:profile-gifts', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Gifts', '/en/profile/my-gifts');

  await expect(page.getByText('Order ID #E2E-GIFT-0001', { exact: true }))
    .toHaveText('Order ID #E2E-GIFT-0001');
  await expect(page.getByText('"A deterministic E2E gift."', { exact: true }))
    .toHaveText('"A deterministic E2E gift."');
});

// Bug caught: switching to sent gifts leaves received records in the active tab.
test('shows the sent-gifts empty state', {
  tag: ['@flow:profile-gifts', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await loginAndOpenDashboard(page);
  await openProfileSection(page, 'My Gifts', '/en/profile/my-gifts');

  await page.getByRole('button', { name: 'Gifts Sent', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'No gifts sent yet' })).toHaveText('No gifts sent yet');
});

// Bug caught: the dashboard feed omits the deterministic activity item after profile navigation.
test('shows the seeded profile feed record', {
  tag: ['@flow:profile-feed', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  await loginAndOpenDashboard(page);

  await expect(page.getByText('E2E deterministic feed update', { exact: true }))
    .toHaveText('E2E deterministic feed update');
});
