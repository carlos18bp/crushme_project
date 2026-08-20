import { createPinia, setActivePinia } from 'pinia';

import { useCartStore } from '@/stores/modules/cartStore';

describe('cartStore', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
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
});
