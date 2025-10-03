<template>
  <div 
    class="rounded-2xl p-6 flex items-center justify-between border-2 border-gray-900"
    style="background-color: #FFDDDD;"
  >
    <div class="flex items-center gap-6">
      <p class="text-7xl font-bold text-gray-900 font-comfortaa">{{ $t('profileDashboard.gifts.number') }}</p>
      <div>
        <p class="text-xl text-gray-900 font-comfortaa">{{ $t('profileDashboard.gifts.title') }}</p>
        <p class="text-xl text-gray-900 font-comfortaa">{{ $t('profileDashboard.gifts.subtitle') }}</p>
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
import giftIcon from '@/assets/profile/icons/gift.png'
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

