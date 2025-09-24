/**
 * Cart Store for CrushMe e-commerce application
 * Manages shopping cart state and operations
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  create_request, 
  update_request, 
  delete_request 
} from '@/services/request_http.js';
import { useAuthStore } from './authStore.js';

export const useCartStore = defineStore('cart', () => {
  // State
  const cart = ref(null);
  const items = ref([]);
  const isLoading = ref(false);
  const isUpdating = ref(false);
  const error = ref(null);

  // Getters
  const totalItems = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0);
  });

  const totalPrice = computed(() => {
    return items.value.reduce((total, item) => total + (item.quantity * item.unit_price), 0);
  });

  const itemsCount = computed(() => items.value.length);

  const isEmpty = computed(() => items.value.length === 0);

  const hasItems = computed(() => items.value.length > 0);

  const cartSummary = computed(() => ({
    total_items: totalItems.value,
    total_price: totalPrice.value,
    items_count: itemsCount.value,
    is_empty: isEmpty.value
  }));

  // Actions

  /**
   * Fetch user's cart
   */
  async function fetchCart() {
    const authStore = useAuthStore();
    if (!authStore.isLoggedIn) {
      // Handle guest cart (localStorage)
      loadGuestCart();
      return { success: true, data: { items: items.value } };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('cart/');
      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      return { success: true, data: response.data.cart };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch cart';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get cart summary (lightweight)
   */
  async function fetchCartSummary() {
    const authStore = useAuthStore();
    if (!authStore.isLoggedIn) {
      return { success: true, data: cartSummary.value };
    }

    try {
      const response = await get_request('cart/summary/');
      return { success: true, data: response.data.cart_summary };
    } catch (err) {
      return { success: false, error: err.response?.data?.error || 'Failed to fetch cart summary' };
    }
  }

  /**
   * Add product to cart
   * @param {number} productId - Product ID
   * @param {number} quantity - Quantity to add
   */
  async function addToCart(productId, quantity = 1) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      addToGuestCart(productId, quantity);
      return { success: true };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request('cart/add/', {
        product_id: productId,
        quantity: quantity
      });

      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to add to cart';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Update cart item quantity
   * @param {number} itemId - Cart item ID
   * @param {number} quantity - New quantity
   */
  async function updateCartItem(itemId, quantity) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      updateGuestCartItem(itemId, quantity);
      return { success: true };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await update_request(`cart/items/${itemId}/update/`, {
        quantity: quantity
      });

      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to update cart item';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Remove item from cart
   * @param {number} itemId - Cart item ID
   */
  async function removeFromCart(itemId) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      removeFromGuestCart(itemId);
      return { success: true };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request(`cart/items/${itemId}/remove/`);

      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to remove item from cart';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Clear entire cart
   */
  async function clearCart() {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      clearGuestCart();
      return { success: true };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request('cart/clear/');

      cart.value = response.data.cart;
      items.value = [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to clear cart';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Get quantity of specific product in cart
   * @param {number} productId - Product ID
   */
  async function getProductQuantity(productId) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      const guestItem = getGuestCartItem(productId);
      return { 
        success: true, 
        data: { 
          product_id: productId,
          quantity_in_cart: guestItem?.quantity || 0,
          is_in_cart: !!guestItem 
        } 
      };
    }

    try {
      const response = await get_request(`cart/products/${productId}/count/`);
      return { success: true, data: response.data };
    } catch (err) {
      return { 
        success: false, 
        error: err.response?.data?.error || 'Failed to get product quantity' 
      };
    }
  }

  /**
   * Validate cart for checkout
   */
  async function validateCart() {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      return { success: false, error: 'Authentication required for checkout' };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('cart/validate/', {});
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart_summary 
      };
    } catch (err) {
      error.value = err.response?.data?.issues || err.response?.data?.error || 'Cart validation failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  // Guest Cart Functions (for non-authenticated users)

  /**
   * Load guest cart from localStorage
   */
  function loadGuestCart() {
    try {
      const guestCart = localStorage.getItem('guest_cart');
      if (guestCart) {
        items.value = JSON.parse(guestCart);
      }
    } catch (err) {
      console.error('Error loading guest cart:', err);
      items.value = [];
    }
  }

  /**
   * Save guest cart to localStorage
   */
  function saveGuestCart() {
    try {
      localStorage.setItem('guest_cart', JSON.stringify(items.value));
    } catch (err) {
      console.error('Error saving guest cart:', err);
    }
  }

  /**
   * Add product to guest cart
   * @param {number} productId - Product ID
   * @param {number} quantity - Quantity to add
   */
  function addToGuestCart(productId, quantity) {
    const existingItem = items.value.find(item => item.product.id === productId);
    
    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      // Note: In a real implementation, you'd need to fetch product data
      items.value.push({
        id: Date.now(), // Temporary ID
        product: { id: productId },
        quantity: quantity,
        unit_price: 0 // Would need to fetch from product
      });
    }
    
    saveGuestCart();
  }

  /**
   * Update guest cart item
   * @param {number} itemId - Item ID
   * @param {number} quantity - New quantity
   */
  function updateGuestCartItem(itemId, quantity) {
    const itemIndex = items.value.findIndex(item => item.id === itemId);
    if (itemIndex !== -1) {
      if (quantity <= 0) {
        items.value.splice(itemIndex, 1);
      } else {
        items.value[itemIndex].quantity = quantity;
      }
      saveGuestCart();
    }
  }

  /**
   * Remove item from guest cart
   * @param {number} itemId - Item ID
   */
  function removeFromGuestCart(itemId) {
    const itemIndex = items.value.findIndex(item => item.id === itemId);
    if (itemIndex !== -1) {
      items.value.splice(itemIndex, 1);
      saveGuestCart();
    }
  }

  /**
   * Clear guest cart
   */
  function clearGuestCart() {
    items.value = [];
    localStorage.removeItem('guest_cart');
  }

  /**
   * Get guest cart item by product ID
   * @param {number} productId - Product ID
   */
  function getGuestCartItem(productId) {
    return items.value.find(item => item.product.id === productId);
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Initialize cart (load guest cart if not authenticated)
   */
  function initializeCart() {
    const authStore = useAuthStore();
    if (!authStore.isLoggedIn) {
      loadGuestCart();
    }
  }

  // Initialize cart on store creation
  initializeCart();

  return {
    // State
    cart,
    items,
    isLoading,
    isUpdating,
    error,
    
    // Getters
    totalItems,
    totalPrice,
    itemsCount,
    isEmpty,
    hasItems,
    cartSummary,
    
    // Actions
    fetchCart,
    fetchCartSummary,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    getProductQuantity,
    validateCart,
    clearError,
    initializeCart,
    
    // Guest cart actions
    loadGuestCart,
    saveGuestCart,
    clearGuestCart
  };
});
