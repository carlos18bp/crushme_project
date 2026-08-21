import { test, expect } from '../helpers/test.js';

const checkoutItem = {
  id: 900001,
  product_id: 900001,
  variation_id: null,
  name: 'E2E Rose Quartz Wand',
  price: 120000,
  quantity: 1,
  stock_status: 'instock',
};

async function preloadCheckout(page, currency = 'USD') {
  await page.addInitScript(({ item, selectedCurrency }) => {
    localStorage.setItem('crushme_cart', JSON.stringify([item]));
    localStorage.setItem('currency', selectedCurrency);
  }, { item: checkoutItem, selectedCurrency: currency });
}

async function fillShippingForm(page) {
  await page.getByLabel('Email').fill('e2e-buyer@example.test');
  await page.getByLabel('Full name').fill('E2E Buyer');
  await page.getByLabel('Address line 1').fill('E2E street 123');
  await page.getByLabel('City').fill('Medellín');
  await page.getByLabel('State').selectOption({ label: 'Antioquia' });
  await page.getByLabel('Postal code').fill('050001');
  await page.getByLabel('Phone').fill('3001234567');
}

async function mockPayPal(page) {
  await page.route('**/api/orders/paypal/config/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ client_id: 'e2e-paypal-client', currency: 'USD', mode: 'sandbox' }),
  }));
  await page.route('https://www.paypal.com/sdk/js?**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/javascript',
    body: `window.paypal = { Buttons: (options) => ({ render: (selector) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.setAttribute('aria-label', 'PayPal');
      button.textContent = 'PayPal';
      button.addEventListener('click', async () => {
        try { await options.createOrder({}, {}); } catch (error) { /* UI handles it */ }
      });
      document.querySelector(selector).appendChild(button);
    } }) };`,
  }));
}

// Bug caught: valid shipping fields never produce the exact order data required by payment.
test('prepares valid shipping details', {
  tag: ['@flow:checkout-shipping-details', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await preloadCheckout(page, 'USD');
  await mockPayPal(page);
  await page.goto('/en/checkout');
  await fillShippingForm(page);

  await page.getByRole('button', { name: 'Continue to payment →', exact: true }).click();

  await expect(page.getByRole('button', { name: 'PayPal', exact: true })).toHaveText('PayPal');
  await expect.poll(() => page.evaluate(() => {
    const data = JSON.parse(sessionStorage.getItem('checkout_order_data'));
    return [data.customer_email, data.shipping_postal_code];
  })).toEqual(['e2e-buyer@example.test', '050001']);
});

// Bug caught: a browser storage failure silently discards prepared shipping data.
test('shows a shipping preparation failure', {
  tag: ['@flow:checkout-shipping-details', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await preloadCheckout(page, 'USD');
  await page.goto('/en/checkout');
  await fillShippingForm(page);
  await page.evaluate(() => {
    const originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function setItem(key, value) {
      if (key === 'checkout_order_data') throw new Error('E2E storage failure');
      return originalSetItem.call(this, key, value);
    };
  });

  await page.getByRole('button', { name: 'Continue to payment →', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Error al preparar la orden.');
  await expect(page.getByText('Error al preparar la orden', { exact: true })).toHaveText('Error al preparar la orden');
});

// Bug caught: a valid discount code leaves totals unchanged.
test('applies the deterministic discount', {
  tag: ['@flow:checkout-discount', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.goto('/en/checkout');
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/discounts/validate/') && response.status() === 200,
  );

  await page.getByPlaceholder('Enter your code').fill('E2E10');
  await page.getByRole('button', { name: 'Validate', exact: true }).click();
  await responsePromise;

  await expect(page.getByText('E2E10', { exact: true })).toHaveText('E2E10');
  await expect(page.getByText('-10%', { exact: true })).toHaveText('-10%');
});

// Bug caught: an unknown discount is displayed as accepted.
test('rejects an unknown discount', {
  tag: ['@flow:checkout-discount', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.goto('/en/checkout');

  await page.getByPlaceholder('Enter your code').fill('NOT-A-CODE');
  await page.getByRole('button', { name: 'Validate', exact: true }).click();

  await expect(page.getByTestId('discount-error')).toHaveText('Discount code not found');
});

// Bug caught: a discount service outage is mistaken for an invalid user code.
test('shows a discount service failure', {
  tag: ['@flow:checkout-discount', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.goto('/en/checkout');
  await page.route('**/api/discounts/validate/**', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Discount service unavailable' }),
  }));

  await page.getByPlaceholder('Enter your code').fill('E2E10');
  await page.getByRole('button', { name: 'Validate', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Hubo un error al validar el código. Por favor intenta de nuevo.');
  await expect(page.getByText('Error al validar el código', { exact: true })).toHaveText('Error al validar el código');
});

// Bug caught: checkout exposes PayPal after its public configuration was rejected.
test('rejects unavailable PayPal configuration', {
  tag: ['@flow:checkout-paypal', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await preloadCheckout(page, 'USD');
  await page.route('**/api/orders/paypal/config/**', (route) => route.fulfill({
    status: 400,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'PayPal configuration rejected' }),
  }));
  await page.goto('/en/checkout');
  await fillShippingForm(page);

  await page.getByRole('button', { name: 'Continue to payment →', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('No se pudo cargar PayPal.');
});

// Bug caught: a PayPal create-order outage leaves the SDK button looking successful.
test('shows a PayPal order failure', {
  tag: ['@flow:checkout-paypal', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await preloadCheckout(page, 'USD');
  await mockPayPal(page);
  await page.route('**/api/orders/paypal/create/**', (route) => route.fulfill({
    status: 502,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'PayPal create unavailable' }),
  }));
  await page.goto('/en/checkout');
  await fillShippingForm(page);
  await page.getByRole('button', { name: 'Continue to payment →', exact: true }).click();

  await page.getByRole('button', { name: 'PayPal', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('PayPal create unavailable');
});

// Bug caught: a successful Wompi preparation loses its reference before rendering the widget.
test('prepares the Wompi widget', {
  tag: ['@flow:checkout-wompi', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.route('**/api/orders/wompi/create/**', (route) => route.fulfill({
    status: 201,
    contentType: 'application/json',
    body: JSON.stringify({
      widget_data: {
        reference: 'E2E-WOMPI-SUCCESS',
        public_key: 'pub_test_e2e',
        currency: 'COP',
        amount_in_cents: 12000000,
        signature: 'e2e-signature',
        redirect_url: 'http://127.0.0.1:5174/en/checkout/wompi/success',
      },
      reference: 'E2E-WOMPI-SUCCESS',
      total: 120000,
      amount_in_cents: 12000000,
      items_count: 1,
    }),
  }));
  await page.route('https://checkout.wompi.co/widget.js', (route) => route.fulfill({
    status: 200,
    contentType: 'application/javascript',
    body: 'document.currentScript.setAttribute("data-e2e-loaded", "true");',
  }));
  await page.goto('/en/checkout');
  await fillShippingForm(page);

  await page.getByRole('button', { name: '💳 Pay with Wompi →', exact: true }).click();

  await expect(page.locator('script[data-reference="E2E-WOMPI-SUCCESS"]')).toHaveAttribute('data-public-key', 'pub_test_e2e');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('wompi_reference'))).toBe('E2E-WOMPI-SUCCESS');
});

// Bug caught: a rejected Wompi request is rendered as a ready payment widget.
test('shows a rejected Wompi request', {
  tag: ['@flow:checkout-wompi', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.route('**/api/orders/wompi/create/**', (route) => route.fulfill({
    status: 400,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Wompi rejected the order data' }),
  }));
  await page.goto('/en/checkout');
  await fillShippingForm(page);

  await page.getByRole('button', { name: '💳 Pay with Wompi →', exact: true }).click();

  await expect(page.getByRole('dialog')).toContainText('Wompi rejected the order data');
});

// Bug caught: a confirmed Wompi payment omits the buyer confirmation details.
test('shows a successful payment result', {
  tag: ['@flow:checkout-payment-status', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('wompi_reference', 'E2E-WOMPI-CONFIRMED');
    localStorage.setItem('wompi_order_data', JSON.stringify({
      total: 120000,
      customer_email: 'e2e-buyer@example.test',
    }));
  });
  await page.route('**/api/orders/wompi/status/E2E-WOMPI-CONFIRMED/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'success', order_id: 1, transaction_id: 'TX-E2E-1' }),
  }));

  await page.goto('/en/checkout/wompi/success');
  const dialog = page.getByRole('dialog');
  await expect(dialog).toContainText('e2e-buyer@example.test');
  await dialog.getByRole('button', { name: 'OK', exact: true }).click();

  await expect.poll(() => page.evaluate(() => localStorage.getItem('wompi_reference'))).toBeNull();
});

// Bug caught: a pending gateway return does not show which reference is being verified.
test('displays pending payment verification', {
  tag: ['@flow:checkout-payment-status', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  // quality: allow-deep-link (the entry is an external Wompi redirect, not an in-app link)
  // quality: allow-no-interaction (the observable behavior is automatic polling after the gateway redirect)
  await page.addInitScript(() => localStorage.setItem('wompi_reference', 'E2E-WOMPI-PENDING'));
  await page.route('**/api/orders/wompi/status/E2E-WOMPI-PENDING/**', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ status: 'pending', message: 'Awaiting gateway confirmation' }),
  }));

  await page.goto('/en/checkout/wompi/success');

  await expect(page.getByRole('dialog')).toContainText('Verificando tu pago con Wompi...');
});

// Bug caught: a gateway return without a local reference starts endless polling.
test('rejects a missing payment reference', {
  tag: ['@flow:checkout-payment-status', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  // quality: allow-deep-link (the entry is an external Wompi redirect, not an in-app link)
  await page.goto('/en/checkout/wompi/success');
  const dialog = page.getByRole('dialog');
  await expect(dialog).toContainText('No se encontró la referencia de pago.');

  await dialog.getByRole('button', { name: 'OK', exact: true }).click();
  await expect(dialog).toHaveCount(0);
});

// Bug caught: arbitrary recipient text is accepted without selecting a real user.
test('rejects an unresolved gift recipient', {
  tag: ['@flow:checkout-gift-recipient', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.goto('/en/checkout');
  await page.getByRole('radio', { name: 'For gift', exact: true }).check();
  const searchResponse = page.waitForResponse(
    (response) => response.url().includes('/api/users/search/') && response.status() === 200,
  );

  await page.getByLabel("Recipient's username").fill('missing_recipient');
  await searchResponse;
  await page.getByLabel("Recipient's username").press('Tab');

  await expect(page.getByRole('alert')).toHaveText('Select a valid recipient from the search results.');
  await expect(page.getByText('Complete all required fields', { exact: true })).toHaveText('Complete all required fields');
});

// Bug caught: a recipient search outage is indistinguishable from no matching user.
test('shows a recipient search failure', {
  tag: ['@flow:checkout-gift-recipient', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await preloadCheckout(page, 'COP');
  await page.goto('/en/checkout');
  await page.getByRole('radio', { name: 'For gift', exact: true }).check();
  await page.route('**/api/users/search/**', (route) => route.fulfill({
    status: 500,
    contentType: 'application/json',
    body: JSON.stringify({ error: 'Recipient search unavailable' }),
  }));

  await page.getByLabel("Recipient's username").fill('e2e_recipient');

  await expect(page.getByRole('alert')).toHaveText('We could not search for gift recipients.');
});
