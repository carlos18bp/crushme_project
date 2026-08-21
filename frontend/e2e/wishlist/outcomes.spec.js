import { test, expect } from '../helpers/test.js';

const PUBLIC_WISHLIST_ID = 900001;
const OWNED_WISHLIST_ID = 900002;
const EMPTY_WISHLIST_ID = 900003;

async function loginAsE2EUser(page) {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/\/en\/confirmation\?/);
  // The confirmation view auto-redirects to Profile; return Home explicitly for each flow setup.
  await page.goto('/en');
  await expect(page).toHaveURL('/en');
}

async function openOwnedWishlistsFromHome(page) {
  await loginAsE2EUser(page);
  await page.getByRole('link', { name: 'Profile', exact: true }).click();
  await expect(page).toHaveURL('/en/profile');
  await page.getByRole('link', { name: 'Wishlist', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'My Wishlists' })).toHaveText('My Wishlists');
}

async function searchPublicWishlists(page, username) {
  await page.getByTestId('wishlist-user-search').fill(username);
  await page.getByRole('button', { name: 'Search', exact: true }).click();
}

async function createWishlistFromModal(page, name) {
  await page.getByRole('button', { name: 'Create Wishlist', exact: true }).click();
  await page.getByTestId('wishlist-name-input').fill(name);
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/wishlists/create/')
      && response.request().method() === 'POST',
  );
  await page.locator('button').filter({ hasText: /^Create$/ }).click();
  const response = await responsePromise;
  const body = await response.json();
  expect(response.status()).toBe(201);
  return body.wishlist;
}

async function openProductWishlistSelector(page) {
  await page.goto('/en/products/900001');
  await page.getByRole('button', { name: 'Add to my wishlist', exact: true }).click();
  await expect(page.getByTestId('wishlist-selector')).toContainText('Add to Wishlist');
}

async function openPublicWishlistPopup(page, wishlistId) {
  const popupPromise = page.waitForEvent('popup');
  await page.getByTestId(`wishlist-buy-${wishlistId}`).click();
  return popupPromise;
}

// Bug caught: an empty wishlist name is submitted without client feedback.
test('rejects an empty wishlist name', {
  tag: ['@flow:wishlist-create', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await page.getByRole('button', { name: 'Create Wishlist', exact: true }).click();
  await page.locator('button').filter({ hasText: /^Create$/ }).click();

  await expect(page.getByTestId('wishlist-action-error')).toHaveText('Enter a wishlist name.');
});

// Bug caught: a create outage leaves the modal pending without the server message.
test('shows a wishlist creation service failure', {
  tag: ['@flow:wishlist-create', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await page.route('**/api/wishlists/create/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ details: 'Wishlist service unavailable' }),
  }));
  await page.getByRole('button', { name: 'Create Wishlist', exact: true }).click();
  await page.getByTestId('wishlist-name-input').fill('Unavailable list');
  await page.locator('button').filter({ hasText: /^Create$/ }).click();

  await expect(page.getByTestId('wishlist-store-error')).toHaveText('Wishlist service unavailable');
});

// Bug caught: selecting a wishlist confirms success without persisting the product.
test('adds a product through the wishlist selector', {
  tag: ['@flow:wishlist-item-manage', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  const name = `Selector target ${Date.now()}`;
  await openOwnedWishlistsFromHome(page);
  const wishlist = await createWishlistFromModal(page, name);
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));

  try {
    await openProductWishlistSelector(page);
    await page.getByTestId(`wishlist-option-${wishlist.id}`).click();
    await expect(page.getByTestId('wishlist-selector-success')).toHaveText('Product added to wishlist!');
  } finally {
    const cleanup = await page.request.delete(`/api/wishlists/${wishlist.id}/delete/`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(cleanup.status()).toBe(200);
  }
});

// Bug caught: adding a duplicate wishlist item silently appears successful.
test('rejects a duplicate wishlist item', {
  tag: ['@flow:wishlist-item-manage', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await loginAsE2EUser(page);
  await openProductWishlistSelector(page);
  await page.getByTestId(`wishlist-option-${OWNED_WISHLIST_ID}`).click();

  await expect(page.getByTestId('wishlist-selector-error')).toHaveText('Product is already in this wishlist');
});

// Bug caught: an item service outage closes the selector without an actionable error.
test('shows a wishlist item service failure', {
  tag: ['@flow:wishlist-item-manage', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await loginAsE2EUser(page);
  await page.route('**/api/wishlists/*/add-woocommerce-product/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Wishlist item service unavailable' }),
  }));
  await openProductWishlistSelector(page);
  await page.getByTestId(`wishlist-option-${OWNED_WISHLIST_ID}`).click();

  await expect(page.getByTestId('wishlist-selector-error')).toHaveText('Wishlist item service unavailable');
});

// Bug caught: expanding an owned wishlist fails to render its persisted item.
test('displays an owned wishlist item', {
  tag: ['@flow:wishlist-item-manage', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (Login is setup; the wishlist display is reached through Profile navigation.)
  await openOwnedWishlistsFromHome(page);
  await page.getByTestId(`wishlist-expand-${OWNED_WISHLIST_ID}`).click();

  await expect(page.getByTestId(`wishlist-card-${OWNED_WISHLIST_ID}`)
    .getByRole('heading', { name: 'E2E Rose Quartz Wand' }))
    .toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: a valid shared URL fails to enter gift checkout for its owner.
test('resolves a shared wishlist into gift checkout', {
  tag: ['@flow:wishlist-public-share', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  // quality: allow-no-interaction (Opening the shared URL is the complete user action under test.)
  await page.goto(`/en/@e2e_crush/${PUBLIC_WISHLIST_ID}`);
  await expect(page).toHaveURL(/\/en\/checkout\?/);

  const checkoutUrl = new URL(page.url());
  expect(checkoutUrl.searchParams.get('giftMode')).toBe('true');
  expect(checkoutUrl.searchParams.get('username')).toBe('e2e_crush');
  expect(checkoutUrl.searchParams.get('wishlistId')).toBe(String(PUBLIC_WISHLIST_ID));
});

// Bug caught: a missing shared wishlist shows a generic blank card.
test('shows a missing shared wishlist error', {
  tag: ['@flow:wishlist-public-share', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  // quality: allow-no-interaction (Opening the invalid shared URL is the complete user action.)
  await page.goto('/en/@missing_crush/999999');

  await expect(page.getByTestId('wishlist-redirect-error')).toContainText('Wishlist not found or is not public');
});

// Bug caught: an empty shared wishlist redirects to an unusable empty checkout.
test('rejects an empty shared wishlist', {
  tag: ['@flow:wishlist-public-share', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  // quality: allow-no-interaction (Opening the empty shared URL is the complete user action.)
  await page.goto(`/en/@e2e_crush/${EMPTY_WISHLIST_ID}`);

  await expect(page.getByTestId('wishlist-redirect-error')).toContainText('This wishlist is empty');
});

// Bug caught: a shared wishlist outage leaves the loading spinner indefinitely.
test('shows a shared wishlist service failure', {
  tag: ['@flow:wishlist-public-share', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  // quality: allow-no-interaction (Opening the shared URL is the complete user action under test.)
  await page.route('**/api/wishlists/@e2e_crush/900001/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Shared wishlist unavailable' }),
  }));
  await page.goto(`/en/@e2e_crush/${PUBLIC_WISHLIST_ID}`);

  await expect(page.getByTestId('wishlist-redirect-error')).toContainText('Shared wishlist unavailable');
});

// Bug caught: shared wishlist checkout omits the product the recipient requested.
test('displays the shared wishlist product in checkout', {
  tag: ['@flow:wishlist-public-share', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (The product display is reached only by opening its shared URL.)
  // quality: allow-no-interaction (Opening the shared URL is the complete user action under test.)
  await page.goto(`/en/@e2e_crush/${PUBLIC_WISHLIST_ID}`);

  await expect(page.getByRole('heading', { name: 'E2E Rose Quartz Wand' })).toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: buying a searched public wishlist does not open gift checkout.
test('opens gift checkout from a searched wishlist', {
  tag: ['@flow:wishlist-direct-gift', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await searchPublicWishlists(page, 'e2e_crush');
  const popup = await openPublicWishlistPopup(page, PUBLIC_WISHLIST_ID);

  await expect(popup).toHaveURL(/\/en\/checkout\?/);
  await expect(popup.getByRole('heading', { name: 'E2E Rose Quartz Wand' })).toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: selecting an empty public wishlist opens an empty gift checkout.
test('rejects direct gifting from an empty wishlist', {
  tag: ['@flow:wishlist-direct-gift', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await searchPublicWishlists(page, 'e2e_crush');
  const popup = await openPublicWishlistPopup(page, EMPTY_WISHLIST_ID);

  await expect(popup.getByTestId('wishlist-redirect-error')).toContainText('This wishlist is empty');
});

// Bug caught: a direct-gift service outage leaves the new tab loading forever.
test('shows a direct gift service failure', {
  tag: ['@flow:wishlist-direct-gift', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await searchPublicWishlists(page, 'e2e_crush');
  await page.context().route('**/api/wishlists/@e2e_crush/900001/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Gift wishlist unavailable' }),
  }));
  const popup = await openPublicWishlistPopup(page, PUBLIC_WISHLIST_ID);

  await expect(popup.getByTestId('wishlist-redirect-error')).toContainText('Gift wishlist unavailable');
});

// Bug caught: a valid username search fails to render its public wishlist names.
test('searches public wishlists by username', {
  tag: ['@flow:wishlist-public-search', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await searchPublicWishlists(page, 'e2e_crush');

  await expect(page.getByTestId(`wishlist-card-${PUBLIC_WISHLIST_ID}`)).toContainText('E2E Public Wishes');
  await expect(page.getByTestId(`wishlist-card-${EMPTY_WISHLIST_ID}`)).toContainText('E2E Empty Wishes');
});

// Bug caught: an expanded public search result hides the wishlist product data.
test('displays products in a public wishlist search result', {
  tag: ['@flow:wishlist-public-search', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (Login is setup; the public result is reached through Profile navigation and search.)
  await openOwnedWishlistsFromHome(page);
  await searchPublicWishlists(page, 'e2e_crush');
  await page.getByTestId(`wishlist-expand-${PUBLIC_WISHLIST_ID}`).click();

  await expect(page.getByTestId(`wishlist-card-${PUBLIC_WISHLIST_ID}`)
    .getByRole('heading', { name: 'E2E Rose Quartz Wand' }))
    .toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: searching a user without public lists shows the owner's create action.
test('shows an empty public wishlist search result', {
  tag: ['@flow:wishlist-public-search', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await searchPublicWishlists(page, 'e2e_recipient');

  await expect(page.getByTestId('wishlist-search-empty')).toHaveText('No public wishlists were found for @e2e_recipient.');
});

// Bug caught: a public wishlist search outage preserves stale results without feedback.
test('shows a public wishlist search service failure', {
  tag: ['@flow:wishlist-public-search', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await openOwnedWishlistsFromHome(page);
  await page.route('**/api/wishlists/user/e2e_crush/**', (route) => route.fulfill({
    status: 503,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Public wishlist search unavailable' }),
  }));
  await searchPublicWishlists(page, 'e2e_crush');

  await expect(page.getByTestId('wishlist-action-error')).toHaveText('Public wishlist search unavailable');
});

// Bug caught: copying an owned public wishlist gives no confirmation.
test('copies an owned wishlist share link', {
  tag: ['@flow:wishlist-copy-share-link', '@role:user', '@outcome:success'],
}, async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write'], {
    origin: 'http://127.0.0.1:5174',
  });
  await openOwnedWishlistsFromHome(page);
  await page.getByTestId(`wishlist-copy-${OWNED_WISHLIST_ID}`).click();

  await expect(page.getByTestId('wishlist-action-status')).toHaveText('Copied!');
});

// Bug caught: a denied clipboard write is reported only in the console.
test('shows a clipboard failure when copying a wishlist', {
  tag: ['@flow:wishlist-copy-share-link', '@role:user', '@outcome:error'],
}, async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {
        writeText: async () => {
          throw new Error('Clipboard denied');
        },
      },
    });
  });
  await openOwnedWishlistsFromHome(page);
  await page.getByTestId(`wishlist-copy-${OWNED_WISHLIST_ID}`).click();

  await expect(page.getByTestId('wishlist-action-error')).toHaveText('The wishlist link could not be copied.');
});
