import { createPinia, setActivePinia } from 'pinia';

import { useCartStore } from '@/stores/modules/cartStore';

describe('cartStore', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
    localStorage.clear();
  });

  test.each([
    ['merges repeated selections of variation 303', 303, 303, 1, 2, 1, [3], [303]],
    ['keeps variations 303 and 304 as separate lines', 303, 304, 1, 1, 2, [1, 1], [303, 304]],
  ])(
    '%s',
    (
      description,
      firstVariationId,
      secondVariationId,
      firstQuantity,
      secondQuantity,
      expectedItemCount,
      expectedQuantities,
      expectedVariationIds,
    ) => {
      // Fails if identical variations duplicate or distinct variations merge into one cart line.
      const store = useCartStore();

      store.addToCart(900001, firstQuantity, {
        variation_id: firstVariationId,
        name: 'Silk set',
        price: '49.90',
      });
      store.addToCart(900001, secondQuantity, {
        variation_id: secondVariationId,
        name: 'Silk set',
        price: '49.90',
      });

      expect(store.items).toHaveLength(expectedItemCount);
      expect(store.items.map((item) => item.quantity)).toEqual(expectedQuantities);
      expect(store.items.map((item) => item.variation_id)).toEqual(expectedVariationIds);
    },
  );

  test('removes a cart line at quantity zero from persisted storage', () => {
    // Fails if zero quantity leaves a purchasable line in memory or localStorage.
    const store = useCartStore();
    store.addToCart(900001, 1, { variation_id: 303, name: 'Silk set', price: '49.90' });

    const result = store.updateCartItem(store.items[0].id, 0);

    expect(result).toEqual({ success: true, data: { items: [] } });
    expect(store.items).toEqual([]);
    expect(localStorage.getItem('crushme_cart')).toBe('[]');
  });

  test('recovers with an empty cart when persisted JSON is corrupt', () => {
    // Fails if malformed browser storage prevents the cart store from starting.
    localStorage.setItem('crushme_cart', '{invalid-json');

    const store = useCartStore();

    expect(store.items).toEqual([]);
    expect(store.totalItems).toBe(0);
    expect(store.totalPrice).toBe(0);
  });

  test('clears every line and removes persisted state', () => {
    // Fails if clear cart empties memory but checkout restores old persisted lines.
    const store = useCartStore();
    store.addToCart(11, 1, { name: 'One', price: 10 });
    store.addToCart(12, 2, { name: 'Two', price: 20 });

    const result = store.clearCart();

    expect(result).toEqual({ success: true, data: { items: [] } });
    expect(store.items).toEqual([]);
    expect(localStorage.getItem('crushme_cart')).toBeNull();
  });

  test('rolls back a quantity change when browser persistence fails', () => {
    // Fails if checkout shows a quantity that was never persisted for the next page load.
    const store = useCartStore();
    store.addToCart(900001, 1, { name: 'Silk set', price: 49.90 });
    jest.spyOn(Storage.prototype, 'setItem').mockImplementationOnce(() => {
      throw new Error('quota exceeded');
    });

    const result = store.updateCartItem(store.items[0].id, 2);

    expect(result).toEqual({ success: false, error: 'Error al actualizar item' });
    expect(store.items[0].quantity).toBe(1);
    expect(JSON.parse(localStorage.getItem('crushme_cart'))[0].quantity).toBe(1);
  });

  test('restores cart lines when clearing browser persistence fails', () => {
    // Fails if a rejected clear operation empties the visible cart but leaves stale storage.
    const store = useCartStore();
    store.addToCart(900001, 1, { name: 'Silk set', price: 49.90 });
    jest.spyOn(Storage.prototype, 'removeItem').mockImplementationOnce(() => {
      throw new Error('storage unavailable');
    });

    const result = store.clearCart();

    expect(result).toEqual({ success: false, error: 'Error al vaciar el carrito' });
    expect(store.items).toHaveLength(1);
    expect(JSON.parse(localStorage.getItem('crushme_cart'))).toHaveLength(1);
  });

  test('rejects a quantity above the checkout limit', () => {
    // Fails if the drawer can persist quantities the product detail UI forbids.
    const store = useCartStore();
    store.addToCart(900001, 99, { name: 'Silk set', price: 49.90 });

    const result = store.updateCartItem(store.items[0].id, 100);

    expect(result).toEqual({ success: false, error: 'La cantidad debe estar entre 1 y 99' });
    expect(store.items[0].quantity).toBe(99);
  });
});
