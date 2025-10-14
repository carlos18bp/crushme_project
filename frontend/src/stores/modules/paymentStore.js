/**
 * Payment Store for CrushMe e-commerce application
 * Manages PayPal checkout flow and payment processing
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  create_request
} from '@/services/request_http.js';

export const usePaymentStore = defineStore('payment', () => {
  // State
  const paypalConfig = ref(null);
  const currentOrder = ref(null);
  const paymentStatus = ref(null);
  const isLoading = ref(false);
  const isProcessing = ref(false);
  const error = ref(null);

  // Getters
  const hasPayPalConfig = computed(() => paypalConfig.value !== null);
  const isPaymentComplete = computed(() => paymentStatus.value === 'COMPLETED');
  const paypalClientId = computed(() => paypalConfig.value?.client_id || null);

  // Actions

  /**
   * Obtener configuración de PayPal
   * GET /api/orders/paypal/config/
   */
  async function fetchPayPalConfig() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('orders/paypal/config/');
      
      paypalConfig.value = {
        client_id: response.data.client_id,
        currency: response.data.currency,
        mode: response.data.mode
      };

      return { 
        success: true, 
        data: paypalConfig.value 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch PayPal configuration';
      return { 
        success: false, 
        error: error.value 
      };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Crear orden PayPal
   * POST /api/orders/paypal/create/
   * @param {Object} shippingData - Datos de envío
   */
  async function createPayPalOrder(shippingData) {
    isProcessing.value = true;
    error.value = null;

    try {
      const response = await create_request('orders/paypal/create/', shippingData);
      
      const orderData = {
        paypal_order_id: response.data.paypal_order_id,
        total: response.data.total,
        items_count: response.data.items_count
      };

      currentOrder.value = orderData;

      return { 
        success: true, 
        data: orderData,
        paypal_order_id: orderData.paypal_order_id
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to create PayPal order';

      return { 
        success: false, 
        error: error.value,
        details: err.response?.data?.details
      };
    } finally {
      isProcessing.value = false;
    }
  }

  /**
   * Capturar pago PayPal y crear orden
   * POST /api/orders/paypal/capture/
   * @param {string} paypalOrderId - ID de la orden de PayPal
   * @param {Object} captureData - Datos completos de la orden (items + shipping + customer)
   */
  async function capturePayPalOrder(paypalOrderId, captureData) {
    isProcessing.value = true;
    error.value = null;

    try {
      // Los datos ya vienen completos con paypal_order_id, items, shipping, etc.
      const response = await create_request('orders/paypal/capture/', captureData);

      const captureResult = {
        order: response.data.order,
        payment: response.data.payment,
        woocommerce_integration: response.data.woocommerce_integration
      };

      currentOrder.value = captureResult.order;
      paymentStatus.value = captureResult.payment.status;

      return {
        success: true,
        data: captureResult,
        order: captureResult.order,
        payment: captureResult.payment
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to capture PayPal payment';

      return {
        success: false,
        error: error.value,
        details: err.response?.data?.details,
        paypal_status: err.response?.data?.paypal_status
      };
    } finally {
      isProcessing.value = false;
    }
  }

  /**
   * Enviar regalo entre usuarios
   * POST /api/orders/gifts/send/
   * @param {Object} giftData - Datos del regalo
   */
  async function sendGift(giftData) {
    isProcessing.value = true;
    error.value = null;

    try {
      console.log('🎁 [GIFT] Enviando regalo:', giftData);

      const response = await create_request('orders/gifts/send/', giftData);

      console.log('✅ [GIFT] Regalo enviado exitosamente:', response.data);

      return {
        success: true,
        data: response.data,
        paypal_order_id: response.data.paypal_order_id,
        receiver_info: response.data.receiver_info
      };
    } catch (err) {
      console.error('❌ [GIFT] Error enviando regalo:', err);

      const errorMessage = err.response?.data?.error || 'Failed to send gift';

      return {
        success: false,
        error: errorMessage,
        details: err.response?.data?.missing_fields,
        user_info: err.response?.data?.user_info
      };
    } finally {
      isProcessing.value = false;
    }
  }

  /**
   * Limpiar estado de pago
   */
  function clearPaymentState() {
    currentOrder.value = null;
    paymentStatus.value = null;
    error.value = null;
  }

  /**
   * Limpiar error
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Obtener estado del pago actual
   */
  function getPaymentState() {
    return {
      hasConfig: hasPayPalConfig.value,
      isLoading: isLoading.value,
      isProcessing: isProcessing.value,
      currentOrder: currentOrder.value,
      paymentStatus: paymentStatus.value,
      error: error.value
    };
  }

  return {
    // State
    paypalConfig,
    currentOrder,
    paymentStatus,
    isLoading,
    isProcessing,
    error,
    
    // Getters
    hasPayPalConfig,
    isPaymentComplete,
    paypalClientId,
    
    // Actions
    fetchPayPalConfig,
    createPayPalOrder,
    capturePayPalOrder,
    sendGift,
    clearPaymentState,
    clearError,
    getPaymentState
  };
});

