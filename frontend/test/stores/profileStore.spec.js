import { createPinia, setActivePinia } from 'pinia';

import { get_request, isAuthenticated } from '@/services/request_http';
import { useProfileStore } from '@/stores/modules/profileStore';

jest.mock('@/services/request_http', () => ({
  create_request: jest.fn(),
  delete_request: jest.fn(),
  get_request: jest.fn(),
  isAuthenticated: jest.fn(),
  update_request: jest.fn(),
}));

describe('profileStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    isAuthenticated.mockReturnValue(true);
  });

  test('refuses profile loading without an authenticated session', async () => {
    // Fails if profile data is requested anonymously and leaks into local state.
    isAuthenticated.mockReturnValue(false);
    const store = useProfileStore();

    const result = await store.fetchProfile();

    expect(result).toEqual({ success: false, error: 'Usuario no autenticado' });
    expect(store.profile).toBeNull();
    expect(get_request).not.toHaveBeenCalled();
  });

  test('derives the default address and sorted links from a loaded profile', async () => {
    // Fails if profile relationships are returned in API order instead of business order.
    get_request.mockResolvedValue({ data: {
      id: 3,
      addresses: [{ id: 1, is_default: false }, { id: 2, is_default: true }],
      links: [{ id: 8, order: 2 }, { id: 7, order: 1 }],
    } });
    const store = useProfileStore();

    await store.fetchProfile();

    expect(store.defaultAddress.id).toBe(2);
    expect(store.sortedLinks.map((link) => link.id)).toEqual([7, 8]);
  });

  test('preserves a profile-loading error independently', async () => {
    get_request.mockRejectedValue({ response: { data: { error: 'Profile unavailable' } } });
    const store = useProfileStore();

    await store.fetchProfile();

    expect(store.profileError).toBe('Profile unavailable');
  });

  test('preserves a feed-loading error independently', async () => {
    get_request.mockRejectedValue({ response: { data: { error: 'Feed unavailable' } } });
    const store = useProfileStore();

    await store.fetchMyFeed();

    expect(store.feedError).toBe('Feed unavailable');
  });

  test('rejects an oversized non-image before upload', () => {
    // Fails if profile uploads accept an invalid MIME type or an excessive payload.
    const store = useProfileStore();
    const file = new File(['payload'], 'profile.pdf', { type: 'application/pdf' });
    Object.defineProperty(file, 'size', { value: 6 * 1024 * 1024 });

    const result = store.validateImageFile(file);

    expect(result).toEqual({
      valid: false,
      errors: [
        'Formato de imagen no válido. Usa JPG, PNG, GIF o WEBP',
        'El archivo excede el tamaño máximo de 5MB',
      ],
    });
  });
});
