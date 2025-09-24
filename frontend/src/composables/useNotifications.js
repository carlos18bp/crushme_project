/**
 * Notifications composable for CrushMe e-commerce application
 * Provides simple console-based notifications for development
 */

export function useNotifications() {
  /**
   * Show success notification
   * @param {string} message - Success message
   * @param {string} title - Optional title (default: 'Success')
   * @param {number} duration - Duration in ms (not used in simple version)
   */
  function notifySuccess(message, title = 'Success', duration = 5000) {
    console.log(`✅ ${title}: ${message}`);
  }

  /**
   * Show error notification
   * @param {string} message - Error message
   * @param {string} title - Optional title (default: 'Error')
   * @param {number} duration - Duration in ms (not used in simple version)
   */
  function notifyError(message, title = 'Error', duration = 8000) {
    console.error(`❌ ${title}: ${message}`);
  }

  /**
   * Show warning notification
   * @param {string} message - Warning message
   * @param {string} title - Optional title (default: 'Warning')
   * @param {number} duration - Duration in ms (not used in simple version)
   */
  function notifyWarning(message, title = 'Warning', duration = 6000) {
    console.warn(`⚠️ ${title}: ${message}`);
  }

  /**
   * Show info notification
   * @param {string} message - Info message
   * @param {string} title - Optional title (default: 'Info')
   * @param {number} duration - Duration in ms (not used in simple version)
   */
  function notifyInfo(message, title = 'Info', duration = 5000) {
    console.info(`ℹ️ ${title}: ${message}`);
  }

  /**
   * Handle API response notifications
   * @param {Object} response - API response object
   * @param {string} successMessage - Success message override
   * @param {string} errorMessage - Error message override
   */
  function handleApiResponse(response, successMessage = null, errorMessage = null) {
    if (response.success) {
      const message = successMessage || response.message || 'Operation completed successfully';
      notifySuccess(message);
    } else {
      const message = errorMessage || response.error || 'An error occurred';
      notifyError(message);
    }
  }

  /**
   * Show cart notification
   * @param {string} productName - Product name
   * @param {string} action - Action performed (added, updated, removed)
   */
  function notifyCart(productName, action = 'added') {
    const messages = {
      added: `${productName} added to cart`,
      updated: `Cart updated for ${productName}`,
      removed: `${productName} removed from cart`
    };
    
    notifySuccess(messages[action] || messages.added, 'Cart Updated');
  }

  /**
   * Show wishlist notification
   * @param {string} productName - Product name
   * @param {string} wishlistName - Wishlist name
   * @param {string} action - Action performed (added, removed)
   */
  function notifyWishlist(productName, wishlistName, action = 'added') {
    const messages = {
      added: `${productName} added to ${wishlistName}`,
      removed: `${productName} removed from ${wishlistName}`
    };
    
    notifySuccess(messages[action] || messages.added, 'Wishlist Updated');
  }

  /**
   * Show order notification
   * @param {string} orderNumber - Order number
   * @param {string} action - Action performed (created, cancelled, updated)
   */
  function notifyOrder(orderNumber, action = 'created') {
    const messages = {
      created: `Order ${orderNumber} created successfully`,
      cancelled: `Order ${orderNumber} cancelled`,
      updated: `Order ${orderNumber} updated`
    };
    
    const title = action === 'created' ? 'Order Placed' : 'Order Updated';
    notifySuccess(messages[action] || messages.created, title);
  }

  /**
   * Show authentication notification
   * @param {string} action - Action performed (login, logout, register)
   * @param {string} userName - User name (optional)
   */
  function notifyAuth(action, userName = '') {
    const messages = {
      login: `Welcome back${userName ? `, ${userName}` : ''}!`,
      logout: 'Successfully logged out',
      register: `Welcome${userName ? `, ${userName}` : ''}! Your account has been created.`
    };
    
    notifySuccess(messages[action] || 'Authentication successful');
  }

  return {
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
    handleApiResponse,
    notifyCart,
    notifyWishlist,
    notifyOrder,
    notifyAuth
  };
}
