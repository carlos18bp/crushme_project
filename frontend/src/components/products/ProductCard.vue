<template>
  <div class="product-card bg-white rounded-2xl md:rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300">
    
    <!-- Imagen del producto con iconos -->
    <div class="product-image relative bg-white p-3 md:p-4">
      <img 
        :src="product.images && product.images.length > 0 ? product.images[0].src : 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop&crop=center'" 
        :alt="product.name" 
        class="w-full h-40 md:h-44 lg:h-48 object-contain cursor-pointer"
        @click="$emit('navigate-to-product', product.id)">
      
      <!-- Action Icons - Esquina superior derecha (solo si no está en modo gift) -->
      <div v-if="!giftMode" class="product-actions absolute top-4 md:top-5 lg:top-6 right-4 md:right-5 lg:right-6 flex space-x-2 md:space-x-2.5 lg:space-x-3">
        <!-- Icono de Lista (Wishlist) -->
        <button 
          @click.stop="handleAddToWishlist"
          class="action-btn bg-white p-2 md:p-2.5 rounded-lg md:rounded-xl shadow-md hover:shadow-lg transition-all duration-200 hover:scale-110"
          :title="$t('products.product.addToList')">
          <img 
            :src="isInList ? ListCheckIcon : ListNoCheckIcon" 
            alt="List icon"
            class="w-5 h-5 md:w-6 md:h-6">
        </button>
        
        <!-- Icono de Corazón (Favoritos) -->
        <button 
          @click.stop="handleToggleWishlist"
          :disabled="isTogglingFavorite"
          class="action-btn bg-white p-2 md:p-2.5 rounded-lg md:rounded-xl shadow-md hover:shadow-lg transition-all duration-200 hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed"
          :title="isFavorited ? $t('products.product.removeFromFavorites') : $t('products.product.addToFavorites')">
          <img 
            :src="isFavorited ? HeartCheckIcon : HeartNoCheckIcon" 
            alt="Heart icon"
            class="w-5 h-5 md:w-6 md:h-6">
        </button>
      </div>
    </div>

    <!-- Información del producto -->
    <div class="product-info px-3 md:px-4 pb-3 md:pb-4">
      <h3 
        class="product-title text-sm md:text-base font-normal text-gray-900 mb-2 md:mb-3 cursor-pointer hover:text-brand-pink-dark transition-colors font-comfortaa line-clamp-2"
        @click="$emit('navigate-to-product', product.id)">
        {{ product.name }}
      </h3>
      
      <div class="product-footer flex flex-col gap-3 md:gap-4 mt-2 md:mt-3">
        <!-- Precio o Find Me para productos variables -->
        <div class="price-section">
          <span v-if="product.type === 'variable'" class="product-price text-lg md:text-xl font-medium text-brand-pink-dark font-poppins italic cursor-pointer hover:text-brand-pink transition-colors" @click="$emit('navigate-to-product', product.id)">
            {{ $t('products.product.findMe') || 'Find me ✨' }}
          </span>
          <span v-else class="product-price text-xl md:text-2xl font-medium text-gray-900 font-poppins">
            {{ displayPrice }}
          </span>
        </div>
        
        <!-- Botones de acción (solo para productos NO variables) -->
        <template v-if="product.type !== 'variable'">
          <div v-if="giftMode" class="product-buttons flex gap-2 md:gap-2.5 w-full">
            <!-- Botón único para modo regalo -->
            <button 
              @click.stop="handleBuyAsGift"
              :disabled="product.stock_status === 'outofstock' || cartStore.isUpdating"
              class="btn-gift text-white px-3 md:px-4 py-2 md:py-2.5 rounded-full text-xs md:text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-poppins hover:opacity-90 whitespace-nowrap flex-1"
              style="background-color: #DA9DFF;">
              {{ cartStore.isUpdating ? ($t('products.product.adding') || 'Adding...') : ($t('products.product.buyAsGift') || 'Buy as Gift') }}
            </button>
          </div>
          <div v-else class="product-buttons flex gap-2 md:gap-2.5 w-full">
            <button 
              @click.stop="handleBuyNow"
              :disabled="product.stock_status === 'outofstock' || cartStore.isUpdating"
              class="btn-buy text-white px-3 md:px-4 py-2 md:py-2.5 rounded-full text-xs md:text-sm font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-poppins hover:opacity-90 flex-1"
              style="background-color: #DA9DFF;">
              {{ cartStore.isUpdating ? ($t('products.product.adding') || 'Adding...') : ($t('products.product.buyNow') || 'Buy now') }}
            </button>
            <button 
              @click.stop="handleAddToCart"
              :disabled="product.stock_status === 'outofstock' || cartStore.isUpdating"
              class="btn-cart text-white px-3 md:px-4 py-2 md:py-2.5 rounded-full text-xs md:text-sm font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-poppins hover:opacity-90 flex-1"
              style="background-color: #DA9DFF;">
              {{ cartStore.isUpdating ? ($t('products.product.adding') || 'Adding...') : ($t('products.product.addToCart') || 'Add to cart') }}
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- Wishlist Selector Modal -->
    <WishlistSelector
      :show="showWishlistSelector"
      :product-id="product.id"
      @close="showWishlistSelector = false"
      @added="handleWishlistAdded"
      @create-wishlist="handleCreateWishlist"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '@/stores/modules/cartStore.js'
import { useAuthStore } from '@/stores/modules/authStore'
import { useProfileStore } from '@/stores/modules/profileStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import WishlistSelector from '@/components/wishlists/WishlistSelector.vue'
import { getFormattedProductPrice, getProductPrice } from '@/utils/priceHelper.js'

// Importar iconos SVG como URLs
import HeartCheckIcon from '@/assets/icons/heart/check.svg?url'
import HeartNoCheckIcon from '@/assets/icons/heart/no_check.svg?url'
import ListCheckIcon from '@/assets/icons/list/check.svg?url'
import ListNoCheckIcon from '@/assets/icons/list/no_check.svg?url'

// Props
const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  isInWishlist: {
    type: Boolean,
    default: false
  },
  isInList: {
    type: Boolean,
    default: false
  },
  isInFavorites: {
    type: Boolean,
    default: false
  },
  giftMode: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'navigate-to-product',
  'add-to-cart',
  'toggle-wishlist',
  'toggle-list',
  'favorite-updated'
])

// Router, i18n and stores
const router = useRouter()
const { t } = useI18n()
const cartStore = useCartStore()
const authStore = useAuthStore()
const profileStore = useProfileStore()
const i18nStore = useI18nStore()

// Local state
const showWishlistSelector = ref(false)
const isFavorited = ref(props.isInFavorites)
const isTogglingFavorite = ref(false)

// Computed: Precio formateado del producto (extrae de short_description)
const displayPrice = computed(() => {
  return getFormattedProductPrice(props.product)
})

// Computed: Precio numérico (para cálculos)
const numericPrice = computed(() => {
  return getProductPrice(props.product)
})

// Watch for changes in isInFavorites prop
watch(() => props.isInFavorites, (newValue) => {
  isFavorited.value = newValue
})

// Methods
const handleToggleWishlist = async () => {
  // Check if user is authenticated
  if (!authStore.isLoggedIn) {
    // Redirect to login
    router.push({ name: `Login-${i18nStore.locale}` })
    return
  }
  
  // Toggle favorite
  isTogglingFavorite.value = true
  
  try {
    if (isFavorited.value) {
      // Remove from favorites
      const result = await profileStore.removeProductFromFavorites(props.product.id)
      if (result.success) {
        isFavorited.value = false
        emit('favorite-updated', { productId: props.product.id, isFavorited: false })
      }
    } else {
      // Add to favorites
      const result = await profileStore.addProductToFavorites(props.product.id)
      if (result.success) {
        isFavorited.value = true
        emit('favorite-updated', { productId: props.product.id, isFavorited: true })
      }
    }
  } catch (error) {
    console.error('Error toggling favorite:', error)
  } finally {
    isTogglingFavorite.value = false
  }
}

const handleAddToWishlist = () => {
  // Check if user is authenticated
  if (!authStore.isLoggedIn) {
    // Redirect to login
    router.push({ name: `Login-${i18nStore.locale}` })
    return
  }
  
  // Show wishlist selector
  showWishlistSelector.value = true
}

const handleWishlistAdded = (wishlistId) => {
  console.log(`Product ${props.product.id} added to wishlist ${wishlistId}`)
  // Optionally show a success message
}

const handleCreateWishlist = () => {
  showWishlistSelector.value = false
  router.push({ name: `ProfileWishlist-${i18nStore.locale}` })
}

const handleBuyNow = () => {
  console.log('🔵 [ProductCard] handleBuyNow clicked for product:', props.product.id)
  
  // Si es un producto variable, redirigir al detalle
  if (props.product.type === 'variable') {
    emit('navigate-to-product', props.product.id)
    return
  }
  
  try {
    // Agregar el producto al carrito (siempre 1 unidad)
    // Nota: En ProductCard no tenemos variaciones, solo productos simples desde la lista
    const result = cartStore.addToCart(props.product.id, 1, {
      name: props.product.name,
      price: numericPrice.value,
      image: props.product.images && props.product.images.length > 0 ? props.product.images[0].src : null,
      stock_status: props.product.stock_status,
      variation_id: null // Los productos desde la lista no tienen variación seleccionada
    })
    
    console.log('🔵 [ProductCard] handleBuyNow result:', result)
    
    if (result.success) {
      // Redirigir al checkout
      router.push({ name: `Checkout-${i18nStore.locale}` })
    }
  } catch (error) {
    console.error('Error al comprar el producto:', error)
  }
}

const handleAddToCart = () => {
  console.log('🟢 [ProductCard] handleAddToCart clicked for product:', props.product.id)
  
  // Si es un producto variable, redirigir al detalle
  if (props.product.type === 'variable') {
    emit('navigate-to-product', props.product.id)
    return
  }
  
  try {
    const result = cartStore.addToCart(props.product.id, 1, {
      name: props.product.name,
      price: numericPrice.value,
      image: props.product.images && props.product.images.length > 0 ? props.product.images[0].src : null,
      stock_status: props.product.stock_status,
      variation_id: null // Los productos desde la lista no tienen variación seleccionada
    })
    
    console.log('🟢 [ProductCard] handleAddToCart result:', result)
    
    if (result.success) {
      // Emitir evento para notificar al componente padre si es necesario
      emit('add-to-cart', props.product)
    }
  } catch (error) {
    console.error('Error adding product to cart:', error)
  }
}

const handleBuyAsGift = () => {
  console.log('🎁 [ProductCard] handleBuyAsGift clicked for product:', props.product.id)
  
  // Si es un producto variable, redirigir al detalle
  if (props.product.type === 'variable') {
    emit('navigate-to-product', props.product.id)
    return
  }
  
  try {
    // Agregar el producto al carrito (siempre 1 unidad)
    const result = cartStore.addToCart(props.product.id, 1, {
      name: props.product.name,
      price: numericPrice.value,
      image: props.product.images && props.product.images.length > 0 ? props.product.images[0].src : null,
      stock_status: props.product.stock_status,
      variation_id: null // Los productos desde la lista no tienen variación seleccionada
    })
    
    console.log('🎁 [ProductCard] handleBuyAsGift result:', result)
    
    if (result.success) {
      // Redirigir al checkout
      router.push({ name: `Checkout-${i18nStore.locale}` })
    }
  } catch (error) {
    console.error('Error al comprar el producto como regalo:', error)
  }
}
</script>

<style scoped>
/* Product Cards - Mobile First */
.product-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
}

@media (min-width: 768px) {
  .product-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.10);
  }
}

@media (min-width: 1024px) {
  .product-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
  }
}

.product-image {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
}

.product-actions {
  opacity: 1;
  transition: opacity 0.3s ease;
}

.action-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.action-btn:hover {
  transform: scale(1.15) rotate(5deg);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.action-btn:active {
  transform: scale(0.95);
}

.product-title {
  line-height: 1.4;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (min-width: 768px) {
  .product-title {
    line-height: 1.5;
  }
}

.product-price {
  font-weight: 500;
  letter-spacing: -0.02em;
}

.btn-buy,
.btn-cart,
.btn-gift {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.02em;
  position: relative;
  overflow: hidden;
}

.btn-buy::before,
.btn-cart::before,
.btn-gift::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-buy:hover::before,
.btn-cart:hover::before,
.btn-gift:hover::before {
  width: 300px;
  height: 300px;
}

.btn-buy:hover,
.btn-cart:hover,
.btn-gift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(192, 132, 252, 0.5);
}

.btn-buy:active,
.btn-cart:active,
.btn-gift:active {
  transform: translateY(0);
}

/* Responsive Design - Mobile First */
.product-buttons {
  width: 100%;
}

.product-buttons button {
  flex: 1;
  text-align: center;
  min-width: 0;
}

/* Touch targets for mobile */
@media (max-width: 640px) {
  .action-btn {
    min-width: 40px;
    min-height: 40px;
  }
  
  .btn-buy,
  .btn-cart,
  .btn-gift {
    min-height: 36px;
  }
}

/* Reduce hover effects on touch devices */
@media (hover: none) {
  .product-card:hover {
    transform: none;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
  
  .action-btn:hover {
    transform: scale(1);
  }
  
  .btn-buy:hover,
  .btn-cart:hover,
  .btn-gift:hover {
    transform: none;
  }
}
</style>
