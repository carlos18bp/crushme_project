import { test, expect } from '../helpers/test.js';

async function openDiaries(page) {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Diaries', exact: true }).first().click();
  await expect(page.getByTestId('public-profile')).toContainText('@e2e_crush');
}

async function openCatalogProduct(page, productId, productName) {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();
  await page
    .getByTestId(`product-card-${productId}`)
    .getByRole('img', { name: productName })
    .click();
  await expect(page).toHaveURL(new RegExp(`/en/products/${productId}(?:\\?.*)?$`));
}

// Bug caught: random discovery loads a profile but leaves the generic Diaries URL unchanged.
test('discovers a random crush through site navigation', {
  tag: ['@flow:diaries-random-crush', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openDiaries(page);

  await expect(page).toHaveURL('/en/diaries/@e2e_crush');
  await expect(
    page.getByTestId('public-profile').getByRole('heading', { name: '@e2e_crush', exact: true }),
  ).toHaveText('@e2e_crush');
});

// Bug caught: the random profile card omits the verified crush biography and state.
test('displays deterministic random crush data', {
  tag: ['@flow:diaries-random-crush', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openDiaries(page);

  await expect(page.getByTestId('public-profile')).toContainText('Deterministic public Crush profile.');
  await expect(page.getByTestId('public-profile')).toContainText('Available for E2E validation');
});

// Bug caught: a failed random request is erased by the parallel suggestions request.
test('retries a failed random crush request', {
  tag: ['@flow:diaries-random-crush', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  const randomRoute = /\/api\/auth\/crush\/random\/(?:\?.*)?$/;
  await page.route(randomRoute, (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Random discovery unavailable' }),
  }));
  await page.goto('/en');
  await page.getByRole('link', { name: 'Diaries', exact: true }).first().click();
  await expect(page.getByTestId('diaries-view-error')).toContainText('Random discovery unavailable');

  await page.unroute(randomRoute);
  await page.getByTestId('diaries-view-retry').click();
  await expect(
    page.getByTestId('public-profile').getByRole('heading', { name: '@e2e_crush', exact: true }),
  ).toHaveText('@e2e_crush');
});

// Bug caught: opening a shared crush profile hides its public biography and wishlist.
test('displays a crush profile opened by username', {
  tag: ['@flow:diaries-public-profile', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (A shared @username profile URL is the product entry point.)
  // quality: allow-no-interaction (Opening the shared profile URL is the complete user action.)
  await page.goto('/en/diaries/@e2e_crush');

  await expect(
    page.getByTestId('public-profile').getByRole('heading', { name: '@e2e_crush', exact: true }),
  ).toHaveText('@e2e_crush');
  await expect(page.getByTestId('public-profile')).toContainText('E2E Public Wishes');
});

// Bug caught: an unknown shared profile renders the default profile instead of a missing-user error.
test('shows a missing crush profile error', {
  tag: ['@flow:diaries-public-profile', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  // quality: allow-no-interaction (Opening the invalid shared profile URL is the complete user action.)
  await page.goto('/en/diaries/@missing_crush');

  await expect(page.getByTestId('diaries-view-error')).toContainText('User not found.');
});

// Bug caught: a public-profile outage leaves the loading state without recovery feedback.
test('shows a public profile service failure', {
  tag: ['@flow:diaries-public-profile', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  // quality: allow-no-interaction (Opening the shared profile URL is the complete user action.)
  await page.route('**/api/auth/public/@e2e_crush/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Public profile unavailable' }),
  }));
  await page.goto('/en/diaries/@e2e_crush');

  await expect(page.getByTestId('diaries-view-error')).toContainText('Public profile unavailable');
});

// Bug caught: selecting a search result does not navigate to that username's public profile.
test('selects a crush search result', {
  tag: ['@flow:diaries-user-search', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openDiaries(page);
  await page.getByTestId('diaries-user-search').fill('e2e_pending_crush');
  await page.getByTestId('diaries-search-result-e2e_pending_crush').click();

  await expect(page).toHaveURL('/en/diaries/@e2e_pending_crush');
  await expect(page.getByRole('heading', { name: '@e2e_pending_crush', exact: true })).toHaveText('@e2e_pending_crush');
});

// Bug caught: a matching search response is replaced by the no-results state.
test('displays an exact crush search result', {
  tag: ['@flow:diaries-user-search', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openDiaries(page);
  await page.getByTestId('diaries-user-search').fill('e2e_crush');

  const result = page.getByTestId('diaries-search-result-e2e_crush');
  await expect(result).toContainText('@e2e_crush');
  await expect(result).toContainText('Crush');
});

// Bug caught: a search outage replaces the whole public profile with an unrelated page error.
test('shows an isolated crush search failure', {
  tag: ['@flow:diaries-user-search', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openDiaries(page);
  await page.route('**/api/users/search/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Crush search unavailable' }),
  }));
  await page.getByTestId('diaries-user-search').fill('e2e_crush');

  await expect(page.getByTestId('diaries-search-error')).toHaveText('Crush search unavailable');
  await expect(page.getByTestId('public-profile')).toContainText('@e2e_crush');
});

// Bug caught: closing a public profile image leaves the blocking modal over the page.
test('opens and closes a public profile image', {
  tag: ['@flow:diaries-media-view', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openDiaries(page);
  await page.getByTestId('public-profile-avatar').click();
  await expect(page.getByRole('dialog', { name: 'Profile image' })).toHaveCount(1);

  await page.getByRole('button', { name: 'Close', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Profile image' })).toHaveCount(0);
});

// Bug caught: the image modal opens without the selected public profile image.
test('displays the selected public profile image', {
  tag: ['@flow:diaries-media-view', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openDiaries(page);
  await page.getByTestId('public-profile-avatar').click();

  await expect(page.getByTestId('profile-image-modal-content')).toHaveAttribute(
    'src',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
  );
});

// Bug caught: product detail omits the seeded review record and exact review count.
test('displays seeded product review data', {
  tag: ['@flow:reviews-display', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openCatalogProduct(page, 900001, 'E2E Rose Quartz Wand');

  await expect(page.getByTestId('product-reviews').getByRole('heading', { name: 'All Reviews (1)' })).toHaveText('All Reviews (1)');
  await expect(page.getByTestId('product-reviews')).toContainText('Deterministic review content for Playwright.');
});

// Bug caught: a product without reviews inherits stale reviews from the previous product.
test('displays the empty review state', {
  tag: ['@flow:reviews-display', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openCatalogProduct(page, 900002, 'E2E Variable Harness');

  await expect(page.getByTestId('reviews-empty')).toHaveText('No reviews yet for this product. Be the first to leave one!');
});

// Bug caught: a review service outage leaves the section empty and its retry action inert.
test('retries a product review service failure', {
  tag: ['@flow:reviews-display', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  const reviewsRoute = /\/api\/reviews\/product\/900001\/\?.*/;
  await page.route(reviewsRoute, (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Review service unavailable' }),
  }));
  await openCatalogProduct(page, 900001, 'E2E Rose Quartz Wand');
  await expect(page.getByTestId('reviews-error')).toContainText('Review service unavailable');

  await page.unroute(reviewsRoute);
  await page.getByTestId('reviews-retry').click();
  await expect(page.getByTestId('product-reviews')).toContainText('Deterministic review content for Playwright.');
});
