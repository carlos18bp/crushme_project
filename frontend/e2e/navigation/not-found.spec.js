import { test, expect } from '../helpers/test.js';
import { NAVIGATION_NOT_FOUND } from '../helpers/flow-tags.js';

test('shows the not-found view for an unknown route', {
  tag: [...NAVIGATION_NOT_FOUND, '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-no-interaction (a 404 is triggered by requesting an unknown URL)
  // quality: allow-deep-link (the unknown URL itself is the user action under test)
  await page.goto('/en/does-not-exist');

  await expect(page.getByRole('heading', { name: '404' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Page Not Found' })).toBeVisible();
});
