import { test, expect } from '../helpers/test.js';

test('renders the deterministic product catalog', {
  tag: ['@flow:catalog-browse', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');
  const productsResponse = page.waitForResponse(
    (response) => response.url().includes('/api/products/woocommerce/products/')
      && response.status() === 200,
  );

  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();
  await productsResponse;

  await expect(page.getByTestId('catalog-heading')).toBeVisible();
  await expect(page.getByTestId('product-card-900001')).toContainText('E2E Rose Quartz Wand');
});

// Bug caught: catalog cards open a different product or fail to navigate to detail.
test('opens the deterministic product from its catalog card', {
  tag: ['@flow:catalog-product-detail', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();

  const productCard = page.getByTestId('product-card-900001');
  await productCard.getByRole('img', { name: 'E2E Rose Quartz Wand' }).click();

  await expect(page.getByRole('heading', { name: 'E2E Rose Quartz Wand', exact: true })).toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: Buy now opens checkout without adding the selected product.
test('takes the deterministic product to checkout from Buy now', {
  tag: ['@flow:catalog-buy-now', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();

  const productCard = page.getByTestId('product-card-900001');
  await Promise.all([
    page.waitForURL('/en/checkout'),
    productCard.getByRole('button', { name: 'Buy now', exact: true }).click(),
  ]);

  await expect(page).toHaveURL('/en/checkout');
  await expect(page.getByRole('heading', { name: 'E2E Rose Quartz Wand', exact: true })).toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: an out-of-stock response still permits checkout.
test('rejects checkout for an out-of-stock product', {
  tag: ['@flow:catalog-buy-now', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.route('**/api/products/woocommerce/products/900001/stock/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      success: true,
      stock: { available: false, status: 'outofstock', quantity: 0 },
    }),
  }));

  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();
  await expect(page.getByTestId('catalog-heading')).toBeVisible();

  const productCard = page.getByTestId('product-card-900001');
  const buyNowButton = productCard.getByRole('button', { name: 'Buy now', exact: true });
  await buyNowButton.click();

  const unavailableProductActions = productCard.getByRole('button', { name: 'Out of Stock', exact: true });
  await expect(unavailableProductActions).toHaveText(['Out of Stock', 'Out of Stock']);
  await expect.poll(async () => unavailableProductActions.evaluateAll(
    (buttons) => buttons.every((button) => button.disabled),
  )).toBe(true);
  await expect(page).toHaveURL('/en/products');

  await page.getByRole('button', { name: 'Cart', exact: true }).click();
  await expect(page.getByRole('dialog')).toContainText('Your cart is empty');
});

// Bug caught: the Trending Products CTA no longer opens the catalog for rendered products.
test('navigates to the catalog from rendered trending products', {
  tag: ['@flow:catalog-trending-navigation', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en');
  await expect(page.getByTestId('product-card-900001')).toContainText('E2E Rose Quartz Wand');
  await page.getByRole('link', { name: 'Shop Their Desires' }).click();

  await expect(page.getByTestId('catalog-heading')).toHaveText('Products');
});
