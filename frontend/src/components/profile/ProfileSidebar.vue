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
          <div class="fixed inset-0 bg-gray-900/80" />
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
                    <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </TransitionChild>

              <!-- Sidebar component for mobile -->
              <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-[#FAF5F5] px-6 pb-4">
                <!-- User Profile Section -->
                <div class="flex items-center gap-3 pt-6 pb-4">
                  <img 
                    class="h-12 w-12 rounded-full object-cover"
                    src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
                    alt="User avatar" 
                  />
                  <span class="text-lg font-medium text-gray-900 font-comfortaa">Diana Mary</span>
                </div>

                <!-- Main Actions -->
                <nav class="flex flex-1 flex-col">
                  <div class="text-xs font-medium text-gray-500 mb-3 font-comfortaa">Main actions</div>
                  <ul role="list" class="flex flex-1 flex-col gap-y-2">
                    <li v-for="item in navigation" :key="item.name">
                      <a 
                        :href="item.href" 
                        :class="[
                          item.current 
                            ? 'bg-white text-gray-900' 
                            : 'text-gray-700 hover:bg-white hover:text-gray-900',
                          'group flex gap-x-3 rounded-lg p-3 text-sm font-medium font-comfortaa transition-all duration-200'
                        ]"
                      >
                        <component 
                          :is="item.icon" 
                          :class="[
                            item.current ? 'text-gray-900' : 'text-gray-600 group-hover:text-gray-900',
                            'h-6 w-6 shrink-0'
                          ]" 
                          aria-hidden="true" 
                        />
                        {{ item.name }}
                      </a>
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
    <div class="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-80 lg:flex-col">
      <!-- Sidebar component for desktop -->
      <div class="flex grow flex-col gap-y-5 overflow-y-auto bg-[#FAF5F5] px-6 py-8">
        <!-- User Profile Section -->
        <div class="bg-white rounded-2xl p-4 flex items-center gap-3 shadow-sm">
          <img 
            class="h-12 w-12 rounded-full object-cover"
            src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
            alt="User avatar" 
          />
          <span class="text-lg font-medium text-gray-900 font-comfortaa">Diana Mary</span>
        </div>

        <!-- Main Actions -->
        <nav class="flex flex-1 flex-col">
          <div class="text-xs font-medium text-gray-500 mb-3 font-comfortaa">Main actions</div>
          <ul role="list" class="flex flex-1 flex-col gap-y-2">
            <li v-for="item in navigation" :key="item.name">
              <a 
                :href="item.href" 
                :class="[
                  item.current 
                    ? 'bg-white text-gray-900' 
                    : 'text-gray-700 hover:bg-white hover:text-gray-900',
                  'group flex gap-x-3 rounded-lg p-3 text-sm font-medium font-comfortaa transition-all duration-200'
                ]"
              >
                <component 
                  :is="item.icon" 
                  :class="[
                    item.current ? 'text-gray-900' : 'text-gray-600 group-hover:text-gray-900',
                    'h-6 w-6 shrink-0'
                  ]" 
                  aria-hidden="true" 
                />
                {{ item.name }}
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>

    <!-- Mobile header -->
    <div class="sticky top-0 z-40 flex items-center gap-x-6 bg-white px-4 py-4 shadow-sm sm:px-6 lg:hidden">
      <button 
        type="button" 
        class="-m-2.5 p-2.5 text-gray-700 hover:text-gray-900 lg:hidden" 
        @click="sidebarOpen = true"
      >
        <span class="sr-only">Open sidebar</span>
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <div class="flex-1 text-sm font-semibold text-gray-900 font-comfortaa">Profile</div>
      <a href="#">
        <span class="sr-only">Your profile</span>
        <img 
          class="h-8 w-8 rounded-full object-cover"
          src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
          alt="User avatar" 
        />
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue'

// Iconos SVG como componentes
const HomeIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
    </svg>
  `
}

const UserIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
    </svg>
  `
}

const ClipboardIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
    </svg>
  `
}

const GiftIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.25v8.25a1.5 1.5 0 0 1-1.5 1.5H5.25a1.5 1.5 0 0 1-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 1 0 9.375 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 1 1 14.625 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />
    </svg>
  `
}

const HeartIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
    </svg>
  `
}

const ClockIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
    </svg>
  `
}

const LogoutIcon = {
  template: `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15" />
    </svg>
  `
}

const navigation = [
  { name: 'Dashboard', href: '#', icon: HomeIcon, current: true },
  { name: 'My Profile', href: '#', icon: UserIcon, current: false },
  { name: 'Wishlist', href: '#', icon: ClipboardIcon, current: false },
  { name: 'My Gifts', href: '#', icon: GiftIcon, current: false },
  { name: 'Favorites', href: '#', icon: HeartIcon, current: false },
  { name: 'Purchase History', href: '#', icon: ClockIcon, current: false },
  { name: 'Logout', href: '#', icon: LogoutIcon, current: false },
]

const sidebarOpen = ref(false)
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}
</style>

