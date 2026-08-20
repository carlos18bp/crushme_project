import { flushPromises, mount } from '@vue/test-utils';

import ProductCard from '@/components/products/ProductCard.vue';
import { get_request } from '@/services/request_http.js';

jest.mock('vue-router', () => ({ useRouter: () => ({ push: jest.fn() }) }));
jest.mock('vue-i18n', () => ({ useI18n: () => ({ t: (key) => key }) }));
jest.mock('@/services/request_http.js', () => ({ get_request: jest.fn() }));
jest.mock('@/stores/modules/cartStore.js', () => ({
  useCartStore: () => ({ isUpdating: false, addToCart: jest.fn(), clearCart: jest.fn() }),
}));
jest.mock('@/stores/modules/authStore', () => ({ useAuthStore: () => ({ isLoggedIn: false }) }));
jest.mock('@/stores/modules/profileStore', () => ({ useProfileStore: () => ({}) }));
jest.mock('@/stores/modules/i18nStore', () => ({ useI18nStore: () => ({ locale: 'en' }) }));
jest.mock('@/stores/modules/currencyStore', () => ({
  useCurrencyStore: () => ({ currentCurrency: 'USD', formatPrice: (price) => `$${price}` }),
}));

const translate = (key) => ({
  'products.outOfStock': 'Out of Stock',
  'products.product.buyNow': 'Buy now',
  'products.product.addToCart': 'Add to cart',
}[key] || key);

test('renders the translated out-of-stock label when stock is unavailable', async () => {
  // Fails if ProductCard references an absent translation key after the stock check.
  get_request.mockResolvedValue({
    data: { success: true, stock: { available: false, status: 'outofstock', quantity: 0 } },
  });
  const wrapper = mount(ProductCard, {
    props: { product: { id: 42, name: 'Test product', price: '10', type: 'simple', images: [] } },
    global: { mocks: { $t: translate }, stubs: { WishlistSelector: true } },
  });

  await wrapper.get('.btn-buy').trigger('click');
  await flushPromises();

  expect(wrapper.get('.btn-buy').text()).toBe('Out of Stock');
});
