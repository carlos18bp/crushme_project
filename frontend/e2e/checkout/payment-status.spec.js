import { test, expect } from '../helpers/test.js';

const declinedReference = 'e2e-declined-reference';

// Bug caught: a declined or unavailable payment leaves the buyer trapped on the result route.
test('returns the buyer to checkout after a declined Wompi payment', {
  tag: ['@flow:checkout-payment-status', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await page.addInitScript((reference) => {
    localStorage.setItem('wompi_reference', reference);
  }, declinedReference);
  await page.route(`**/api/orders/wompi/status/${declinedReference}/**`, (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'error', error: 'Payment declined' }),
  }));

  const statusResponse = page.waitForResponse(
    (response) => response.url().includes(`/api/orders/wompi/status/${declinedReference}/`),
  );
  await page.goto('/en/checkout/wompi/success');

  expect((await statusResponse).status()).toBe(200);
  const paymentDialog = page.getByRole('dialog');
  await expect(paymentDialog).toContainText('Payment declined');
  await paymentDialog.getByRole('button', { name: 'Volver al checkout' }).click();
  await expect(page).toHaveURL(/\/en\/checkout$/);
});
