import { createPinia, setActivePinia } from 'pinia';

import { get_request } from '@/services/request_http';
import { useProductStore } from '@/stores/modules/productStore';

jest.mock('@/services/request_http', () => ({
  get_request: jest.fn(),
}));

describe('productStore', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    get_request.mockResolvedValue({ data: { data: [] } });
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('returns an empty result for a one-character WooCommerce search', async () => {
    // Fails if incomplete catalog queries send unnecessary API requests.
    const store = useProductStore();

    const result = await store.searchWooProducts('a');

    expect(result).toEqual({ success: true, data: [], message: 'Query too short' });
    expect(get_request).not.toHaveBeenCalled();
  });

  test('replaces catalog products when the requested page changes', async () => {
    // Fails if catalog pagination appends duplicate products from previous pages.
    get_request
      .mockResolvedValueOnce({ data: { data: [{ id: 1, name: 'First page' }] } })
      .mockResolvedValueOnce({ data: { data: [{ id: 2, name: 'Second page' }] } });
    const store = useProductStore();

    await store.fetchWooProducts({ page: 1 });
    const result = await store.fetchWooProducts({ page: 2 });

    expect(result.data).toEqual([{ id: 2, name: 'Second page' }]);
    expect(store.wooProducts).toEqual([{ id: 2, name: 'Second page' }]);
  });

  test('clears stale variations when the backend rejects a load', async () => {
    // Fails if product detail displays variations belonging to a previously viewed product.
    get_request
      .mockResolvedValueOnce({ data: { success: true, data: [{ id: 301, price: '45' }] } })
      .mockRejectedValueOnce({ response: { data: { error: 'Variations unavailable' } } });
    const store = useProductStore();
    await store.fetchWooProductVariations(10);

    const result = await store.fetchWooProductVariations(11);

    expect(result).toEqual({ success: false, error: 'Variations unavailable' });
    expect(store.wooProductVariations).toEqual([]);
    expect(store.wooError).toBe('Variations unavailable');
  });

  test('sorts catalog prices numerically without mutating the source', () => {
    // Fails if price sorting is lexical or changes the cached API ordering.
    const products = [
      { id: 1, name: 'A', price: '100' },
      { id: 2, name: 'B', price: '20' },
    ];
    const store = useProductStore();

    const sorted = store.sortWooProducts(products, 'price', 'asc');

    expect(sorted.map((product) => product.id)).toEqual([2, 1]);
    expect(products.map((product) => product.id)).toEqual([1, 2]);
  });
});
