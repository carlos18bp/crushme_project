/**
 * Main store index for CrushMe e-commerce application
 * Exports all Pinia stores for easy importing
 */

// Export all stores
export { useAuthStore } from './modules/authStore.js';
export { useProductStore } from './modules/productStore.js';
export { useCartStore } from './modules/cartStore.js';
export { useOrderStore } from './modules/orderStore.js';
export { useWishlistStore } from './modules/wishlistStore.js';

/**
 * Convenience function to initialize all stores
 * Call this in your main.js or app initialization
 */
export function initializeStores() {
  // Import stores to trigger initialization
  const authStore = useAuthStore();
  const cartStore = useCartStore();
  
  // Initialize auth state
  authStore.initializeAuth();
  
  // Initialize cart
  cartStore.initializeCart();
  
  console.log('🏪 All stores initialized successfully');
}

/**
 * Reset all stores to initial state
 * Useful for logout or testing
 */
export function resetAllStores() {
  const authStore = useAuthStore();
  const productStore = useProductStore();
  const cartStore = useCartStore();
  const orderStore = useOrderStore();
  const wishlistStore = useWishlistStore();
  
  // Reset auth
  authStore.logout();
  
  // Clear products
  productStore.clearCurrentProduct();
  productStore.clearSearch();
  productStore.clearCategory();
  
  // Clear cart
  cartStore.clearGuestCart();
  
  // Clear orders
  orderStore.clearCurrentOrder();
  orderStore.clearOrderTracking();
  
  // Clear wishlists
  wishlistStore.clearCurrentWishlist();
  
  console.log('🧹 All stores reset successfully');
}
