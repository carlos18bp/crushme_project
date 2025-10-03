<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <!-- Browse Diaries -->
    <router-link 
      :to="`/${i18nStore.locale}/diaries`"
      class="bg-white rounded-xl p-4 flex items-center gap-3 hover:shadow-lg transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-brand-blue-light"
    >
      <div class="flex-shrink-0">
        <img 
          :src="diarieIcon" 
          alt="Browse Diaries" 
          class="w-12 h-12 object-contain"
        />
      </div>
      <p class="text-sm font-poppins font-semibold text-gray-900">
        {{ $t('profileDashboard.quickActions.browseDiaries') }}
      </p>
    </router-link>

    <!-- Shop Trending Products -->
    <router-link 
      :to="`/${i18nStore.locale}/products`"
      class="bg-white rounded-xl p-4 flex items-center gap-3 hover:shadow-lg transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-brand-blue-light"
    >
      <div class="flex-shrink-0">
        <img 
          :src="cartIcon" 
          alt="Shop" 
          class="w-12 h-12 object-contain"
        />
      </div>
      <p class="text-sm font-poppins font-semibold text-gray-900">
        {{ $t('profileDashboard.quickActions.shopProducts') }}
      </p>
    </router-link>

    <!-- Create My Wishlist -->
    <router-link 
      :to="`/${i18nStore.locale}/wishlists`"
      class="bg-white rounded-xl p-4 flex items-center gap-3 hover:shadow-lg transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-brand-blue-light"
    >
      <div class="flex-shrink-0">
        <img 
          :src="wishlistIcon" 
          alt="Wishlist" 
          class="w-12 h-12 object-contain"
        />
      </div>
      <p class="text-sm font-poppins font-semibold text-gray-900">
        {{ $t('profileDashboard.quickActions.createWishlist') }}
      </p>
    </router-link>

    <!-- History -->
    <router-link 
      :to="{ name: `ProfileHistory-${i18nStore.locale}` }"
      class="bg-white rounded-xl p-4 flex items-center gap-3 hover:shadow-lg transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-brand-blue-light"
    >
      <div class="flex-shrink-0">
        <img 
          :src="historyIcon" 
          alt="History" 
          class="w-12 h-12 object-contain"
        />
      </div>
      <p class="text-sm font-poppins font-semibold text-gray-900">
        {{ $t('profileDashboard.quickActions.history') }}
      </p>
    </router-link>
  </div>
</template>

<script setup>
import { useI18nStore } from '@/stores/modules/i18nStore'
import diarieIcon from '@/assets/profile/icons/diarie.png'
import cartIcon from '@/assets/profile/icons/cart.png'
import wishlistIcon from '@/assets/profile/icons/wishlist.png'
import historyIcon from '@/assets/profile/icons/history.png'

const i18nStore = useI18nStore()
</script>

<style scoped>
.font-poppins {
  font-family: 'Poppins', sans-serif;
}
</style>

