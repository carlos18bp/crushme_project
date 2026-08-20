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
