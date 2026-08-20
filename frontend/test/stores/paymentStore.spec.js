import { createPinia, setActivePinia } from 'pinia';

import { get_request } from '@/services/request_http';
import { usePaymentStore } from '@/stores/modules/paymentStore';

jest.mock('@/services/request_http', () => ({
  get_request: jest.fn(),
  create_request: jest.fn(),
}));

describe('paymentStore', () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createPinia());
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('returns the gateway error when the Wompi status request fails', async () => {
    // Fails if a failed Wompi status request is surfaced as pending or loses the gateway error.
    get_request.mockRejectedValue({ response: { data: { error: 'Wompi unavailable' } } });
    const store = usePaymentStore();

    const result = await store.checkWompiPaymentStatus('TX-2008');

    expect(get_request).toHaveBeenCalledWith('orders/wompi/status/TX-2008/');
    expect(result).toEqual({ status: 'error', error: 'Wompi unavailable' });
  });
});
