import { createPinia, setActivePinia } from 'pinia';

import { create_request, get_request } from '@/services/request_http';
import { useWishlistStore } from '@/stores/modules/wishlistStore';

jest.mock('@/services/request_http', () => ({
  create_request: jest.fn(),
  delete_request: jest.fn(),
  get_request: jest.fn(),
  patch_request: jest.fn(),
  update_request: jest.fn(),
}));

describe('wishlistStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('prepends a newly created wishlist', async () => {
    // Fails if create succeeds but the profile list remains stale.
    get_request.mockResolvedValue({ data: { wishlists: [{ id: 1, name: 'Existing', is_active: true }] } });
    create_request.mockResolvedValue({
      data: { message: 'Created', wishlist: { id: 2, name: 'Birthday', is_active: true, is_public: true } },
    });
    const store = useWishlistStore();
    await store.fetchWishlists();

    const result = await store.createWishlist({ name: 'Birthday', is_public: true });

    expect(result.data.id).toBe(2);
    expect(store.wishlists.map((wishlist) => wishlist.id)).toEqual([2, 1]);
    expect(store.publicUserWishlists.map((wishlist) => wishlist.name)).toEqual(['Birthday']);
  });

  test('keeps the product validation message returned by the backend', async () => {
    // Fails if a duplicate-product rejection becomes an unhelpful generic error.
    create_request.mockRejectedValue({
      response: { data: { woocommerce_product_id: ['Product already belongs to this wishlist'] } },
    });
    const store = useWishlistStore();

    const result = await store.addWooCommerceProductToWishlist(2, 900001);

    expect(result).toEqual({ success: false, error: 'Product already belongs to this wishlist' });
    expect(store.error).toBe('Product already belongs to this wishlist');
    expect(store.isUpdating).toBe(false);
  });
});
