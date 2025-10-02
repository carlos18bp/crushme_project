<template>
  <div class="profile-view">
    <!-- Sidebar Component -->
    <ProfileSidebar />

    <!-- Main Content Area -->
    <main class="lg:pl-80">
      <div class="px-4 py-10 sm:px-6 lg:px-8">
        <!-- Content will go here -->
        <h1 class="text-2xl font-semibold text-gray-900 font-comfortaa">Welcome to your Profile</h1>
        <p class="mt-2 text-gray-600 font-comfortaa">Your profile content will be displayed here</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import ProfileSidebar from '@/components/profile/ProfileSidebar.vue'
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
  background-color: #FAF5F5; /* Fondo rosado/beige claro suave */
  font-family: 'Comfortaa', cursive;
}

.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>
