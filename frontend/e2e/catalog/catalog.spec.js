import { test, expect } from '../helpers/test.js';
import { CATALOG_BROWSE } from '../helpers/flow-tags.js';

test('renders the deterministic product catalog', {
  tag: [...CATALOG_BROWSE, '@role:guest', '@outcome:display'],
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
