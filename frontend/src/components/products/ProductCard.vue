<template>
  <div class="product-card bg-white rounded-3xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300">
    
    <!-- Imagen del producto con iconos -->
    <div class="product-image relative bg-white p-4">
      <img 
        :src="product.images && product.images.length > 0 ? product.images[0].src : 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop&crop=center'" 
        :alt="product.name" 
        class="w-full h-48 object-contain cursor-pointer"
        @click="$emit('navigate-to-product', product.id)">
      
      <!-- Action Icons - Esquina superior derecha -->
      <div class="product-actions absolute top-6 right-6 flex space-x-3">
        <!-- Icono de Lista -->
        <button 
          @click.stop="handleToggleList"
          class="action-btn bg-white p-2.5 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 hover:scale-110"
          :title="$t('products.product.addToList')">
          <img 
            :src="isInList ? ListCheckIcon : ListNoCheckIcon" 
            alt="List icon"
            class="w-6 h-6">
        </button>
        
        <!-- Icono de Corazón -->
        <button 
          @click.stop="handleToggleWishlist"
          class="action-btn bg-white p-2.5 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 hover:scale-110"
          :title="$t('products.product.addToWishlist')">
          <img 
            :src="isInWishlist ? HeartCheckIcon : HeartNoCheckIcon" 
            alt="Heart icon"
            class="w-6 h-6">
        </button>
      </div>
    </div>

    <!-- Información del producto -->
    <div class="product-info px-4 pb-4">
      <h3 
        class="product-title text-base font-normal text-gray-900 mb-3 cursor-pointer hover:text-brand-pink-dark transition-colors font-comfortaa"
        @click="$emit('navigate-to-product', product.id)">
        {{ product.name }}
      </h3>
      
      <div class="product-footer flex items-center justify-between gap-3 mt-3">
        <!-- Precio -->
        <div class="price-section">
          <span class="product-price text-2xl font-medium text-gray-900 font-poppins">
            ${{ product.price }}
          </span>
        </div>
        
        <!-- Botones de acción -->
        <div class="product-buttons flex gap-2 flex-shrink-0">
          <button 
            @click.stop="$emit('navigate-to-product', product.id)"
            class="btn-buy text-white px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 font-poppins hover:opacity-90"
            style="background-color: #DA9DFF;">
            {{ $t('products.product.buyNow') || 'Buy now' }}
          </button>
          <button 
            @click.stop="handleAddToCart"
            :disabled="product.stock_status === 'outofstock' || cartStore.isUpdating"
            class="btn-cart text-white px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-poppins hover:opacity-90"
            style="background-color: #DA9DFF;">
            {{ cartStore.isUpdating ? ($t('products.product.adding') || 'Adding...') : ($t('products.product.addToCart') || 'Add to cart') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCartStore } from '@/stores/modules/cartStore.js'

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
  }
})

// Emits
const emit = defineEmits([
  'navigate-to-product',
  'add-to-cart',
  'toggle-wishlist',
  'toggle-list'
])

// i18n setup
const { t } = useI18n()

// Cart store
const cartStore = useCartStore()

// Methods
const handleToggleWishlist = () => {
  emit('toggle-wishlist', props.product.id)
}

const handleToggleList = () => {
  emit('toggle-list', props.product.id)
}

const handleAddToCart = async () => {
  try {
    const result = await cartStore.addToCart(props.product.id, 1, {
      name: props.product.name,
      price: parseFloat(props.product.price),
      image: props.product.images && props.product.images.length > 0 ? props.product.images[0].src : null,
      stock_status: props.product.stock_status
    })
    
    if (result.success) {
      // Emitir evento para notificar al componente padre si es necesario
      emit('add-to-cart', props.product)
    }
  } catch (error) {
    console.error('Error adding product to cart:', error)
  }
}
</script>

<style scoped>
/* Product Cards */
.product-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.product-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
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
  line-height: 1.5;
  letter-spacing: -0.01em;
}

.product-price {
  font-weight: 500;
  letter-spacing: -0.02em;
}

.btn-buy,
.btn-cart {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.02em;
  position: relative;
  overflow: hidden;
}

.btn-buy::before,
.btn-cart::before {
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
.btn-cart:hover::before {
  width: 300px;
  height: 300px;
}

.btn-buy:hover,
.btn-cart:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(192, 132, 252, 0.5);
}

.btn-buy:active,
.btn-cart:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 768px) {
  .product-buttons {
    flex-direction: column;
    width: 100%;
    gap: 0.5rem;
  }
  
  .product-buttons button {
    width: 100%;
    text-align: center;
  }
}
</style>
