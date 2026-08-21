import { test, expect } from '../helpers/test.js';

async function openCatalog(page) {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();
  await expect(page.getByTestId('catalog-heading')).toHaveText('Products');
}

async function openProduct(page, productId, productName) {
  await openCatalog(page);
  await page
    .getByTestId(`product-card-${productId}`)
    .getByRole('img', { name: productName })
    .click();
  await expect(page).toHaveURL(new RegExp(`/en/products/${productId}(?:\\?.*)?$`));
}

async function login(page) {
  await page.goto('/en/login');
  await page.getByTestId('login-username').fill('e2e_user');
  await page.getByTestId('login-password').fill('E2E-password-123!');
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/auth/login/') && response.status() === 200,
  );
  await page.getByTestId('login-submit').click();
  await responsePromise;
  await expect(page).toHaveURL('/en');
}

async function breakCartPersistence(page) {
  await page.evaluate(() => {
    const originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function setItem(key, value) {
      if (key === 'crushme_cart') throw new Error('E2E storage failure');
      return originalSetItem.call(this, key, value);
    };
  });
}

// Bug caught: a catalog API outage leaves a blank product page without recovery controls.
test('shows the catalog outage', {
  tag: ['@flow:catalog-browse', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route(/\/api\/products\/woocommerce\/products\/\?.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Catalog unavailable' }),
  }));

  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();

  await expect(page.getByText('Catalog unavailable', { exact: true })).toHaveText('Catalog unavailable');
  await expect(page.getByTestId('catalog-retry')).toHaveText('Try Again');
});

// Bug caught: changing sort updates the select but never sends the selected order to the catalog.
test('applies price sorting', {
  tag: ['@flow:catalog-filter-sort', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openCatalog(page);
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('sort_by=price_asc') && response.status() === 200,
  );

  await page.getByTestId('catalog-sort').selectOption('priceLowHigh');
  const response = await responsePromise;

  expect(new URL(response.url()).searchParams.get('sort_by')).toBe('price_asc');
  await expect(page.getByTestId('catalog-sort')).toHaveValue('priceLowHigh');
});

// Bug caught: selecting the seeded category renders products from an unrelated category.
test('displays the filtered category', {
  tag: ['@flow:catalog-filter-sort', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openCatalog(page);
  await page.getByRole('button', { name: /Toys/ }).click();
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('category_id=134') && response.status() === 200,
  );

  await page.getByTestId('catalog-category-134').click();
  await responsePromise;

  await expect(page.getByTestId('catalog-heading')).toHaveText('Juguetes');
  await expect(page.locator('[data-testid^="product-card-"]')).toHaveCount(2);
});

// Bug caught: a sort request failure keeps stale products on screen as if sorting succeeded.
test('shows a sorting failure', {
  tag: ['@flow:catalog-filter-sort', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openCatalog(page);
  await page.route(/\/api\/products\/woocommerce\/products\/\?.*sort_by=price_desc.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Sorting service unavailable' }),
  }));

  await page.getByTestId('catalog-sort').selectOption('priceHighLow');

  await expect(page.getByText('Sorting service unavailable', { exact: true })).toHaveText('Sorting service unavailable');
});

// Bug caught: submitting a search does not send the exact user query to the backend.
test('submits the catalog search', {
  tag: ['@flow:catalog-search', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openCatalog(page);
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/products/search/') && response.status() === 200,
  );

  await page.getByTestId('catalog-search').fill('Rose Quartz');
  await page.getByTestId('catalog-search').press('Enter');
  const response = await responsePromise;

  expect(new URL(response.url()).searchParams.get('q')).toBe('Rose Quartz');
  await expect(page.getByTestId('catalog-search')).toHaveValue('Rose Quartz');
});

// Bug caught: search results include products that do not match the entered query.
test('displays matching search results', {
  tag: ['@flow:catalog-search', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openCatalog(page);
  await page.getByTestId('catalog-search').fill('Rose Quartz');
  await page.getByTestId('catalog-search').press('Enter');

  await expect(page.locator('[data-testid^="product-card-"]')).toHaveCount(1);
  await expect(page.getByTestId('product-card-900001')).toContainText('E2E Rose Quartz Wand');
});

// Bug caught: a rejected search silently replaces the catalog with an empty result set.
test('shows a search failure', {
  tag: ['@flow:catalog-search', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openCatalog(page);
  await page.route(/\/api\/products\/woocommerce\/products\/search\/.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Search service unavailable' }),
  }));

  await page.getByTestId('catalog-search').fill('Rose Quartz');
  await page.getByTestId('catalog-search').press('Enter');

  await expect(page.getByText('Search service unavailable', { exact: true })).toHaveText('Search service unavailable');
});

// Bug caught: a missing product is rendered as a valid detail page.
test('shows a missing product error', {
  tag: ['@flow:catalog-product-detail', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await openCatalog(page);
  await page.route(/\/api\/products\/woocommerce\/products\/900001\/.*/, (route) => route.fulfill({
    status: 404,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Product not found in E2E' }),
  }));

  await page.getByTestId('product-card-900001').getByRole('img', { name: 'E2E Rose Quartz Wand' }).click();

  await expect(page.getByRole('heading', { name: 'Error loading product' })).toHaveText('Error loading product');
  await expect(page.getByText('Product not found in E2E', { exact: true })).toHaveText('Product not found in E2E');
});

// Bug caught: a product service outage leaves the detail spinner running forever.
test('shows a product detail failure', {
  tag: ['@flow:catalog-product-detail', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openCatalog(page);
  await page.route(/\/api\/products\/woocommerce\/products\/900001\/.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Product service unavailable' }),
  }));

  await page.getByTestId('product-card-900001').getByRole('img', { name: 'E2E Rose Quartz Wand' }).click();

  await expect(page.getByText('Product service unavailable', { exact: true })).toHaveText('Product service unavailable');
  await expect(page.getByTestId('product-detail-retry')).toHaveText('Try again');
});

// Bug caught: choosing a variation stores the parent product without its variation identifier.
test('selects the large variation', {
  tag: ['@flow:catalog-product-variation', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openProduct(page, 900002, 'E2E Variable Harness');
  const option = page.getByTestId('variation-Size-Large');

  await option.click();
  await page.getByRole('button', { name: 'Add to Cart', exact: true }).click();

  await expect(option).toHaveClass(/active/);
  await expect.poll(() => page.evaluate(() => {
    const [item] = JSON.parse(localStorage.getItem('crushme_cart'));
    return item.variation_id;
  })).toBe(910002);
});

// Bug caught: a rejected variation lookup still enables adding an unresolvable SKU.
test('shows a missing variation error', {
  tag: ['@flow:catalog-product-variation', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await openProduct(page, 900002, 'E2E Variable Harness');
  await page.route(/\/api\/products\/woocommerce\/products\/900002\/variations\/910002\/.*/, (route) => route.fulfill({
    status: 404,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Variation not found in E2E' }),
  }));

  await page.getByTestId('variation-Size-Large').click();

  await expect(page.getByText('Variation not found in E2E', { exact: true })).toHaveText('Variation not found in E2E');
});

// Bug caught: a variation service outage preserves a stale selectable variation.
test('shows a variation service failure', {
  tag: ['@flow:catalog-product-variation', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openProduct(page, 900002, 'E2E Variable Harness');
  await page.route(/\/api\/products\/woocommerce\/products\/900002\/variations\/910002\/.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Variation service unavailable' }),
  }));

  await page.getByTestId('variation-Size-Large').click();

  await expect(page.getByText('Variation service unavailable', { exact: true })).toHaveText('Variation service unavailable');
});

// Bug caught: the variable detail omits the deterministic choices returned by the catalog API.
test('displays available variations', {
  tag: ['@flow:catalog-product-variation', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openProduct(page, 900002, 'E2E Variable Harness');

  await expect(page.getByTestId('variation-Size-Small')).toHaveText('Small');
  await expect(page.getByTestId('variation-Size-Large')).toHaveText('Large');
});

// Bug caught: the home carousel no longer renders the deterministic trending product.
test('displays trending catalog data', {
  tag: ['@flow:catalog-trending-navigation', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');

  const card = page.getByTestId('product-card-900001').first();
  await expect(card).toContainText('E2E Rose Quartz Wand');
  await card.getByRole('img', { name: 'E2E Rose Quartz Wand' }).click();
  await expect(page).toHaveURL('/en/products/900001');
});

// Bug caught: a trending API outage leaves an empty carousel without an error state.
test('shows a trending service failure', {
  tag: ['@flow:catalog-trending-navigation', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.goto('/en/terms');
  await page.route(/\/api\/products\/woocommerce\/products\/trending\/.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Trending service unavailable' }),
  }));

  await page.getByRole('link', { name: 'Home', exact: true }).first().click();

  await expect(page.getByText('Error loading trending products', { exact: true })).toHaveText('Error loading trending products');
});

// Bug caught: a successful favorite request does not update the product action state.
test('favorites a catalog product', {
  tag: ['@flow:catalog-favorite-product', '@role:user', '@outcome:success'],
}, async ({ page }) => {
  await login(page);
  await openCatalog(page);
  const card = page.getByTestId('product-card-900002');
  const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/favorites/products/add/') && response.status() === 201,
  );

  try {
    await card.getByTitle('Add to favorites').click();
    await responsePromise;
    await expect(card.getByTitle('Remove from favorites')).toHaveAttribute('title', 'Remove from favorites');
  } finally {
    const cleanup = await page.request.delete('/api/favorites/products/900002/', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(cleanup.status()).toBe(200);
  }
});

// Bug caught: guests can favorite a product without authenticating.
test('rejects a guest favorite', {
  tag: ['@flow:catalog-favorite-product', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await openCatalog(page);

  await page.getByTestId('product-card-900002').getByTitle('Add to favorites').click();

  await expect(page).toHaveURL('/en/login');
  await expect(page.getByTestId('login-submit')).toHaveText('Sign in');
});

// Bug caught: a failed favorite request silently toggles the heart icon.
test('shows a favorite service failure', {
  tag: ['@flow:catalog-favorite-product', '@role:user', '@outcome:failure'],
}, async ({ page }) => {
  await login(page);
  await openCatalog(page);
  await page.route(/\/api\/favorites\/products\/900001\/.*/, (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Favorite service unavailable' }),
  }));
  const card = page.getByTestId('product-card-900001');

  await card.getByTitle('Remove from favorites').click();

  await expect(card.getByRole('alert')).toHaveText('Favorite service unavailable');
  await expect(card.getByTitle('Remove from favorites')).toHaveAttribute('title', 'Remove from favorites');
});

// Bug caught: a saved favorite is rendered as an unsaved product after catalog reload.
test('displays the seeded favorite state', {
  tag: ['@flow:catalog-favorite-product', '@role:user', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (Login is setup; the favorite is reached through the visible Shop navigation.)
  await login(page);
  await openCatalog(page);
  const card = page.getByTestId('product-card-900001');

  await expect(card.getByTitle('Remove from favorites')).toHaveAttribute('title', 'Remove from favorites');
  await expect(card.getByRole('img', { name: 'Heart icon' })).toHaveAttribute('alt', 'Heart icon');
});

// Bug caught: Buy Now navigates after browser storage rejects the cart mutation.
test('shows a buy now persistence failure', {
  tag: ['@flow:catalog-buy-now', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openProduct(page, 900001, 'E2E Rose Quartz Wand');
  await breakCartPersistence(page);

  await page.getByRole('button', { name: 'Buy Now', exact: true }).click();

  await expect(page.getByTestId('cart-action-error')).toHaveText('Error al agregar al carrito');
  await expect(page).toHaveURL(/\/en\/products\/900001(?:\?.*)?$/);
});
