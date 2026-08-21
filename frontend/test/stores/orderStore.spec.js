import { createPinia, setActivePinia } from 'pinia';

import { create_request, get_request } from '@/services/request_http';
import { useOrderStore } from '@/stores/modules/orderStore';

jest.mock('@/services/request_http', () => ({
  create_request: jest.fn(),
  get_request: jest.fn(),
}));

describe('orderStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('maps purchase history and pagination from the backend contract', async () => {
    // Fails if history reads the obsolete orders field or loses server pagination.
    const purchases = [{ id: 8, status: 'delivered', total: '75.50' }];
    get_request.mockResolvedValue({
      data: { purchases, current_page: 2, total_pages: 4, total_count: 31, has_next: true },
    });
    const store = useOrderStore();

    const result = await store.fetchOrders(2);

    expect(result).toEqual({
      success: true,
      data: purchases,
      pagination: { currentPage: 2, totalPages: 4, totalCount: 31, hasNext: true, hasPrevious: false },
    });
    expect(store.orders).toEqual(purchases);
    expect(store.totalSpent).toBe(75.5);
  });

  test('replaces the cancelled order in local state', async () => {
    // Fails if cancellation succeeds remotely but history keeps the prior status.
    get_request.mockResolvedValue({ data: { purchases: [{ id: 8, status: 'processing', total: '75.50' }] } });
    create_request.mockResolvedValue({
      data: { message: 'Cancelled', order: { id: 8, status: 'cancelled', total: '75.50' } },
    });
    const store = useOrderStore();
    await store.fetchOrders();

    const result = await store.cancelOrder(8, 'Changed mind');

    expect(result.data.status).toBe('cancelled');
    expect(store.orders[0].status).toBe('cancelled');
    expect(store.getOrderStatistics().by_status.cancelled).toBe(1);
  });
});
