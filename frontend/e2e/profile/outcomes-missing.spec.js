import { test, expect } from '../helpers/test.js';

const profileResponse = {
  id: 1,
  username: 'e2e_user',
  email: 'e2e-user@example.test',
  first_name: 'E2E',
  last_name: 'User',
  addresses: [],
  links: [],
  gallery_photos: [],
  crush_verification_status: 'none',
};

async function loginAndOpenProfile(page, username = 'e2e_user', password = 'E2E-password-123!') {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill(username);
  await page.getByTestId('login-password').fill(password);
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/\/en\/confirmation\?/);
  // The confirmation view auto-redirects to Profile; return Home explicitly for deterministic setup.
  await page.goto('/en');
  await expect(page).toHaveURL('/en');
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  await expect(page).toHaveURL('/en/profile');
}

async function openMyProfile(page) {
  await page.getByRole('link', { name: 'My Profile', exact: true }).click();
  await expect(page).toHaveURL('/en/profile/my-profile');
}

async function selectProfileImage(page, name = 'profile.png', mimeType = 'image/png') {
  await page.getByTestId('profile-picture-input').setInputFiles({
    name,
    mimeType,
    buffer: Buffer.from('deterministic-profile-image'),
  });
}

// Bug caught: a profile API outage falls back to a generic user greeting.
test('shows a dashboard profile-loading failure', {
  tag: ['@flow:profile-dashboard', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/profile/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Profile dashboard unavailable' }),
  }));

  await loginAndOpenProfile(page);

  await expect(page.getByTestId('profile-dashboard-error')).toHaveText('Profile dashboard unavailable');
});

// Bug caught: selecting a valid profile image gives no observable preview.
test('previews a selected profile image', {
  tag: ['@flow:profile-upload', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (Login is setup; profile media is reached through authenticated UI navigation.)
  await loginAndOpenProfile(page);
  await openMyProfile(page);

  await selectProfileImage(page);

  await expect(page.getByRole('img', { name: 'Profile', exact: true })).toHaveAttribute('src', /^blob:/);
});

// Bug caught: an unsupported profile file is silently discarded.
test('rejects an invalid profile image', {
  tag: ['@flow:profile-upload', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await loginAndOpenProfile(page);
  await openMyProfile(page);

  await selectProfileImage(page, 'profile.pdf', 'application/pdf');

  await expect(page.getByRole('dialog')).toContainText('Formato de imagen no válido');
});

// Bug caught: a successful media upload never reaches the user confirmation.
test('confirms a successful profile image upload', {
  tag: ['@flow:profile-upload', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  let multipartUploads = 0;
  await page.route('**/api/auth/update_profile/**', (route) => {
    if (route.request().headers()['content-type']?.includes('multipart/form-data')) {
      multipartUploads += 1;
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(profileResponse),
    });
  });
  await loginAndOpenProfile(page);
  await openMyProfile(page);
  await selectProfileImage(page);

  await page.getByRole('button', { name: 'Save Changes', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Perfil actualizado correctamente');
  expect(multipartUploads).toBe(1);
});

// Bug caught: a failed media request still reports the whole profile as saved.
test('shows a profile image upload service failure', {
  tag: ['@flow:profile-upload', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/auth/update_profile/**', (route) => {
    if (route.request().headers()['content-type']?.includes('multipart/form-data')) {
      return route.fulfill({
        status: 503,
        contentType: 'text/plain',
        body: 'Profile image service unavailable',
      });
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(profileResponse),
    });
  });
  await loginAndOpenProfile(page);
  await openMyProfile(page);
  await selectProfileImage(page);

  await page.getByRole('button', { name: 'Save Changes', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Profile image service unavailable');
});

// Bug caught: an existing pending verification is rendered as a new request form.
test('shows the pending crush-verification status', {
  tag: ['@flow:profile-crush-verification', '@role:crush', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (Login is setup; verification status is reached through authenticated UI navigation.)
  await loginAndOpenProfile(page, 'e2e_pending_crush', 'E2E-pending-password-123!');

  await openMyProfile(page);

  await expect(page.getByTestId('crush-verification-pending')).toContainText('Pending Request');
});

// Bug caught: a gifts API outage is indistinguishable from an empty gift history.
test('shows a gifts-loading failure', {
  tag: ['@flow:profile-gifts', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/orders/gifts/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Gifts service unavailable' }),
  }));
  await loginAndOpenProfile(page);

  await page.getByRole('link', { name: 'My Gifts', exact: true }).click();

  await expect(page.getByTestId('profile-gifts-error')).toHaveText('Gifts service unavailable');
});

// Bug caught: a feed API outage is rendered as a legitimate empty feed.
test('shows a profile feed-loading failure', {
  tag: ['@flow:profile-feed', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/feeds/my-feeds/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Feed service unavailable' }),
  }));

  await loginAndOpenProfile(page);

  await expect(page.getByTestId('profile-feed-error')).toHaveText('Feed service unavailable');
});
