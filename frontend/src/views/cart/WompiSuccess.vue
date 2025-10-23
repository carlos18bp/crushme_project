<template>
  <div class="wompi-success-view">
    <div class="success-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <h2>Verificando tu pago...</h2>
        <p>Por favor espera mientras confirmamos tu transacción</p>
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
        <button @click="goToHome" class="btn-primary">Ir al inicio</button>
      </div>

      <!-- Error State -->
      <div v-else class="error-state">
        <div class="error-icon">❌</div>
        <h2>Error en el Pago</h2>
        <p class="error-message">{{ errorMessage }}</p>
        <div class="error-actions">
          <button @click="goToCheckout" class="btn-secondary">Volver al checkout</button>
          <button @click="retry" class="btn-primary">Reintentar verificación</button>
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

async function confirmPayment() {
  try {
    // Obtener transaction_id de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const transactionId = urlParams.get('id');
    
    if (!transactionId) {
      throw new Error('No se encontró el ID de transacción en la URL');
    }

    console.log('✅ [WOMPI] Transaction ID desde URL:', transactionId);

    // Recuperar datos de la orden guardados en localStorage
    const orderDataStr = localStorage.getItem('wompi_order_data');
    
    if (!orderDataStr) {
      throw new Error('No se encontraron los datos de la orden. Por favor vuelve al checkout.');
    }

    const orderData = JSON.parse(orderDataStr);
    console.log('📦 [WOMPI] Datos de orden recuperados:', orderData);

    // Confirmar pago con el backend
    const result = await paymentStore.confirmWompiPayment(transactionId, orderData);

    if (result.success) {
      console.log('✅ [WOMPI] Pago confirmado exitosamente:', result.order);
      
      success.value = true;
      orderNumber.value = result.order.order_number;
      total.value = parseFloat(result.order.total);
      email.value = result.order.email;

      // Limpiar localStorage
      localStorage.removeItem('wompi_transaction_id');
      localStorage.removeItem('wompi_order_data');

      // Limpiar sessionStorage
      sessionStorage.removeItem('checkout_order_data');

      // Limpiar carrito
      cartStore.clearCart();

      // Limpiar estado de pago
      paymentStore.clearPaymentState();

    } else {
      throw new Error(result.error || 'Error al confirmar el pago');
    }

  } catch (error) {
    console.error('❌ [WOMPI] Error al confirmar pago:', error);
    
    success.value = false;
    errorMessage.value = error.message || 'Error al verificar el pago. Por favor contacta a soporte.';

  } finally {
    loading.value = false;
  }
}

// Lifecycle
onMounted(async () => {
  await confirmPayment();
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
