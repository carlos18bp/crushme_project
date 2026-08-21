import { createPinia, setActivePinia } from 'pinia';

import { get_request } from '@/services/request_http';
import { useCrushStore } from '@/stores/modules/crushStore';

jest.mock('@/services/request_http', () => ({ get_request: jest.fn() }));

describe('crushStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  test('trims a username search and stores its exact results', async () => {
    // Fails if whitespace changes the search contract or results are not rendered.
    const results = [{ username: 'e2e_crush', shipping_cost: 10500 }];
    get_request.mockResolvedValue({ data: { success: true, count: 1, results } });
    const store = useCrushStore();

    const response = await store.searchUsers('  e2e  ', 3);

    expect(response).toEqual(results);
    expect(get_request).toHaveBeenCalledWith('users/search/?q=e2e&limit=3');
    expect(store.searchResults).toEqual(results);
  });

  test('derives page boundaries from the server pagination contract', async () => {
    // Fails if Crush pagination enables navigation beyond the final page.
    get_request.mockResolvedValue({
      data: { success: true, results: [{ username: 'one' }], total: 51, offset: 50, limit: 50, count: 1 },
    });
    const store = useCrushStore();

    await store.fetchCrushList({ limit: 50, offset: 50 });

    expect(store.currentPage).toBe(2);
    expect(store.totalPages).toBe(2);
    expect(store.hasNextPage).toBe(false);
    expect(store.hasPrevPage).toBe(true);
  });

  test('keeps search failures isolated from profile loading errors', async () => {
    // Fails if a rejected search replaces the entire public-profile view.
    get_request.mockRejectedValue({ response: { data: { error: 'Search unavailable' } } });
    const store = useCrushStore();

    await expect(store.searchUsers('e2e_crush')).rejects.toEqual({
      response: { data: { error: 'Search unavailable' } },
    });

    expect(store.searchError).toBe('Search unavailable');
    expect(store.error).toBeNull();
    expect(store.searchResults).toEqual([]);
  });

  test('rejects a random crush failure with the backend message', async () => {
    // Fails if a parallel list request can reduce discovery errors to an Axios status string.
    get_request.mockRejectedValue({
      response: { data: { error: 'Random discovery unavailable' } },
    });
    const store = useCrushStore();

    await expect(store.fetchRandomCrush()).rejects.toThrow('Random discovery unavailable');

    expect(store.error).toBe('Random discovery unavailable');
  });

  test('rejects a public profile failure with the backend message', async () => {
    // Fails if missing-profile errors lose their user-facing backend detail.
    get_request.mockRejectedValue({
      response: { data: { error: 'User not found.' } },
    });
    const store = useCrushStore();

    await expect(store.fetchPublicProfile('missing_crush')).rejects.toThrow('User not found.');

    expect(store.error).toBe('User not found.');
  });
});
