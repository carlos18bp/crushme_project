<template>
  <div class="mb-8">
    <h1 class="text-3xl font-medium text-gray-900 font-comfortaa">
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

