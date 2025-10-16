<template>
  <div 
    class="rounded-lg md:rounded-xl p-3 md:p-5 flex items-center border-2 border-gray-900 min-h-[130px] sm:min-h-[150px] md:min-h-[180px]"
    style="background-color: #FFDDDD;"
  >
    <div class="flex items-center gap-2 sm:gap-3 md:gap-4">
      <p class="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 font-comfortaa">
        {{ isLoading ? '...' : giftsCount }}
      </p>
      <div>
        <p class="text-xs sm:text-sm md:text-base lg:text-lg text-gray-900 font-comfortaa leading-tight">{{ $t('profileDashboard.gifts.title') }}</p>
        <p class="text-xs sm:text-sm md:text-base lg:text-lg text-gray-900 font-comfortaa leading-tight">{{ $t('profileDashboard.gifts.subtitle') }}</p>
      </div>
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
      // API returns array directly, not wrapped in 'orders' property
      gifts.value = Array.isArray(response.data) ? response.data : (response.data.orders || [])
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

