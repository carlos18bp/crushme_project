import { test, expect } from '../helpers/test.js';

function siteNavigation(page) {
  return page.getByRole('navigation').filter({
    has: page.getByRole('link', { name: 'Profile', exact: true }),
  });
}

async function openHomeThroughNavigation(page) {
  await page.goto('/en');
  await siteNavigation(page).getByRole('link', { name: 'About Us', exact: true }).click();
  await expect(page).toHaveURL('/en/about');
  await siteNavigation(page).getByRole('link', { name: 'Home', exact: true }).click();
  await expect(page).toHaveURL('/en');
}

async function openContactFromHome(page) {
  await page.goto('/en');
  await siteNavigation(page).getByRole('link', { name: 'Contact', exact: true }).click();
  await expect(page).toHaveURL('/en/contact');
}

async function fillContactForm(page) {
  await page.getByLabel('From:').fill('visitor@example.test');
  await page.getByLabel('Name:').fill('E2E Visitor');
  await page.getByLabel('Subject:').fill('E2E contact request');
  await page.getByLabel('Message').fill('Please confirm that this message reached support.');
}

// Bug caught: the Home link can render an empty catalog instead of the deterministic featured product.
test('shows the deterministic featured product after navigating home', {
  tag: ['@flow:public-home', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openHomeThroughNavigation(page);

  await expect(page.getByTestId('product-card-900001')).toContainText('E2E Rose Quartz Wand');
});

// Bug caught: a failed trending-products request leaves visitors without a visible loading failure.
test('shows the trending-products failure after navigating home', {
  tag: ['@flow:public-home', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/products/woocommerce/products/trending/**', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Trending service unavailable' }),
  }));

  await openHomeThroughNavigation(page);

  await expect(page.getByText('Error loading trending products', { exact: true })).toHaveText('Error loading trending products');
});

// Bug caught: the About link opens a page without the localized company content.
test('shows localized About content after using site navigation', {
  tag: ['@flow:public-about', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');
  await siteNavigation(page).getByRole('link', { name: 'About Us', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'About Us', exact: true })).toHaveText('About Us');
  await expect(page).toHaveURL('/en/about');
});

// Bug caught: the privacy-policy footer link opens a stale or empty policy page.
test('shows the privacy policy from the footer link', {
  tag: ['@flow:public-privacy', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await page.goto('/en');
  const privacyLink = page.getByRole('link', { name: 'Privacy Policy', exact: true });
  await privacyLink.scrollIntoViewIfNeeded();
  await privacyLink.click();

  await expect(page.getByRole('heading', { name: 'Privacy Policy', exact: true })).toHaveText('Privacy Policy');
  await expect(page).toHaveURL('/en/privacy');
});

// Bug caught: a submitted contact form reports success but keeps the visitor's message in the form.
test('submits a contact message and clears the form', {
  tag: ['@flow:public-contact-submit', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openContactFromHome(page);
  await fillContactForm(page);
  const responsePromise = page.waitForResponse((response) => (
    response.url().includes('/api/contact/') && response.request().method() === 'POST'
  ));

  await page.getByRole('button', { name: 'Send', exact: true }).click();

  expect((await responsePromise).status()).toBe(201);
  await expect(page.getByRole('dialog')).toContainText('Mensaje de contacto enviado exitosamente. Te responderemos pronto.');
  await expect(page.getByLabel('From:')).toHaveValue('');
});

// Bug caught: server-side contact validation is hidden and lets the visitor believe a bad message was sent.
test('shows the server validation message for a rejected contact submission', {
  tag: ['@flow:public-contact-submit', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.route('**/api/contact/', (route) => route.fulfill({
    status: 400,
    contentType: 'application/json',
    body: JSON.stringify({ success: false, errors: { email: ['Enter a valid email address.'] } }),
  }));
  await openContactFromHome(page);
  await fillContactForm(page);

  await page.getByRole('button', { name: 'Send', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Enter a valid email address.');
  await expect(page.getByLabel('From:')).toHaveValue('visitor@example.test');
});

// Bug caught: a contact-service outage is swallowed instead of explaining why the message was not sent.
test('shows contact-service failure feedback after a server error', {
  tag: ['@flow:public-contact-submit', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.route('**/api/contact/', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ message: 'Contact service unavailable' }),
  }));
  await openContactFromHome(page);
  await fillContactForm(page);

  await page.getByRole('button', { name: 'Send', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Contact service unavailable');
  await expect(page.getByLabel('Subject:')).toHaveValue('E2E contact request');
});

// Bug caught: FAQ questions stop revealing their answer after a visitor expands one.
test('expands a frequently asked question', {
  tag: ['@flow:public-faq-toggle', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await openHomeThroughNavigation(page);
  const question = page.getByRole('button', { name: 'How do I send a gift to a Crush?', exact: true });
  const answer = page.getByText("Just choose something from her diary or wishlist, add it to your cart, and complete your purchase. She'll see your treat right away, and you'll get notified when it's on its way.", { exact: true });

  await question.click();

  await expect(answer).toHaveText("Just choose something from her diary or wishlist, add it to your cart, and complete your purchase. She'll see your treat right away, and you'll get notified when it's on its way.");
  await expect(answer).toBeVisible();
});

// Bug caught: the FAQ section renders stale answer data after navigation to the home page.
test('shows the FAQ answer data after navigating home', {
  tag: ['@flow:public-faq-toggle', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await openHomeThroughNavigation(page);
  const question = page.getByRole('button', { name: 'Is shipping discreet?', exact: true });
  const answer = page.getByText("Yes, all packages are shipped in discreet, unmarked packaging. We understand privacy is important, so your order will arrive without any branding or indication of what's inside.", { exact: true });

  await question.click();

  await expect(answer).toHaveText("Yes, all packages are shipped in discreet, unmarked packaging. We understand privacy is important, so your order will arrive without any branding or indication of what's inside.");
  await expect(answer).toBeVisible();
});
