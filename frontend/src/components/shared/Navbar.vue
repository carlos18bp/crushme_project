<template>
  <nav class="navbar-gradient fixed top-0 left-0 right-0 z-[1000] backdrop-blur-[10px] min-h-[60px] px-8 py-2">
    <div class="max-w-7xl mx-auto flex items-center justify-between gap-8">
      <!-- Logo -->
      <router-link :to="`/${i18nStore.locale}`" class="flex items-center no-underline">
        <img 
          src="@/assets/logo/BUY.png" 
          alt="Logo" 
          class="h-28 w-auto transition-transform duration-300 hover:scale-105"
        />
      </router-link>

      <!-- Navigation Links -->
      <ul class="nav-menu flex list-none gap-10 m-0 p-0 flex-1 justify-center" :class="{ 'active': menuOpen }">
        <li class="m-0">
          <router-link :to="`/${i18nStore.locale}`" class="nav-link font-comfortaa text-lg font-light text-brand-dark no-underline relative transition-colors duration-300 py-2 uppercase tracking-wider hover:text-brand-pink-dark" @click="closeMenu">
            {{ $t('navbar.home') }}
          </router-link>
        </li>
        <li class="m-0">
          <router-link :to="`/${i18nStore.locale}/diaries`" class="nav-link font-comfortaa text-lg font-light text-brand-dark no-underline relative transition-colors duration-300 py-2 uppercase tracking-wider hover:text-brand-pink-dark" @click="closeMenu">
            {{ $t('navbar.diaries') }}
          </router-link>
        </li>
        <li class="m-0">
          <router-link :to="`/${i18nStore.locale}/shop`" class="nav-link font-comfortaa text-lg font-light text-brand-dark no-underline relative transition-colors duration-300 py-2 uppercase tracking-wider hover:text-brand-pink-dark" @click="closeMenu">
            {{ $t('navbar.shop') }}
          </router-link>
        </li>
        <li class="m-0">
          <router-link :to="`/${i18nStore.locale}/about`" class="nav-link font-comfortaa text-lg font-light text-brand-dark no-underline relative transition-colors duration-300 py-2 uppercase tracking-wider hover:text-brand-pink-dark" @click="closeMenu">
            {{ $t('navbar.aboutUs') }}
          </router-link>
        </li>
        <li class="m-0">
          <router-link :to="`/${i18nStore.locale}/contact`" class="nav-link font-comfortaa text-lg font-light text-brand-dark no-underline relative transition-colors duration-300 py-2 uppercase tracking-wider hover:text-brand-pink-dark" @click="closeMenu">
            {{ $t('navbar.contact') }}
          </router-link>
        </li>
      </ul>

      <!-- Right Section: Icons -->
      <div class="flex items-center gap-4">
        <!-- Cart Icon -->
        <button @click="openCart" class="flex items-center justify-center text-brand-dark no-underline transition-all duration-300 p-2 hover:text-brand-pink-dark hover:scale-110 relative" aria-label="Cart">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 stroke-[1.5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <!-- Badge con cantidad de items -->
          <span 
            v-if="cartStore.totalItems > 0"
            class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-poppins font-medium">
            {{ cartStore.totalItems }}
          </span>
        </button>

        <!-- User Icon -->
        <router-link :to="`/${i18nStore.locale}/account`" class="flex items-center justify-center text-brand-dark no-underline transition-all duration-300 p-2 hover:text-brand-pink-dark hover:scale-110" aria-label="Account">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 stroke-[1.5]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </router-link>

        <!-- Mobile Menu Toggle -->
        <button 
          class="menu-toggle hidden bg-transparent border-none cursor-pointer p-2 z-[1001]" 
          @click="toggleMenu"
          aria-label="Toggle menu"
        >
          <span class="hamburger block w-6 h-0.5 bg-brand-dark relative transition-all duration-300" :class="{ 'active': menuOpen }"></span>
        </button>
      </div>
    </div>

    <!-- Cart Drawer -->
    <CartDrawer ref="cartDrawerRef" @checkout="handleCheckout" />
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useCartStore } from '@/stores/modules/cartStore'
import CartDrawer from '@/components/products/CartDrawer.vue'

const i18nStore = useI18nStore()
const cartStore = useCartStore()
const menuOpen = ref(false)
const cartDrawerRef = ref(null)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const closeMenu = () => {
  menuOpen.value = false
}

const openCart = () => {
  cartDrawerRef.value?.openCart()
}

const handleCheckout = () => {
  // Aquí puedes redirigir a la página de checkout
  console.log('Redirecting to checkout...')
  // router.push(`/${i18nStore.locale}/checkout`)
}
</script>

<style scoped>
/* Degradado personalizado del navbar */
.navbar-gradient {
  background: linear-gradient(180deg, #E9C3CD 0%, rgba(233, 195, 205, 0.8) 40%, rgba(233, 195, 205, 0.4) 70%, transparent 100%);
}

/* Animación del underline para nav links */
.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #BF5E81;
  transition: width 0.3s ease;
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.nav-link.router-link-active {
  color: #BF5E81 !important;
  font-weight: 600;
}

/* Hamburger menu animation */
.hamburger::before,
.hamburger::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 2px;
  background: #11181E;
  transition: all 0.3s ease;
}

.hamburger::before {
  top: -8px;
}

.hamburger::after {
  bottom: -8px;
}

.hamburger.active {
  background: transparent !important;
}

.hamburger.active::before {
  top: 0;
  transform: rotate(45deg);
}

.hamburger.active::after {
  bottom: 0;
  transform: rotate(-45deg);
}

/* Responsive Design */
@media (max-width: 768px) {
  .menu-toggle {
    display: block !important;
  }

  .nav-menu {
    position: fixed;
    top: 65px;
    left: 0;
    right: 0;
    flex-direction: column;
    background: linear-gradient(180deg, #E9C3CD 0%, rgba(233, 195, 205, 0.9) 70%, transparent 100%);
    padding: 2rem;
    gap: 1.5rem;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    max-height: calc(100vh - 65px);
    overflow-y: auto;
  }

  .nav-menu.active {
    transform: translateX(0);
  }

  .nav-menu li {
    text-align: center;
  }

  .nav-menu .nav-link {
    font-size: 1.125rem;
    display: block;
    padding: 0.75rem 0;
  }
}
</style>
