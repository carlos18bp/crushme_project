<template>
  <div class="checkout-gift-section">
    <!-- Username Search -->
    <div class="form-group">
      <label for="username">{{ $t('cart.checkout.form.username') }} <span class="text-red-500">*</span></label>
      <div class="username-search-container">
        <input
          type="text"
          id="username"
          v-model="searchQuery"
          :placeholder="$t('cart.checkout.form.placeholders.searchUser')"
          class="form-input username-search-input"
          autocomplete="off"
          @focus="showResults = searchResults.length > 0"
          @blur="() => setTimeout(() => showResults = false, 200)"
        >
        <!-- Search Results Dropdown -->
        <div v-if="showResults && searchResults.length > 0" class="username-search-results">
          <div
            v-for="user in searchResults"
            :key="user.username"
            class="username-search-item"
            @mousedown="selectUser(user)"
          >
            <!-- Profile Picture -->
            <div class="search-user-avatar">
              <img
                v-if="user.profile_picture"
                :src="user.profile_picture"
                :alt="user.username"
                class="avatar-image"
                @error="handleImageError"
                @load="() => console.log('✅ [GIFT] Imagen cargada:', user.profile_picture)"
              >
              <div v-else class="avatar-placeholder">
                <span class="avatar-initial">{{ user.username.charAt(0).toUpperCase() }}</span>
              </div>
            </div>

            <!-- User Info -->
            <div class="search-user-main">
              <div class="username-row">
                <span class="search-username">@{{ user.username }}</span>
                <span v-if="user.is_crush" class="search-crush-badge">💖 Crush</span>
              </div>
            </div>

            <!-- Shipping Cost -->
            <div class="search-shipping-info">
              <span class="shipping-icon">📦</span>
              <span class="shipping-cost">{{ formatCOP(user.shipping_cost) }}</span>
            </div>
          </div>
        </div>
      </div>
      <p v-if="isUserAuthenticated" class="gift-field-description">
        <span class="highlight">@{{ currentUsername }}</span> {{ $t('cart.checkout.form.help.username') }}
      </p>
    </div>

    <!-- Gift Note -->
    <div class="form-group">
      <label for="note">{{ $t('cart.checkout.form.note') }}</label>
      <textarea
        id="note"
        v-model="form.note"
        :placeholder="$t('cart.checkout.form.placeholders.note')"
        class="form-textarea"
        rows="3"
      ></textarea>
    </div>

    <!-- ⭐ Shipping Info (informativo) -->
    <div v-if="displayShippingCost > 0" class="gift-shipping-info">
      <div class="shipping-info-header">
        <span class="shipping-icon">📦</span>
        <span class="shipping-label">Costo de envío al destinatario</span>
      </div>
      <div class="shipping-cost">
        {{ formatCOP(displayShippingCost) }}
      </div>
      <p class="shipping-note">
        Incluye envío base ({{ formatCOP(shippingCost) }}) + recargo de procesamiento ({{ formatCOP(dropshippingCost) }})
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/modules/authStore.js';
import { useCrushStore } from '@/stores/modules/crushStore.js';
import { useCurrencyStore } from '@/stores/modules/currencyStore.js';

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  shippingCost: {
    type: Number,
    default: 0
  },
  dropshippingCost: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['update:modelValue', 'user-selected', 'shipping-change']);

const authStore = useAuthStore();
const crushStore = useCrushStore();
const currencyStore = useCurrencyStore();

const searchQuery = ref('');
const showResults = ref(false);
const selectedUserShipping = ref(0);
let searchTimeout = null;

// Helper para formatear precios usando currencyStore
const formatCOP = (price) => currencyStore.formatPrice(price);

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const isUserAuthenticated = computed(() => authStore.isLoggedIn);
const currentUsername = computed(() => authStore.username);
const searchResults = computed(() => crushStore.searchResults);

// Shipping total mostrado (base + dropshipping)
const displayShippingCost = computed(() => {
  return props.shippingCost + props.dropshippingCost;
});

// Watch search query and trigger search
watch(searchQuery, (newQuery) => {
  // Sync with form
  form.value.username = newQuery;

  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }

  // Debounce search
  if (newQuery && newQuery.length >= 2) {
    searchTimeout = setTimeout(async () => {
      // Limpiar el @ si existe
      const cleanQuery = newQuery.replace('@', '').trim();
      
      if (cleanQuery.length >= 2) {
        console.log('🔍 [GIFT] Buscando usuario:', cleanQuery);
        await crushStore.searchUsers(cleanQuery, 5);
        showResults.value = crushStore.searchResults.length > 0;
        
        // Log de resultados
        console.log('📋 [GIFT] Resultados encontrados:', crushStore.searchResults.length);
        crushStore.searchResults.forEach((user, index) => {
          console.log(`  ${index + 1}. @${user.username}`, {
            is_crush: user.is_crush,
            shipping: user.shipping_cost,
            photo: user.profile_picture ? '✅ Tiene foto' : '❌ Sin foto'
          });
        });
      }
    }, 300);
  } else {
    crushStore.clearSearchResults();
    showResults.value = false;
  }
});

// Sync form username with search query
watch(() => form.value.username, (newUsername) => {
  if (newUsername !== searchQuery.value) {
    searchQuery.value = newUsername;
  }
});

const selectUser = (user) => {
  console.log('👤 [GIFT] Usuario seleccionado:', user);
  console.log('📦 [GIFT] Shipping cost del usuario:', user.shipping_cost);
  console.log('💖 [GIFT] Es crush:', user.is_crush);
  console.log('🖼️ [GIFT] Foto de perfil:', user.profile_picture);
  
  searchQuery.value = `@${user.username}`;
  form.value.username = user.username;
  
  // Shipping base del usuario
  const baseShipping = user.shipping_cost || 15000;
  selectedUserShipping.value = baseShipping;
  
  // Shipping total = base + dropshipping
  const totalShipping = baseShipping + props.dropshippingCost;
  
  showResults.value = false;
  crushStore.clearSearchResults();
  
  // Emitir eventos
  emit('user-selected', user);
  emit('shipping-change', totalShipping); // ⭐ Emitir total con dropshipping
  
  console.log('📦 [GIFT] Desglose de shipping:', {
    base: baseShipping,
    dropshipping: props.dropshippingCost,
    total: totalShipping
  });
  console.log('✅ [GIFT] Shipping total actualizado a:', totalShipping);
};

/**
 * Manejar error al cargar imagen
 */
const handleImageError = (event) => {
  console.error('❌ [GIFT] Error cargando imagen:', event.target.src);
  // Ocultar la imagen y mostrar placeholder
  event.target.style.display = 'none';
};
</script>

<style scoped>
.checkout-gift-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #ec4899;
  box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
}

.form-textarea {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  resize: vertical;
  min-height: 80px;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #ec4899;
  box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
}

/* Username Search */
.username-search-container {
  position: relative;
}

.username-search-input {
  width: 100%;
}

.username-search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 50;
}

.username-search-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.username-search-item:last-child {
  border-bottom: none;
}

.username-search-item:hover {
  background-color: #fce7f3;
  transform: translateX(4px);
}

/* Avatar */
.search-user-avatar {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
}

.avatar-image {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f9a8d4;
}

.avatar-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #f9a8d4;
}

.avatar-initial {
  color: white;
  font-size: 1.125rem;
  font-weight: 700;
}

/* User Info */
.search-user-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.username-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.search-username {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.9375rem;
}

.search-crush-badge {
  padding: 0.125rem 0.5rem;
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
  color: white;
  font-size: 0.6875rem;
  border-radius: 9999px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}

.search-shipping-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 0.5rem;
  border: 1px solid #fbbf24;
}

.shipping-icon {
  font-size: 1rem;
}

.search-shipping-info .shipping-cost {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #92400e;
  white-space: nowrap;
}

.gift-field-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.highlight {
  color: #ec4899;
  font-weight: 600;
}

/* Gift Shipping Info */
.gift-shipping-info {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  border-radius: 0.75rem;
  border: 1px solid #f9a8d4;
}

.shipping-info-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.shipping-icon {
  font-size: 1.25rem;
}

.shipping-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #be185d;
}

.shipping-cost {
  font-size: 1.5rem;
  font-weight: 700;
  color: #be185d;
  margin-bottom: 0.5rem;
}

.shipping-note {
  font-size: 0.75rem;
  color: #9f1239;
  margin: 0;
  font-style: italic;
}
</style>
