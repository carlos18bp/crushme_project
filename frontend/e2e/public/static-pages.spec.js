import { test, expect } from '../helpers/test.js';
import { PUBLIC_TERMS } from '../helpers/flow-tags.js';

test('renders the localized terms page', {
  tag: [...PUBLIC_TERMS, '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: /terms/i }).click();

  await expect(page.getByTestId('terms-heading')).toBeVisible();
  await expect(page).toHaveURL(/\/en\/terms/);
});
