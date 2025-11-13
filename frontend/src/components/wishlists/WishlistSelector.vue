<template>
  <div v-if="show" class="fixed inset-0 bg-white/40 backdrop-blur-md flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-xl">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Add to Wishlist</h2>
      
      <!-- Loading -->
      <div v-if="wishlistStore.isLoading" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-pink-medium"></div>
      </div>
      
      <!-- Wishlists List -->
      <div v-else-if="wishlistStore.wishlists.length > 0" class="space-y-2 max-h-96 overflow-y-auto">
        <button
          v-for="wishlist in wishlistStore.wishlists"
          :key="wishlist.id"
          @click="selectWishlist(wishlist.id)"
          :disabled="isAdding"
          class="w-full text-left p-3 border-2 border-gray-200 rounded-lg hover:border-brand-pink-medium hover:bg-brand-pink-medium/5 transition-all disabled:opacity-50"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <p class="font-semibold text-gray-900">{{ wishlist.name }}</p>
              <p class="text-xs text-gray-500">{{ wishlist.total_items }} items</p>
            </div>
            <svg v-if="isAdding && selectedWishlistId === wishlist.id" class="animate-spin h-5 w-5 text-brand-pink-medium" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </button>
      </div>
      
      <!-- Empty State -->
      <div v-else class="text-center py-8">
        <p class="text-gray-500 mb-4">You don't have any wishlists yet</p>
        <button
          @click="$emit('create-wishlist')"
          class="px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-lg hover:bg-brand-pink-medium hover:text-white transition-colors"
        >
          Create Wishlist
        </button>
      </div>
      
      <!-- Success Message -->
      <div v-if="successMessage" class="mt-4 p-4 bg-green-50 border-2 border-green-200 rounded-xl animate-fade-in">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-green-800">{{ successMessage }}</p>
          </div>
        </div>
      </div>
      
      <!-- Error -->
      <div v-if="error" class="mt-4 p-4 bg-pink-50 border-2 border-pink-200 rounded-xl animate-fade-in">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <svg class="w-5 h-5 text-pink-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-pink-800">{{ error }}</p>
          </div>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex gap-3 mt-6">
        <button
          @click="$emit('close')"
          :disabled="isAdding"
          class="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 bg-white rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useWishlistStore } from '@/stores/modules/wishlistStore'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  productId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['close', 'added', 'create-wishlist'])

const wishlistStore = useWishlistStore()
const isAdding = ref(false)
const selectedWishlistId = ref(null)
const error = ref(null)
const successMessage = ref(null)

// Watch for show prop to load wishlists
watch(() => props.show, async (newValue, oldValue) => {
  // Solo cargar si cambió de false a true (evitar loops)
  if (newValue && !oldValue) {
    error.value = null
    successMessage.value = null
    selectedWishlistId.value = null
    isAdding.value = false
    await wishlistStore.fetchWishlists()
  }
  // Limpiar estado cuando se cierra
  if (!newValue && oldValue) {
    error.value = null
    successMessage.value = null
    selectedWishlistId.value = null
    isAdding.value = false
  }
})

const selectWishlist = async (wishlistId) => {
  if (isAdding.value) return
  
  isAdding.value = true
  selectedWishlistId.value = wishlistId
  error.value = null
  successMessage.value = null
  
  try {
    const result = await wishlistStore.addWooCommerceProductToWishlist(
      wishlistId,
      props.productId,
      '', // notes
      'medium' // priority
    )
    
    if (result.success) {
      // Mostrar mensaje de éxito
      successMessage.value = 'Product added to wishlist!'
      emit('added', wishlistId)
      
      // Delay para que el usuario vea el éxito antes de cerrar
      setTimeout(() => {
        emit('close')
      }, 800)
    } else {
      // Mostrar error de forma más amigable
      error.value = result.error || 'Failed to add product to wishlist'
    }
  } catch (err) {
    error.value = 'An error occurred while adding the product'
    console.error('Error adding to wishlist:', err)
  } finally {
    isAdding.value = false
    selectedWishlistId.value = null
  }
}
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
