import { createPinia, setActivePinia } from 'pinia';

import { create_request } from '@/services/request_http';
import { useContactStore } from '@/stores/modules/contactStore';

jest.mock('@/services/request_http', () => ({ create_request: jest.fn() }));

describe('contactStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  test('stores the accepted contact response', async () => {
    // Fails if a successful contact request leaves stale form state behind.
    const contact = { id: 11, email: 'buyer@example.test' };
    create_request.mockResolvedValue({
      data: { success: true, message: 'Message received', contact },
    });
    const store = useContactStore();

    const result = await store.sendContactForm({ email: contact.email, texto: 'Hello' });

    expect(result).toEqual({ success: true, message: 'Message received', contact });
    expect(store.lastSubmittedContact).toEqual(contact);
    expect(store.successMessage).toBe('Message received');
    expect(store.isSubmitting).toBe(false);
  });

  test('exposes field validation returned by the API', async () => {
    // Fails if contact validation is collapsed into a generic connection error.
    create_request.mockRejectedValue({ response: { data: { errors: { email: ['Invalid email'] } } } });
    const store = useContactStore();

    const result = await store.sendContactForm({ email: 'invalid' });

    expect(result).toEqual({ success: false, errors: { email: ['Invalid email'] } });
    expect(store.errorMessages).toEqual(['Invalid email']);
    expect(store.hasErrors).toBe(true);
  });
});
