import { createPinia, setActivePinia } from 'pinia';

import { create_request, get_request } from '@/services/request_http';
import { useReviewStore } from '@/stores/modules/reviewStore';

jest.mock('@/services/request_http', () => ({
  create_request: jest.fn(),
  delete_request: jest.fn(),
  get_request: jest.fn(),
  patch_request: jest.fn(),
}));

describe('reviewStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  test('stores reviews and their exact server total', async () => {
    // Fails if the review list renders a local count instead of the paginated total.
    const reviews = [{ id: 1, rating: 5, comment: 'Excellent' }];
    get_request.mockResolvedValue({ data: { success: true, reviews, total_reviews: 12 } });
    const store = useReviewStore();

    const result = await store.fetchProductReviews(900001);

    expect(result.success).toBe(true);
    expect(store.productReviews).toEqual(reviews);
    expect(store.totalReviews).toBe(12);
    expect(store.currentProductId).toBe(900001);
  });

  test('adds a created user review to both visible collections', async () => {
    // Fails if a new authenticated review is absent until a page reload.
    const review = { id: 4, woocommerce_product_id: 900001, is_user_review: true, rating: 4 };
    create_request.mockResolvedValue({ data: { success: true, review } });
    const store = useReviewStore();
    store.currentProductId = 900001;

    const result = await store.createReview({ woocommerce_product_id: 900001, rating: 4 });

    expect(result.review).toEqual(review);
    expect(store.productReviews).toEqual([review]);
    expect(store.myReviews).toEqual([review]);
    expect(store.hasReviewedProduct).toBe(true);
  });
});
