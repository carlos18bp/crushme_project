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
  const wompiConfig = ref(null);
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
   * Obtener configuración de Wompi
   * GET /api/orders/wompi/config/
   */
  async function fetchWompiConfig() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('orders/wompi/config/');
      
      wompiConfig.value = {
        public_key: response.data.public_key,
        currency: response.data.currency,
        environment: response.data.environment
      };

      return { 
        success: true, 
        data: wompiConfig.value 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch Wompi configuration';
      return { 
        success: false, 
        error: error.value 
      };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Crear transacción Wompi
   * POST /api/orders/wompi/create/
   * @param {Object} orderData - Datos de la orden
   */
  async function createWompiTransaction(orderData) {
    isProcessing.value = true;
    error.value = null;

    try {
      console.log('💳 [WOMPI] Preparando widget de pago...', orderData);
      
      const response = await create_request('orders/wompi/create/', orderData);
      
      // El backend ahora retorna widget_data en lugar de payment_url
      const transactionData = {
        widget_data: response.data.widget_data,
        reference: response.data.reference,
        total: response.data.total,
        amount_in_cents: response.data.amount_in_cents,
        items_count: response.data.items_count
      };

      currentOrder.value = transactionData;

      console.log('✅ [WOMPI] Widget data recibida:', transactionData);

      return { 
        success: true, 
        data: transactionData
      };
    } catch (err) {
      console.error('❌ [WOMPI] Error preparando widget:', err);
      error.value = err.response?.data?.error || 'Failed to prepare Wompi widget';

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
   * Verificar estado del pago Wompi (polling)
   * GET /api/orders/wompi/status/{reference}/
   * @param {string} reference - Referencia de la transacción
   */
  async function checkWompiPaymentStatus(reference) {
    try {
      const response = await get_request(`orders/wompi/status/${reference}/`);
      
      return {
        status: response.data.status, // 'pending', 'success', or 'error'
        order_id: response.data.order_id,
        transaction_id: response.data.transaction_id,
        error: response.data.error,
        message: response.data.message
      };
    } catch (err) {
      console.error('❌ [WOMPI] Error verificando estado:', err);
      
      return {
        status: 'error',
        error: err.response?.data?.error || 'Failed to check payment status'
      };
    }
  }

  /**
   * Confirmar pago Wompi y crear orden
   * POST /api/orders/wompi/confirm/
   * @param {string} transactionId - ID de la transacción de Wompi
   * @param {Object} confirmData - Datos completos de la orden
   */
  async function confirmWompiPayment(transactionId, confirmData) {
    isProcessing.value = true;
    error.value = null;

    try {
      console.log('✅ [WOMPI] Confirmando pago...', { transactionId, confirmData });
      
      const dataToSend = {
        transaction_id: transactionId,
        ...confirmData
      };

      const response = await create_request('orders/wompi/confirm/', dataToSend);

      const confirmResult = {
        order: response.data.order,
        payment: response.data.payment,
        woocommerce_integration: response.data.woocommerce_integration
      };

      currentOrder.value = confirmResult.order;
      paymentStatus.value = confirmResult.payment.status;

      console.log('✅ [WOMPI] Pago confirmado:', confirmResult);

      return {
        success: true,
        data: confirmResult,
        order: confirmResult.order,
        payment: confirmResult.payment
      };
    } catch (err) {
      console.error('❌ [WOMPI] Error confirmando pago:', err);
      error.value = err.response?.data?.error || 'Failed to confirm Wompi payment';

      return {
        success: false,
        error: error.value,
        details: err.response?.data?.details,
        status: err.response?.data?.status
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
   * Validar código de descuento
   * POST /api/discounts/validate/
   */
  async function validateDiscountCode(code) {
    isLoading.value = true;
    error.value = null;

    try {
      console.log('🎟️ [PAYMENT STORE] Validando código de descuento:', code);

      const response = await create_request('discounts/validate/', {
        code: code
      });

      console.log('🎟️ [PAYMENT STORE] Respuesta de validación:', response.data);

      return {
        success: true,
        data: response.data
      };
    } catch (err) {
      console.error('❌ [PAYMENT STORE] Error validando código:', err);
      error.value = err.response?.data?.error || 'Failed to validate discount code';

      return {
        success: false,
        error: error.value,
        data: err.response?.data
      };
    } finally {
      isLoading.value = false;
    }
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
    wompiConfig,
    currentOrder,
    paymentStatus,
    isLoading,
    isProcessing,
    error,
    
    // Getters
    hasPayPalConfig,
    isPaymentComplete,
    paypalClientId,
    
    // Actions - PayPal
    fetchPayPalConfig,
    createPayPalOrder,
    capturePayPalOrder,
    sendGift,
    
    // Actions - Wompi
    fetchWompiConfig,
    createWompiTransaction,
    checkWompiPaymentStatus,
    confirmWompiPayment,
    
    // Actions - Discounts
    validateDiscountCode,
    
    // Actions - Common
    clearPaymentState,
    clearError,
    getPaymentState
  };
});

