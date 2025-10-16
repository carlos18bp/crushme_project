<template>
  <div class="checkout-view">
    <div class="checkout-container">
      <!-- Left Column - Shipping Information -->
      <div class="shipping-section">
        <div class="shipping-card">
          <h2 class="section-title">{{ $t('cart.checkout.shippingInformation') }}</h2>
          
          <!-- Shipping Type -->
          <div class="shipping-type">
            <label class="radio-label">
              <input type="radio" name="shipping-type" value="me" v-model="shippingType" checked>
              <span>{{ $t('cart.checkout.shippingType.forMe') }}</span>
            </label>
            <label class="radio-label">
              <input type="radio" name="shipping-type" value="gift" v-model="shippingType">
              <span>{{ $t('cart.checkout.shippingType.forGift') }}</span>
            </label>
          </div>

          <!-- Form Fields -->

          <!-- Email (shown for both shipping types) -->
          <div class="form-group">
            <label for="email">{{ $t('cart.checkout.form.email') }} <span class="text-red-500">*</span></label>
            <input
              type="email"
              id="email"
              v-model="shippingForm.email"
              :placeholder="$t('cart.checkout.form.placeholders.email')"
              class="form-input"
              required
            >
          </div>

          <!-- For Me Shipping Fields -->
          <template v-if="shippingType === 'me'" class="gift-form-section">
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
              <label for="country">Country</label>
              <select
                id="country"
                v-model="shippingForm.country"
                class="form-input form-select"
                disabled
              >
                <option value="CO">🇨🇴 Colombia</option>
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
              <label for="city">Ciudad <span class="text-red-500">*</span></label>
              <input
                type="text"
                id="city"
                v-model="shippingForm.city"
                placeholder="Ej: Bogotá, Medellín, Cali..."
                class="form-input"
                required
                list="colombia-cities"
              >
              <datalist id="colombia-cities">
                <option value="Medellín"></option>
                <option value="Bogotá"></option>
                <option value="Cali"></option>
                <option value="Barranquilla"></option>
                <option value="Cartagena"></option>
                <option value="San Andrés Isla"></option>
                <option value="Santa Catalina"></option>
                <option value="Providencia"></option>
                <option value="Bucaramanga"></option>
                <option value="Pereira"></option>
                <option value="Manizales"></option>
                <option value="Ibagué"></option>
                <option value="Villavicencio"></option>
                <option value="Pasto"></option>
                <option value="Neiva"></option>
              </datalist>
              <p class="city-shipping-info" v-if="shippingForm.city">
                <span v-if="shippingForm.city.toLowerCase().includes('medellín') || shippingForm.city.toLowerCase().includes('medellin')">
                  📦 Envío a Medellín: {{ formatCOP(10500) }}
                </span>
                <span v-else-if="shippingForm.city.toLowerCase().includes('san andrés') || 
                              shippingForm.city.toLowerCase().includes('san andres') ||
                              shippingForm.city.toLowerCase().includes('santa catalina') ||
                              shippingForm.city.toLowerCase().includes('providencia')">
                  📦 Envío a Islas: {{ formatCOP(45000) }}
                </span>
                <span v-else>
                  📦 Envío estándar: {{ formatCOP(15000) }}
                </span>
              </p>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="state">Departamento <span class="text-red-500">*</span></label>
                <select
                  id="state"
                  v-model="shippingForm.state"
                  class="form-input form-select"
                  required
                >
                  <option value="">Selecciona un departamento</option>
                  <option v-for="state in availableStates" :key="state.isoCode" :value="state.name">
                    {{ state.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="zipcode">Código Postal <span class="text-red-500">*</span></label>
                <input
                  type="text"
                  id="zipcode"
                  v-model="shippingForm.zipCode"
                  placeholder="11001"
                  class="form-input"
                  required
                >
              </div>
            </div>

            <div class="form-group">
              <label for="phone">Phone <span class="text-red-500">*</span></label>
              <div class="phone-input">
                <select v-model="shippingForm.phoneCode" class="phone-code" disabled>
                  <option v-for="country in countryCodes" :key="country.code" :value="country.dial_code">
                    {{ country.flag }} {{ country.dial_code }}
                  </option>
                </select>
                <input
                  type="tel"
                  id="phone"
                  v-model="shippingForm.phone"
                  placeholder="300 123 4567"
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
          </template>

          <!-- For Gift Shipping Fields -->
          <template v-if="shippingType === 'gift'" class="gift-form-section">
            <div class="form-group">
              <label for="username">{{ $t('cart.checkout.form.username') }} <span class="text-red-500">*</span></label>
              <div class="username-search-container">
                <input
                  type="text"
                  id="username"
                  v-model="usernameSearchQuery"
                  :placeholder="$t('cart.checkout.form.placeholders.searchUser')"
                  class="form-input username-search-input"
                  autocomplete="off"
                  @focus="showUserSearchResults = crushStore.searchResults.length > 0"
                  @blur="setTimeout(() => showUserSearchResults = false, 200)"
                >
                <!-- Search Results Dropdown -->
                <div v-if="showUserSearchResults && crushStore.searchResults.length > 0" class="username-search-results">
                  <div
                    v-for="user in crushStore.searchResults"
                    :key="user.id"
                    class="username-search-item"
                    @mousedown="selectUser(user)"
                  >
                    <img
                      :src="user.profile_picture_url || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=40'"
                      :alt="user.username"
                      class="search-avatar"
                    >
                    <div class="search-user-info">
                      <span class="search-username">@{{ user.username }}</span>
                      <span v-if="user.is_crush" class="search-crush-label">Crush</span>
                    </div>
                  </div>
                </div>
              </div>
              <p v-if="isUserAuthenticated" class="gift-field-description">
                <span class="highlight">@{{ authStore.username }}</span> {{ $t('cart.checkout.form.help.username') }}
              </p>
            </div>

            <div class="form-group">
              <label for="note">{{ $t('cart.checkout.form.note') }}</label>
              <textarea
                id="note"
                v-model="shippingForm.note"
                :placeholder="$t('cart.checkout.form.placeholders.note')"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
          </template>

          <div class="form-group">
            <h3 class="payment-title">{{ $t('cart.checkout.form.paymentMethod') }}</h3>
            <p class="payment-subtitle">{{ $t('cart.checkout.form.selectPaymentMethod') }}</p>
            
            <!-- PayPal Button Container -->
            <div id="paypal-button-container" class="paypal-container"></div>
            <p v-if="paypalError" class="payment-error">{{ paypalError }}</p>
          </div>
        </div>
      </div>

      <!-- Right Column - Order Summary -->
      <div class="summary-section">
        <div class="summary-card">
          <h2 class="section-title">{{ $t('cart.checkout.form.orderSummary') }}</h2>
          
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
                <!-- ⭐ Mostrar atributos de variación -->
                <p class="product-meta" v-if="item.attributes && Object.keys(item.attributes).length > 0">
                  <span v-for="(value, key) in item.attributes" :key="key">
                    {{ key }}: {{ value }}
                  </span>
                </p>
                <!-- ⭐ Mostrar ID de variación (debug) -->
                <p class="product-meta variation-id" v-if="item.variation_id">
                  Variación: #{{ item.variation_id }}
                </p>
              </div>
              <div class="product-quantity">
                <span>{{ item.quantity }}</span>
              </div>
              <div class="product-price">
                {{ formatCOP(item.price * item.quantity) }}
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
              <span>{{ $t('cart.checkout.form.subtotal') }}</span>
              <span class="total-value">{{ formatCOP(subtotal) }}</span>
            </div>
            <div class="total-row">
              <span>{{ $t('cart.checkout.form.shipping') }}</span>
              <span class="total-value">
                {{ formatCOP(shipping) }}
                <span v-if="shippingForm.city" class="shipping-city-note">
                  ({{ shippingForm.city }})
                </span>
              </span>
            </div>
            <div class="total-row tax-row">
              <span>{{ $t('cart.checkout.form.tax') }}</span>
              <span class="total-value">{{ formatCOP(tax) }}</span>
            </div>
          </div>

          <!-- Final Total -->
          <div class="final-total">
            <div class="total-row">
              <span class="total-label">{{ $t('cart.checkout.form.total') }}</span>
              <span class="total-amount">{{ formatCOP(total) }}</span>
            </div>
            <p class="tax-note">{{ $t('cart.checkout.form.includesTax', { tax: formatCOP(tax) }) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useCartStore } from '@/stores/modules/cartStore.js';
import { useAuthStore } from '@/stores/modules/authStore.js';
import { useCrushStore } from '@/stores/modules/crushStore.js';
import { useI18nStore } from '@/stores/modules/i18nStore';
import { usePaymentStore } from '@/stores/modules/paymentStore.js';
import { useRouter } from 'vue-router';
import { useAlert } from '@/composables/useAlert.js';
import { Country, State } from 'country-state-city';
import { formatCOP } from '@/utils/priceHelper.js';

const router = useRouter();
const cartStore = useCartStore();
const authStore = useAuthStore();
const crushStore = useCrushStore();
const i18nStore = useI18nStore();
const paymentStore = usePaymentStore();
const { showSuccess, showError, showLoading, closeAlert } = useAlert();

// Get all countries with flags
const countries = Country.getAllCountries().map(country => ({
  ...country,
  flag: country.flag || '🏳️'
}));

// Country codes for phone selector - Only Colombia for national shipping
const countryCodes = [
  { code: 'CO', dial_code: '+57', flag: '🇨🇴', name: 'Colombia' },
];

// Shipping form data
const shippingType = ref('me');
const shippingForm = ref({
  email: '',
  fullName: '',
  country: 'CO', // ⭐ Default to Colombia, store ISO code
  address1: '',
  address2: '',
  city: '',
  state: '',
  zipCode: '',
  phoneCode: '+57', // ⭐ Colombia phone code
  phone: '',
  additionalDetails: '',
  // ⭐ New fields for gift shipping
  username: '',
  note: ''
});

const discountCode = ref('');
const paypalError = ref('');
const paypalScriptLoaded = ref(false);

// ⭐ User search functionality for gift shipping
const usernameSearchQuery = ref('');
const showUserSearchResults = ref(false);
let usernameSearchTimeout = null;

// Computed property for available states - Only Colombia for national shipping
const availableStates = computed(() => {
  return State.getStatesOfCountry('CO');
});

// Get cart items
const cartItems = computed(() => cartStore.items);

// Check if user is authenticated and has username
const isUserAuthenticated = computed(() => authStore.isLoggedIn && authStore.username);

// ⭐ User search functionality
const searchUsers = async (query) => {
  if (!query || !query.trim()) {
    crushStore.clearSearch();
    return;
  }

  try {
    await crushStore.searchUsers(query.trim(), 5);
  } catch (error) {
    console.error('Error searching users:', error);
  }
};

// ⭐ Select user from search results
const selectUser = (user) => {
  shippingForm.value.username = `@${user.username}`;
  usernameSearchQuery.value = `@${user.username}`;
  showUserSearchResults.value = false;
  crushStore.clearSearch();
};

// ⭐ Watch username input for search and sync with shippingForm
watch(usernameSearchQuery, (newQuery) => {
  // Sync with shippingForm.username
  shippingForm.value.username = newQuery;

  // Clear previous timeout
  if (usernameSearchTimeout) {
    clearTimeout(usernameSearchTimeout);
  }

  // Clear search if query is empty
  if (!newQuery.trim()) {
    crushStore.clearSearch();
    showUserSearchResults.value = false;
    return;
  }

  // Debounce search (300ms)
  usernameSearchTimeout = setTimeout(async () => {
    await searchUsers(newQuery);
    showUserSearchResults.value = crushStore.searchResults.length > 0;
  }, 300);
});

// ⭐ Clear user search when shipping type changes
watch(shippingType, (newType) => {
  if (newType !== 'gift') {
    usernameSearchQuery.value = '';
    showUserSearchResults.value = false;
    crushStore.clearSearch();
  }
});

// ⭐ Sync shippingForm.username with search query when in gift mode
watch(() => shippingForm.value.username, (newUsername) => {
  if (shippingType.value === 'gift' && newUsername !== usernameSearchQuery.value) {
    usernameSearchQuery.value = newUsername;
  }
});

// Calculate totals
const subtotal = computed(() => cartStore.totalPrice);

// ⭐ Funciones auxiliares para creación de órdenes
const createRegularOrder = async () => {
  console.log('📦 [REGULAR] Creando orden regular...');

  // Validar que los campos obligatorios estén completos
  if (!shippingForm.value.email || !shippingForm.value.fullName ||
      !shippingForm.value.address1 || !shippingForm.value.city ||
      !shippingForm.value.state || !shippingForm.value.zipCode ||
      !shippingForm.value.phone) {
    paypalError.value = 'Por favor completa todos los campos obligatorios antes de proceder al pago.';

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

  // Obtener nombre del país a partir del isoCode
  const selectedCountry = countries.find(c => c.isoCode === shippingForm.value.country);
  const countryName = selectedCountry ? selectedCountry.name : shippingForm.value.country;

  // Preparar items del carrito
  const items = cartStore.items.map(item => ({
    woocommerce_product_id: item.product_id || item.id,
    woocommerce_variation_id: item.variation_id || null,
    product_name: item.name,
    quantity: item.quantity,
    unit_price: parseFloat(item.price),
    attributes: item.attributes || null
  }));

  console.log('📦 [REGULAR] Items del carrito:', items);

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
    notes: shippingForm.value.additionalDetails || '',
    shipping: shipping.value // ⭐ Agregar costo de envío calculado
  };

  console.log('📤 [REGULAR] Enviando datos completos al backend:', orderData);

  // Crear orden en el backend
  const result = await paymentStore.createPayPalOrder(orderData);

  if (!result.success) {
    paypalError.value = result.error || 'Error al crear la orden.';
    throw new Error(result.error);
  }

  console.log('✅ [REGULAR] Orden creada en backend:', result.paypal_order_id);

  return result.paypal_order_id;
};

const createGiftOrder = async () => {
  console.log('🎁 [GIFT] Creando orden de regalo...');

  // Validar campos específicos para regalo
  if (!shippingForm.value.email) {
    paypalError.value = 'El email es obligatorio para enviar regalos.';
    await showError('Por favor ingresa tu email para enviar el regalo.', '📧 Email Requerido');
    throw new Error('Email required for gift');
  }

  if (!shippingForm.value.username) {
    paypalError.value = 'Selecciona un usuario destinatario para el regalo.';
    await showError('Por favor selecciona el usuario que recibirá el regalo.', '👤 Usuario Requerido');
    throw new Error('Username required for gift');
  }

  // Preparar items del carrito para regalo
  const items = cartStore.items.map(item => ({
    woocommerce_product_id: item.product_id || item.id,
    woocommerce_variation_id: item.variation_id || null,
    product_name: item.name,
    quantity: item.quantity,
    unit_price: parseFloat(item.price),
    attributes: item.attributes || null
  }));

  console.log('🎁 [GIFT] Items del regalo:', items);

  // Preparar datos del regalo
  const giftData = {
    customer_email: shippingForm.value.email,
    sender_username: authStore.isLoggedIn ? authStore.username : null,
    receiver_username: shippingForm.value.username.replace('@', ''), // Remover @ si existe
    items: items,
    gift_message: shippingForm.value.note || ''
  };

  console.log('🎁 [GIFT] Datos del regalo:', giftData);

  // Enviar regalo
  const result = await paymentStore.sendGift(giftData);

  if (!result.success) {
    paypalError.value = result.error || 'Error al enviar el regalo.';

    // Mostrar error específico según el tipo
    if (result.error.includes('not found')) {
      await showError(
        'El usuario destinatario no fue encontrado. Verifica el nombre de usuario.',
        '❌ Usuario No Encontrado'
      );
    } else if (result.error.includes('shipping information')) {
      await showError(
        'El usuario destinatario no tiene información completa de envío registrada.',
        '❌ Información de Envío Incompleta'
      );
    } else {
      await showError(
        result.error || 'Hubo un problema al enviar el regalo.',
        '❌ Error al Enviar Regalo'
      );
    }

    throw new Error(result.error);
  }

  console.log('✅ [GIFT] Regalo enviado exitosamente:', result.paypal_order_id);

  return result.paypal_order_id;
};

// ⭐ Funciones auxiliares para captura de pagos
const captureGiftPayment = async (paypalOrderId) => {
  console.log('🎁 [GIFT] Capturando pago de regalo...');

  // Preparar items del carrito para regalo
  const items = cartStore.items.map(item => ({
    woocommerce_product_id: item.product_id || item.id,
    woocommerce_variation_id: item.variation_id || null,
    product_name: item.name,
    quantity: item.quantity,
    unit_price: parseFloat(item.price),
    attributes: item.attributes || null
  }));

  console.log('🎁 [GIFT] Items del regalo para captura:', items);

  // Preparar datos de captura para regalo
  const captureData = {
    paypal_order_id: paypalOrderId,
    customer_email: shippingForm.value.email,
    sender_username: authStore.isLoggedIn ? authStore.username : null,
    receiver_username: shippingForm.value.username.replace('@', ''), // Remover @ si existe
    items: items,
    gift_message: shippingForm.value.note || '',
    shipping: shipping.value // ⭐ Agregar costo de envío calculado
  };

  console.log('🎁 [GIFT] Datos de captura de regalo:', captureData);

  // El backend maneja la captura automáticamente para regalos
  // Pero necesitamos llamar al endpoint de captura estándar con datos del destinatario
  const result = await paymentStore.capturePayPalOrder(paypalOrderId, captureData);

  // Cerrar loading
  closeAlert();

  if (!result.success) {
    paypalError.value = result.error || 'Error al procesar el pago del regalo.';

    await showError(
      result.error || 'Hubo un problema al procesar el pago del regalo.',
      '❌ Error en el Pago del Regalo'
    );

    throw new Error(result.error);
  }

  console.log('✅ [GIFT] Pago de regalo procesado exitosamente');
  console.log('📦 [GIFT] Orden creada:', result.order);

  // Mostrar mensaje de éxito con detalles del regalo
  await showSuccess(
    `¡Tu regalo ha sido enviado exitosamente!\n\n` +
    `🎁 Destinatario: ${result.order.customer_name || 'Usuario'}\n` +
    `📦 Productos: ${result.order.items_count} artículo(s)\n` +
    `💰 Total: $${result.order.total}\n` +
    `📋 Orden: ${result.order.order_number}\n\n` +
    `El destinatario recibirá una notificación y sus productos serán enviados a su dirección registrada.`,
    '🎉 ¡Regalo Enviado!',
    { timer: 8000 }
  );

  console.log('🧹 [GIFT] Limpiando carrito y estado...');

  // Limpiar carrito
  cartStore.clearCart();

  // Limpiar estado de pago
  paymentStore.clearPaymentState();

  console.log('🔄 [GIFT] Redirigiendo al home...');

  // Pequeño delay para asegurar que la alerta se muestre antes de redirigir
  setTimeout(() => {
    router.push({ name: `Home-${i18nStore.locale}` });
  }, 1000);
};

const captureRegularPayment = async (paypalOrderId) => {
  console.log('📦 [REGULAR] Capturando pago regular...');

  // Obtener nombre del país a partir del isoCode
  const selectedCountry = countries.find(c => c.isoCode === shippingForm.value.country);
  const countryName = selectedCountry ? selectedCountry.name : shippingForm.value.country;

  // Preparar items del carrito
  const items = cartStore.items.map(item => ({
    woocommerce_product_id: item.product_id || item.id,
    woocommerce_variation_id: item.variation_id || null,
    product_name: item.name,
    quantity: item.quantity,
    unit_price: parseFloat(item.price),
    attributes: item.attributes || null
  }));

  // Preparar datos completos de captura
  const captureData = {
    paypal_order_id: paypalOrderId,
    items: items,
    customer_email: shippingForm.value.email,
    customer_name: shippingForm.value.fullName,
    shipping_address: shippingForm.value.address1,
    shipping_city: shippingForm.value.city,
    shipping_state: shippingForm.value.state,
    shipping_postal_code: shippingForm.value.zipCode,
    shipping_country: countryName,
    phone_number: `${shippingForm.value.phoneCode} ${shippingForm.value.phone}`,
    notes: shippingForm.value.additionalDetails || '',
    shipping: shipping.value // ⭐ Agregar costo de envío calculado
  };

  console.log('📦 [REGULAR] Datos de captura:', captureData);

  // Capturar el pago en el backend
  const result = await paymentStore.capturePayPalOrder(paypalOrderId, captureData);

  // Cerrar loading
  closeAlert();

  if (!result.success) {
    paypalError.value = result.error || 'Error al procesar el pago.';

    await showError(
      result.error || 'Hubo un problema al procesar tu pago. Por favor contacta a soporte.',
      '❌ Error en el Pago'
    );

    throw new Error(result.error);
  }

  console.log('✅ [REGULAR] Pago procesado exitosamente');
  console.log('📦 [REGULAR] Orden creada:', result.order);

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

  console.log('🧹 [REGULAR] Limpiando carrito y estado...');

  // Limpiar carrito
  cartStore.clearCart();

  // Limpiar estado de pago
  paymentStore.clearPaymentState();

  console.log('🔄 [REGULAR] Redirigiendo al home...');

  // Pequeño delay para asegurar que la alerta se muestre antes de redirigir
  setTimeout(() => {
    router.push({ name: `Home-${i18nStore.locale}` });
  }, 1000);
};

const shipping = computed(() => {
  // ⭐ Cálculo de envío según ciudad colombiana
  const ciudad = (shippingForm.value.city || '').toLowerCase().trim();
  
  // Validar que haya ciudad seleccionada
  if (!ciudad) {
    return 15000; // Tarifa por defecto si no hay ciudad
  }
  
  // Aplicar tarifas según la ciudad
  switch (ciudad) {
    case 'medellín':
    case 'medellin': // Sin tilde también
      return 10500;
      
    case 'san andrés isla':
    case 'san andres isla': // Sin tilde
    case 'san andrés':
    case 'san andres':
    case 'santa catalina':
    case 'providencia':
      return 45000;
      
    default:
      return 15000; // Tarifa estándar para otras ciudades
  }
});

const tax = computed(() => {
  // 19% de impuesto sobre el subtotal
  return subtotal.value * 0.19;
});

const total = computed(() => {
  return subtotal.value + shipping.value + tax.value;
});

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
          // Validar que haya items en el carrito
          if (!cartStore.items || cartStore.items.length === 0) {
            paypalError.value = 'El carrito está vacío. Agrega productos antes de proceder al pago.';

            await showError(
              'Tu carrito está vacío. Por favor agrega productos antes de proceder al pago.',
              '🛒 Carrito Vacío'
            );

            throw new Error('Cart is empty');
          }

          // ⭐ Si es envío como regalo, usar endpoint especial
          if (shippingType.value === 'gift') {
            return await createGiftOrder();
          }

          // ⭐ Si es envío normal, usar flujo estándar
          return await createRegularOrder();

        } catch (error) {
          console.error('❌ [PAYPAL] Error al crear orden:', error);
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

          // ⭐ Si es envío como regalo, usar flujo especial
          if (shippingType.value === 'gift') {
            await captureGiftPayment(data.orderID);
          } else {
            // ⭐ Si es envío normal, usar flujo estándar
            await captureRegularPayment(data.orderID);
          }

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

  // Limpiar búsqueda de usuarios
  if (usernameSearchTimeout) {
    clearTimeout(usernameSearchTimeout);
  }
  crushStore.clearSearch();
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
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: start;
}

@media (min-width: 1024px) {
  .checkout-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }
}

/* Shipping Section */
.shipping-section {
  width: 100%;
  order: 2;
}

@media (min-width: 1024px) {
  .shipping-section {
    order: 1;
  }
}

.shipping-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

@media (min-width: 640px) {
  .shipping-card {
    padding: 1.75rem;
    border-radius: 20px;
  }
}

@media (min-width: 1024px) {
  .shipping-card {
    padding: 2.5rem;
    border-radius: 24px;
  }
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
}

@media (min-width: 640px) {
  .section-title {
    font-size: 1.5rem;
    margin-bottom: 1.25rem;
  }
}

@media (min-width: 1024px) {
  .section-title {
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
  }
}

/* Shipping Type Radio */
.shipping-type {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .shipping-type {
    flex-direction: row;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
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
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.375rem;
}

@media (min-width: 640px) {
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  .form-group label {
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }
}

@media (min-width: 1024px) {
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .form-group label {
    font-size: 0.9rem;
  }
}

.text-red-500 {
  color: #ef4444;
}

.form-input {
  width: 100%;
  padding: 0.75rem 0.875rem;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  background: #fafafa;
}

@media (min-width: 640px) {
  .form-input {
    padding: 0.875rem 1rem;
    border-radius: 12px;
    font-size: 0.9375rem;
  }
}

@media (min-width: 1024px) {
  .form-input {
    font-size: 0.95rem;
  }
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
  color: #6b7280;
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

/* Gift form styles */
.gift-form-section {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.gift-field-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
  line-height: 1.4;
}

.gift-field-description .highlight {
  color: #ec4899;
  font-weight: 500;
}

/* City Shipping Info */
.city-shipping-info {
  font-size: 0.75rem;
  color: #059669;
  margin-top: 0.375rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

@media (min-width: 640px) {
  .city-shipping-info {
    font-size: 0.8125rem;
  }
}

/* Username Search Styles */
.username-search-container {
  position: relative;
}

.username-search-input {
  padding-right: 40px;
}

.username-search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
}

.username-search-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.username-search-item:hover {
  background-color: #f8fafc;
}

.username-search-item:last-child {
  border-radius: 0 0 12px 12px;
}

.search-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.search-user-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-username {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: #11181E;
  display: block;
}

.search-crush-label {
  font-family: 'Poppins', sans-serif;
  font-size: 0.75rem;
  color: #FF3FD5;
  font-weight: 400;
  background: rgba(255, 63, 213, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
}

/* Form Row */
.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .form-row {
    grid-template-columns: 1fr 1fr;
  }
}

/* Phone Input */
.phone-input {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .phone-input {
    flex-direction: row;
    gap: 0.5rem;
  }
}

.phone-code {
  padding: 0.75rem 0.875rem;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  background: #fafafa;
  font-size: 0.875rem;
  cursor: pointer;
  min-width: auto;
  width: 100%;
  transition: all 0.3s ease;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
  appearance: none;
}

@media (min-width: 640px) {
  .phone-code {
    padding: 0.875rem;
    border-radius: 12px;
    font-size: 0.9375rem;
    min-width: 120px;
    width: auto;
  }
}

@media (min-width: 1024px) {
  .phone-code {
    font-size: 0.95rem;
  }
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
  width: 100%;
  order: 1;
}

@media (min-width: 1024px) {
  .summary-section {
    position: sticky;
    top: 2rem;
    order: 2;
  }
}

.summary-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

@media (min-width: 640px) {
  .summary-card {
    padding: 1.75rem;
    border-radius: 20px;
  }
}

@media (min-width: 1024px) {
  .summary-card {
    padding: 2.5rem;
    border-radius: 24px;
  }
}

/* Products List */
.products-list {
  margin-bottom: 2rem;
}

.product-item {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: 0.75rem;
  align-items: start;
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
}

@media (min-width: 640px) {
  .product-item {
    grid-template-columns: 70px 1fr auto;
    gap: 0.875rem;
    align-items: center;
    padding: 1.125rem 0;
  }
}

@media (min-width: 1024px) {
  .product-item {
    grid-template-columns: 80px 1fr auto auto;
    gap: 1rem;
    padding: 1.25rem 0;
  }
}

.product-item:last-child {
  border-bottom: none;
}

.product-image {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  overflow: hidden;
  background: #f5f5f5;
}

@media (min-width: 640px) {
  .product-image {
    width: 70px;
    height: 70px;
    border-radius: 11px;
  }
}

@media (min-width: 1024px) {
  .product-image {
    width: 80px;
    height: 80px;
    border-radius: 12px;
  }
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
  font-size: 0.875rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

@media (min-width: 640px) {
  .product-name {
    font-size: 0.9375rem;
  }
}

@media (min-width: 1024px) {
  .product-name {
    font-size: 1rem;
  }
}

.product-meta {
  font-size: 0.75rem;
  color: #666;
  margin: 0.15rem 0;
  line-height: 1.3;
}

@media (min-width: 640px) {
  .product-meta {
    font-size: 0.8125rem;
  }
}

@media (min-width: 1024px) {
  .product-meta {
    font-size: 0.85rem;
  }
}

.product-meta span {
  display: inline-block;
  margin-right: 0.75rem;
}

.product-meta.variation-id {
  font-size: 0.75rem;
  color: #999;
  font-style: italic;
}

.product-quantity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  grid-column: 2;
  justify-self: start;
  margin-top: 0.25rem;
}

@media (min-width: 640px) {
  .product-quantity {
    grid-column: auto;
    justify-self: auto;
    margin-top: 0;
  }
}

@media (min-width: 1024px) {
  .product-quantity {
    font-size: 1rem;
  }
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
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1a1a1a;
  text-align: right;
  grid-column: 2;
  justify-self: end;
  margin-top: 0.25rem;
}

@media (min-width: 640px) {
  .product-price {
    font-size: 1rem;
    grid-column: auto;
    justify-self: auto;
    margin-top: 0;
  }
}

@media (min-width: 1024px) {
  .product-price {
    font-size: 1.1rem;
  }
}

/* Discount Section */
.discount-section {
  padding: 1rem 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 1rem;
}

@media (min-width: 640px) {
  .discount-section {
    padding: 1.25rem 0;
    margin-bottom: 1.25rem;
  }
}

@media (min-width: 1024px) {
  .discount-section {
    padding: 1.5rem 0;
    margin-bottom: 1.5rem;
  }
}

.discount-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 0.625rem;
}

@media (min-width: 640px) {
  .discount-title {
    font-size: 0.9375rem;
  }
}

@media (min-width: 1024px) {
  .discount-title {
    font-size: 1rem;
    margin-bottom: 0.75rem;
  }
}

.discount-input {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

@media (min-width: 640px) {
  .discount-input {
    flex-direction: row;
    gap: 0.75rem;
  }
}

.discount-input .form-input {
  flex: 1;
}

.validate-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  width: 100%;
}

@media (min-width: 640px) {
  .validate-btn {
    padding: 0.875rem 2rem;
    border-radius: 12px;
    font-size: 0.9375rem;
    width: auto;
  }
}

@media (min-width: 1024px) {
  .validate-btn {
    font-size: 0.95rem;
  }
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
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a1a;
}

@media (min-width: 640px) {
  .total-label {
    font-size: 1.125rem;
  }
}

@media (min-width: 1024px) {
  .total-label {
    font-size: 1.25rem;
  }
}

.total-amount {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1a1a1a;
}

@media (min-width: 640px) {
  .total-amount {
    font-size: 1.375rem;
  }
}

@media (min-width: 1024px) {
  .total-amount {
    font-size: 1.5rem;
  }
}

.tax-note {
  font-size: 0.85rem;
  color: #999;
  margin: 0;
}

/* Shipping City Note */
.shipping-city-note {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 400;
  display: block;
  margin-top: 0.125rem;
}

@media (min-width: 640px) {
  .shipping-city-note {
    display: inline;
    margin-left: 0.375rem;
    margin-top: 0;
  }
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

/* Username Search Mobile Styles */
@media (max-width: 768px) {
  .username-search-results {
    max-height: 150px;
  }

  .username-search-item {
    padding: 10px 12px;
    gap: 8px;
  }

  .search-avatar {
    width: 28px;
    height: 28px;
  }

  .search-username {
    font-size: 0.8125rem;
  }

  .search-crush-label {
    font-size: 0.6875rem;
  }
}

/* Payment Title Responsive */
.payment-title {
  font-size: 0.9375rem;
}

@media (min-width: 640px) {
  .payment-title {
    font-size: 1rem;
  }
}

@media (min-width: 1024px) {
  .payment-title {
    font-size: 1.1rem;
  }
}

.payment-subtitle {
  font-size: 0.8125rem;
}

@media (min-width: 640px) {
  .payment-subtitle {
    font-size: 0.875rem;
  }
}

@media (min-width: 1024px) {
  .payment-subtitle {
    font-size: 0.9rem;
  }
}
</style>
