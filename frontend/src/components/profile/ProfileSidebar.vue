<template>
  <div>
    <!-- Mobile sidebar overlay -->
    <TransitionRoot as="template" :show="sidebarOpen">
      <Dialog class="relative z-50 lg:hidden" @close="sidebarOpen = false">
        <TransitionChild 
          as="template" 
          enter="transition-opacity ease-linear duration-300" 
          enter-from="opacity-0" 
          enter-to="opacity-100" 
          leave="transition-opacity ease-linear duration-300" 
          leave-from="opacity-100" 
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-white/20 backdrop-blur-lg" />
        </TransitionChild>

        <div class="fixed inset-0 flex">
          <TransitionChild 
            as="template" 
            enter="transition ease-in-out duration-300 transform" 
            enter-from="-translate-x-full" 
            enter-to="translate-x-0" 
            leave="transition ease-in-out duration-300 transform" 
            leave-from="translate-x-0" 
            leave-to="-translate-x-full"
          >
            <DialogPanel class="relative mr-16 flex w-full max-w-xs flex-1">
              <TransitionChild 
                as="template" 
                enter="ease-in-out duration-300" 
                enter-from="opacity-0" 
                enter-to="opacity-100" 
                leave="ease-in-out duration-300" 
                leave-from="opacity-100" 
                leave-to="opacity-0"
              >
                <div class="absolute left-full top-0 flex w-16 justify-center pt-5">
                  <button type="button" class="-m-2.5 p-2.5" @click="sidebarOpen = false">
                    <span class="sr-only">Close sidebar</span>
                    <svg class="w-6 h-6 text-brand-pink-medium" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </TransitionChild>

              <!-- Sidebar component for mobile -->
              <div class="flex grow flex-col gap-y-5 overflow-y-auto px-4 pb-4 bg-white">
                <!-- User Profile Section -->
                <div class="flex items-center gap-3 pt-6 pb-4 border-b border-gray-200">
                  <div class="h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden ring-2 ring-brand-pink-light">
                    <img
                      v-if="userProfileImage"
                      class="h-12 w-12 rounded-full object-cover"
                      :src="userProfileImage"
                      alt="User avatar"
                    />
                    <UserIcon
                      v-else
                      class="h-8 w-8 text-brand-pink-medium"
                    />
                  </div>
                  <span class="text-base font-medium text-brand-dark font-comfortaa">@{{ authStore.username }}</span>
                </div>

                <!-- Main Actions -->
                <nav class="flex flex-1 flex-col">
                  <div class="text-xs font-semibold text-gray-500 mb-3 font-comfortaa uppercase tracking-wide">{{ $t('profileSidebar.mainActions') }}</div>
                  <ul role="list" class="flex flex-1 flex-col gap-y-1.5">
                        <li v-for="item in navigation" :key="item.name">
                          <button 
                            v-if="item.name === $t('profileSidebar.logout')"
                            @click="handleLogout"
                            :class="[
                              'text-gray-700 hover:bg-gray-50 hover:text-brand-pink-dark',
                              'group flex gap-x-3 rounded-lg p-3 text-sm font-medium font-comfortaa transition-all duration-200 w-full text-left'
                            ]"
                          >
                            <component 
                              :is="item.icon" 
                              :class="[
                                'text-gray-400 group-hover:text-brand-pink-dark',
                                'h-5 w-5 shrink-0'
                              ]" 
                              aria-hidden="true" 
                            />
                            {{ item.name }}
                          </button>
                          <router-link 
                            v-else
                            :to="item.to"
                            @click="sidebarOpen = false"
                            :class="[
                              item.current 
                                ? 'bg-brand-pink-lighter text-brand-pink-dark' 
                                : 'text-gray-700 hover:bg-gray-50 hover:text-brand-pink-dark',
                              'group flex gap-x-3 rounded-lg p-3 text-sm font-medium font-comfortaa transition-all duration-200'
                            ]"
                          >
                            <component 
                              :is="item.icon" 
                              :class="[
                                item.current ? 'text-brand-pink-dark' : 'text-gray-400 group-hover:text-brand-pink-dark',
                                'h-5 w-5 shrink-0'
                              ]" 
                              aria-hidden="true" 
                            />
                            {{ item.name }}
                          </router-link>
                        </li>
                  </ul>
                </nav>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>

    <!-- Static sidebar for desktop -->
    <div class="hidden lg:flex lg:w-80 lg:flex-col border-r border-gray-200/50 bg-white/20 backdrop-blur-lg">
      <!-- Sidebar component for desktop -->
      <div class="flex grow flex-col gap-y-5 overflow-y-auto px-6 py-8">
        <!-- User Profile Section -->
        <div class="bg-white rounded-2xl p-4 flex items-center gap-3 shadow-sm">
          <div class="h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center overflow-hidden">
            <img
              v-if="userProfileImage"
              class="h-12 w-12 rounded-full object-cover"
              :src="userProfileImage"
              alt="User avatar"
            />
            <UserIcon
              v-else
              class="h-8 w-8 text-gray-400"
            />
          </div>
          <span class="text-lg font-medium text-gray-900 font-comfortaa">@{{ authStore.username }}</span>
        </div>

        <!-- Main Actions -->
        <nav class="flex flex-1 flex-col">
          <div class="text-xs font-medium text-gray-500 mb-3 font-comfortaa">{{ $t('profileSidebar.mainActions') }}</div>
          <ul role="list" class="flex flex-1 flex-col gap-y-2">
                        <li v-for="item in navigation" :key="item.name">
                          <button 
                            v-if="item.name === $t('profileSidebar.logout')"
                            @click="handleLogout"
                            :class="[
                              'text-gray-700 hover:bg-white hover:text-gray-900',
                              'group flex gap-x-3 rounded-lg p-3 text-sm font-medium font-comfortaa transition-all duration-200 w-full text-left'
                            ]"
                          >
                            <component 
                              :is="item.icon" 
                              :class="[
                                'text-gray-600 group-hover:text-gray-900',
                                'h-6 w-6 shrink-0'
                              ]" 
                              aria-hidden="true" 
                            />
                            {{ item.name }}
                          </button>
                          <router-link 
                            v-else
                            :to="item.to" 
                            :class="[
                              item.current 
                                ? 'bg-white text-brand-pink-dark' 
                                : 'text-gray-700 hover:bg-white hover:text-gray-900',
                              'group flex gap-x-3 rounded-lg p-3 text-sm font-medium font-comfortaa transition-all duration-200'
                            ]"
                          >
                            <component 
                              :is="item.icon" 
                              :class="[
                                item.current ? 'text-brand-pink-dark' : 'text-gray-600 group-hover:text-gray-900',
                                'h-6 w-6 shrink-0'
                              ]" 
                              aria-hidden="true" 
                            />
                            {{ item.name }}
                          </router-link>
                        </li>
          </ul>
        </nav>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useAuthStore } from '@/stores/modules/authStore'
import {
  HomeIcon,
  UserIcon,
  ClipboardDocumentListIcon,
  GiftIcon,
  HeartIcon,
  ClockIcon,
  ShoppingBagIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const i18nStore = useI18nStore()
const authStore = useAuthStore()
const { t } = useI18n()
const sidebarOpen = ref(false)

// Expose function to open sidebar from parent
const openSidebar = () => {
  sidebarOpen.value = true
}

defineExpose({
  openSidebar
})

const handleLogout = async () => {
  sidebarOpen.value = false
  await authStore.logout()
  router.push({ name: `Home-${i18nStore.locale}` })
}

// Computed property for user profile image
const userProfileImage = computed(() => {
  return authStore.user?.profile_picture_url || null
})

const navigation = computed(() => [
  { 
    name: t('profileSidebar.dashboard'),
    to: { name: `Profile-${i18nStore.locale}` },
    icon: HomeIcon, 
    current: route.name === `Profile-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.shop'),
    to: { name: `Products-${i18nStore.locale}` }, 
    icon: ShoppingBagIcon, 
    current: route.name === `Products-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.myProfile'),
    to: { name: `MyProfile-${i18nStore.locale}` }, 
    icon: UserIcon, 
    current: route.name === `MyProfile-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.wishlist'),
    to: { name: `ProfileWishlist-${i18nStore.locale}` }, 
    icon: ClipboardDocumentListIcon, 
    current: route.name === `ProfileWishlist-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.myGifts'),
    to: { name: `MyGifts-${i18nStore.locale}` }, 
    icon: GiftIcon, 
    current: route.name === `MyGifts-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.favorites'),
    to: { name: `ProfileFavorites-${i18nStore.locale}` }, 
    icon: HeartIcon, 
    current: route.name === `ProfileFavorites-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.purchaseHistory'),
    to: { name: `ProfileHistory-${i18nStore.locale}` }, 
    icon: ClockIcon, 
    current: route.name === `ProfileHistory-${i18nStore.locale}`
  },
  { 
    name: t('profileSidebar.logout'),
    to: '#', 
    icon: ArrowLeftOnRectangleIcon, 
    current: false
  },
])
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

