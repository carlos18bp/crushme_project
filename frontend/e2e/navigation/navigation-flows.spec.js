import { test, expect } from '../helpers/test.js';

function siteNavigation(page) {
  return page.getByRole('navigation').filter({
    has: page.getByRole('link', { name: 'Profile', exact: true }),
  });
}

test.describe('responsive site navigation', () => {
  test.use({ viewport: { width: 390, height: 844 } });

  // Bug caught: opening the mobile menu no longer lets a visitor reach Contact.
  test('opens the mobile menu and navigates to Contact', {
    tag: ['@flow:navigation-mobile-menu', '@role:guest', '@outcome:success'],
  }, async ({ page }) => {
    await page.goto('/en/about');
    await page.getByRole('button', { name: 'Toggle menu', exact: true }).click();
    await siteNavigation(page).getByRole('link', { name: 'Contact', exact: true }).click();

    await expect(page).toHaveURL('/en/contact');
  });

  // Bug caught: the mobile navigation route succeeds but the Contact content is blank.
  test('shows Contact content after mobile-menu navigation', {
    tag: ['@flow:navigation-mobile-menu', '@role:guest', '@outcome:display'],
  }, async ({ page }) => {
    await page.goto('/en');
    await page.getByRole('button', { name: 'Toggle menu', exact: true }).click();
    await siteNavigation(page).getByRole('link', { name: 'Contact', exact: true }).click();

    await expect(page.getByRole('heading', { name: 'New Message', exact: true })).toHaveText('New Message');
  });
});

// Bug caught: changing locale rewrites the route instead of preserving the current sign-in destination.
test('switches locale while preserving the sign-in route', {
  tag: ['@flow:navigation-locale-switch', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Sign In', exact: true }).click();
  await page.getByRole('button', { name: 'ES', exact: true }).click();

  await expect(page).toHaveURL('/es/login');
});

// Bug caught: locale switching reaches the Spanish sign-in route but keeps English content rendered.
test('shows Spanish sign-in content after locale switching', {
  tag: ['@flow:navigation-locale-switch', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Sign In', exact: true }).click();
  await page.getByRole('button', { name: 'ES', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'Regresa a tu mundo privado.', exact: true })).toHaveText('Regresa a tu mundo privado.');
});
