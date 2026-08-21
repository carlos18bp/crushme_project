import { createPinia, setActivePinia } from 'pinia';

import { useCart } from '@/composables/useCart';

describe('useCart', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  test('preserves product details when adding an object', async () => {
    // Fails if the composable drops the product name or price before persisting it.
    const cart = useCart();

    const result = await cart.addToCart({ id: 41, name: 'Silk robe', price: '89.50' }, 2);

    expect(result.success).toBe(true);
    expect(cart.cartItems.value).toEqual([
      expect.objectContaining({ product_id: 41, name: 'Silk robe', price: 89.5, quantity: 2 }),
    ]);
    expect(cart.totalPrice.value).toBe(179);
  });

  test('rejects checkout for an empty local cart', async () => {
    // Fails if an empty local cart is accepted because a removed backend method is called.
    const cart = useCart();

    const result = await cart.validateForCheckout();

    expect(result).toEqual({ success: false, error: 'Cart is empty' });
    expect(cart.getCartSummary()).toEqual({
      total_items: 0,
      total_price: 0,
      items_count: 0,
      is_empty: true,
    });
  });

  test('returns the persisted quantity for a product', async () => {
    // Fails if the composable calls the obsolete remote-cart quantity API.
    const cart = useCart();
    await cart.addToCart({ id: 52, name: 'Candle', price: 30 }, 3);

    const result = await cart.getProductQuantity(52);

    expect(result).toEqual({ success: true, data: { quantity_in_cart: 3 } });
    expect(cart.isProductInCart(52)).toBe(true);
    expect(cart.getCartItemByProductId(52).name).toBe('Candle');
  });
});
