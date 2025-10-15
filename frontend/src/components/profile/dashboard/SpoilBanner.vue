<template>
  <div 
    class="rounded-2xl p-6 relative overflow-hidden border-2 border-gray-900"
    style="background-color: rgba(66, 142, 255, 0.2);"
  >
    <div class="relative z-10">
      <p class="text-gray-600 font-comfortaa text-lg mb-4">
        {{ $t('profileDashboard.banner.title') }}
      </p>
      <button
        @click="handleShopRedirect"
        class="bg-brand-pink-medium hover:bg-brand-pink-dark text-white font-comfortaa px-6 py-2.5 rounded-full transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer"
      >
        {{ $t('profileDashboard.banner.button') }}
      </button>
    </div>
    
    <!-- Banner Image -->
    <div class="absolute bottom-0 right-0 h-full flex items-end">
      <img 
        :src="bannerImage" 
        alt="Products" 
        class="h-[85%] w-auto object-contain"
      />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import bannerImage from '@/assets/profile/banner/banner.png'

const router = useRouter()
const i18nStore = useI18nStore()

const handleShopRedirect = () => {
  router.push({ name: `Products-${i18nStore.locale}` })
}
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

