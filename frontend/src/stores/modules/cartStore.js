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
  const cartSummary = ref(null);
  const validationResult = ref(null);
  const guestCartData = ref(null);
  
  // Loading states
  const isLoading = ref(false);
  const isUpdating = ref(false);
  const isLoadingSummary = ref(false);
  const isValidating = ref(false);
  const isSyncing = ref(false);
  
  // Error states
  const error = ref(null);
  const validationError = ref(null);
  const syncError = ref(null);
  
  // Filters and selections
  const selectedItems = ref([]);
  const bulkActionMode = ref(false);

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

  const isCartEmpty = computed(() => items.value.length === 0);

  const hasSelectedItems = computed(() => selectedItems.value.length > 0);

  const selectedItemsCount = computed(() => selectedItems.value.length);

  const selectedItemsTotal = computed(() => {
    return selectedItems.value.reduce((total, item) => total + (item.quantity * item.unit_price), 0);
  });

  const cartSummaryData = computed(() => ({
    total_items: totalItems.value,
    total_price: totalPrice.value,
    items_count: itemsCount.value,
    is_empty: isEmpty.value,
    has_items: hasItems.value,
    selected_items: selectedItemsCount.value,
    selected_total: selectedItemsTotal.value
  }));

  const inStockItems = computed(() => 
    items.value.filter(item => item.product?.stock_status === 'instock' || item.product?.is_in_stock)
  );

  const outOfStockItems = computed(() => 
    items.value.filter(item => item.product?.stock_status === 'outofstock' || !item.product?.is_in_stock)
  );

  const hasOutOfStockItems = computed(() => outOfStockItems.value.length > 0);

  const canCheckout = computed(() => 
    hasItems.value && !hasOutOfStockItems.value && !isUpdating.value
  );

  const cartWeight = computed(() => {
    return items.value.reduce((total, item) => {
      const weight = item.product?.weight || 0;
      return total + (weight * item.quantity);
    }, 0);
  });

  const uniqueProducts = computed(() => {
    const productIds = new Set();
    return items.value.filter(item => {
      if (productIds.has(item.product.id)) {
        return false;
      }
      productIds.add(item.product.id);
      return true;
    });
  });

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
   * Initialize cart (load guest cart if not authenticated)
   */
  async function initializeCart() {
    const authStore = useAuthStore();
    if (!authStore.isLoggedIn) {
      loadGuestCart();
      return { success: true, data: { items: items.value } };
    }
    
    return await fetchCart();
  }

  /**
   * Get cart summary (lightweight)
   */
  async function fetchCartSummary() {
    const authStore = useAuthStore();
    if (!authStore.isLoggedIn) {
      return { success: true, data: cartSummaryData.value };
    }

    isLoadingSummary.value = true;
    error.value = null;

    try {
      const response = await get_request('cart/summary/');
      cartSummary.value = response.data.cart_summary;
      return { success: true, data: response.data.cart_summary };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch cart summary';
      return { success: false, error: error.value };
    } finally {
      isLoadingSummary.value = false;
    }
  }

  /**
   * Add product to cart
   * @param {number} productId - Product ID
   * @param {number} quantity - Quantity to add
   * @param {object} options - Additional options
   */
  async function addToCart(productId, quantity = 1, options = {}) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      addToGuestCart(productId, quantity, options);
      return { success: true, data: { items: items.value } };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request('cart/add/', {
        product_id: productId,
        quantity: quantity,
        ...options
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
   * Add multiple products to cart
   * @param {Array} products - Array of {productId, quantity} objects
   */
  async function addMultipleToCart(products) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      products.forEach(({ productId, quantity }) => {
        addToGuestCart(productId, quantity);
      });
      return { success: true, data: { items: items.value } };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request('cart/add-multiple/', {
        products: products
      });

      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to add products to cart';
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
      return { success: true, data: { items: items.value } };
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
   * Update multiple cart items
   * @param {Array} updates - Array of {itemId, quantity} objects
   */
  async function updateMultipleCartItems(updates) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      updates.forEach(({ itemId, quantity }) => {
        updateGuestCartItem(itemId, quantity);
      });
      return { success: true, data: { items: items.value } };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await update_request('cart/items/bulk-update/', {
        updates: updates
      });

      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to update cart items';
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
      return { success: true, data: { items: items.value } };
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
   * Remove multiple items from cart
   * @param {Array} itemIds - Array of item IDs to remove
   */
  async function removeMultipleFromCart(itemIds) {
    const authStore = useAuthStore();
    
    if (!authStore.isLoggedIn) {
      // Handle guest cart
      itemIds.forEach(itemId => {
        removeFromGuestCart(itemId);
      });
      return { success: true, data: { items: items.value } };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request('cart/items/bulk-remove/', {
        item_ids: itemIds
      });

      cart.value = response.data.cart;
      items.value = response.data.cart?.items || [];
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to remove items from cart';
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
      return { success: true, data: { items: [] } };
    }

    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request('cart/clear/');

      cart.value = response.data.cart;
      items.value = [];
      selectedItems.value = [];
      
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

    isValidating.value = true;
    validationError.value = null;

    try {
      const response = await create_request('cart/validate/', {});
      validationResult.value = response.data;
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.cart_summary 
      };
    } catch (err) {
      validationError.value = err.response?.data?.issues || err.response?.data?.error || 'Cart validation failed';
      return { success: false, error: validationError.value };
    } finally {
      isValidating.value = false;
    }
  }

  /**
   * Sync guest cart with user cart after login
   */
  async function syncGuestCart() {
    const authStore = useAuthStore();
    
    if (authStore.isLoggedIn && items.value.length > 0) {
      isSyncing.value = true;
      syncError.value = null;

      try {
        const guestItems = items.value.map(item => ({
          product_id: item.product.id,
          quantity: item.quantity
        }));

        const response = await create_request('cart/sync-guest/', {
          items: guestItems
        });

        cart.value = response.data.cart;
        items.value = response.data.cart?.items || [];
        
        return { 
          success: true, 
          message: response.data.message,
          data: response.data.cart 
        };
      } catch (err) {
        syncError.value = err.response?.data?.error || 'Failed to sync guest cart';
        return { success: false, error: syncError.value };
      } finally {
        isSyncing.value = false;
      }
    }
    
    return { success: true };
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
   * @param {object} options - Additional options
   */
  function addToGuestCart(productId, quantity, options = {}) {
    const existingItem = items.value.find(item => item.product.id === productId);
    
    if (existingItem) {
      existingItem.quantity += quantity;
    } else {
      // Note: In a real implementation, you'd need to fetch product data
      items.value.push({
        id: Date.now(), // Temporary ID
        product: { 
          id: productId,
          name: options.name || `Product ${productId}`,
          price: options.price || 0,
          image: options.image || null,
          stock_status: options.stock_status || 'instock'
        },
        quantity: quantity,
        unit_price: options.price || 0,
        added_at: new Date().toISOString()
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

  // ========== NEW UTILITY FUNCTIONS ==========

  /**
   * Select cart item for bulk operations
   * @param {number} itemId - Item ID
   */
  function selectCartItem(itemId) {
    const item = items.value.find(item => item.id === itemId);
    if (item && !selectedItems.value.find(selected => selected.id === itemId)) {
      selectedItems.value.push(item);
    }
  }

  /**
   * Deselect cart item
   * @param {number} itemId - Item ID
   */
  function deselectCartItem(itemId) {
    const index = selectedItems.value.findIndex(item => item.id === itemId);
    if (index !== -1) {
      selectedItems.value.splice(index, 1);
    }
  }

  /**
   * Toggle item selection
   * @param {number} itemId - Item ID
   */
  function toggleItemSelection(itemId) {
    const isSelected = selectedItems.value.find(item => item.id === itemId);
    if (isSelected) {
      deselectCartItem(itemId);
    } else {
      selectCartItem(itemId);
    }
  }

  /**
   * Select all items
   */
  function selectAllItems() {
    selectedItems.value = [...items.value];
  }

  /**
   * Deselect all items
   */
  function deselectAllItems() {
    selectedItems.value = [];
  }

  /**
   * Toggle select all items
   */
  function toggleSelectAll() {
    if (selectedItems.value.length === items.value.length) {
      deselectAllItems();
    } else {
      selectAllItems();
    }
  }

  /**
   * Remove selected items
   */
  async function removeSelectedItems() {
    const itemIds = selectedItems.value.map(item => item.id);
    const result = await removeMultipleFromCart(itemIds);
    if (result.success) {
      selectedItems.value = [];
    }
    return result;
  }

  /**
   * Update selected items quantity
   * @param {number} quantity - New quantity for all selected items
   */
  async function updateSelectedItemsQuantity(quantity) {
    const updates = selectedItems.value.map(item => ({
      itemId: item.id,
      quantity: quantity
    }));
    return await updateMultipleCartItems(updates);
  }

  /**
   * Get cart item by ID
   * @param {number} itemId - Item ID
   */
  function getCartItemById(itemId) {
    return items.value.find(item => item.id === itemId);
  }

  /**
   * Check if product is in cart
   * @param {number} productId - Product ID
   */
  function isProductInCart(productId) {
    return items.value.some(item => item.product.id === productId);
  }

  /**
   * Get product quantity in cart
   * @param {number} productId - Product ID
   */
  function getProductQuantityInCart(productId) {
    const item = items.value.find(item => item.product.id === productId);
    return item ? item.quantity : 0;
  }

  /**
   * Calculate shipping cost (placeholder)
   * @param {string} shippingMethod - Shipping method
   */
  function calculateShipping(shippingMethod = 'standard') {
    // This would typically call an API to calculate shipping
    const baseCost = 5.99;
    const weightMultiplier = cartWeight.value * 0.1;
    return baseCost + weightMultiplier;
  }

  /**
   * Apply discount code (placeholder)
   * @param {string} discountCode - Discount code
   */
  async function applyDiscountCode(discountCode) {
    // This would typically call an API to validate and apply discount
    return { success: false, error: 'Discount code functionality not implemented' };
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
    validationError.value = null;
    syncError.value = null;
  }

  /**
   * Clear validation result
   */
  function clearValidation() {
    validationResult.value = null;
    validationError.value = null;
  }

  /**
   * Clear selected items
   */
  function clearSelection() {
    selectedItems.value = [];
    bulkActionMode.value = false;
  }

  /**
   * Set bulk action mode
   * @param {boolean} mode - Bulk action mode
   */
  function setBulkActionMode(mode) {
    bulkActionMode.value = mode;
    if (!mode) {
      clearSelection();
    }
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
    cartSummary,
    validationResult,
    guestCartData,
    selectedItems,
    bulkActionMode,
    
    // Loading states
    isLoading,
    isUpdating,
    isLoadingSummary,
    isValidating,
    isSyncing,
    
    // Error states
    error,
    validationError,
    syncError,
    
    // Getters
    totalItems,
    totalPrice,
    itemsCount,
    isEmpty,
    hasItems,
    isCartEmpty,
    hasSelectedItems,
    selectedItemsCount,
    selectedItemsTotal,
    cartSummaryData,
    inStockItems,
    outOfStockItems,
    hasOutOfStockItems,
    canCheckout,
    cartWeight,
    uniqueProducts,
    
    // Actions
    fetchCart,
    fetchCartSummary,
    initializeCart,
    addToCart,
    addMultipleToCart,
    updateCartItem,
    updateMultipleCartItems,
    removeFromCart,
    removeMultipleFromCart,
    clearCart,
    getProductQuantity,
    validateCart,
    syncGuestCart,
    
    // Guest cart actions
    loadGuestCart,
    saveGuestCart,
    clearGuestCart,
    addToGuestCart,
    updateGuestCartItem,
    removeFromGuestCart,
    getGuestCartItem,
    
    // Selection and bulk operations
    selectCartItem,
    deselectCartItem,
    toggleItemSelection,
    selectAllItems,
    deselectAllItems,
    toggleSelectAll,
    removeSelectedItems,
    updateSelectedItemsQuantity,
    
    // Utility functions
    getCartItemById,
    isProductInCart,
    getProductQuantityInCart,
    calculateShipping,
    applyDiscountCode,
    
    // Clear functions
    clearError,
    clearValidation,
    clearSelection,
    setBulkActionMode
  };
});
