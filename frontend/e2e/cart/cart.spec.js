import { test, expect } from '../helpers/test.js';

const persistedCartItem = {
  id: 900001,
  product_id: 900001,
  variation_id: null,
  name: 'E2E Rose Quartz Wand',
  price: 120000,
  quantity: 1,
};

async function preloadCart(page) {
  await page.addInitScript((item) => {
    localStorage.setItem('crushme_cart', JSON.stringify([item]));
  }, persistedCartItem);
}

async function openCart(page) {
  await page.goto('/en');
  await page.getByRole('button', { name: 'Cart', exact: true }).click();
  return page.getByRole('dialog');
}

// Bug caught: adding an in-stock product appears to work but the cart omits it.
test('adds the deterministic in-stock product to the cart', {
  tag: ['@flow:cart-add', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await page.goto('/en');
  await page.getByRole('link', { name: 'Shop', exact: true }).first().click();

  const productCard = page.getByTestId('product-card-900001');
  await productCard.getByRole('button', { name: 'Add to cart', exact: true }).click();

  await page.getByRole('button', { name: 'Cart', exact: true }).click();
  await expect(page.getByRole('dialog')).toContainText('E2E Rose Quartz Wand');
});

// Bug caught: the drawer ignores cart state persisted before the app loads.
test('renders one persisted cart line after opening the drawer', {
  tag: ['@flow:cart-open', '@role:guest', '@outcome:display'],
}, async ({ page }) => {
  await preloadCart(page);
  const cartDialog = await openCart(page);

  await expect(cartDialog.getByRole('listitem')).toHaveCount(1);
});

// Bug caught: increasing a drawer line only changes the display and not checkout state.
test('persists an incremented cart quantity from the drawer', {
  tag: ['@flow:cart-quantity-update', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await preloadCart(page);
  const cartDialog = await openCart(page);

  await cartDialog.getByRole('button', { name: '+', exact: true }).click();

  await expect(cartDialog).toContainText('$240000.00');
  await expect.poll(async () => page.evaluate(() => {
    const [item] = JSON.parse(localStorage.getItem('crushme_cart'));
    return item.quantity;
  })).toBe(2);
});

// Bug caught: removing a drawer line leaves it persisted for checkout.
test('persists cart removal from the drawer', {
  tag: ['@flow:cart-remove', '@role:guest', '@outcome:success'],
}, async ({ page }) => {
  await preloadCart(page);
  const cartDialog = await openCart(page);

  await cartDialog.getByRole('button', { name: 'Remove', exact: true }).click();

  await expect(cartDialog).toContainText('Your cart is empty');
  await expect.poll(() => page.evaluate(() => localStorage.getItem('crushme_cart'))).toBe('[]');
});
