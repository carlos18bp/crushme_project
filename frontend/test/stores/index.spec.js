import { createPinia, setActivePinia } from 'pinia';

import {
  initializeStores,
  resetAllStores,
  useCartStore,
} from '@/stores';

describe('store registry', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  test('initializes the persisted cart through bound store imports', () => {
    // Fails if re-exported store symbols are not locally bound in initializeStores.
    localStorage.setItem('crushme_cart', JSON.stringify([
      { id: 7, product_id: 70, name: 'Gift', price: 12, quantity: 2 },
    ]));

    initializeStores();

    expect(useCartStore().items).toEqual([
      { id: 7, product_id: 70, name: 'Gift', price: 12, quantity: 2 },
    ]);
  });

  test('resets the local cart with the implemented action', () => {
    // Fails if resetAllStores calls the removed clearGuestCart action.
    const cart = useCartStore();
    cart.addToCart(70, 1, { name: 'Gift', price: 12 });

    resetAllStores();

    expect(cart.items).toEqual([]);
    expect(localStorage.getItem('crushme_cart')).toBeNull();
  });
});
