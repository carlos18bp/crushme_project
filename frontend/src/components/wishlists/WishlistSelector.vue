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
      
      <!-- Error -->
      <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-sm text-red-800">{{ error }}</p>
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

// Watch for show prop to load wishlists
watch(() => props.show, async (newValue) => {
  if (newValue) {
    error.value = null
    await wishlistStore.fetchWishlists()
  }
})

const selectWishlist = async (wishlistId) => {
  if (isAdding.value) return
  
  isAdding.value = true
  selectedWishlistId.value = wishlistId
  error.value = null
  
  try {
    const result = await wishlistStore.addWooCommerceProductToWishlist(
      wishlistId,
      props.productId,
      '', // notes
      'medium' // priority
    )
    
    if (result.success) {
      emit('added', wishlistId)
      emit('close')
    } else {
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


