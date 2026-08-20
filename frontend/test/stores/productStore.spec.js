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
});
