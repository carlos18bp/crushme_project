<template>
  <div class="wompi-success-view">
    <div class="success-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <h2>Procesando tu pago...</h2>
        <p>Wompi está confirmando tu transacción. Esto puede tomar unos segundos.</p>
        <p class="polling-info">⏳ Verificando estado... ({{ pollingAttempts }}/{{ maxPollingAttempts }})</p>
      </div>

      <!-- Success State -->
      <div v-else-if="success" class="success-state">
        <div class="success-icon">✅</div>
        <h2>¡Pago Exitoso!</h2>
        <div class="order-details">
          <p class="order-number">Número de orden: <strong>{{ orderNumber }}</strong></p>
          <p class="order-total">Total: <strong>{{ formatPrice(total) }}</strong></p>
          <p class="order-email">Recibirás un email de confirmación en: <strong>{{ email }}</strong></p>
        </div>
        <p class="redirect-message">Redirigiendo al inicio en {{ redirectCountdown }} segundo{{ redirectCountdown !== 1 ? 's' : '' }}...</p>
        <button @click="goToHome" class="btn-primary">Ir al inicio ahora</button>
      </div>

      <!-- Error State -->
      <div v-else class="error-state">
        <div class="error-icon">❌</div>
        <h2>Error en el Pago</h2>
        <p class="error-message">{{ errorMessage }}</p>
        
        <!-- Instrucciones si no hay transaction ID -->
        <div v-if="!hasTransactionId" class="manual-instructions">
          <p class="instruction-title">💡 ¿Completaste el pago en Wompi?</p>
          <p class="instruction-text">
            Si completaste el pago exitosamente pero llegaste aquí directamente, 
            copia el <strong>ID de transacción</strong> de la URL de Wompi y pégalo aquí:
          </p>
          <div class="manual-input-group">
            <input 
              v-model="manualTransactionId" 
              type="text" 
              placeholder="Ej: test_abc123"
              class="manual-input"
            />
            <button @click="verifyManualTransaction" class="btn-primary">Verificar</button>
          </div>
        </div>
        
        <div class="error-actions">
          <button @click="goToCheckout" class="btn-secondary">Volver al checkout</button>
          <button v-if="hasTransactionId" @click="retry" class="btn-primary">Reintentar verificación</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCartStore } from '@/stores/modules/cartStore.js';
import { usePaymentStore } from '@/stores/modules/paymentStore.js';
import { useCurrencyStore } from '@/stores/modules/currencyStore.js';
import { useI18nStore } from '@/stores/modules/i18nStore';

const router = useRouter();
const cartStore = useCartStore();
const paymentStore = usePaymentStore();
const currencyStore = useCurrencyStore();
const i18nStore = useI18nStore();

// State
const loading = ref(true);
const success = ref(false);
const orderNumber = ref('');
const total = ref(0);
const email = ref('');
const errorMessage = ref('');
const redirectCountdown = ref(3);
const hasTransactionId = ref(false);
const manualTransactionId = ref('');
const pollingAttempts = ref(0);
const maxPollingAttempts = ref(60); // 60 intentos = 1 minuto (1 intento cada segundo)
const pollingInterval = ref(null);

// Methods
const formatPrice = (price) => {
  return currencyStore.formatPrice(price);
};

function goToHome() {
  router.push({ name: `Home-${i18nStore.locale}` });
}

function goToCheckout() {
  router.push({ name: `Checkout-${i18nStore.locale}` });
}

async function retry() {
  loading.value = true;
  success.value = false;
  errorMessage.value = '';
  await confirmPayment();
}

async function verifyManualTransaction() {
  if (!manualTransactionId.value.trim()) {
    errorMessage.value = 'Por favor ingresa un ID de transacción válido';
    return;
  }
  
  // Actualizar URL con el transaction ID manual
  const newUrl = `${window.location.pathname}?id=${manualTransactionId.value.trim()}`;
  window.history.pushState({}, '', newUrl);
  
  // Reintentar confirmación
  await retry();
}

async function checkPaymentStatus() {
  try {
    // Obtener reference de localStorage
    const reference = localStorage.getItem('wompi_reference');
    
    if (!reference) {
      throw new Error('No se encontró la referencia de pago. Por favor vuelve al checkout.');
    }

    console.log(`🔍 [WOMPI] Verificando estado del pago (intento ${pollingAttempts.value + 1}/${maxPollingAttempts.value})`);
    
    // Llamar al endpoint de polling
    const result = await paymentStore.checkWompiPaymentStatus(reference);
    
    if (result.status === 'success') {
      // Pago procesado exitosamente por el webhook
      console.log('✅ [WOMPI] Pago confirmado por webhook:', result);
      
      // Detener polling
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value);
        pollingInterval.value = null;
      }
      
      success.value = true;
      orderNumber.value = result.order_id;
      
      // Recuperar datos de orden para mostrar total y email
      const orderDataStr = localStorage.getItem('wompi_order_data');
      if (orderDataStr) {
        const orderData = JSON.parse(orderDataStr);
        total.value = parseFloat(orderData.total || 0);
        email.value = orderData.customer_email || '';
      }

      // Limpiar localStorage
      localStorage.removeItem('wompi_reference');
      localStorage.removeItem('wompi_order_data');
      localStorage.removeItem('wompi_widget_data');

      // Limpiar sessionStorage
      sessionStorage.removeItem('checkout_order_data');

      // Limpiar carrito
      cartStore.clearCart();

      // Limpiar estado de pago
      paymentStore.clearPaymentState();

      loading.value = false;

      // Iniciar contador de redirección
      const countdownInterval = setInterval(() => {
        redirectCountdown.value--;
        if (redirectCountdown.value <= 0) {
          clearInterval(countdownInterval);
          goToHome();
        }
      }, 1000);
      
    } else if (result.status === 'error') {
      // Error al procesar el pago
      console.error('❌ [WOMPI] Error en el pago:', result.error);
      
      // Detener polling
      if (pollingInterval.value) {
        clearInterval(pollingInterval.value);
        pollingInterval.value = null;
      }
      
      loading.value = false;
      success.value = false;
      errorMessage.value = result.error || 'Error al procesar el pago';
      
    } else {
      // Status 'pending' - continuar polling
      pollingAttempts.value++;
      
      if (pollingAttempts.value >= maxPollingAttempts.value) {
        // Timeout - demasiados intentos
        console.warn('⏱️ [WOMPI] Timeout esperando confirmación del pago');
        
        if (pollingInterval.value) {
          clearInterval(pollingInterval.value);
          pollingInterval.value = null;
        }
        
        loading.value = false;
        success.value = false;
        errorMessage.value = 'El pago está tomando más tiempo de lo esperado. Por favor verifica tu email o contacta a soporte.';
      }
    }

  } catch (error) {
    console.error('❌ [WOMPI] Error al verificar estado:', error);
    
    // Detener polling en caso de error
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value);
      pollingInterval.value = null;
    }
    
    loading.value = false;
    success.value = false;
    errorMessage.value = error.message || 'Error al verificar el pago. Por favor contacta a soporte.';
  }
}

function startPolling() {
  // Verificar inmediatamente
  checkPaymentStatus();
  
  // Luego verificar cada segundo
  pollingInterval.value = setInterval(() => {
    checkPaymentStatus();
  }, 1000);
}

// Lifecycle
onMounted(() => {
  console.log('🚀 [WOMPI SUCCESS] Iniciando polling de estado de pago');
  startPolling();
});

// Cleanup on unmount
import { onUnmounted } from 'vue';
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
});
</script>

<style scoped>
.wompi-success-view {
  min-height: 100vh;
  background: var(--color-brand-pink-lighter);
  padding: 2rem 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-container {
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 24px;
  padding: 3rem 2rem;
  box-shadow: 0 10px 40px rgba(191, 94, 129, 0.15);
  text-align: center;
  border: 1px solid var(--color-brand-pink-light);
}

/* Loading State */
.loading-state h2 {
  font-size: 1.625rem;
  font-weight: 600;
  color: var(--color-brand-dark);
  margin: 1.5rem 0 0.75rem 0;
  font-family: 'Comfortaa', cursive;
}

.loading-state p {
  color: var(--color-brand-blue-medium);
  font-size: 1rem;
}

.polling-info {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--color-brand-purple-light);
  font-style: italic;
}

.spinner {
  width: 70px;
  height: 70px;
  border: 5px solid var(--color-brand-pink-light);
  border-top: 5px solid var(--color-brand-pink);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Success State */
.success-state {
  animation: fadeIn 0.5s ease-in;
}

.success-icon {
  font-size: 5.5rem;
  margin-bottom: 1.25rem;
}

.success-state h2 {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-brand-pink);
  margin-bottom: 1.75rem;
  font-family: 'Comfortaa', cursive;
}

.order-details {
  background: var(--color-brand-pink-lighter);
  border-radius: 16px;
  padding: 1.75rem;
  margin: 1.5rem 0 2rem 0;
  text-align: left;
  border: 1px solid var(--color-brand-pink-light);
}

.order-details p {
  margin: 0.875rem 0;
  color: var(--color-brand-dark);
  font-size: 1rem;
}

.order-number,
.order-total,
.order-email {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.order-details strong {
  color: var(--color-brand-pink-dark);
  font-weight: 600;
  font-size: 1.125rem;
}

.redirect-message {
  color: var(--color-brand-blue-medium);
  font-size: 0.9375rem;
  margin: 1.5rem 0 1rem 0;
  font-style: italic;
}

/* Error State */
.error-state {
  animation: fadeIn 0.5s ease-in;
}

.error-icon {
  font-size: 5.5rem;
  margin-bottom: 1.25rem;
}

.error-state h2 {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--color-brand-pink-dark);
  margin-bottom: 1rem;
  font-family: 'Comfortaa', cursive;
}

.error-message {
  color: var(--color-brand-blue-medium);
  font-size: 1rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Buttons */
.btn-primary,
.btn-secondary {
  width: 100%;
  padding: 1rem 2rem;
  border-radius: 16px;
  font-size: 1.0625rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  font-family: 'Poppins', sans-serif;
}

.btn-primary {
  background: var(--color-brand-purple-light);
  color: white;
  box-shadow: 0 6px 20px rgba(218, 157, 255, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(218, 157, 255, 0.5);
  opacity: 0.9;
}

.btn-secondary {
  background: white;
  color: var(--color-brand-dark);
  border: 2px solid var(--color-brand-pink-light);
}

.btn-secondary:hover {
  background: var(--color-brand-pink-lighter);
  border-color: var(--color-brand-pink-medium);
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Manual Instructions */
.manual-instructions {
  background: var(--color-brand-pink-lighter);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  text-align: left;
  border: 1px solid var(--color-brand-pink-light);
}

.instruction-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-brand-pink-dark);
  margin-bottom: 0.75rem;
}

.instruction-text {
  color: var(--color-brand-dark);
  font-size: 0.9375rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.manual-input-group {
  display: flex;
  gap: 0.75rem;
  flex-direction: column;
}

.manual-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid var(--color-brand-pink-light);
  border-radius: 12px;
  font-size: 1rem;
  font-family: 'Poppins', sans-serif;
  transition: border-color 0.3s ease;
}

.manual-input:focus {
  outline: none;
  border-color: var(--color-brand-purple-light);
}

.manual-input::placeholder {
  color: var(--color-brand-blue-medium);
  opacity: 0.6;
}

/* Responsive */
@media (max-width: 640px) {
  .success-container {
    padding: 2rem 1.5rem;
  }

  .success-state h2,
  .error-state h2 {
    font-size: 1.5rem;
  }

  .success-icon,
  .error-icon {
    font-size: 4rem;
  }
}
</style>
