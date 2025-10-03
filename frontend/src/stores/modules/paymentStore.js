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
      console.log('💳 [PAYMENT STORE] Obteniendo configuración de PayPal...');
      const response = await get_request('orders/paypal/config/');
      
      paypalConfig.value = {
        client_id: response.data.client_id,
        currency: response.data.currency,
        mode: response.data.mode
      };

      console.log('✅ [PAYMENT STORE] Configuración de PayPal obtenida:', {
        currency: paypalConfig.value.currency,
        mode: paypalConfig.value.mode,
        hasClientId: !!paypalConfig.value.client_id
      });

      return { 
        success: true, 
        data: paypalConfig.value 
      };
    } catch (err) {
      console.error('❌ [PAYMENT STORE] Error al obtener configuración de PayPal:', err);
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
      console.log('💳 [PAYMENT STORE] Creando orden PayPal...');
      console.log('📦 [PAYMENT STORE] Datos de envío:', shippingData);

      const response = await create_request('orders/paypal/create/', shippingData);
      
      const orderData = {
        paypal_order_id: response.data.paypal_order_id,
        total: response.data.total,
        items_count: response.data.items_count
      };

      currentOrder.value = orderData;

      console.log('✅ [PAYMENT STORE] Orden PayPal creada exitosamente:', {
        paypal_order_id: orderData.paypal_order_id,
        total: orderData.total,
        items_count: orderData.items_count
      });

      return { 
        success: true, 
        data: orderData,
        paypal_order_id: orderData.paypal_order_id
      };
    } catch (err) {
      console.error('❌ [PAYMENT STORE] Error al crear orden PayPal:', err);
      error.value = err.response?.data?.error || 'Failed to create PayPal order';
      
      // Detalles adicionales del error
      if (err.response?.data?.details) {
        console.error('📋 [PAYMENT STORE] Detalles del error:', err.response.data.details);
      }

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
      console.log('💳 [PAYMENT STORE] Capturando pago PayPal...');
      console.log('📋 [PAYMENT STORE] PayPal Order ID:', paypalOrderId);
      console.log('📦 [PAYMENT STORE] Datos completos:', captureData);

      // Los datos ya vienen completos con paypal_order_id, items, shipping, etc.
      const response = await create_request('orders/paypal/capture/', captureData);
      
      const captureResult = {
        order: response.data.order,
        payment: response.data.payment,
        woocommerce_integration: response.data.woocommerce_integration
      };

      currentOrder.value = captureResult.order;
      paymentStatus.value = captureResult.payment.status;

      console.log('✅ [PAYMENT STORE] Pago capturado exitosamente');
      console.log('📋 [PAYMENT STORE] Orden creada:', {
        order_number: captureResult.order.order_number,
        order_id: captureResult.order.id,
        total: captureResult.order.total,
        status: captureResult.order.status
      });
      console.log('💰 [PAYMENT STORE] Estado del pago:', captureResult.payment.status);
      console.log('🛒 [PAYMENT STORE] WooCommerce:', {
        sent: captureResult.woocommerce_integration.sent,
        woocommerce_order_id: captureResult.woocommerce_integration.woocommerce_order_id
      });

      return { 
        success: true, 
        data: captureResult,
        order: captureResult.order,
        payment: captureResult.payment
      };
    } catch (err) {
      console.error('❌ [PAYMENT STORE] Error al capturar pago PayPal:', err);
      error.value = err.response?.data?.error || 'Failed to capture PayPal payment';
      
      // Detalles adicionales del error
      if (err.response?.data?.details) {
        console.error('📋 [PAYMENT STORE] Detalles del error:', err.response.data.details);
      }
      if (err.response?.data?.paypal_status) {
        console.error('💳 [PAYMENT STORE] Estado de PayPal:', err.response.data.paypal_status);
      }

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
   * Limpiar estado de pago
   */
  function clearPaymentState() {
    console.log('🧹 [PAYMENT STORE] Limpiando estado de pago');
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
    clearPaymentState,
    clearError,
    getPaymentState
  };
});

