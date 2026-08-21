import { test, expect } from '../helpers/test.js';

const cartItem = {
  id: 900001,
  product_id: 900001,
  variation_id: null,
  name: 'E2E Rose Quartz Wand',
  price: 120000,
  quantity: 1,
  stock_status: 'instock',
};

async function preloadCart(page, overrides = {}) {
  await page.addInitScript((item) => {
    localStorage.setItem('crushme_cart', JSON.stringify([item]));
  }, { ...cartItem, ...overrides });
}

async function openCart(page) {
  await page.goto('/en');
  await page.getByRole('button', { name: 'Cart', exact: true }).click();
  return page.getByRole('dialog');
}

async function openProduct(page) {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();
  await page
    .getByTestId('product-card-900001')
    .getByRole('img', { name: 'E2E Rose Quartz Wand' })
    .click();
  await expect(page.getByRole('heading', { name: 'E2E Rose Quartz Wand' })).toHaveText('E2E Rose Quartz Wand');
}

async function breakCartWrites(page) {
  await page.evaluate(() => {
    const originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function setItem(key, value) {
      if (key === 'crushme_cart') throw new Error('E2E storage failure');
      return originalSetItem.call(this, key, value);
    };
  });
}

// Bug caught: an out-of-stock response still adds the product through the cart action.
test('rejects an out-of-stock cart addition', {
  tag: ['@flow:cart-add', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await page.route(/\/api\/products\/woocommerce\/products\/900001\/stock\/.*/, (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      success: true,
      stock: { available: false, status: 'outofstock', quantity: 0 },
    }),
  }));
  await page.goto('/en');
  const catalogReady = page.waitForResponse((response) => (
    response.url().includes('/api/products/woocommerce/stats/')
      && response.status() === 200
  ));
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();
  await catalogReady;
  const card = page.getByTestId('product-card-900001');

  await card.getByRole('button', { name: 'Add to cart', exact: true }).click();
  await expect(card.getByRole('button', { name: 'Out of Stock' })).toHaveCount(2);

  await page.getByRole('button', { name: 'Cart', exact: true }).click();
  await expect(page.getByRole('dialog')).toContainText('Your cart is empty');
});

// Bug caught: a failed browser write reports a successful cart addition.
test('shows a cart persistence failure', {
  tag: ['@flow:cart-add', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await openProduct(page);
  await breakCartWrites(page);

  await page.getByRole('button', { name: 'Add to Cart', exact: true }).click();

  await expect(page.getByTestId('cart-action-error')).toHaveText('Error al agregar al carrito');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('crushme_cart'))).toBeNull();
});

// Bug caught: the drawer permits a quantity above the product limit.
test('rejects quantity one hundred', {
  tag: ['@flow:cart-quantity-update', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await preloadCart(page, { quantity: 99 });
  const dialog = await openCart(page);

  await dialog.getByRole('button', { name: '+', exact: true }).click();

  await expect(dialog.getByRole('alert')).toHaveText('Maximum quantity reached');
  await expect.poll(() => page.evaluate(() => {
    const [item] = JSON.parse(localStorage.getItem('crushme_cart'));
    return item.quantity;
  })).toBe(99);
});

// Bug caught: a rejected quantity write changes the visible cart but not persisted checkout data.
test('shows a quantity persistence failure', {
  tag: ['@flow:cart-quantity-update', '@role:guest', '@outcome:failure'],
}, async ({ page }) => {
  await preloadCart(page);
  const dialog = await openCart(page);
  await breakCartWrites(page);

  await dialog.getByRole('button', { name: '+', exact: true }).click();

  await expect(dialog.getByRole('alert')).toHaveText('Error updating cart');
  await expect(dialog.getByRole('listitem')).toContainText('$120000.00');
});

// Bug caught: removing the visible line leaves a stale cart row in the drawer.
test('displays the empty removal state', {
  tag: ['@flow:cart-remove', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await preloadCart(page);
  const dialog = await openCart(page);

  await dialog.getByRole('button', { name: 'Remove', exact: true }).click();

  await expect(dialog.getByRole('listitem')).toHaveCount(0);
  await expect(dialog).toContainText('Your cart is empty');
});

// Bug caught: checkout accepts an item already marked out of stock.
test('rejects checkout for a stale cart line', {
  tag: ['@flow:cart-checkout-validation', '@role:guest', '@outcome:error'],
}, async ({ page }) => {
  await preloadCart(page, { stock_status: 'outofstock' });
  const dialog = await openCart(page);

  await dialog.getByRole('button', { name: 'Checkout', exact: true }).click();

  await expect(dialog.getByRole('alert')).toHaveText('This item is out of stock');
  await expect(page).toHaveURL('/en');
});

// Bug caught: checkout omits the exact cart product selected in the drawer.
test('displays the checkout cart line', {
  tag: ['@flow:cart-checkout-validation', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await preloadCart(page);
  const dialog = await openCart(page);

  await dialog.getByRole('button', { name: 'Checkout', exact: true }).click();

  await expect(page).toHaveURL('/en/checkout');
  await expect(page.getByRole('heading', { name: 'E2E Rose Quartz Wand', exact: true })).toHaveText('E2E Rose Quartz Wand');
});

// Bug caught: the drawer hides the clear action even when a cart line is present.
test('displays the clear cart action', {
  tag: ['@flow:cart-clear', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await preloadCart(page);
  const dialog = await openCart(page);

  await expect(dialog.getByTestId('clear-cart')).toHaveText('Clear cart');
  await expect(dialog.getByRole('listitem')).toHaveCount(1);
});

// Bug caught: confirming clear cart leaves the persisted lines available to checkout.
test('clears the persisted cart', {
  tag: ['@flow:cart-clear', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await preloadCart(page);
  const dialog = await openCart(page);
  page.once('dialog', async (confirmation) => {
    expect(confirmation.message()).toBe('Are you sure you want to clear your cart?');
    await confirmation.accept();
  });

  await dialog.getByTestId('clear-cart').click();

  await expect(dialog).toContainText('Your cart is empty');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('crushme_cart'))).toBeNull();
});
