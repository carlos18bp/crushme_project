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

    <!-- Content Panel -->
    <div class="relative z-10 h-screen overflow-hidden flex items-center justify-center p-0 sm:p-4 md:p-6 lg:p-8">
      <div class="w-full h-full sm:max-w-[1400px] sm:max-h-[700px]">
        <!-- Main Panel with Sidebar and Content -->
        <div class="bg-white/20 backdrop-blur-lg rounded-none sm:rounded-2xl shadow-2xl h-full flex overflow-hidden">
          <!-- Sidebar Component -->
          <ProfileSidebar ref="sidebarRef" />

          <!-- Main Content Area (router-view) with margin for fixed sidebar -->
          <main class="flex-1 overflow-y-auto flex flex-col lg:ml-80">
            <!-- Mobile Header -->
            <ProfileMobileHeader 
              :title="$t('profileSidebar.profile')" 
              @open-sidebar="openSidebar"
            />
            
            <!-- Content -->
            <div class="flex-1 overflow-y-auto">
              <router-view />
            </div>
          </main>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProfileSidebar from '@/components/profile/ProfileSidebar.vue'
import ProfileMobileHeader from '@/components/profile/ProfileMobileHeader.vue'
import backgroundImage from '@/assets/backgrounds/background_1.png'

const sidebarRef = ref(null)

const openSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.openSidebar()
  }
}

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

