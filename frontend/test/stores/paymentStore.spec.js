import { createPinia, setActivePinia } from 'pinia';

import { create_request, get_request } from '@/services/request_http';
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

  test('stores the canonical PayPal order returned by the backend', async () => {
    // Fails if PayPal creation loses the server order identifier needed for capture.
    create_request.mockResolvedValue({
      data: { paypal_order_id: 'PAYPAL-41', total: '125.00', items_count: 2 },
    });
    const store = usePaymentStore();

    const result = await store.createPayPalOrder({ customer_email: 'buyer@example.test' });

    expect(result).toEqual({
      success: true,
      data: { paypal_order_id: 'PAYPAL-41', total: '125.00', items_count: 2 },
      paypal_order_id: 'PAYPAL-41',
    });
    expect(store.currentOrder.paypal_order_id).toBe('PAYPAL-41');
    expect(store.isProcessing).toBe(false);
  });

  test('stores the captured payment status', async () => {
    // Fails if a completed PayPal capture remains pending in checkout state.
    create_request.mockResolvedValue({
      data: {
        order: { id: 7, order_number: 'CM-7' },
        payment: { status: 'COMPLETED' },
        woocommerce_integration: { synced: true },
      },
    });
    const store = usePaymentStore();

    const result = await store.capturePayPalOrder('PAYPAL-41', { paypal_order_id: 'PAYPAL-41' });

    expect(result.order.order_number).toBe('CM-7');
    expect(store.currentOrder.id).toBe(7);
    expect(store.paymentStatus).toBe('COMPLETED');
    expect(store.isPaymentComplete).toBe(true);
  });

  test('preserves discount validation details on rejection', async () => {
    // Fails if checkout cannot distinguish an invalid code from a service outage.
    create_request.mockRejectedValue({
      response: { status: 400, data: { error: 'Discount expired', code: 'OLD10' } },
    });
    const store = usePaymentStore();

    const result = await store.validateDiscountCode('OLD10');

    expect(result).toEqual({
      success: false,
      error: 'Discount expired',
      data: { error: 'Discount expired', code: 'OLD10' },
      status: 400,
    });
    expect(store.error).toBe('Discount expired');
  });
});
