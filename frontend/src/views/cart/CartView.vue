<template>
  <div class="min-h-screen bg-gray-50 pt-20">
    <div class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-comfortaa font-bold text-gray-900">
          {{ $t('cart.shoppingCart') || 'Carrito de Compras' }}
        </h1>
        <p class="mt-2 font-poppins text-sm text-gray-600">
          {{ cartStore.totalItems }} {{ cartStore.totalItems === 1 ? 'producto' : 'productos' }} en tu carrito
        </p>
      </div>

      <!-- Empty cart -->
      <div v-if="cartStore.isEmpty" class="bg-white rounded-xl shadow-sm p-12 text-center">
        <div class="text-gray-400 mb-6">
          <svg class="mx-auto h-24 w-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l-1 12H6L5 9z" />
          </svg>
        </div>
        <h2 class="text-2xl font-comfortaa font-semibold text-gray-900 mb-3">
          {{ $t('cart.emptyCart') || 'Tu carrito está vacío' }}
        </h2>
        <p class="font-poppins text-gray-600 mb-8">
          {{ $t('cart.startShopping') || '¡Comienza a agregar productos!' }}
        </p>
        <router-link
          :to="{ name: `Products-${i18nStore.locale}` }"
          class="inline-flex items-center justify-center rounded-full bg-gray-900 px-8 py-3 font-poppins text-base font-semibold text-white hover:bg-gray-800 transition-colors">
          {{ $t('cart.continueShopping') || 'Continuar Comprando' }}
        </router-link>
      </div>

      <!-- Cart with items -->
      <div v-else class="lg:grid lg:grid-cols-12 lg:gap-x-8">
        <!-- Cart items -->
        <div class="lg:col-span-7">
          <div class="bg-white rounded-xl shadow-sm overflow-hidden">
            <ul role="list" class="divide-y divide-gray-200">
              <li v-for="item in cartStore.items" :key="item.id" class="p-6 hover:bg-gray-50 transition-colors">
                <div class="flex items-start space-x-4">
                  <!-- Product image -->
                  <div class="h-24 w-24 shrink-0 overflow-hidden rounded-lg border border-gray-200">
                    <img 
                      :src="item.image || 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop&crop=center'" 
                      :alt="item.name || 'Product image'" 
                      class="h-full w-full object-cover" />
                  </div>

                  <!-- Product details -->
                  <div class="flex-1 min-w-0">
                    <div class="flex justify-between">
                      <h3 class="font-comfortaa font-semibold text-gray-900 text-lg">
                        {{ item.name || 'Product' }}
                      </h3>
                    </div>
                    
                    <!-- Price per unit -->
                    <p class="mt-1 font-poppins text-sm text-gray-600">
                      Precio unitario: ${{ item.price?.toFixed(2) || '0.00' }}
                    </p>

                    <!-- Attributes if any -->
                    <div v-if="item.color || item.size" class="mt-2 flex flex-wrap gap-2">
                      <span v-if="item.color" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-poppins bg-gray-100 text-gray-800">
                        Color: {{ item.color }}
                      </span>
                      <span v-if="item.size" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-poppins bg-gray-100 text-gray-800">
                        Talla: {{ item.size }}
                      </span>
                    </div>

                    <!-- Quantity controls and subtotal -->
                    <div class="mt-4 flex items-center justify-between">
                      <!-- Quantity controls -->
                      <div class="flex items-center space-x-2">
                        <button 
                          @click="updateQuantity(item.id, item.quantity - 1)"
                          :disabled="item.quantity <= 1 || cartStore.isUpdating"
                          class="w-8 h-8 rounded-full border-2 border-gray-300 flex items-center justify-center hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 hover:text-gray-900 transition-colors">
                          <span class="text-lg font-medium">-</span>
                        </button>
                        <span class="font-poppins text-base text-gray-900 min-w-[3rem] text-center font-semibold">
                          {{ item.quantity }}
                        </span>
                        <button 
                          @click="updateQuantity(item.id, item.quantity + 1)"
                          :disabled="cartStore.isUpdating"
                          class="w-8 h-8 rounded-full border-2 border-gray-300 flex items-center justify-center hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 hover:text-gray-900 transition-colors">
                          <span class="text-lg font-medium">+</span>
                        </button>
                      </div>

                      <!-- Subtotal and remove -->
                      <div class="flex items-center space-x-4">
                        <p class="font-poppins text-lg font-semibold text-gray-900">
                          ${{ (item.price * item.quantity).toFixed(2) }}
                        </p>
                        <button 
                          type="button" 
                          @click="removeItem(item.id)"
                          :disabled="cartStore.isUpdating"
                          class="font-poppins text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                          {{ cartStore.isUpdating ? 'Eliminando...' : 'Eliminar' }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Order summary -->
        <div class="lg:col-span-5 mt-6 lg:mt-0">
          <div class="bg-white rounded-xl shadow-sm p-6 sticky top-6">
            <h2 class="text-xl font-comfortaa font-semibold text-gray-900 mb-6">
              Resumen del Pedido
            </h2>

            <!-- Summary details -->
            <div class="space-y-4 mb-6">
              <div class="flex justify-between font-poppins text-base text-gray-700">
                <span>Subtotal ({{ cartStore.totalItems }} productos)</span>
                <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between font-poppins text-base text-gray-700">
                <span>Envío</span>
                <span>$0.00</span>
              </div>
              <div class="border-t border-gray-200 pt-4">
                <div class="flex justify-between font-poppins text-xl font-bold text-gray-900">
                  <span>Total</span>
                  <span>${{ cartStore.totalPrice.toFixed(2) }}</span>
                </div>
              </div>
            </div>

            <!-- Checkout button -->
            <button
              @click="handleCheckout"
              :disabled="cartStore.isEmpty || cartStore.isUpdating"
              class="w-full flex items-center justify-center rounded-full bg-gray-900 px-6 py-4 font-poppins text-base font-semibold text-white shadow-sm hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4">
              Proceder al Pago
            </button>

            <!-- Continue shopping link -->
            <router-link
              :to="{ name: `Products-${i18nStore.locale}` }"
              class="block text-center font-poppins text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors">
              ← Continuar Comprando
            </router-link>

            <!-- Security badges -->
            <div class="mt-6 pt-6 border-t border-gray-200">
              <div class="flex items-center justify-center space-x-4 text-xs text-gray-500">
                <div class="flex items-center">
                  <svg class="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                  <span>Pago seguro</span>
                </div>
                <div class="flex items-center">
                  <svg class="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
                    <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z" />
                  </svg>
                  <span>Envío rápido</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/modules/cartStore.js'
import { useI18nStore } from '@/stores/modules/i18nStore.js'

// Composables
const router = useRouter()
const cartStore = useCartStore()
const i18nStore = useI18nStore()

// Methods
const updateQuantity = (itemId, newQuantity) => {
  if (newQuantity <= 0) {
    removeItem(itemId)
    return
  }
  
  try {
    cartStore.updateCartItem(itemId, newQuantity)
  } catch (error) {
    console.error('Error updating cart item:', error)
  }
}

const removeItem = (itemId) => {
  try {
    cartStore.removeFromCart(itemId)
  } catch (error) {
    console.error('Error removing cart item:', error)
  }
}

const handleCheckout = () => {
  try {
    console.log('🛒 [CHECKOUT] Iniciando checkout...')
    console.log('🛒 [CHECKOUT] Carrito vacío?', cartStore.isEmpty)
    console.log('🛒 [CHECKOUT] Items en carrito:', cartStore.items)
    console.log('🛒 [CHECKOUT] Locale actual:', i18nStore.locale)
    
    if (!cartStore.isEmpty) {
      console.log('🛒 [CHECKOUT] Redirigiendo a checkout...')
      router.push({ name: `Checkout-${i18nStore.locale}` })
    } else {
      console.log('❌ [CHECKOUT] Carrito vacío, no se puede proceder')
    }
  } catch (error) {
    console.error('❌ [CHECKOUT] Error durante checkout:', error)
    alert('Error al procesar el checkout. Por favor intenta de nuevo.')
  }
}

// Initialize cart on mount
onMounted(() => {
  console.log('🛒 Inicializando carrito en CartView...')
  cartStore.initializeCart()
  console.log('📦 Items en carrito:', cartStore.items)
})
</script>

<style scoped>
/* Smooth transitions */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Hover effects for cart items */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}
</style>
