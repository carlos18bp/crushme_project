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
                alt="CrushMe Logo" 
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
                      :to="`/${i18nStore.locale}/products`" 
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
                      :to="`/${i18nStore.locale}/login`" 
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
        
        <!-- Social Media Section -->
        <div class="mb-8 md:mb-12">
          <h3 class="text-white text-xl md:text-2xl font-semibold mb-4 md:mb-6 [text-shadow:0_2px_4px_rgba(0,0,0,0.3)] text-center md:text-left">
            {{ $t('footer.followUs') || 'Síguenos' }}
          </h3>
          <div class="flex justify-center md:justify-start gap-6">
            <!-- Instagram -->
            <a 
              href="https://www.instagram.com/crushme.com.co?igsh=c3U0eHFqMzllOXU2&utm_source=qr" 
              target="_blank" 
              rel="noopener noreferrer"
              class="social-link text-white hover:text-pink-300 transition-all duration-300 hover:scale-110"
              aria-label="Instagram"
            >
              <svg class="w-8 h-8 md:w-10 md:h-10" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
            </a>
            
            <!-- Facebook -->
            <a 
              href="https://www.facebook.com/share/1N2kJUbUBW/?mibextid=wwXIfr" 
              target="_blank" 
              rel="noopener noreferrer"
              class="social-link text-white hover:text-pink-300 transition-all duration-300 hover:scale-110"
              aria-label="Facebook"
            >
              <svg class="w-8 h-8 md:w-10 md:h-10" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            </a>
            
            <!-- WhatsApp -->
            <a 
              href="https://wa.me/573239397946" 
              target="_blank" 
              rel="noopener noreferrer"
              class="social-link text-white hover:text-pink-300 transition-all duration-300 hover:scale-110"
              aria-label="WhatsApp"
            >
              <svg class="w-8 h-8 md:w-10 md:h-10" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
              </svg>
            </a>
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
