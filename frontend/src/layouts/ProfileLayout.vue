<template>
  <div class="profile-layout">
    <!-- Background Image -->
    <div 
      class="absolute inset-0 z-0"
      :style="{ 
        backgroundImage: `url(${backgroundImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }"
    ></div>

    <!-- Gradient Overlay -->
    <div class="absolute inset-0 z-0 bg-gradient-to-br from-brand-pink-lighter/30 via-brand-purple-light/20 to-brand-blue-light/30"></div>

    <!-- Language Selector -->
    <LanguageSelector position="fixed" size="normal" theme="light" />

    <!-- Content Panel -->
    <div class="relative z-10 h-screen overflow-hidden flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div class="w-full h-full max-w-[1400px] max-h-[700px]">
        <!-- Main Panel with Sidebar and Content -->
        <div class="bg-white/40 backdrop-blur-lg rounded-2xl shadow-2xl h-full flex overflow-hidden">
          <!-- Sidebar Component -->
          <ProfileSidebar />

          <!-- Main Content Area (router-view) -->
          <main class="flex-1 overflow-y-auto">
            <router-view />
          </main>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ProfileSidebar from '@/components/profile/ProfileSidebar.vue'
import LanguageSelector from '@/components/shared/LanguageSelector.vue'
import backgroundImage from '@/assets/backgrounds/background_1.png'

onMounted(() => {
  console.log('🎨 ProfileLayout mounted!')
  console.log('Background image:', backgroundImage)
})
</script>

<style scoped>
.profile-layout {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'Comfortaa', cursive;
}
</style>

