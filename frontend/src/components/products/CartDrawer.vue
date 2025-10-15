<template>
  <div>

    <!-- Drawer del carrito -->
    <TransitionRoot as="template" :show="open">
      <Dialog class="relative z-[1100]" @close="open = false">
        <TransitionChild 
          as="template" 
          enter="ease-in-out duration-500" 
          enter-from="opacity-0" 
          enter-to="opacity-100" 
          leave="ease-in-out duration-500" 
          leave-from="opacity-100" 
          leave-to="opacity-0">
          <div class="fixed inset-0 bg-gray-500/75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-hidden">
          <div class="absolute inset-0 overflow-hidden">
            <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10 sm:pl-16">
              <TransitionChild 
                as="template" 
                enter="transform transition ease-in-out duration-500 sm:duration-700" 
                enter-from="translate-x-full" 
                enter-to="translate-x-0" 
                leave="transform transition ease-in-out duration-500 sm:duration-700" 
                leave-from="translate-x-0" 
                leave-to="translate-x-full">
                <DialogPanel class="pointer-events-auto w-screen max-w-md">
                  <div class="flex h-full flex-col overflow-y-auto bg-gray-50 shadow-xl">
                    
                    <!-- Header del carrito -->
                    <div class="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
                      <div class="flex items-start justify-between border-b border-gray-200 pb-4">
                        <DialogTitle class="text-2xl font-comfortaa font-semibold text-gray-900">
                          {{ $t('cart.shoppingCart') }}
                        </DialogTitle>
                        <div class="ml-3 flex h-7 items-center">
                          <button 
                            type="button" 
                            class="relative -m-2 p-2 text-gray-600 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100" 
                            @click="open = false">
                            <span class="absolute -inset-0.5" />
                            <span class="sr-only">{{ $t('cart.closePanel') }}</span>
                            <XMarkIcon class="size-6" aria-hidden="true" />
                          </button>
                        </div>
                      </div>

                      <!-- Empty cart -->
                      <div v-if="cartStore.isEmpty" class="mt-12 text-center py-8">
                        <div class="text-gray-400 mb-6">
                          <svg class="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l-1 12H6L5 9z" />
                          </svg>
                        </div>
                        <h3 class="text-xl font-comfortaa font-semibold text-gray-900 mb-2">{{ $t('cart.emptyCart') }}</h3>
                        <p class="text-sm font-poppins text-gray-500">{{ $t('cart.startShopping') }}</p>
                      </div>

                      <!-- Cart items -->
                      <div v-else class="mt-6">
                        <div class="flow-root">
                          <ul role="list" class="space-y-4">
                            <li v-for="item in cartStore.items" :key="item.id" class="flex bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                              <!-- Product image -->
                              <div class="size-20 shrink-0 overflow-hidden rounded-lg border border-gray-200">
                                <img 
                                  :src="item.image || 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=300&h=300&fit=crop&crop=center'" 
                                  :alt="item.name || $t('cart.labels.product')" 
                                  class="size-full object-cover" />
                              </div>

                              <!-- Product details -->
                              <div class="ml-4 flex flex-1 flex-col justify-between">
                                <div>
                                  <div class="flex justify-between">
                                    <h3 class="font-comfortaa font-medium text-gray-900 text-sm leading-tight">
                                      {{ item.name || $t('cart.labels.product') }}
                                    </h3>
                                    <p class="ml-4 font-poppins font-semibold text-gray-900">${{ (item.price * item.quantity).toFixed(2) }}</p>
                                  </div>
                                  <p class="mt-1 text-xs font-poppins text-gray-500">
                                    ${{ item.price?.toFixed(2) || '0.00' }}
                                  </p>
                                </div>
                                
                                <div class="flex items-center justify-between mt-3">
                                  <!-- Quantity controls -->
                                  <div class="flex items-center space-x-1">
                                    <button 
                                      @click="updateQuantity(item.id, item.quantity - 1)"
                                      :disabled="item.quantity <= 1 || cartStore.isUpdating"
                                      class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-gray-600 hover:text-gray-900 transition-colors">
                                      <span class="text-sm font-medium">-</span>
                                    </button>
                                    <span class="font-poppins text-sm text-gray-900 min-w-[2rem] text-center font-medium">
                                      {{ item.quantity }}
                                    </span>
                                    <button 
                                      @click="updateQuantity(item.id, item.quantity + 1)"
                                      :disabled="cartStore.isUpdating"
                                      class="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-gray-600 hover:text-gray-900 transition-colors">
                                      <span class="text-sm font-medium">+</span>
                                    </button>
                                  </div>

                                  <!-- Remove button -->
                                  <button
                                    type="button"
                                    @click="removeItem(item.id)"
                                    :disabled="cartStore.isUpdating"
                                    class="font-poppins text-xs font-medium text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                                    {{ cartStore.isUpdating ? $t('cart.removing') : $t('cart.remove') }}
                                  </button>
                                </div>
                              </div>
                            </li>
                          </ul>
                        </div>
                      </div>
                    </div>

                    <!-- Footer con totales y checkout -->
                    <div v-if="!cartStore.isEmpty" class="border-t border-gray-200 bg-white px-6 py-6">
                      <!-- Subtotal -->
                      <div class="flex justify-between font-poppins text-lg font-medium text-gray-900 mb-1">
                        <p>{{ $t('cart.subtotal') }}</p>
                        <p>${{ cartStore.totalPrice.toFixed(2) }}</p>
                      </div>
                      
                      <!-- Shipping -->
                      <div class="flex justify-between font-poppins text-lg font-medium text-gray-900 mb-3">
                        <p>{{ $t('cart.shipping') }}</p>
                        <p>{{ $t('cart.summary.shippingCalculated') }}</p>
                      </div>
                      
                      <!-- Total -->
                      <div class="flex justify-between font-poppins text-xl font-semibold text-gray-900 border-t border-gray-200 pt-3 mb-4">
                        <p>{{ $t('cart.total') }}</p>
                        <p>${{ cartStore.totalPrice.toFixed(2) }}</p>
                      </div>

                      <!-- Checkout button -->
                      <div class="mb-4">
                        <button
                          @click="handleCheckout"
                          :disabled="cartStore.isEmpty || cartStore.isUpdating"
                          class="flex w-full items-center justify-center rounded-full bg-gray-900 px-6 py-4 font-poppins text-base font-semibold text-white shadow-sm hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                          {{ $t('cart.checkoutButton') }}
                        </button>
                      </div>

                      <!-- Continue shopping -->
                      <div class="flex justify-center text-center">
                        <p class="font-poppins text-sm text-gray-500">
                          {{ $t('cart.or') }}{{ ' ' }}
                          <button
                            type="button"
                            class="font-medium text-gray-900 hover:text-gray-700 transition-colors"
                            @click="open = false">
                            {{ $t('cart.continueShopping') }}
                            <span aria-hidden="true"> &rarr;</span>
                          </button>
                        </p>
                      </div>
                    </div>
                  </div>
                </DialogPanel>
              </TransitionChild>
            </div>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

// Composables
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useCartStore } from '@/stores/modules/cartStore.js'
import { useI18nStore } from '@/stores/modules/i18nStore'

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['close', 'checkout'])

// Composables
const { t } = useI18n()
const router = useRouter()
const cartStore = useCartStore()
const i18nStore = useI18nStore()

// State
const open = ref(props.isOpen)

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

const clearCart = () => {
  if (confirm(t('cart.confirmations.clearCart'))) {
    try {
      cartStore.clearCart()
    } catch (error) {
      console.error('Error clearing cart:', error)
    }
  }
}

const handleCheckout = () => {
  try {
    console.log('🛒 [CART DRAWER] Iniciando checkout...')
    console.log('🛒 [CART DRAWER] Carrito vacío?', cartStore.isEmpty)
    console.log('🛒 [CART DRAWER] Items en carrito:', cartStore.items)
    console.log('🛒 [CART DRAWER] Locale actual:', i18nStore.locale)
    
    if (!cartStore.isEmpty) {
      console.log('🛒 [CART DRAWER] Redirigiendo a checkout...')
      
      // Cerrar el drawer
      open.value = false
      
      // Redirigir al checkout
      router.push({ name: `Checkout-${i18nStore.locale}` })
      
      console.log('✅ [CART DRAWER] Redirección completada')
    } else {
      console.log('❌ [CART DRAWER] Carrito vacío, no se puede proceder')
    }
  } catch (error) {
    console.error('❌ [CART DRAWER] Error durante checkout:', error)
    alert(t('cart.messages.generalError'))
  }
}

// Watch props changes
const updateOpen = (newValue) => {
  open.value = newValue
}

// Initialize cart on mount
onMounted(() => {
  cartStore.initializeCart()
})

// Expose methods for parent components
defineExpose({
  openCart: () => { open.value = true },
  closeCart: () => { open.value = false },
  toggleCart: () => { open.value = !open.value }
})
</script>

<style scoped>
/* Custom scrollbar for cart items */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Smooth transitions for quantity buttons */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>
