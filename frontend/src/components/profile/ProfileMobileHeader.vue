<template>
  <div class="lg:hidden flex items-center justify-between bg-white/80 backdrop-blur-md px-3 py-3 shadow-sm border-b border-brand-pink-light/30">
    <button 
      type="button" 
      class="p-2 text-brand-pink-dark hover:bg-brand-pink-lighter rounded-lg transition-colors" 
      @click="$emit('open-sidebar')"
    >
      <span class="sr-only">Open menu</span>
      <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
    
    <div class="flex-1 text-center">
      <h2 class="text-sm font-semibold text-brand-dark font-comfortaa">{{ title }}</h2>
    </div>
    
    <button 
      @click="router.push({ name: `MyProfile-${i18nStore.locale}` })"
      class="p-1"
    >
      <span class="sr-only">Your profile</span>
      <div class="h-8 w-8 rounded-full bg-brand-pink-lighter flex items-center justify-center overflow-hidden ring-2 ring-brand-pink-light">
        <img
          v-if="userProfileImage"
          class="h-8 w-8 rounded-full object-cover"
          :src="userProfileImage"
          alt="User avatar"
        />
        <UserIcon
          v-else
          class="h-5 w-5 text-brand-pink-medium"
        />
      </div>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { UserIcon } from '@heroicons/vue/24/outline'

defineProps({
  title: {
    type: String,
    default: 'Profile'
  }
})

defineEmits(['open-sidebar'])

const router = useRouter()
const i18nStore = useI18nStore()
const authStore = useAuthStore()

const userProfileImage = computed(() => {
  return authStore.user?.profile_picture_url || null
})
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>
