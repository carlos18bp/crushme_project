<template>
  <footer class="footer-container">
    <!-- Background Image -->
    <div class="footer-background">
      <img 
        src="@/assets/backgrounds/Fotter.png" 
        alt="Footer Background" 
        class="background-image"
      />
    </div>
    
    <!-- Content Overlay -->
    <div class="footer-content">
      <div class="max-w-7xl mx-auto px-8 pt-32 pb-20">
        
        <!-- Top Section: Logo and Tagline -->
        <div class="footer-top mb-12">
          <div class="flex flex-col items-start">
            <!-- Logo -->
            <router-link :to="`/${i18nStore.locale}`" class="footer-logo mb-6">
              <img 
                src="@/assets/logo/BUY.png" 
                alt="BuyItForMe Logo" 
                class="h-48 w-auto transition-transform duration-300 hover:scale-105"
              />
            </router-link>
            
            <!-- Tagline -->
            <p class="footer-tagline text-white text-xl font-light max-w-md leading-relaxed">
              {{ $t('footer.tagline') }} <span class="text-red-400">❤️</span>
            </p>
          </div>
        </div>
        
        <!-- Middle Section: Navigation Links -->
        <div class="footer-middle mb-12">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
            
            <!-- Navigation Column -->
            <div class="footer-navigation">
              <h3 class="text-white text-2xl font-semibold mb-6">
                {{ $t('footer.navigation.title') }}
              </h3>
              <nav>
                <ul class="footer-nav-list space-y-4">
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.navigation.home') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/diaries`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.navigation.diaries') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/shop`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.navigation.shop') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/about`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.navigation.aboutUs') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/contact`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.navigation.contact') }}
                    </router-link>
                  </li>
                </ul>
              </nav>
            </div>
            
            <!-- Account Column -->
            <div class="footer-account">
              <h3 class="text-white text-2xl font-semibold mb-6">
                {{ $t('footer.account.title') }}
              </h3>
              <nav>
                <ul class="footer-account-list space-y-4">
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/terms`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.account.termsConditions') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/signin`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
                    >
                      {{ $t('footer.account.signIn') }}
                    </router-link>
                  </li>
                  <li>
                    <router-link 
                      :to="`/${i18nStore.locale}/signup`" 
                      class="footer-nav-link text-white text-xl font-light hover:text-pink-300 transition-colors duration-300"
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
        <div class="footer-bottom border-t border-white/20 pt-8">
          <div class="flex flex-col md:flex-row justify-between items-center gap-4">
            <p class="footer-copyright text-white text-base font-poppins font-light">
              {{ $t('footer.allRightsReserved') }} {{ $t('footer.year') }}
            </p>
            <p class="footer-made-with-love text-white text-base font-poppins font-light">
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
.footer-container {
  position: relative;
  overflow: hidden;
  min-height: 600px;
}

.footer-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.footer-content {
  position: relative;
  z-index: 2;
}

.footer-logo {
  display: inline-block;
}

.footer-tagline {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.footer-navigation h3,
.footer-account h3 {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.footer-nav-link {
  display: block;
  text-decoration: none;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  position: relative;
}

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

.footer-copyright,
.footer-made-with-love {
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .footer-content {
    padding-top: 6rem;
    padding-bottom: 3rem;
  }
  
  .footer-top {
    margin-bottom: 2rem;
    text-align: center;
  }
  
  .footer-top .flex {
    align-items: center;
  }
  
  .footer-middle {
    margin-bottom: 2rem;
  }
  
  .footer-middle .grid {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }
  
  .footer-bottom .flex {
    text-align: center;
  }
}

/* Animation for hover effects */
.footer-logo img {
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

.footer-logo:hover img {
  filter: drop-shadow(0 6px 12px rgba(236, 72, 153, 0.4));
}

/* Custom scrollbar if needed */
.footer-container::-webkit-scrollbar {
  width: 8px;
}

.footer-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.footer-container::-webkit-scrollbar-thumb {
  background: rgba(236, 72, 153, 0.5);
  border-radius: 4px;
}

.footer-container::-webkit-scrollbar-thumb:hover {
  background: rgba(236, 72, 153, 0.7);
}
</style>
