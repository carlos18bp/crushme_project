<template>
  <div 
    class="rounded-lg md:rounded-xl p-3 md:p-5 border-2 border-gray-900 min-h-[130px] sm:min-h-[150px] md:min-h-[180px] flex items-center"
    style="background-color: rgba(66, 142, 255, 0.2);"
  >
    <div class="w-full">
      <p class="text-gray-600 font-comfortaa text-xs sm:text-sm md:text-base lg:text-lg mb-2 sm:mb-3 md:mb-4 leading-tight">
        {{ $t('profileDashboard.banner.title') }}
      </p>
      <button
        @click="handleShopRedirect"
        class="bg-brand-pink-medium hover:bg-brand-pink-dark text-white font-comfortaa px-3 py-1.5 sm:px-4 sm:py-2 md:px-6 md:py-2.5 rounded-full transition-all duration-200 shadow-md hover:shadow-lg cursor-pointer text-xs sm:text-sm md:text-base"
      >
        {{ $t('profileDashboard.banner.button') }}
      </button>
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

