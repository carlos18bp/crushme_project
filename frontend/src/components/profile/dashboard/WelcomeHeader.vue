<template>
  <div class="mb-4 md:mb-6">
    <p
      v-if="profileStore.profileError"
      role="alert"
      data-testid="profile-dashboard-error"
      class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
    >
      {{ profileStore.profileError }}
    </p>
    <h1 v-else class="text-lg sm:text-xl md:text-2xl lg:text-3xl font-medium text-gray-900 font-comfortaa leading-tight">
      {{ welcomeMessage }}
    </h1>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProfileStore } from '@/stores/modules/profileStore'

const { t } = useI18n()
const profileStore = useProfileStore()

// Load profile if not loaded
onMounted(async () => {
  if (!profileStore.hasProfile) {
    await profileStore.fetchProfile()
  }
})

// Get username or default
const username = computed(() => {
  return profileStore.userInfo?.username || 'User'
})

// Get welcome message with username interpolation
const welcomeMessage = computed(() => {
  return t('profileDashboard.welcome', { username: username.value })
})
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>
