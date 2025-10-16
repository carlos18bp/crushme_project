<template>
  <div class="profile-dashboard">
    <div class="px-3 sm:px-4 md:px-6 py-4 sm:py-6 md:py-8 lg:px-8">
      <!-- Welcome Header -->
      <WelcomeHeader />

      <!-- Cards Grid -->
      <div class="grid grid-cols-2 md:grid-cols-2 gap-3 sm:gap-4 md:gap-6 mb-4 sm:mb-6 md:mb-8">
        <!-- Ready to spoil banner -->
        <SpoilBanner />

        <!-- Gifts sent card -->
        <GiftsCard />
      </div>

      <!-- Quick Actions -->
      <QuickActions />

      <!-- Feed -->
      <Feed />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import WelcomeHeader from '@/components/profile/dashboard/WelcomeHeader.vue'
import SpoilBanner from '@/components/profile/dashboard/SpoilBanner.vue'
import GiftsCard from '@/components/profile/dashboard/GiftsCard.vue'
import QuickActions from '@/components/profile/dashboard/QuickActions.vue'
import Feed from '@/components/profile/dashboard/Feed.vue'

onMounted(() => {
  console.log('✅ ProfileDashboard mounted!')
  console.log('Components loaded:', { WelcomeHeader, SpoilBanner, GiftsCard, QuickActions, Feed })
})
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

