<template>
  <footer class="relative overflow-hidden min-h-[600px]">
    <!-- Background Image -->
    <div class="absolute top-0 left-0 right-0 bottom-0 z-[1]">
      <img 
        src="@/assets/backgrounds/Fotter.png" 
        alt="Footer Background" 
        class="w-full h-full object-cover object-center"
      />
    </div>
    
    <!-- Content Overlay -->
    <div class="relative z-[2]">
      <div class="max-w-7xl mx-auto px-6 md:px-8 pt-20 md:pt-24 lg:pt-32 pb-12 md:pb-16 lg:pb-20">
        
        <!-- Top Section: Logo and Tagline -->
        <div class="mb-8 md:mb-12">
          <div class="flex flex-col items-center md:items-start">
            <!-- Logo -->
            <router-link :to="`/${i18nStore.locale}`" class="inline-block mb-4 md:mb-6">
              <img 
                src="@/assets/logo/BUY.png" 
                alt="BuyItForMe Logo" 
                class="h-32 md:h-40 lg:h-48 w-auto transition-transform duration-300 hover:scale-105 drop-shadow-[0_4px_8px_rgba(0,0,0,0.3)] hover:drop-shadow-[0_6px_12px_rgba(236,72,153,0.4)]"
              />
            </router-link>
            
            <!-- Tagline -->
            <p class="text-white text-lg md:text-xl font-light max-w-md leading-relaxed [text-shadow:0_2px_4px_rgba(0,0,0,0.3)] text-center md:text-left">
              {{ $t('footer.tagline') }} <span class="text-red-400">❤️</span>
            </p>
          </div>
        </div>
        
        <!-- Middle Section: Navigation Links -->
        <div class="mb-8 md:mb-12">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 text-center md:text-left">
            
            <!-- Navigation Column -->
            <div>
              <h3 class="text-white text-xl md:text-2xl font-semibold mb-4 md:mb-6 [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]">
                {{ $t('footer.navigation.title') }}
              </h3>
              <nav>
                <ul class="space-y-3 md:space-y-4 list-none m-0 p-0">
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.navigation.home') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/diaries`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.navigation.diaries') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/shop`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.navigation.shop') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/about`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.navigation.aboutUs') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/contact`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.navigation.contact') }}
                    </router-link>
                  </li>
                </ul>
              </nav>
            </div>
            
            <!-- Account Column -->
            <div>
              <h3 class="text-white text-xl md:text-2xl font-semibold mb-4 md:mb-6 [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]">
                {{ $t('footer.account.title') }}
              </h3>
              <nav>
                <ul class="space-y-3 md:space-y-4 list-none m-0 p-0">
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/terms`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.account.termsConditions') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/privacy`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.account.privacyPolicy') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/signin`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.account.signIn') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/signup`" 
                      class="footer-nav-link text-white text-base md:text-lg lg:text-xl font-light hover:text-pink-300 transition-colors duration-300 no-underline inline-block relative [text-shadow:0_2px_4px_rgba(0,0,0,0.3)]"
                    >
                      {{ $t('footer.account.signUp') }}
                    </router-link>
                  </li>
                </ul>
              </nav>
            </div>
            
          </div>
        </div>
        
        <!-- Bottom Section: Copyright -->
        <div class="border-t border-white/20 pt-6 md:pt-8">
          <div class="flex flex-col md:flex-row justify-between items-center gap-3 md:gap-4 text-center">
            <p class="text-white text-sm md:text-base font-poppins font-light [text-shadow:0_2px_4px_rgba(0,0,0,0.3)] m-0">
              {{ $t('footer.allRightsReserved') }} {{ $t('footer.year') }}
            </p>
            <p class="text-white text-sm md:text-base font-poppins font-light [text-shadow:0_2px_4px_rgba(0,0,0,0.3)] m-0">
              {{ $t('footer.madeWithLove') }} <span class="text-red-400">💕</span>
            </p>
          </div>
        </div>
        
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useI18nStore } from '@/stores/modules/i18nStore'

// Store
const i18nStore = useI18nStore()
</script>

<style scoped>
/* Underline hover effect for nav links */
.footer-nav-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(45deg, #ec4899, #f97316);
  transition: width 0.3s ease;
}

.footer-nav-link:hover::after {
  width: 100%;
}
</style>
