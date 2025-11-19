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
            <label for="email">{{ shippingType === 'gift' ? $t('cart.checkout.form.emailGift') : $t('cart.checkout.form.email') }} <span class="text-red-500">*</span></label>
            <input
              type="email"
              id="email"
              v-model="shippingForm.email"
              :placeholder="shippingType === 'gift' ? $t('cart.checkout.form.placeholders.emailGift') : $t('cart.checkout.form.placeholders.email')"
              class="form-input"
              required
            >
            <p v-if="shippingType === 'gift'" class="gift-field-description">
              {{ $t('cart.checkout.form.help.emailGift') }}
            </p>
          </div>

          <!-- For Me Shipping Fields -->
          <template v-if="shippingType === 'me'" class="gift-form-section">
            <div class="form-group">
              <label for="fullname">{{ $t('cart.checkout.form.fullName') }} <span class="text-red-500">*</span></label>
              <input
                type="text"
                id="fullname"
                v-model="shippingForm.fullName"
                :placeholder="$t('cart.checkout.form.placeholders.fullName')"
                class="form-input"
                required
              >
            </div>

            <div class="form-group">
              <label for="country">{{ $t('cart.checkout.form.country') }}</label>
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
              <label for="address1">{{ $t('cart.checkout.form.address1') }} <span class="text-red-500">*</span></label>
              <input
                type="text"
                id="address1"
                v-model="shippingForm.address1"
                :placeholder="$t('cart.checkout.form.placeholders.address1')"
                class="form-input"
                required
              >
            </div>

            <div class="form-group">
              <label for="address2">{{ $t('cart.checkout.form.address2') }}</label>
              <input
                type="text"
                id="address2"
                v-model="shippingForm.address2"
                :placeholder="$t('cart.checkout.form.placeholders.address2')"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label for="city">{{ $t('cart.checkout.form.city') }} <span class="text-red-500">*</span></label>
              <input
                type="text"
                id="city"
                v-model="shippingForm.city"
                :placeholder="$t('cart.checkout.form.placeholders.city')"
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
                <span>
                  {{ $t('cart.checkout.form.shippingCost', { cost: formatPrice(shipping) }) }}
                </span>
              </p>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="state">{{ $t('cart.checkout.form.state') }} <span class="text-red-500">*</span></label>
                <select
                  id="state"
                  v-model="shippingForm.state"
                  class="form-input form-select"
                  required
                >
                  <option value="">{{ $t('cart.checkout.form.placeholders.selectState') }}</option>
                  <option v-for="state in availableStates" :key="state.isoCode" :value="state.name">
                    {{ state.name }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="zipcode">{{ $t('cart.checkout.form.zipCode') }} <span class="text-red-500">*</span></label>
                <input
                  type="text"
                  id="zipcode"
                  v-model="shippingForm.zipCode"
                  :placeholder="$t('cart.checkout.form.placeholders.zipCode')"
                  class="form-input"
                  required
                >
              </div>
            </div>

            <div class="form-group">
              <label for="phone">{{ $t('cart.checkout.form.phone') }} <span class="text-red-500">*</span></label>
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
                  :placeholder="$t('cart.checkout.form.placeholders.phone')"
                  class="form-input phone-number"
                  required
                >
              </div>
            </div>

            <div class="form-group">
              <label for="additional">{{ $t('cart.checkout.form.additionalDetails') }}</label>
              <textarea
                id="additional"
                v-model="shippingForm.additionalDetails"
                :placeholder="$t('cart.checkout.form.placeholders.additionalDetails')"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
          </template>

          <!-- For Gift Shipping Fields -->
          <template v-if="shippingType === 'gift'" class="gift-form-section">
            <div class="form-group">
              <label for="username">{{ $t('cart.checkout.form.recipientUsername') }} <span class="text-red-500">*</span></label>
              <div class="username-search-container">
                <input
                  type="text"
                  id="username"
                  v-model="usernameSearchQuery"
                  :placeholder="$t('cart.checkout.form.placeholders.searchUser')"
                  class="form-input username-search-input"
                  autocomplete="off"
                  @focus="showUserSearchResults = crushStore.searchResults.length > 0"
                  @blur="handleUsernameBlur"
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
                      :src="user.profile_picture || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=40'"
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
              <p class="gift-field-description">
                {{ $t('cart.checkout.form.help.recipientUsername') }}
              </p>
            </div>

            <div class="form-group">
              <label for="note">{{ giftNoteLabel }}</label>
              <textarea
                id="note"
                v-model="shippingForm.note"
                :placeholder="$t('cart.checkout.form.placeholders.giftNote')"
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
          </template>

          <!-- Payment Section -->
          <div class="form-group payment-button-section">
            <!-- COP: Wompi Widget integrado -->
            <div v-if="currencyStore.currentCurrency === 'COP'">
              <div v-if="!isFormValid" class="payment-disabled-message">
                <p>{{ $t('cart.checkout.form.buttons.completeRequired') }}</p>
              </div>
              <div v-else-if="wompiWidgetData" class="wompi-widget-wrapper">
                <WompiWidget :widget-data="wompiWidgetData" render-mode="button" />
              </div>
              <button 
                v-else
                @click="prepareWompiPayment" 
                :disabled="!isFormValid || isPreparingPayment"
                class="payment-btn"
              >
                <span v-if="isPreparingPayment">{{ $t('cart.checkout.form.buttons.preparing') || 'Preparando...' }}</span>
                <span v-else>💳 {{ $t('cart.checkout.form.buttons.payWithWompi') }}</span>
              </button>
            </div>

            <!-- USD: PayPal Button -->
            <button 
              v-else
              @click="proceedToPayment" 
              :disabled="!isFormValid"
              class="payment-btn"
              :class="{ 'payment-btn-disabled': !isFormValid }"
            >
              <span v-if="!isFormValid">{{ $t('cart.checkout.form.buttons.completeRequired') }}</span>
              <span v-else>{{ $t('cart.checkout.form.buttons.continueToPay') }}</span>
            </button>

            <p v-if="formError" class="payment-error">{{ formError }}</p>
          </div>

          <!-- PayPal Buttons Section (USD only) - Hidden until form is valid -->
          <div v-if="showPayPalButtons && currencyStore.currentCurrency === 'USD'" id="paypal-section" class="paypal-section">
            <h3 class="paypal-title">{{ $t('cart.checkout.form.paypal.title') }}</h3>
            <div id="paypal-button-container"></div>
          </div>
        </div>
      </div>

      <!-- Right Column - Order Summary -->
      <div class="summary-section">
        <div class="summary-card">
          <h2 class="section-title">{{ $t('cart.checkout.form.orderSummary') }}</h2>
          
          <!-- Loading State -->
          <div v-if="cartStore.isUpdating" class="loading-state">
            <p>{{ $t('cart.checkout.form.loadingProducts') }}</p>
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
                <p class="product-meta" v-if="item.color">{{ $t('cart.checkout.form.color') }}: {{ item.color }}</p>
                <p class="product-meta" v-if="item.size">{{ $t('cart.checkout.form.size') }}: {{ item.size }}</p>
                <!-- ⭐ Mostrar atributos de variación -->
                <p class="product-meta" v-if="item.attributes && Object.keys(item.attributes).length > 0">
                  <span v-for="(value, key) in item.attributes" :key="key">
                    {{ key }}: {{ value }}
                  </span>
                </p>
                <!-- ⭐ Mostrar ID de variación (debug) -->
                <p class="product-meta variation-id" v-if="item.variation_id">
                  {{ $t('cart.checkout.form.variation') }}: #{{ item.variation_id }}
                </p>
              </div>
              <div class="product-quantity">
                <span>{{ item.quantity }}</span>
              </div>
              <div class="product-price">
                {{ formatPrice(item.price * item.quantity) }}
              </div>
            </div>
          </div>

          <!-- Discount Code -->
          <div class="discount-section">
            <h3 class="discount-title">{{ $t('cart.checkout.form.discountCode') }}</h3>
            
            <!-- Input y botón de validación -->
            <div v-if="!discountData" class="discount-input">
              <input 
                type="text" 
                v-model="discountCode"
                :placeholder="$t('cart.checkout.form.placeholders.discountCode')"
                class="form-input"
                :disabled="isValidatingDiscount"
                @keyup.enter="validateDiscountCode"
              >
              <button 
                @click="validateDiscountCode" 
                :disabled="isValidatingDiscount || !discountCode.trim()"
                class="validate-btn"
              >
                {{ isValidatingDiscount ? $t('cart.checkout.form.buttons.validating') : $t('cart.checkout.form.buttons.validate') }}
              </button>
            </div>

            <!-- Código aplicado -->
            <div v-if="discountData" class="discount-applied">
              <div class="discount-applied-content">
                <span class="discount-code-badge">{{ discountData.code }}</span>
                <span class="discount-percentage">-{{ discountData.discount_percentage }}%</span>
              </div>
              <button @click="removeDiscount" class="remove-discount-btn" title="Remover descuento">
                ✕
              </button>
            </div>

            <!-- Error de validación -->
            <p v-if="discountError && !discountData" class="discount-error">{{ discountError }}</p>
          </div>

          <!-- Totals -->
          <div class="totals-section">
            <div class="total-row">
              <span>{{ $t('cart.checkout.form.subtotal') }}</span>
              <div class="subtotal-values">
                <!-- Subtotal original tachado si hay descuento -->
                <span v-if="discountData" class="original-subtotal">{{ formatPrice(subtotal) }}</span>
                <!-- Nuevo subtotal (o subtotal normal si no hay descuento) -->
                <span class="total-value" :class="{ 'discounted-subtotal': discountData }">
                  {{ formatPrice(subtotalAfterDiscount) }}
                </span>
              </div>
            </div>
            <div class="total-row">
              <span>{{ $t('cart.checkout.form.shipping') }}</span>
              <span class="total-value">
                {{ formatPrice(shipping) }}
                <span v-if="shippingType === 'gift' && selectedGiftUser" class="shipping-city-note">
                  ({{ selectedGiftUser.username }})
                </span>
                <span v-else-if="shippingForm.city" class="shipping-city-note">
                  ({{ shippingForm.city }})
                </span>
              </span>
            </div>
            
            <!-- Badge de descuento aplicado -->
            <div v-if="discountData" class="total-row discount-row">
              <span class="discount-label">
                {{ $t('cart.checkout.form.discountApplied', { code: discountData.code, percentage: discountData.discount_percentage }) }}
              </span>
              <span class="total-value discount-value">-{{ formatPrice(discountAmount) }}</span>
            </div>
            
            <div class="total-row tax-row">
              <span>{{ $t('cart.checkout.form.tax') }} <span class="tax-included-badge">{{ $t('cart.checkout.form.taxIncludedBadge') }}</span></span>
              <span class="total-value tax-included-value">{{ formatPrice(tax) }}</span>
            </div>
          </div>

          <!-- Final Total -->
          <div class="final-total">
            <div class="total-row">
              <span class="total-label">{{ $t('cart.checkout.form.total') }}</span>
              <span class="total-amount">{{ formatPrice(total) }}</span>
            </div>
            <p class="tax-note">{{ $t('cart.checkout.form.taxIncluded', { tax: formatPrice(tax) }) }}</p>
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
import { useProductStore } from '@/stores/modules/productStore.js';
import { useRouter } from 'vue-router';
import { useAlert } from '@/composables/useAlert.js';
import { Country, State } from 'country-state-city';
import { useCurrencyStore } from '@/stores/modules/currencyStore.js';
import WompiWidget from '@/components/WompiWidget.vue';

const router = useRouter();
const currencyStore = useCurrencyStore();

// ⭐ Helper para formatear precios usando currencyStore (maneja COP y USD automáticamente)
const formatPrice = (price) => {
  return currencyStore.formatPrice(price);
};

// ⭐ Helper para convertir precios de COP a la moneda actual
// Tasa de cambio aproximada: 1 USD = 4000 COP
const convertFromCOP = (copPrice) => {
  if (currencyStore.currentCurrency === 'USD') {
    return Math.round((copPrice / 4000) * 100) / 100; // Redondear a 2 decimales
  }
  return copPrice; // Si es COP, devolver el mismo valor
};

const cartStore = useCartStore();
const authStore = useAuthStore();
const crushStore = useCrushStore();
const i18nStore = useI18nStore();
const paymentStore = usePaymentStore();
const productStore = useProductStore();
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
const discountData = ref(null); // Datos del descuento validado
const discountError = ref('');
const isValidatingDiscount = ref(false);
const formError = ref('');

// ⭐ PayPal state
const showPayPalButtons = ref(false);
const paypalScriptLoaded = ref(false);

// ⭐ Producto de dropshipping (recargo oculto)
const DROPSHIPPING_PRODUCT_ID = 48500;
const dropshippingProduct = ref(null);
const isLoadingDropshipping = ref(false);

// ⭐ User search functionality for gift shipping
const usernameSearchQuery = ref('');
const showUserSearchResults = ref(false);
const selectedGiftUser = ref(null); // ⭐ Usuario seleccionado completo (con shipping_cost)
let usernameSearchTimeout = null;

// ⭐ Wishlist data from query params
const wishlistId = ref(null);
const wishlistName = ref(null);

// Computed property for available states - Only Colombia for national shipping
const availableStates = computed(() => {
  return State.getStatesOfCountry('CO');
});

// Get cart items
const cartItems = computed(() => cartStore.items);

// Check if user is authenticated and has username
const isUserAuthenticated = computed(() => authStore.isLoggedIn && authStore.username);

// ⭐ Dynamic gift note label with selected username
const giftNoteLabel = computed(() => {
  if (selectedGiftUser.value && selectedGiftUser.value.username) {
    return i18nStore.locale === 'es' 
      ? `Nota para @${selectedGiftUser.value.username}`
      : `Note for @${selectedGiftUser.value.username}`;
  }
  return i18nStore.locale === 'es' ? 'Nota para el destinatario' : 'Note for recipient';
});

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

// ⭐ Handle username input blur
const handleUsernameBlur = () => {
  setTimeout(() => {
    showUserSearchResults.value = false;
  }, 200);
};

// ⭐ Select user from search results
const selectUser = (user) => {
  console.log('👤 [SELECT USER] Usuario seleccionado:', user);
  
  // Guardar usuario completo con shipping_cost
  selectedGiftUser.value = user;
  
  // Ocultar resultados y limpiar búsqueda ANTES de actualizar el query
  // Esto previene que el watch vuelva a disparar la búsqueda
  showUserSearchResults.value = false;
  crushStore.clearSearch();
  
  // Limpiar el timeout de búsqueda
  if (usernameSearchTimeout) {
    clearTimeout(usernameSearchTimeout);
    usernameSearchTimeout = null;
  }
  
  // Actualizar campos del formulario
  shippingForm.value.username = `@${user.username}`;
  usernameSearchQuery.value = `@${user.username}`;
  
  console.log('💰 [SELECT USER] Costo de envío del usuario:', user.shipping_cost);
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
    selectedGiftUser.value = null; // Limpiar usuario seleccionado
    return;
  }

  // No buscar si ya hay un usuario seleccionado y el query coincide
  if (selectedGiftUser.value && newQuery === `@${selectedGiftUser.value.username}`) {
    console.log('⏭️ [WATCH] Usuario ya seleccionado, no buscar de nuevo');
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
    selectedGiftUser.value = null; // Limpiar usuario seleccionado
    crushStore.clearSearch();
  }
});

// ⭐ Sync shippingForm.username with search query when in gift mode
watch(() => shippingForm.value.username, (newUsername) => {
  if (shippingType.value === 'gift' && newUsername !== usernameSearchQuery.value) {
    usernameSearchQuery.value = newUsername;
  }
});

/**
 * ⭐ Cargar producto de dropshipping (recargo)
 * Este producto siempre se consulta y se agrega a la orden
 * pero NO se muestra al cliente en la lista de productos
 */
const loadDropshippingProduct = async () => {
  isLoadingDropshipping.value = true;
  
  try {
    console.log(`📦 [DROPSHIPPING] Consultando producto ${DROPSHIPPING_PRODUCT_ID}...`);
    
    const result = await productStore.fetchWooProduct(DROPSHIPPING_PRODUCT_ID);
    
    if (result.success && result.data) {
      dropshippingProduct.value = result.data;
      console.log('✅ [DROPSHIPPING] Producto cargado:', {
        id: result.data.id,
        name: result.data.name,
        price: result.data.price
      });
    } else {
      console.error('❌ [DROPSHIPPING] Error al cargar producto:', result.error);
      // No mostramos error al usuario porque es un proceso interno
    }
  } catch (error) {
    console.error('❌ [DROPSHIPPING] Error inesperado:', error);
  } finally {
    isLoadingDropshipping.value = false;
  }
};

// Calculate totals
const subtotal = computed(() => cartStore.totalPrice);

/**
 * ⭐ Validación del formulario
 */
const isFormValid = computed(() => {
  // Si es modo "para mí", validar campos completos
  if (shippingType.value === 'me') {
    const valid = !!(
      shippingForm.value.email &&
      shippingForm.value.fullName &&
      shippingForm.value.address1 &&
      shippingForm.value.city &&
      shippingForm.value.state &&
      shippingForm.value.zipCode &&
      shippingForm.value.phone
    );
    
    // Debug: mostrar qué campos faltan
    if (!valid) {
      console.log('🔍 [VALIDATION] Campos faltantes:', {
        email: !!shippingForm.value.email,
        fullName: !!shippingForm.value.fullName,
        address1: !!shippingForm.value.address1,
        city: !!shippingForm.value.city,
        state: !!shippingForm.value.state,
        zipCode: !!shippingForm.value.zipCode,
        phone: !!shippingForm.value.phone
      });
    }
    
    return valid;
  }
  
  // Si es modo regalo, solo validar email y username
  if (shippingType.value === 'gift') {
    return !!(
      shippingForm.value.email &&
      shippingForm.value.username
    );
  }
  
  return false;
});

/**
 * ⭐ Preparar datos de orden y continuar al pago
 */
const proceedToPayment = async () => {
  formError.value = '';

  try {
    console.log('📦 [CHECKOUT] Preparando datos para pago...');

    // Validar que el formulario esté completo
    if (!isFormValid.value) {
      formError.value = 'Por favor completa todos los campos obligatorios';
      await showError(
        'Completa todos los campos obligatorios antes de continuar.',
        '⚠️ Campos Incompletos'
      );
      return;
    }

    // Validar que haya items en el carrito
    if (!cartStore.items || cartStore.items.length === 0) {
      formError.value = 'El carrito está vacío';
      await showError('Tu carrito está vacío.', '🛒 Carrito Vacío');
      return;
    }

    // Obtener nombre del país
    const selectedCountry = countries.find(c => c.isoCode === shippingForm.value.country);
    const countryName = selectedCountry ? selectedCountry.name : shippingForm.value.country;

    // Preparar items del carrito
    const items = cartStore.items.map(item => ({
      woocommerce_product_id: item.product_id || item.id,
      woocommerce_variation_id: item.variation_id || null,
      product_name: item.name,
      quantity: item.quantity,
      unit_price: currencyStore.currentCurrency === 'USD' ? parseFloat(parseFloat(item.price).toFixed(2)) : parseFloat(item.price),
      attributes: item.attributes || null
    }));

    // ⭐ Agregar producto de dropshipping (recargo oculto)
    if (dropshippingProduct.value) {
      items.push({
        woocommerce_product_id: dropshippingProduct.value.id,
        woocommerce_variation_id: null,
        product_name: dropshippingProduct.value.name,
        quantity: 1,
        unit_price: currencyStore.currentCurrency === 'USD' ? parseFloat(parseFloat(dropshippingProduct.value.price).toFixed(2)) : parseFloat(dropshippingProduct.value.price),
        attributes: null
      });
      console.log('📦 [DROPSHIPPING] Producto agregado a items');
    }

    // Preparar datos de orden según el tipo de envío
    let orderData;

    if (shippingType.value === 'gift') {
      // Orden de regalo
      orderData = {
        items: items,
        customer_email: shippingForm.value.email,
        customer_name: isUserAuthenticated.value 
          ? `${authStore.user?.first_name || ''} ${authStore.user?.last_name || ''}`.trim() || authStore.username
          : shippingForm.value.email,
        receiver_username: shippingForm.value.username.replace('@', ''),
        gift_message: shippingForm.value.note || '',
        is_gift: true,
        shipping: currencyStore.currentCurrency === 'USD' ? parseFloat(baseShipping.value.toFixed(2)) : baseShipping.value,
        // ⭐ Enviar subtotal SIN descuento para validación del backend
        subtotal: currencyStore.currentCurrency === 'USD' ? parseFloat(subtotal.value.toFixed(2)) : subtotal.value,
        // ⭐ Enviar total CON descuento aplicado (para PayPal/Wompi)
        total: currencyStore.currentCurrency === 'USD' ? parseFloat(total.value.toFixed(2)) : total.value,
        // Incluir código de descuento - el backend validará y aplicará el descuento
        discount_code: discountData.value ? discountData.value.code : null,
        // Incluir wishlist data si existe
        is_from_wishlist: !!wishlistId.value,
        wishlist_id: wishlistId.value || null,
        wishlist_name: wishlistName.value || null,
        // Datos de envío del destinatario (si están disponibles)
        shipping_address: selectedGiftUser.value?.address || 'Dirección del destinatario',
        shipping_city: selectedGiftUser.value?.city || 'Ciudad',
        shipping_state: selectedGiftUser.value?.state || 'Departamento',
        shipping_postal_code: selectedGiftUser.value?.postal_code || '00000',
        shipping_country: countryName,
        phone_number: selectedGiftUser.value?.phone || '+57 300 0000000'
      };

      // Si hay un usuario autenticado, agregar como sender
      if (isUserAuthenticated.value) {
        orderData.sender_username = authStore.username;
      }

    } else {
      // Orden regular
      orderData = {
        items: items,
        customer_email: shippingForm.value.email,
        customer_name: shippingForm.value.fullName,
        shipping_address: shippingForm.value.address1,
        shipping_address_line_2: shippingForm.value.address2 || '',
        shipping_city: shippingForm.value.city,
        shipping_state: shippingForm.value.state,
        shipping_postal_code: shippingForm.value.zipCode,
        shipping_country: countryName,
        phone_number: `${shippingForm.value.phoneCode} ${shippingForm.value.phone}`,
        notes: shippingForm.value.additionalDetails || '',
        shipping: currencyStore.currentCurrency === 'USD' ? parseFloat(baseShipping.value.toFixed(2)) : baseShipping.value,
        // ⭐ Enviar subtotal SIN descuento para validación del backend
        subtotal: currencyStore.currentCurrency === 'USD' ? parseFloat(subtotal.value.toFixed(2)) : subtotal.value,
        // ⭐ Enviar total CON descuento aplicado (para PayPal/Wompi)
        total: currencyStore.currentCurrency === 'USD' ? parseFloat(total.value.toFixed(2)) : total.value,
        // Incluir código de descuento - el backend validará y aplicará el descuento
        discount_code: discountData.value ? discountData.value.code : null
      };
    }

    console.log('📤 [CHECKOUT] Datos de orden preparados:', orderData);
    console.log('🎟️ [CHECKOUT] discount_code en orderData:', orderData.discount_code);
    
    // Log del descuento aplicado
    if (discountData.value) {
      console.log('🎟️ [DISCOUNT] Código de descuento incluido en orden:', {
        code: discountData.value.code,
        percentage: discountData.value.discount_percentage,
        subtotal_original: orderData.subtotal,
        descuento_aplicado: discountAmount.value,
        total_con_descuento: orderData.total,
        shipping: orderData.shipping,
        discount_code_enviado: orderData.discount_code,
        nota: 'Backend validará el descuento usando subtotal + discount_code'
      });
    } else {
      console.log('ℹ️ [CHECKOUT] No hay código de descuento aplicado');
    }

    // PayPal para USD - guardar datos y mostrar botón
    sessionStorage.setItem('checkout_order_data', JSON.stringify(orderData));
    showPayPalButtons.value = true;
    
    // Scroll al botón de PayPal
    setTimeout(() => {
      const paypalSection = document.getElementById('paypal-section');
      if (paypalSection) {
        paypalSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);

  } catch (error) {
    console.error('❌ [CHECKOUT] Error al preparar datos:', error);
    formError.value = 'Error al preparar la orden';
    await showError('Error al preparar la orden.', '❌ Error');
  }
};

/**
 * ⭐ Variables para Wompi Widget
 */
const wompiWidgetData = ref(null);
const isPreparingPayment = ref(false);

/**
 * ⭐ Preparar widget de Wompi (COP) - Muestra el widget integrado
 */
const prepareWompiPayment = async () => {
  formError.value = '';
  isPreparingPayment.value = true;

  try {
    console.log('📦 [CHECKOUT] Preparando datos para Wompi...');

    // Validar formulario
    if (!isFormValid.value) {
      formError.value = 'Por favor completa todos los campos obligatorios';
      await showError('Completa todos los campos obligatorios.', '⚠️ Campos Incompletos');
      isPreparingPayment.value = false;
      return;
    }

    // Validar carrito
    if (!cartStore.items || cartStore.items.length === 0) {
      formError.value = 'El carrito está vacío';
      await showError('Tu carrito está vacío.', '🛒 Carrito Vacío');
      isPreparingPayment.value = false;
      return;
    }

    // Preparar datos de orden (mismo código que proceedToPayment)
    const selectedCountry = countries.find(c => c.isoCode === shippingForm.value.country);
    const countryName = selectedCountry ? selectedCountry.name : shippingForm.value.country;

    const items = cartStore.items.map(item => ({
      woocommerce_product_id: item.product_id || item.id,
      woocommerce_variation_id: item.variation_id || null,
      product_name: item.name,
      quantity: item.quantity,
      unit_price: parseFloat(item.price),
      attributes: item.attributes || null
    }));

    // Agregar dropshipping
    if (dropshippingProduct.value) {
      items.push({
        woocommerce_product_id: dropshippingProduct.value.id,
        woocommerce_variation_id: null,
        product_name: dropshippingProduct.value.name,
        quantity: 1,
        unit_price: parseFloat(dropshippingProduct.value.price),
        attributes: null
      });
    }

    let orderData;
    if (shippingType.value === 'gift') {
      orderData = {
        items: items,
        customer_email: shippingForm.value.email,
        customer_name: isUserAuthenticated.value 
          ? `${authStore.user?.first_name || ''} ${authStore.user?.last_name || ''}`.trim() || authStore.username
          : shippingForm.value.email,
        receiver_username: shippingForm.value.username.replace('@', ''),
        gift_message: shippingForm.value.note || '',
        is_gift: true,
        shipping: baseShipping.value,
        subtotal: subtotal.value,
        total: total.value,
        discount_code: discountData.value ? discountData.value.code : null,
        is_from_wishlist: !!wishlistId.value,
        wishlist_id: wishlistId.value || null,
        wishlist_name: wishlistName.value || null,
        shipping_address: selectedGiftUser.value?.address || 'Dirección del destinatario',
        shipping_city: selectedGiftUser.value?.city || 'Ciudad',
        shipping_state: selectedGiftUser.value?.state || 'Departamento',
        shipping_postal_code: selectedGiftUser.value?.postal_code || '00000',
        shipping_country: countryName,
        phone_number: selectedGiftUser.value?.phone || '+57 300 0000000'
      };
      if (isUserAuthenticated.value) {
        orderData.sender_username = authStore.username;
      }
    } else {
      orderData = {
        items: items,
        customer_email: shippingForm.value.email,
        customer_name: shippingForm.value.fullName,
        shipping_address: shippingForm.value.address1,
        shipping_city: shippingForm.value.city,
        shipping_state: shippingForm.value.state,
        shipping_postal_code: shippingForm.value.postalCode,
        shipping_country: countryName,
        phone_number: `${shippingForm.value.phoneCode}${shippingForm.value.phone}`,
        shipping: baseShipping.value,
        subtotal: subtotal.value,
        total: total.value,
        notes: shippingForm.value.note || '',
        discount_code: discountData.value ? discountData.value.code : null
      };
    }

    console.log('💳 [WOMPI] Creando transacción...', orderData);
    
    const result = await paymentStore.createWompiTransaction(orderData);
    
    if (!result.success) {
      formError.value = result.error || 'Error al preparar pago con Wompi';
      await showError(formError.value, '❌ Error en Wompi');
      isPreparingPayment.value = false;
      return;
    }
    
    console.log('✅ [WOMPI] Widget data recibida:', result.data);
    
    // Guardar datos para confirmar después
    localStorage.setItem('wompi_reference', result.data.reference);
    localStorage.setItem('wompi_order_data', JSON.stringify(orderData));
    localStorage.setItem('wompi_widget_data', JSON.stringify(result.data.widget_data));
    
    // Mostrar el widget
    wompiWidgetData.value = result.data.widget_data;
    isPreparingPayment.value = false;
    
  } catch (error) {
    console.error('❌ [WOMPI] Error inesperado:', error);
    formError.value = 'Error al procesar el pago con Wompi';
    await showError(formError.value, '❌ Error');
    isPreparingPayment.value = false;
  }
};

/**
 * ⭐ Cargar SDK de PayPal (USD)
 */
const loadPayPalScript = async () => {
  return new Promise(async (resolve, reject) => {
    if (window.paypal) {
      console.log('💳 [PAYPAL] SDK ya está cargado');
      paypalScriptLoaded.value = true;
      resolve();
      return;
    }

    const existingScript = document.querySelector('script[src*="paypal.com/sdk/js"]');
    if (existingScript) {
      existingScript.addEventListener('load', () => {
        console.log('💳 [PAYPAL] SDK cargado desde script existente');
        paypalScriptLoaded.value = true;
        resolve();
      });
      return;
    }

    console.log('💳 [PAYPAL] Cargando SDK...');
    
    // Usar client ID desde vite.config.js
    const clientId = import.meta.env.VITE_PAYPAL_CLIENT_ID;
    const currency = currencyStore.currentCurrency; // USD
    
    console.log('💳 [PAYPAL] Client ID:', clientId);
    console.log('💳 [PAYPAL] Currency:', currency);
    
    const script = document.createElement('script');
    // SDK v6 - Parámetros simplificados (buyer-country y enable-funding causan error 400)
    script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=${currency}&components=buttons`;
    script.setAttribute('data-sdk-integration-source', 'developer-studio');
    
    script.onload = () => {
      console.log('✅ [PAYPAL] SDK cargado exitosamente');
      paypalScriptLoaded.value = true;
      resolve();
    };
    
    script.onerror = (error) => {
      console.error('❌ [PAYPAL] Error al cargar SDK:', error);
      reject(error);
    };
    
    document.head.appendChild(script);
  });
};

/**
 * ⭐ Inicializar botones de PayPal
 */
const initPayPalButtons = () => {
  if (!window.paypal) {
    console.error('❌ [PAYPAL] SDK no está disponible');
    return;
  }

  const container = document.getElementById('paypal-button-container');
  if (!container) {
    console.error('❌ [PAYPAL] Contenedor no encontrado');
    return;
  }

  container.innerHTML = '';

  const orderDataStr = sessionStorage.getItem('checkout_order_data');
  if (!orderDataStr) {
    console.error('❌ [PAYPAL] No hay datos de orden');
    return;
  }

  const orderData = JSON.parse(orderDataStr);

  window.paypal.Buttons({
    style: {
      layout: 'vertical',
      color: 'gold',
      shape: 'rect',
      label: 'paypal'
    },

    createOrder: async (data, actions) => {
      console.log('💳 [PAYPAL] Creando orden...');
      
      try {
        // Si es regalo, usar endpoint de gifts
        if (orderData.is_gift) {
          const result = await paymentStore.sendGift(orderData);
          if (!result.success) throw new Error(result.error);
          return result.paypal_order_id;
        }

        // Si no es regalo, usar flujo normal
        const result = await paymentStore.createPayPalOrder(orderData);
        if (!result.success) throw new Error(result.error);
        return result.paypal_order_id;

      } catch (error) {
        console.error('❌ [PAYPAL] Error al crear orden:', error);
        await showError(error.message || 'Error al crear orden', '❌ Error');
        throw error;
      }
    },

    onApprove: async (data, actions) => {
      console.log('✅ [PAYPAL] Pago aprobado');

      try {
        showLoading('Procesando tu pago...', '💳 Procesando');

        const captureData = {
          paypal_order_id: data.orderID,
          ...orderData
        };

        const result = await paymentStore.capturePayPalOrder(data.orderID, captureData);

        closeAlert();

        if (!result.success) {
          throw new Error(result.error);
        }

        console.log('✅ [PAYPAL] Pago procesado exitosamente');

        await showSuccess(
          `Tu orden ha sido creada exitosamente.\n\n` +
          `📋 Orden: ${result.order.order_number}\n` +
          `💰 Total: $${result.order.total}\n\n` +
          `Recibirás un email de confirmación pronto.`,
          '🎉 ¡Pago Exitoso!',
          { timer: 8000 }
        );

        // Limpiar datos
        sessionStorage.removeItem('checkout_order_data');
        cartStore.clearCart();
        paymentStore.clearPaymentState();

        // Redirigir al home
        setTimeout(() => {
          router.push({ name: `Home-${i18nStore.locale}` });
        }, 1000);

      } catch (error) {
        console.error('❌ [PAYPAL] Error al capturar pago:', error);
        closeAlert();
        await showError(error.message || 'Error al procesar el pago', '❌ Error');
      }
    },

    onCancel: (data) => {
      console.log('⚠️ [PAYPAL] Pago cancelado');
      showError('Has cancelado el proceso de pago.', '⚠️ Pago Cancelado', { timer: 5000 });
    },

    onError: (err) => {
      console.error('❌ [PAYPAL] Error:', err);
      showError('Hubo un error con PayPal. Por favor intenta de nuevo.', '❌ Error en PayPal');
    }
  }).render('#paypal-button-container');
};

/**
 * ⭐ Validar código de descuento
 */
const validateDiscountCode = async () => {
  if (!discountCode.value || !discountCode.value.trim()) {
    discountError.value = 'Por favor ingresa un código de descuento';
    return;
  }

  isValidatingDiscount.value = true;
  discountError.value = '';

  try {
    console.log('🎟️ [DISCOUNT] Validando código:', discountCode.value);

    const result = await paymentStore.validateDiscountCode(discountCode.value.trim().toUpperCase());

    console.log('🎟️ [DISCOUNT] Respuesta:', result);

    if (result.success && result.data.exists && result.data.is_valid) {
      // Código válido
      discountData.value = {
        code: result.data.code,
        discount_percentage: parseFloat(result.data.discount_percentage)
      };
      
      await showSuccess(
        `¡Código aplicado! Descuento del ${result.data.discount_percentage}%`,
        '🎉 Descuento Aplicado'
      );
      
      console.log('✅ [DISCOUNT] Descuento aplicado:', discountData.value);
    } else {
      // Código no válido
      discountData.value = null;
      discountError.value = result.data?.message || result.error || 'Código de descuento no válido';
      
      await showError(
        result.data?.message || result.error || 'El código ingresado no es válido o ha expirado',
        '❌ Código Inválido'
      );
    }

  } catch (error) {
    console.error('❌ [DISCOUNT] Error al validar:', error);
    discountData.value = null;
    discountError.value = 'Error al validar el código';
    
    await showError(
      'Hubo un error al validar el código. Por favor intenta de nuevo.',
      '❌ Error'
    );
  } finally {
    isValidatingDiscount.value = false;
  }
};

/**
 * ⭐ Remover código de descuento
 */
const removeDiscount = () => {
  discountData.value = null;
  discountCode.value = '';
  discountError.value = '';
  console.log('🗑️ [DISCOUNT] Descuento removido');
};

/**
 * ⭐ Cálculo del costo de envío BASE (sin recargo)
 * Este es el valor real que se envía al backend
 */
const baseShipping = computed(() => {
  // ⭐ Si es modo regalo y hay usuario seleccionado, usar su shipping_cost
  if (shippingType.value === 'gift' && selectedGiftUser.value && selectedGiftUser.value.shipping_cost) {
    const cost = parseFloat(selectedGiftUser.value.shipping_cost);
    // ⭐ Convertir el shipping_cost si viene en COP y el currency actual es USD
    const convertedCost = convertFromCOP(cost);
    console.log(`📦 [SHIPPING] Costo del usuario destinatario: ${cost} COP → ${convertedCost} ${currencyStore.currentCurrency}`);
    return convertedCost;
  }
  
  // ⭐ Si es modo "para mí", calcular según ciudad
  const ciudad = (shippingForm.value.city || '').toLowerCase().trim();
  
  if (!ciudad) {
    return convertFromCOP(15000); // ~$3.75 USD
  }
  
  switch (ciudad) {
    case 'medellín':
    case 'medellin':
      return convertFromCOP(10500); // ~$2.63 USD
      
    case 'san andrés isla':
    case 'san andres isla':
    case 'san andrés':
    case 'san andres':
    case 'santa catalina':
    case 'providencia':
      return convertFromCOP(45000); // ~$11.25 USD
      
    default:
      return convertFromCOP(15000); // ~$3.75 USD
  }
});

/**
 * ⭐ Cálculo del envío MOSTRADO al cliente
 * Incluye el costo base + el recargo de dropshipping
 */
const shipping = computed(() => {
  let total = baseShipping.value;
  
  // Agregar recargo de dropshipping si está disponible
  if (dropshippingProduct.value && dropshippingProduct.value.price) {
    const dropshippingPrice = parseFloat(dropshippingProduct.value.price);
    total += dropshippingPrice;
    console.log(`📦 [DROPSHIPPING] Shipping mostrado: ${baseShipping.value} + ${dropshippingPrice} = ${total}`);
  }
  
  return total;
});

/**
 * ⭐ Cálculo del IVA (19%)
 * El IVA ya está INCLUIDO en los precios de los productos
 * Este cálculo es solo informativo para mostrar al cliente
 * Se calcula sobre el subtotal CON descuento aplicado
 */
const tax = computed(() => {
  // Calcular el IVA que ya está incluido en el subtotal (con descuento si aplica)
  // Fórmula: IVA = Subtotal - (Subtotal / 1.19)
  // O simplificado: IVA = Subtotal * (0.19 / 1.19)
  return subtotalAfterDiscount.value * (0.19 / 1.19);
});

/**
 * ⭐ Monto del descuento aplicado
 * Se aplica solo al subtotal, NO al shipping
 */
const discountAmount = computed(() => {
  if (!discountData.value) return 0;
  
  const discount = (subtotal.value * discountData.value.discount_percentage) / 100;
  console.log('🎟️ [DISCOUNT] Monto calculado:', {
    subtotal: subtotal.value,
    percentage: discountData.value.discount_percentage,
    discount: discount
  });
  
  return discount;
});

/**
 * ⭐ Subtotal después del descuento
 */
const subtotalAfterDiscount = computed(() => {
  return subtotal.value - discountAmount.value;
});

/**
 * ⭐ Total de la orden
 * Subtotal (con descuento si aplica) + Shipping (sin descuento)
 */
const total = computed(() => {
  const calculatedTotal = subtotalAfterDiscount.value + shipping.value;
  console.log('💰 [TOTAL] Cálculo:', {
    subtotal: subtotal.value,
    discount: discountAmount.value,
    subtotal_after_discount: subtotalAfterDiscount.value,
    shipping: shipping.value,
    tax_included: tax.value,
    total: calculatedTotal
  });
  return calculatedTotal;
});

// Initialize cart on mount
onMounted(async () => {
  // Cargar el carrito desde localStorage
  cartStore.loadCart();
  
  // Si el carrito está vacío, redirigir al carrito
  if (cartStore.isEmpty) {
    router.push({ name: `Cart-${i18nStore.locale}` });
    return;
  }

  // ⭐ Read query params for wishlist purchase
  const route = router.currentRoute.value;
  if (route.query.giftMode === 'true') {
    shippingType.value = 'gift';
    
    if (route.query.username) {
      const username = route.query.username;
      const formattedUsername = username.startsWith('@') ? username : `@${username}`;
      shippingForm.value.username = formattedUsername;
      usernameSearchQuery.value = formattedUsername;
      
      // ⭐ Buscar el usuario automáticamente para obtener su shipping_cost
      try {
        const cleanUsername = username.replace('@', '').trim();
        console.log('🔍 [CHECKOUT] Buscando usuario automáticamente:', cleanUsername);
        
        await crushStore.searchUsers(cleanUsername, 5);
        
        // Si encontramos resultados, seleccionar el primero que coincida exactamente
        if (crushStore.searchResults.length > 0) {
          const exactMatch = crushStore.searchResults.find(
            user => user.username.toLowerCase() === cleanUsername.toLowerCase()
          );
          
          if (exactMatch) {
            console.log('✅ [CHECKOUT] Usuario encontrado automáticamente:', exactMatch);
            // Seleccionar el usuario automáticamente
            selectUser(exactMatch);
          } else {
            console.warn('⚠️ [CHECKOUT] No se encontró coincidencia exacta para:', cleanUsername);
          }
        } else {
          console.warn('⚠️ [CHECKOUT] No se encontraron resultados para:', cleanUsername);
        }
      } catch (error) {
        console.error('❌ [CHECKOUT] Error al buscar usuario automáticamente:', error);
      }
    }
    
    if (route.query.wishlistId) {
      wishlistId.value = parseInt(route.query.wishlistId);
      wishlistName.value = route.query.wishlistName || null;
      console.log('🎁 [WISHLIST] Compra desde wishlist:', {
        id: wishlistId.value,
        name: wishlistName.value
      });
    }
  }

  // ⭐ Cargar producto de dropshipping (recargo)
  // Este producto siempre se consulta al inicio
  await loadDropshippingProduct();
});

// Watch para cargar PayPal cuando se muestre
watch(showPayPalButtons, async (newValue) => {
  if (newValue && currencyStore.currentCurrency === 'USD') {
    try {
      await loadPayPalScript();
      setTimeout(() => {
        initPayPalButtons();
      }, 100);
    } catch (error) {
      console.error('❌ [PAYPAL] Error al inicializar:', error);
      await showError('No se pudo cargar PayPal.', '❌ Error');
    }
  }
});

// Cleanup on unmount
onBeforeUnmount(() => {
  // Limpiar búsqueda de usuarios
  if (usernameSearchTimeout) {
    clearTimeout(usernameSearchTimeout);
  }
  selectedGiftUser.value = null;
  crushStore.clearSearch();
});
</script>

<style scoped>
.checkout-view {
  min-height: 100vh;
  background: var(--color-brand-pink-lighter);
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
  border: 2px solid var(--color-brand-pink-light);
  border-radius: 10px;
  font-size: 0.875rem;
  transition: all 0.3s ease;
  background: white;
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
  border-color: var(--color-brand-purple-light);
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
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
  border: 2px solid var(--color-brand-pink-light);
  border-radius: 12px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  background: white;
  transition: all 0.3s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--color-brand-purple-light);
  background: white;
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
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

/* Payment Button Section */
.payment-button-section {
  margin-top: 2rem;
}

.payment-btn {
  width: 100%;
  background: var(--color-brand-purple-light);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1.125rem 2rem;
  font-size: 1.125rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(218, 157, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.payment-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(218, 157, 255, 0.4);
  opacity: 0.95;
}

.payment-btn:disabled,
.payment-btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #cbd5e1;
  color: #64748b;
  box-shadow: none;
  transform: none;
}

.payment-btn:active:not(:disabled) {
  transform: translateY(0);
}

/* Payment Disabled Message */
.payment-disabled-message {
  padding: 1rem;
  background: #f1f5f9;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  text-align: center;
}

.payment-disabled-message p {
  margin: 0;
  color: #64748b;
  font-size: 0.9375rem;
  font-weight: 500;
}

/* Wompi Widget Wrapper */
.wompi-widget-wrapper {
  width: 100%;
  overflow: visible;
}

.payment-error {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background-color: rgba(191, 94, 129, 0.1);
  border: 2px solid var(--color-brand-pink-dark);
  border-radius: 12px;
  color: var(--color-brand-pink-dark);
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
  background: var(--color-brand-purple-light);
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

.validate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(218, 157, 255, 0.4);
  opacity: 0.9;
}

.validate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Discount Applied */
.discount-applied {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background: var(--color-brand-pink-lighter);
  border: 2px solid var(--color-brand-pink-light);
  border-radius: 12px;
}

.discount-applied-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.discount-code-badge {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-brand-purple-light);
  background: white;
  padding: 0.375rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--color-brand-pink-light);
}

.discount-percentage {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-brand-pink);
}

.remove-discount-btn {
  background: transparent;
  border: none;
  color: var(--color-brand-pink-dark);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  transition: all 0.2s ease;
  border-radius: 6px;
}

.remove-discount-btn:hover {
  background: var(--color-brand-pink-light);
  color: var(--color-brand-dark);
}

.discount-error {
  margin-top: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-brand-pink-dark);
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

.discount-row {
  color: var(--color-brand-pink);
}

.discount-label {
  font-weight: 600;
  color: var(--color-brand-pink);
}

.discount-value {
  font-weight: 700;
  color: var(--color-brand-pink);
}

/* Subtotal con descuento */
.subtotal-values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.original-subtotal {
  font-size: 0.875rem;
  color: #999;
  text-decoration: line-through;
  font-weight: 400;
}

.discounted-subtotal {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-brand-pink);
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
  color: #059669;
  margin: 0;
  font-weight: 500;
}

/* Tax Included Badge */
.tax-included-badge {
  font-size: 0.75rem;
  color: #059669;
  font-weight: 500;
  background: rgba(5, 150, 105, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 4px;
}

.tax-included-value {
  color: #059669 !important;
  font-style: italic;
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

/* Wompi Section - REMOVED (botón integrado directamente en el formulario) */

/* PayPal Section */
.paypal-section {
  margin-top: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  border: 2px solid var(--color-brand-pink-light);
  box-shadow: 0 4px 12px rgba(191, 94, 129, 0.1);
}

.paypal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-brand-dark);
  margin-bottom: 1.5rem;
  text-align: center;
  font-family: 'Comfortaa', cursive;
}

#paypal-button-container {
  max-width: 500px;
  margin: 0 auto;
}
</style>
