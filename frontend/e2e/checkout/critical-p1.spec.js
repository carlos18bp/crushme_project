import { test, expect } from '../helpers/test.js';

const persistedCartItem = {
  id: 900001,
  product_id: 900001,
  variation_id: null,
  name: 'E2E Rose Quartz Wand',
  price: 120000,
  quantity: 1,
};

async function preloadCheckout(page, currency = 'USD') {
  await page.addInitScript(({ item, selectedCurrency }) => {
    localStorage.setItem('crushme_cart', JSON.stringify([item]));
    localStorage.setItem('currency', selectedCurrency);
  }, { item: persistedCartItem, selectedCurrency: currency });
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

test.describe('critical checkout journeys', () => {
  // Bug caught: checkout enables payment without every required shipping field.
  test('disables payment while shipping details are incomplete', {
    tag: ['@flow:checkout-shipping-details', '@role:guest', '@outcome:error'],
  }, async ({ page }) => {
    await preloadCheckout(page, 'USD');
    await page.goto('/en/checkout');
    await page.getByRole('radio', { name: 'For gift', exact: true }).check();
    await page.getByRole('radio', { name: 'For me', exact: true }).check();

    await expect(
      page.getByRole('button', { name: 'Complete all required fields', exact: true }),
    ).toBeDisabled();
  });

  // Bug caught: checkout sends PayPal an incomplete order or fails to process its approval.
  test('completes a PayPal order through the SDK button', {
    tag: ['@flow:checkout-paypal', '@role:guest', '@outcome:success'],
  }, async ({ page }) => {
    await preloadCheckout(page, 'USD');
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
          const orderID = await options.createOrder({}, {});
          await options.onApprove({ orderID }, {});
        });
        document.querySelector(selector).appendChild(button);
      } }) };`,
    }));
    await page.route('**/api/orders/paypal/create/**', (route) => route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ paypal_order_id: 'E2E-PAYPAL-001', total: 123, items_count: 1 }),
    }));
    await page.route('**/api/orders/paypal/capture/**', (route) => route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        order: { order_number: 'E2E-ORDER-001', total: 123 },
        payment: { status: 'COMPLETED' },
        woocommerce_integration: {},
      }),
    }));

    await page.goto('/en/checkout');
    await fillShippingForm(page);
    await page.getByRole('button', { name: 'Continue to payment →', exact: true }).click();

    const createResponse = page.waitForResponse(
      (response) => response.url().includes('/api/orders/paypal/create/')
        && response.request().method() === 'POST',
    );
    const captureResponse = page.waitForResponse(
      (response) => response.url().includes('/api/orders/paypal/capture/')
        && response.request().method() === 'POST',
    );
    await page.getByRole('button', { name: 'PayPal', exact: true }).click();

    const [createRequest, captureRequest] = await Promise.all([
      createResponse.then((response) => response.request()),
      captureResponse.then((response) => response.request()),
    ]);
    const createPayload = createRequest.postDataJSON();
    const capturePayload = captureRequest.postDataJSON();

    expect(createPayload.customer_email).toBe('e2e-buyer@example.test');
    expect(createPayload.shipping_city).toBe('Medellín');
    expect(createPayload.items[0].woocommerce_product_id).toBe(900001);
    expect(capturePayload.customer_email).toBe('e2e-buyer@example.test');
    expect(capturePayload.shipping_city).toBe('Medellín');
    expect(capturePayload.items[0].woocommerce_product_id).toBe(900001);
    await expect(page.getByRole('dialog')).toContainText('E2E-ORDER-001');
  });

  // Bug caught: a Wompi outage leaves the buyer without an observable payment error.
  test('shows a Wompi transaction creation failure', {
    tag: ['@flow:checkout-wompi', '@role:guest', '@outcome:failure'],
  }, async ({ page }) => {
    await preloadCheckout(page, 'COP');
    await page.route('**/api/orders/wompi/create/**', (route) => route.fulfill({
      status: 502,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Failed to create Wompi transaction' }),
    }));

    await page.goto('/en/checkout');
    await fillShippingForm(page);
    const wompiResponse = page.waitForResponse(
      (response) => response.url().includes('/api/orders/wompi/create/')
        && response.request().method() === 'POST',
    );
    await page.getByRole('button', { name: '💳 Pay with Wompi →', exact: true }).click();

    expect((await wompiResponse).status()).toBe(502);
    await expect(page.getByRole('dialog')).toContainText('Failed to create Wompi transaction');
  });

  // Bug caught: selecting a gift recipient is lost before payment preparation.
  test('keeps the selected gift recipient in the Wompi payload', {
    tag: ['@flow:checkout-gift-recipient', '@role:guest', '@outcome:success'],
  }, async ({ page }) => {
    await preloadCheckout(page, 'COP');
    await page.route('**/api/orders/wompi/create/**', (route) => route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        widget_data: { reference: 'E2E-WOMPI-001', public_key: 'pub_test' },
        reference: 'E2E-WOMPI-001',
        total: 120000,
        amount_in_cents: 12000000,
        items_count: 1,
      }),
    }));
    await page.route('https://checkout.wompi.co/**', (route) => route.abort());

    await page.goto('/en/checkout');
    await page.getByRole('radio', { name: 'For gift', exact: true }).check();
    await page.getByLabel("Recipient's username").fill('e2e_recipient');
    await page.getByTestId('gift-recipient-option-e2e_recipient').click();
    await page.getByLabel('Your email').fill('e2e-buyer@example.test');

    const wompiResponse = page.waitForResponse(
      (response) => response.url().includes('/api/orders/wompi/create/')
        && response.request().method() === 'POST',
    );
    await page.getByRole('button', { name: '💳 Pay with Wompi →', exact: true }).click();

    const response = await wompiResponse;
    expect(response.status()).toBe(201);
    const payload = response.request().postDataJSON();
    expect(payload.receiver_username).toBe('e2e_recipient');
    expect(payload.is_gift).toBe(true);
  });

});
