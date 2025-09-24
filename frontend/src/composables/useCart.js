/**
 * Cart composable for CrushMe e-commerce application
 * Provides cart functionality with notifications and error handling
 */
import { computed } from 'vue';
import { useCartStore, useProductStore } from '@/stores/index.js';
import { useNotifications } from './useNotifications.js';

export function useCart() {
  const cartStore = useCartStore();
  const productStore = useProductStore();
  const { notifyCart, notifyError, handleApiResponse } = useNotifications();

  // Computed properties
  const cartItems = computed(() => cartStore.items);
  const totalItems = computed(() => cartStore.totalItems);
  const totalPrice = computed(() => cartStore.totalPrice);
  const isEmpty = computed(() => cartStore.isEmpty);
  const isLoading = computed(() => cartStore.isLoading || cartStore.isUpdating);

  /**
   * Add product to cart with notification
   * @param {number|Object} product - Product ID or product object
   * @param {number} quantity - Quantity to add
   */
  async function addToCart(product, quantity = 1) {
    const productId = typeof product === 'object' ? product.id : product;
    const productName = typeof product === 'object' ? product.name : 'Product';

    try {
      const response = await cartStore.addToCart(productId, quantity);
      
      if (response.success) {
        notifyCart(productName, 'added');
        return response;
      } else {
        notifyError(response.error);
        return response;
      }
    } catch (error) {
      notifyError('Failed to add product to cart');
      return { success: false, error: error.message };
    }
  }

  /**
   * Update cart item quantity
   * @param {number} itemId - Cart item ID
   * @param {number} quantity - New quantity
   */
  async function updateQuantity(itemId, quantity) {
    const item = cartItems.value.find(item => item.id === itemId);
    const productName = item?.product?.name || 'Product';

    try {
      const response = await cartStore.updateCartItem(itemId, quantity);
      
      if (response.success) {
        notifyCart(productName, 'updated');
        return response;
      } else {
        notifyError(response.error);
        return response;
      }
    } catch (error) {
      notifyError('Failed to update cart item');
      return { success: false, error: error.message };
    }
  }

  /**
   * Remove item from cart
   * @param {number} itemId - Cart item ID
   */
  async function removeFromCart(itemId) {
    const item = cartItems.value.find(item => item.id === itemId);
    const productName = item?.product?.name || 'Product';

    try {
      const response = await cartStore.removeFromCart(itemId);
      
      if (response.success) {
        notifyCart(productName, 'removed');
        return response;
      } else {
        notifyError(response.error);
        return response;
      }
    } catch (error) {
      notifyError('Failed to remove item from cart');
      return { success: false, error: error.message };
    }
  }

  /**
   * Clear entire cart
   */
  async function clearCart() {
    try {
      const response = await cartStore.clearCart();
      handleApiResponse(response, 'Cart cleared successfully');
      return response;
    } catch (error) {
      notifyError('Failed to clear cart');
      return { success: false, error: error.message };
    }
  }

  /**
   * Get product quantity in cart
   * @param {number} productId - Product ID
   */
  async function getProductQuantity(productId) {
    try {
      return await cartStore.getProductQuantity(productId);
    } catch (error) {
      return { success: false, error: error.message, data: { quantity_in_cart: 0 } };
    }
  }

  /**
   * Validate cart for checkout
   */
  async function validateForCheckout() {
    try {
      const response = await cartStore.validateCart();
      
      if (!response.success) {
        notifyError(response.error, 'Cart Validation Failed');
      }
      
      return response;
    } catch (error) {
      notifyError('Failed to validate cart');
      return { success: false, error: error.message };
    }
  }

  /**
   * Quick add to cart with product lookup
   * @param {number} productId - Product ID
   * @param {number} quantity - Quantity to add
   */
  async function quickAddToCart(productId, quantity = 1) {
    // Get product details first
    let product = productStore.getProductById(productId);
    
    if (!product) {
      const productResponse = await productStore.fetchProduct(productId);
      if (productResponse.success) {
        product = productResponse.data;
      }
    }

    if (product) {
      return await addToCart(product, quantity);
    } else {
      notifyError('Product not found');
      return { success: false, error: 'Product not found' };
    }
  }

  /**
   * Increment item quantity
   * @param {number} itemId - Cart item ID
   */
  async function incrementQuantity(itemId) {
    const item = cartItems.value.find(item => item.id === itemId);
    if (item) {
      return await updateQuantity(itemId, item.quantity + 1);
    }
    return { success: false, error: 'Item not found' };
  }

  /**
   * Decrement item quantity
   * @param {number} itemId - Cart item ID
   */
  async function decrementQuantity(itemId) {
    const item = cartItems.value.find(item => item.id === itemId);
    if (item) {
      const newQuantity = Math.max(0, item.quantity - 1);
      return await updateQuantity(itemId, newQuantity);
    }
    return { success: false, error: 'Item not found' };
  }

  /**
   * Check if product is in cart
   * @param {number} productId - Product ID
   */
  function isProductInCart(productId) {
    return cartItems.value.some(item => item.product.id === productId);
  }

  /**
   * Get cart item by product ID
   * @param {number} productId - Product ID
   */
  function getCartItemByProductId(productId) {
    return cartItems.value.find(item => item.product.id === productId);
  }

  /**
   * Get cart summary
   */
  function getCartSummary() {
    return {
      total_items: totalItems.value,
      total_price: totalPrice.value,
      items_count: cartItems.value.length,
      is_empty: isEmpty.value
    };
  }

  return {
    // State
    cartItems,
    totalItems,
    totalPrice,
    isEmpty,
    isLoading,
    
    // Actions
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
    getProductQuantity,
    validateForCheckout,
    quickAddToCart,
    incrementQuantity,
    decrementQuantity,
    
    // Helpers
    isProductInCart,
    getCartItemByProductId,
    getCartSummary
  };
}
