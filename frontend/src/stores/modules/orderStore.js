/**
 * Order Store for CrushMe e-commerce application
 * Manages orders, order history, and tracking
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  create_request 
} from '@/services/request_http.js';
import { ORDER_STATUS, ORDER_STATUS_LABELS } from '@/utils/constants.js';

export const useOrderStore = defineStore('order', () => {
  // State
  const orders = ref([]);
  const currentOrder = ref(null);
  const recentOrders = ref([]);
  const orderTracking = ref(null);
  
  const isLoading = ref(false);
  const isLoadingOrder = ref(false);
  const isCreatingOrder = ref(false);
  const error = ref(null);

  // Getters
  const totalOrders = computed(() => orders.value.length);

  const ordersByStatus = computed(() => {
    const grouped = {};
    Object.values(ORDER_STATUS).forEach(status => {
      grouped[status] = orders.value.filter(order => order.status === status);
    });
    return grouped;
  });

  const pendingOrders = computed(() => 
    orders.value.filter(order => order.status === ORDER_STATUS.PENDING)
  );

  const processingOrders = computed(() => 
    orders.value.filter(order => order.status === ORDER_STATUS.PROCESSING)
  );

  const shippedOrders = computed(() => 
    orders.value.filter(order => order.status === ORDER_STATUS.SHIPPED)
  );

  const deliveredOrders = computed(() => 
    orders.value.filter(order => order.status === ORDER_STATUS.DELIVERED)
  );

  const cancelledOrders = computed(() => 
    orders.value.filter(order => order.status === ORDER_STATUS.CANCELLED)
  );

  const hasOrders = computed(() => orders.value.length > 0);

  const totalSpent = computed(() => {
    return deliveredOrders.value.reduce((total, order) => total + parseFloat(order.total), 0);
  });

  // Actions

  /**
   * Fetch user's orders (purchase history)
   * @param {number} page - Page number (default: 1)
   */
  async function fetchOrders(page = 1) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request(`orders/history/?page=${page}`);
      // Backend returns 'purchases' array in history endpoint
      orders.value = response.data.purchases || response.data.orders || [];
      
      // Return pagination data
      return { 
        success: true, 
        data: orders.value,
        pagination: {
          currentPage: response.data.current_page || page,
          totalPages: response.data.total_pages || 1,
          totalCount: response.data.total_count || orders.value.length,
          hasNext: response.data.has_next || false,
          hasPrevious: response.data.has_previous || false
        }
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch orders';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch order by ID
   * @param {number} orderId - Order ID
   */
  async function fetchOrder(orderId) {
    isLoadingOrder.value = true;
    error.value = null;

    try {
      const response = await get_request(`orders/${orderId}/`);
      currentOrder.value = response.data.order;
      
      // Update order in the orders list if it exists
      const orderIndex = orders.value.findIndex(o => o.id === orderId);
      if (orderIndex !== -1) {
        orders.value[orderIndex] = response.data.order;
      }
      
      return { success: true, data: response.data.order };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch order';
      currentOrder.value = null;
      return { success: false, error: error.value };
    } finally {
      isLoadingOrder.value = false;
    }
  }

  /**
   * Create new order from cart
   * @param {Object} orderData - Order information
   * @param {string} orderData.shipping_address - Shipping address
   * @param {string} orderData.shipping_city - City
   * @param {string} orderData.shipping_state - State
   * @param {string} orderData.shipping_postal_code - Postal code
   * @param {string} orderData.shipping_country - Country
   * @param {string} orderData.phone_number - Phone number
   * @param {string} orderData.notes - Additional notes
   */
  async function createOrder(orderData) {
    isCreatingOrder.value = true;
    error.value = null;

    try {
      const response = await create_request('orders/create/', orderData);
      
      const newOrder = response.data.order;
      currentOrder.value = newOrder;
      
      // Add to orders list
      orders.value.unshift(newOrder);
      
      return { 
        success: true, 
        message: response.data.message,
        data: newOrder 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to create order';
      return { success: false, error: error.value };
    } finally {
      isCreatingOrder.value = false;
    }
  }

  /**
   * Cancel order
   * @param {number} orderId - Order ID
   * @param {string} reason - Cancellation reason
   */
  async function cancelOrder(orderId, reason = '') {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request(`orders/${orderId}/cancel/`, { reason });
      
      const updatedOrder = response.data.order;
      
      // Update order in the list
      const orderIndex = orders.value.findIndex(order => order.id === orderId);
      if (orderIndex !== -1) {
        orders.value[orderIndex] = updatedOrder;
      }
      
      // Update current order if it's the same
      if (currentOrder.value?.id === orderId) {
        currentOrder.value = updatedOrder;
      }
      
      return { 
        success: true, 
        message: response.data.message,
        data: updatedOrder 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to cancel order';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Track order by order number
   * @param {string} orderNumber - Order number
   */
  async function trackOrder(orderNumber) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request(`orders/track/${orderNumber}/`);
      orderTracking.value = response.data.tracking;
      return { success: true, data: response.data.tracking };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to track order';
      orderTracking.value = null;
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch recent orders
   */
  async function fetchRecentOrders() {
    try {
      const response = await get_request('orders/recent/');
      recentOrders.value = response.data.recent_orders || [];
      return { success: true, data: recentOrders.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch recent orders';
      return { success: false, error: error.value };
    }
  }

  /**
   * Get order by ID from current orders
   * @param {number} orderId - Order ID
   */
  function getOrderById(orderId) {
    return orders.value.find(order => order.id === orderId) || null;
  }

  /**
   * Get order status label
   * @param {string} status - Order status
   */
  function getStatusLabel(status) {
    return ORDER_STATUS_LABELS[status] || status;
  }

  /**
   * Check if order can be cancelled
   * @param {Object} order - Order object
   */
  function canCancelOrder(order) {
    return order && [ORDER_STATUS.PENDING, ORDER_STATUS.PROCESSING].includes(order.status);
  }

  /**
   * Check if order is delivered
   * @param {Object} order - Order object
   */
  function isOrderDelivered(order) {
    return order && order.status === ORDER_STATUS.DELIVERED;
  }

  /**
   * Check if order is in transit
   * @param {Object} order - Order object
   */
  function isOrderInTransit(order) {
    return order && [ORDER_STATUS.PROCESSING, ORDER_STATUS.SHIPPED].includes(order.status);
  }

  /**
   * Filter orders by status
   * @param {string} status - Order status
   */
  function filterOrdersByStatus(status) {
    return orders.value.filter(order => order.status === status);
  }

  /**
   * Filter orders by date range
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   */
  function filterOrdersByDateRange(startDate, endDate) {
    return orders.value.filter(order => {
      const orderDate = new Date(order.created_at);
      return orderDate >= startDate && orderDate <= endDate;
    });
  }

  /**
   * Sort orders by criteria
   * @param {string} sortBy - Sort criteria (date, total, status)
   * @param {string} order - Sort order (asc, desc)
   */
  function sortOrders(sortBy = 'created_at', order = 'desc') {
    const sorted = [...orders.value].sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'created_at':
          comparison = new Date(a.created_at) - new Date(b.created_at);
          break;
        case 'total':
          comparison = parseFloat(a.total) - parseFloat(b.total);
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'order_number':
          comparison = a.order_number.localeCompare(b.order_number);
          break;
        default:
          comparison = 0;
      }
      
      return order === 'desc' ? -comparison : comparison;
    });
    
    orders.value = sorted;
    return sorted;
  }

  /**
   * Clear current order
   */
  function clearCurrentOrder() {
    currentOrder.value = null;
  }

  /**
   * Clear order tracking
   */
  function clearOrderTracking() {
    orderTracking.value = null;
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Calculate order statistics
   */
  function getOrderStatistics() {
    return {
      total: totalOrders.value,
      by_status: {
        pending: pendingOrders.value.length,
        processing: processingOrders.value.length,
        shipped: shippedOrders.value.length,
        delivered: deliveredOrders.value.length,
        cancelled: cancelledOrders.value.length
      },
      total_spent: totalSpent.value
    };
  }

  return {
    // State
    orders,
    currentOrder,
    recentOrders,
    orderTracking,
    isLoading,
    isLoadingOrder,
    isCreatingOrder,
    error,
    
    // Getters
    totalOrders,
    ordersByStatus,
    pendingOrders,
    processingOrders,
    shippedOrders,
    deliveredOrders,
    cancelledOrders,
    hasOrders,
    totalSpent,
    
    // Actions
    fetchOrders,
    fetchOrder,
    createOrder,
    cancelOrder,
    trackOrder,
    fetchRecentOrders,
    getOrderById,
    getStatusLabel,
    canCancelOrder,
    isOrderDelivered,
    isOrderInTransit,
    filterOrdersByStatus,
    filterOrdersByDateRange,
    sortOrders,
    clearCurrentOrder,
    clearOrderTracking,
    clearError,
    getOrderStatistics
  };
});
