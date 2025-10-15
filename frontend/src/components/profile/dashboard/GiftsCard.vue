<template>
  <div 
    class="rounded-2xl p-6 flex items-center justify-between border-2 border-gray-900"
    style="background-color: #FFDDDD;"
  >
    <div class="flex items-center gap-6">
      <p class="text-7xl font-bold text-gray-900 font-comfortaa">
        {{ isLoading ? '...' : giftsCount }}
      </p>
      <div>
        <p class="text-xl text-gray-900 font-comfortaa">{{ $t('profile.dashboard.gifts.title') }}</p>
        <p class="text-xl text-gray-900 font-comfortaa">{{ $t('profile.dashboard.gifts.subtitle') }}</p>
      </div>
    </div>
    
    <!-- Gift Icon -->
    <div class="flex-shrink-0">
      <img 
        :src="giftIcon" 
        alt="Gift" 
        class="w-20 h-20 object-contain"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useAuthStore } from '@/stores/modules/authStore'
import { get_request } from '@/services/request_http.js'
import giftIcon from '@/assets/profile/icons/gift.png'

const authStore = useAuthStore()

// Local state for gifts data
const gifts = ref([])
const isLoading = ref(false)

// Computed property for gifts count (received gifts)
const giftsCount = computed(() => {
  return gifts.value.length
})

// Load gifts when component is mounted
onMounted(async () => {
  if (authStore.isLoggedIn) {
    await loadGifts()
  }
})

const loadGifts = async () => {
  isLoading.value = true

  try {
    // Get received gifts (similar to MyGifts.vue)
    const response = await get_request('orders/gifts/?type=received')

    if (response.data) {
      gifts.value = response.data.orders || []
    } else {
      gifts.value = []
    }
  } catch (error) {
    console.error('🎁 [GiftsCard] Error loading gifts:', error)
    gifts.value = []
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

