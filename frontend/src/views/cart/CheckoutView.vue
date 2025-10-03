<template>
  <div class="checkout-view">
    <div class="checkout-container">
      <!-- Left Column - Shipping Information -->
      <div class="shipping-section">
        <div class="shipping-card">
          <h2 class="section-title">Shipping information</h2>
          
          <!-- Shipping Type -->
          <div class="shipping-type">
            <label class="radio-label">
              <input type="radio" name="shipping-type" value="me" v-model="shippingType" checked>
              <span>For me</span>
            </label>
            <label class="radio-label">
              <input type="radio" name="shipping-type" value="gift" v-model="shippingType">
              <span>For gift</span>
            </label>
          </div>

          <!-- Form Fields -->
          <div class="form-group">
            <label for="email">Email <span class="text-red-500">*</span></label>
            <input 
              type="email" 
              id="email" 
              v-model="shippingForm.email"
              placeholder="you@example.com"
              class="form-input"
              required
            >
          </div>

          <div class="form-group">
            <label for="fullname">Full name <span class="text-red-500">*</span></label>
            <input 
              type="text" 
              id="fullname" 
              v-model="shippingForm.fullName"
              placeholder="John Doe"
              class="form-input"
              required
            >
          </div>

          <div class="form-group">
            <label for="country">Country or Region</label>
            <select
              id="country"
              v-model="shippingForm.country"
              @change="onCountryChange"
              class="form-input form-select"
            >
              <option value="">Select a country</option>
              <option v-for="country in countries" :key="country.isoCode" :value="country.isoCode">
                {{ country.flag }} {{ country.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="address1">Address line 1 <span class="text-red-500">*</span></label>
            <input 
              type="text" 
              id="address1" 
              v-model="shippingForm.address1"
              placeholder="123 Main Street"
              class="form-input"
              required
            >
          </div>

          <div class="form-group">
            <label for="address2">Address line 2</label>
            <input 
              type="text" 
              id="address2" 
              v-model="shippingForm.address2"
              placeholder="Apt, suite, unit number, etc. (optional)"
              class="form-input"
            >
          </div>

          <div class="form-group">
            <label for="city">City <span class="text-red-500">*</span></label>
            <input 
              type="text" 
              id="city" 
              v-model="shippingForm.city"
              placeholder="New York"
              class="form-input"
              required
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="state">State / Province <span class="text-red-500">*</span></label>
              <select
                id="state"
                v-model="shippingForm.state"
                :disabled="!shippingForm.country"
                class="form-input form-select"
                required
              >
                <option value="">{{ shippingForm.country ? 'Select a state' : 'Select country first' }}</option>
                <option v-for="state in availableStates" :key="state.isoCode" :value="state.name">
                  {{ state.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="zipcode">ZIP / Postal Code <span class="text-red-500">*</span></label>
              <input 
                type="text" 
                id="zipcode" 
                v-model="shippingForm.zipCode"
                placeholder="10001"
                class="form-input"
                required
              >
            </div>
          </div>

          <div class="form-group">
            <label for="phone">Phone <span class="text-red-500">*</span></label>
            <div class="phone-input">
              <select v-model="shippingForm.phoneCode" class="phone-code">
                <option v-for="country in countryCodes" :key="country.code" :value="country.dial_code">
                  {{ country.flag }} {{ country.dial_code }}
                </option>
              </select>
              <input 
                type="tel" 
                id="phone" 
                v-model="shippingForm.phone"
                placeholder="123 456 7890"
                class="form-input phone-number"
                required
              >
            </div>
          </div>

          <div class="form-group">
            <label for="additional">Additional address details (optional)</label>
            <textarea 
              id="additional" 
              v-model="shippingForm.additionalDetails"
              placeholder="Special delivery instructions, gate codes, building details, etc."
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <h3 class="payment-title">Payment method</h3>
            <p class="payment-subtitle">Select your preferred payment method</p>
            
            <!-- PayPal Button Container -->
            <div id="paypal-button-container" class="paypal-container"></div>
            <p v-if="paypalError" class="payment-error">{{ paypalError }}</p>
          </div>
        </div>
      </div>

      <!-- Right Column - Order Summary -->
      <div class="summary-section">
        <div class="summary-card">
          <h2 class="section-title">Order Summary</h2>
          
          <!-- Loading State -->
          <div v-if="cartStore.isUpdating" class="loading-state">
            <p>Cargando productos...</p>
          </div>
          
          <!-- Products List -->
          <div v-else class="products-list">
            <div 
              v-for="item in cartItems" 
              :key="item.id"
              class="product-item"
            >
              <div class="product-image">
                <img 
                  :src="item.image || 'https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=200'" 
                  :alt="item.name || 'Product'"
                >
              </div>
              <div class="product-details">
                <h4 class="product-name">{{ item.name || 'Product' }}</h4>
                <p class="product-meta" v-if="item.color">Color: {{ item.color }}</p>
                <p class="product-meta" v-if="item.size">Talla: {{ item.size }}</p>
              </div>
              <div class="product-quantity">
                <span>{{ item.quantity }}</span>
              </div>
              <div class="product-price">
                ${{ formatPrice(item.price * item.quantity) }}
              </div>
            </div>
          </div>

          <!-- Discount Code -->
          <div class="discount-section">
            <h3 class="discount-title">Discount code</h3>
            <div class="discount-input">
              <input 
                type="text" 
                v-model="discountCode"
                placeholder="Enter your discount code"
                class="form-input"
              >
              <button class="validate-btn">Validate</button>
            </div>
          </div>

          <!-- Totals -->
          <div class="totals-section">
            <div class="total-row">
              <span>Subtotal</span>
              <span class="total-value">${{ formatPrice(subtotal) }}</span>
            </div>
            <div class="total-row">
              <span>Shipping</span>
              <span class="total-value">${{ formatPrice(shipping) }}</span>
            </div>
            <div class="total-row tax-row">
              <span>Tax (19%)</span>
              <span class="total-value">${{ formatPrice(tax) }}</span>
            </div>
          </div>

          <!-- Final Total -->
          <div class="final-total">
            <div class="total-row">
              <span class="total-label">Total</span>
              <span class="total-amount">${{ formatPrice(total) }}</span>
            </div>
            <p class="tax-note">Includes ${{ formatPrice(tax) }} in taxes</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useCartStore } from '@/stores/modules/cartStore.js';
import { useI18nStore } from '@/stores/modules/i18nStore';
import { usePaymentStore } from '@/stores/modules/paymentStore.js';
import { useRouter } from 'vue-router';
import { useAlert } from '@/composables/useAlert.js';
import { Country, State } from 'country-state-city';

const router = useRouter();
const cartStore = useCartStore();
const i18nStore = useI18nStore();
const paymentStore = usePaymentStore();
const { showSuccess, showError, showLoading, closeAlert } = useAlert();

// Get all countries with flags
const countries = Country.getAllCountries().map(country => ({
  ...country,
  flag: country.flag || '🏳️'
}));

// Country codes for phone selector
const countryCodes = [
  { code: 'US', dial_code: '+1', flag: '🇺🇸', name: 'United States' },
  { code: 'CA', dial_code: '+1', flag: '🇨🇦', name: 'Canada' },
  { code: 'MX', dial_code: '+52', flag: '🇲🇽', name: 'Mexico' },
  { code: 'CO', dial_code: '+57', flag: '🇨🇴', name: 'Colombia' },
  { code: 'AR', dial_code: '+54', flag: '🇦🇷', name: 'Argentina' },
  { code: 'BR', dial_code: '+55', flag: '🇧🇷', name: 'Brazil' },
  { code: 'CL', dial_code: '+56', flag: '🇨🇱', name: 'Chile' },
  { code: 'ES', dial_code: '+34', flag: '🇪🇸', name: 'Spain' },
  { code: 'GB', dial_code: '+44', flag: '🇬🇧', name: 'United Kingdom' },
];

// Shipping form data
const shippingType = ref('me');
const shippingForm = ref({
  email: '',
  fullName: '',
  country: 'US', // Default to US, store ISO code
  address1: '',
  address2: '',
  city: '',
  state: '',
  zipCode: '',
  phoneCode: '+1',
  phone: '',
  additionalDetails: ''
});

const discountCode = ref('');
const paypalError = ref('');
const paypalScriptLoaded = ref(false);

// Computed property for available states based on selected country
const availableStates = computed(() => {
  if (!shippingForm.value.country) return [];
  return State.getStatesOfCountry(shippingForm.value.country);
});

// Function to handle country change
const onCountryChange = () => {
  // Reset state when country changes
  shippingForm.value.state = '';
};

// Get cart items
const cartItems = computed(() => cartStore.items);

// Calculate totals
const subtotal = computed(() => cartStore.totalPrice);

const shipping = computed(() => {
  // Calcular envío estándar (puedes ajustar la lógica según necesites)
  const subtotalValue = subtotal.value;
  if (subtotalValue >= 100) {
    return 0; // Envío gratis para compras mayores a $100
  }
  return 10; // Envío estándar $10
});

const tax = computed(() => {
  // 19% de impuesto sobre el subtotal
  return subtotal.value * 0.19;
});

const total = computed(() => {
  return subtotal.value + shipping.value + tax.value;
});

// Format price helper
const formatPrice = (price) => {
  return Number(price).toFixed(2);
};

// PayPal Integration Functions
/**
 * Carga el SDK de PayPal dinámicamente
 */
const loadPayPalScript = async () => {
  return new Promise(async (resolve, reject) => {
    // Verificar si ya existe el script
    if (window.paypal) {
      console.log('💳 [PAYPAL] SDK ya está cargado');
      paypalScriptLoaded.value = true;
      resolve();
      return;
    }

    // Verificar si el script ya está en el DOM
    const existingScript = document.querySelector('script[src*="paypal.com/sdk/js"]');
    if (existingScript) {
      existingScript.addEventListener('load', () => {
        console.log('💳 [PAYPAL] SDK cargado desde script existente');
        paypalScriptLoaded.value = true;
        resolve();
      });
      return;
    }

    console.log('💳 [PAYPAL] Obteniendo configuración de PayPal...');
    
    // Obtener configuración de PayPal desde el backend
    const configResult = await paymentStore.fetchPayPalConfig();
    
    if (!configResult.success) {
      console.error('❌ [PAYPAL] Error al obtener configuración');
      paypalError.value = 'Error al obtener configuración de PayPal. Por favor recarga la página.';
      reject(new Error(configResult.error));
      return;
    }

    const config = configResult.data;
    console.log('💳 [PAYPAL] Cargando SDK con configuración del backend...');
    
    const script = document.createElement('script');
    
    // Configurar el script según la documentación de PayPal usando config del backend
    script.src = `https://www.paypal.com/sdk/js?client-id=${config.client_id}&buyer-country=US&currency=${config.currency}&components=buttons&enable-funding=venmo,paylater,card`;
    script.setAttribute('data-sdk-integration-source', 'developer-studio');
    
    script.onload = () => {
      console.log('✅ [PAYPAL] SDK cargado exitosamente');
      console.log('💳 [PAYPAL] Configuración:', {
        currency: config.currency,
        mode: config.mode
      });
      paypalScriptLoaded.value = true;
      resolve();
    };
    
    script.onerror = (error) => {
      console.error('❌ [PAYPAL] Error al cargar SDK:', error);
      paypalError.value = 'Error al cargar PayPal. Por favor recarga la página.';
      reject(error);
    };
    
    document.head.appendChild(script);
  });
};

/**
 * Inicializa los botones de PayPal
 */
const initPayPalButtons = () => {
  if (!window.paypal) {
    console.error('❌ [PAYPAL] SDK no está disponible');
    paypalError.value = 'PayPal no está disponible. Por favor recarga la página.';
    return;
  }

  const container = document.getElementById('paypal-button-container');
  if (!container) {
    console.error('❌ [PAYPAL] Contenedor no encontrado');
    return;
  }

  // Limpiar contenedor si ya tiene botones
  container.innerHTML = '';

  console.log('💳 [PAYPAL] Renderizando botones...');

  try {
    window.paypal.Buttons({
      // Estilo de los botones
      style: {
        layout: 'vertical',
        color: 'gold',
        shape: 'rect',
        label: 'paypal'
      },

      // Crear orden
      createOrder: async (data, actions) => {
        console.log('💳 [PAYPAL] Creando orden...');
        console.log('📦 [PAYPAL] Items del carrito:', cartStore.items);
        console.log('💰 [PAYPAL] Total:', total.value);

        try {
          // Validar que los campos obligatorios estén completos
          if (!shippingForm.value.email || !shippingForm.value.fullName || 
              !shippingForm.value.address1 || !shippingForm.value.city || 
              !shippingForm.value.state || !shippingForm.value.zipCode || 
              !shippingForm.value.phone) {
            paypalError.value = 'Por favor completa todos los campos obligatorios antes de proceder al pago.';
            
            // Mostrar alerta de validación
            await showError(
              'Por favor completa todos los campos obligatorios:\n\n' +
              '• Email\n' +
              '• Nombre completo\n' +
              '• Dirección\n' +
              '• Ciudad\n' +
              '• Estado/Provincia\n' +
              '• Código Postal\n' +
              '• Teléfono',
              '⚠️ Campos Incompletos'
            );
            
            throw new Error('Incomplete shipping information');
          }

          // Validar que haya items en el carrito
          if (!cartStore.items || cartStore.items.length === 0) {
            paypalError.value = 'El carrito está vacío. Agrega productos antes de proceder al pago.';
            
            await showError(
              'Tu carrito está vacío. Por favor agrega productos antes de proceder al pago.',
              '🛒 Carrito Vacío'
            );
            
            throw new Error('Cart is empty');
          }

          // Obtener nombre del país a partir del isoCode
          const selectedCountry = countries.find(c => c.isoCode === shippingForm.value.country);
          const countryName = selectedCountry ? selectedCountry.name : shippingForm.value.country;

          // Preparar items del carrito para el backend
          const items = cartStore.items.map(item => ({
            woocommerce_product_id: item.product_id || item.id,
            product_name: item.name,
            quantity: item.quantity,
            unit_price: parseFloat(item.price)
          }));

          console.log('📦 [PAYPAL] Items del carrito:', items);

          // Preparar datos completos para el backend
          const orderData = {
            items: items,
            customer_email: shippingForm.value.email,
            customer_name: shippingForm.value.fullName,
            shipping_address: shippingForm.value.address1,
            shipping_city: shippingForm.value.city,
            shipping_state: shippingForm.value.state,
            shipping_postal_code: shippingForm.value.zipCode,
            shipping_country: countryName,
            phone_number: `${shippingForm.value.phoneCode} ${shippingForm.value.phone}`,
            notes: shippingForm.value.additionalDetails || ''
          };

          console.log('📤 [PAYPAL] Enviando datos completos al backend:', orderData);

          // Crear orden en el backend
          const result = await paymentStore.createPayPalOrder(orderData);
          
          if (!result.success) {
            paypalError.value = result.error || 'Error al crear la orden.';
            throw new Error(result.error);
          }

          console.log('✅ [PAYPAL] Orden creada en backend:', result.paypal_order_id);
          
          // Retornar el PayPal Order ID para continuar con el flujo
          return result.paypal_order_id;
        } catch (error) {
          console.error('❌ [PAYPAL] Error al crear orden:', error);
          
          if (!paypalError.value) {
            paypalError.value = 'Error al crear la orden. Por favor intenta de nuevo.';
            
            // Mostrar error si no se mostró una validación específica
            await showError(
              'Hubo un problema al crear tu orden. Por favor verifica tus datos e intenta de nuevo.',
              '❌ Error al Crear Orden'
            );
          }
          throw error;
        }
      },

      // Aprobar pago
      onApprove: async (data, actions) => {
        console.log('✅ [PAYPAL] Pago aprobado por el usuario');
        console.log('📋 [PAYPAL] Order ID:', data.orderID);

        try {
          // Mostrar loading mientras procesamos el pago
          showLoading('Procesando tu pago...', '💳 Procesando Pago');

          // Obtener nombre del país a partir del isoCode
          const selectedCountry = countries.find(c => c.isoCode === shippingForm.value.country);
          const countryName = selectedCountry ? selectedCountry.name : shippingForm.value.country;

          // Preparar items del carrito para el backend
          const items = cartStore.items.map(item => ({
            woocommerce_product_id: item.product_id || item.id,
            product_name: item.name,
            quantity: item.quantity,
            unit_price: parseFloat(item.price)
          }));

          // Preparar datos completos de captura
          const captureData = {
            paypal_order_id: data.orderID,
            items: items,
            customer_email: shippingForm.value.email,
            customer_name: shippingForm.value.fullName,
            shipping_address: shippingForm.value.address1,
            shipping_city: shippingForm.value.city,
            shipping_state: shippingForm.value.state,
            shipping_postal_code: shippingForm.value.zipCode,
            shipping_country: countryName,
            phone_number: `${shippingForm.value.phoneCode} ${shippingForm.value.phone}`,
            notes: shippingForm.value.additionalDetails || ''
          };

          console.log('📤 [PAYPAL] Capturando pago en el backend...');

          // Capturar el pago en el backend
          const result = await paymentStore.capturePayPalOrder(data.orderID, captureData);
          
          // Cerrar loading
          closeAlert();
          
          if (!result.success) {
            paypalError.value = result.error || 'Error al procesar el pago.';
            
            // Mostrar error
            await showError(
              result.error || 'Hubo un problema al procesar tu pago. Por favor contacta a soporte.',
              '❌ Error en el Pago'
            );
            
            throw new Error(result.error);
          }

          console.log('✅ [PAYPAL] Pago procesado exitosamente');
          console.log('📦 [PAYPAL] Orden creada:', result.order);
          
          // Mostrar mensaje de éxito con detalles de la orden
          await showSuccess(
            `Tu orden ha sido creada exitosamente.\n\n` +
            `📋 Orden: ${result.order.order_number}\n` +
            `💰 Total: $${result.order.total}\n` +
            `📦 Estado: ${result.order.status_display}\n\n` +
            `Recibirás un email de confirmación pronto.`,
            '🎉 ¡Pago Exitoso!',
            { timer: 8000 }
          );
          
          // Limpiar carrito
          cartStore.clearCart();
          
          // Limpiar estado de pago
          paymentStore.clearPaymentState();
          
          // Redirigir al home
          router.push({ name: `Home-${i18nStore.locale}` });
          
        } catch (error) {
          console.error('❌ [PAYPAL] Error al capturar pago:', error);
          
          // Asegurarse de cerrar loading si hay error
          closeAlert();
          
          if (!paypalError.value) {
            paypalError.value = 'Error al procesar el pago. Por favor contacta a soporte.';
            
            // Mostrar error si no se mostró antes
            await showError(
              'Hubo un problema inesperado al procesar tu pago. Por favor intenta de nuevo o contacta a soporte.',
              '❌ Error en el Pago'
            );
          }
        }
      },

      // Cancelar
      onCancel: (data) => {
        console.log('⚠️ [PAYPAL] Pago cancelado por el usuario');
        paypalError.value = 'Pago cancelado. Puedes intentar de nuevo cuando quieras.';
        
        // Mostrar alerta de cancelación
        showError(
          'Has cancelado el proceso de pago. Puedes intentar de nuevo cuando quieras.',
          '⚠️ Pago Cancelado',
          { 
            confirmButtonText: 'Entendido',
            timer: 5000 
          }
        );
      },

      // Error
      onError: (err) => {
        console.error('❌ [PAYPAL] Error en el proceso:', err);
        paypalError.value = 'Ocurrió un error con PayPal. Por favor intenta de nuevo.';
        
        // Mostrar alerta de error
        showError(
          'Hubo un problema con PayPal. Por favor verifica tu conexión e intenta de nuevo.',
          '❌ Error de PayPal'
        );
      }
    }).render('#paypal-button-container');

    console.log('✅ [PAYPAL] Botones renderizados exitosamente');
  } catch (error) {
    console.error('❌ [PAYPAL] Error al renderizar botones:', error);
    paypalError.value = 'Error al cargar los botones de PayPal.';
  }
};

// Initialize cart on mount
onMounted(async () => {
  // Cargar el carrito desde localStorage
  cartStore.loadCart();
  
  // Si el carrito está vacío, redirigir al carrito
  if (cartStore.isEmpty) {
    router.push({ name: `Cart-${i18nStore.locale}` });
    return;
  }

  // Cargar e inicializar PayPal
  try {
    await loadPayPalScript();
    // Esperar un momento para que el DOM se actualice
    setTimeout(() => {
      initPayPalButtons();
    }, 100);
  } catch (error) {
    console.error('❌ [PAYPAL] Error al inicializar PayPal:', error);
    
    // Mostrar error de inicialización
    await showError(
      'No se pudo cargar el sistema de pagos de PayPal. Por favor recarga la página e intenta de nuevo.',
      '❌ Error al Cargar PayPal'
    );
  }
});

// Cleanup on unmount
onBeforeUnmount(() => {
  // Limpiar el contenedor de PayPal
  const container = document.getElementById('paypal-button-container');
  if (container) {
    container.innerHTML = '';
  }
});
</script>

<style scoped>
.checkout-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #e8f0f7 0%, #f5e6f0 50%, #e8f0f7 100%);
  padding: 2rem 1rem;
}

.checkout-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}

/* Shipping Section */
.shipping-section {
  width: 100%;
}

.shipping-card {
  background: white;
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1.5rem;
}

/* Shipping Type Radio */
.shipping-type {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  color: #333;
}

.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #6366f1;
}

/* Form Groups */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.5rem;
}

.text-red-500 {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: #fafafa;
}

.form-input:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input::placeholder {
  color: #999;
}

.form-select {
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
  appearance: none;
}

.form-select:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.form-select option {
  padding: 0.5rem;
}

.form-textarea {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  background: #fafafa;
  transition: all 0.3s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* Form Row */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Phone Input */
.phone-input {
  display: flex;
  gap: 0.5rem;
}

.phone-code {
  padding: 0.875rem;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: #fafafa;
  font-size: 0.95rem;
  cursor: pointer;
  min-width: 120px;
  transition: all 0.3s ease;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
  appearance: none;
}

.phone-code:focus {
  outline: none;
  border-color: #6366f1;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.phone-number {
  flex: 1;
}

/* Payment Section */
.payment-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.payment-subtitle {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.paypal-container {
  margin-top: 1rem;
  min-height: 150px;
  width: 100%;
}

.payment-error {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background-color: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-size: 0.9rem;
  text-align: center;
}

/* Summary Section */
.summary-section {
  position: sticky;
  top: 2rem;
}

.summary-card {
  background: white;
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* Products List */
.products-list {
  margin-bottom: 2rem;
}

.product-item {
  display: grid;
  grid-template-columns: 80px 1fr auto auto;
  gap: 1rem;
  align-items: center;
  padding: 1.25rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.product-item:last-child {
  border-bottom: none;
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-details {
  flex: 1;
}

.product-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}

.product-meta {
  font-size: 0.85rem;
  color: #666;
  margin: 0.15rem 0;
}

.product-quantity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

.quantity-btn {
  background: none;
  border: none;
  font-size: 0.7rem;
  color: #999;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.product-price {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
  text-align: right;
}

/* Discount Section */
.discount-section {
  padding: 1.5rem 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 1.5rem;
}

.discount-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.75rem;
}

.discount-input {
  display: flex;
  gap: 0.75rem;
}

.discount-input .form-input {
  flex: 1;
}

.validate-btn {
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.validate-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

/* Totals Section */
.totals-section {
  margin-bottom: 1.5rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  font-size: 0.95rem;
  color: #333;
}

.total-value {
  font-weight: 500;
  color: #1a1a1a;
}

.tax-row {
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #f0f0f0;
}

/* Final Total */
.final-total {
  padding-top: 1.5rem;
}

.final-total .total-row {
  padding: 0;
  margin-bottom: 0.5rem;
}

.total-label {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a1a;
}

.total-amount {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
}

.tax-note {
  font-size: 0.85rem;
  color: #999;
  margin: 0;
}

/* Loading State */
.loading-state {
  padding: 2rem;
  text-align: center;
  color: #666;
}

.loading-state p {
  margin: 0;
  font-size: 1rem;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .checkout-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .summary-section {
    position: static;
  }
}

@media (max-width: 768px) {
  .checkout-view {
    padding: 1rem;
  }

  .shipping-card,
  .summary-card {
    padding: 1.5rem;
    border-radius: 16px;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .product-item {
    grid-template-columns: 60px 1fr;
    gap: 0.75rem;
  }

  .product-image {
    width: 60px;
    height: 60px;
  }

  .product-quantity,
  .product-price {
    grid-column: 2;
    justify-self: end;
  }

  .discount-input {
    flex-direction: column;
  }

  .validate-btn {
    width: 100%;
  }
}
</style>
