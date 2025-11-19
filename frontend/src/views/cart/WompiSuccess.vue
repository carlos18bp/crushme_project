<template>
  <div class="wompi-success-view">
    <!-- Contenedor vacío - Todo se maneja con SweetAlert2 -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/stores/modules/cartStore.js';
import { usePaymentStore } from '@/stores/modules/paymentStore.js';
import { useCurrencyStore } from '@/stores/modules/currencyStore.js';
import { useI18nStore } from '@/stores/modules/i18nStore';
import { useAlert } from '@/composables/useAlert.js';

const router = useRouter();
const cartStore = useCartStore();
const paymentStore = usePaymentStore();
const currencyStore = useCurrencyStore();
const i18nStore = useI18nStore();
const { showLoading, showSuccess, showError, closeAlert } = useAlert();

// State
const pollingInterval = ref(null);
const maxPollingAttempts = ref(300); // 300 segundos = 5 minutos (máximo, se detiene antes si responde)
const pollingAttempts = ref(0);

// Methods
const formatPrice = (price) => {
  return currencyStore.formatPrice(price);
};

function goToHome() {
  closeAlert();
  router.push({ name: `Home-${i18nStore.locale}` });
}

async function checkPaymentStatus() {
  try {
    const reference = localStorage.getItem('wompi_reference');
    
    if (!reference) {
      throw new Error('No se encontró la referencia de pago.');
    }

    console.log(`🔍 [WOMPI] Verificando estado del pago...`);
    
    const result = await paymentStore.checkWompiPaymentStatus(reference);
    
    if (result.status === 'success') {
      console.log('✅ [WOMPI] Pago confirmado:', result);
      
      // Detener polling
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value);
        pollingInterval.value = null;
      }
      
      // Recuperar datos de orden
      const orderDataStr = localStorage.getItem('wompi_order_data');
      let total = 0;
      let email = '';
      
      if (orderDataStr) {
        const orderData = JSON.parse(orderDataStr);
        total = parseFloat(orderData.total || 0);
        email = orderData.customer_email || '';
      }

      // Limpiar datos
      localStorage.removeItem('wompi_reference');
      localStorage.removeItem('wompi_order_data');
      localStorage.removeItem('wompi_widget_data');
      sessionStorage.removeItem('checkout_order_data');
      cartStore.clearCart();
      paymentStore.clearPaymentState();

      // Mostrar éxito con SweetAlert2
      closeAlert();
      await showSuccess(
        `Tu pago ha sido confirmado exitosamente.\nRecibirás un email de confirmación en: ${email}`,
        '🎉 ¡Pago Exitoso!',
        {
          timer: 5000,
          timerProgressBar: true,
          willClose: () => {
            goToHome();
          }
        }
      );
      
    } else if (result.status === 'error') {
      console.error('❌ [WOMPI] Error:', result.error);
      
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value);
        pollingInterval.value = null;
      }
      
      closeAlert();
      await showError(
        result.error || 'Hubo un problema al procesar tu pago.',
        '❌ Error en el Pago',
        {
          confirmButtonText: 'Volver al checkout',
          willClose: () => {
            router.push({ name: `Checkout-${i18nStore.locale}` });
          }
        }
      );
      
    } else {
      // Status 'pending' - continuar polling
      pollingAttempts.value++;
      
      if (pollingAttempts.value >= maxPollingAttempts.value) {
        console.warn('⏱️ [WOMPI] Timeout');
        
        if (pollingInterval.value) {
          clearInterval(pollingInterval.value);
          pollingInterval.value = null;
        }
        
        closeAlert();
        await showError(
          'El pago está tomando más tiempo de lo esperado. Por favor verifica tu email o contacta a soporte.',
          '⏱️ Tiempo de espera agotado'
        );
      }
    }

  } catch (error) {
    console.error('❌ [WOMPI] Error:', error);
    
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value);
      pollingInterval.value = null;
    }
    
    closeAlert();
    await showError(
      error.message || 'Error al verificar el pago.',
      '❌ Error'
    );
  }
}

function startPolling() {
  // Mostrar loading
  showLoading('Verificando tu pago con Wompi...', '💳 Procesando');
  
  // Verificar inmediatamente
  checkPaymentStatus();
  
  // Luego verificar cada segundo
  pollingInterval.value = setInterval(() => {
    checkPaymentStatus();
  }, 1000);
}

// Lifecycle
onMounted(() => {
  console.log('🚀 [WOMPI SUCCESS] Iniciando verificación de pago');
  startPolling();
});

// Cleanup
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
  closeAlert();
});
</script>

<style scoped>
.wompi-success-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8E8F0 0%, #E8F4F8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
