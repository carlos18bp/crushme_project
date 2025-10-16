<template>
  <section class="relative min-h-screen flex items-center pt-[60px]">
    <!-- Content Container -->
    <div class="relative w-full z-[2]">
      <div class="max-w-[1800px] mx-auto px-6 md:px-12 py-12 md:py-20">
        <div class="grid grid-cols-1 lg:grid-cols-[0.9fr_1.1fr] gap-8 lg:gap-8 items-center mb-12 md:mb-20">
          
          <!-- Left Content: Text and Buttons -->
          <div class="flex flex-col gap-6 md:gap-8 text-center lg:text-left items-center lg:items-start">
            <h1 class="font-comfortaa text-3xl md:text-4xl lg:text-5xl xl:text-[3.5rem] font-normal leading-tight text-black m-0">
              {{ $t('hero.title') }}<br>
              {{ $t('hero.titleSecondLine') }} 💕
            </h1>
            
            <p class="font-poppins text-lg md:text-xl lg:text-2xl font-light leading-relaxed text-black m-0 max-w-[600px]">
              {{ $t('hero.subtitle') }}
            </p>
            
            <!-- Call to Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 md:gap-6 w-full sm:w-auto">
              <router-link 
                :to="`/${i18nStore.locale}/products`"
                class="font-poppins text-base md:text-lg font-medium text-white bg-[#4A6FA5] border-none rounded-full px-8 md:px-12 py-3 md:py-4 cursor-pointer no-underline inline-block transition-all duration-300 shadow-[0_4px_12px_rgba(74,111,165,0.3)] hover:bg-[#3d5a8a] hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(74,111,165,0.4)] text-center"
              >
                {{ $t('hero.buttons.shop') }}
              </router-link>
              
              <router-link 
                :to="`/${i18nStore.locale}/diaries`"
                class="font-poppins text-base md:text-lg font-medium text-white bg-[rgba(233,195,205,0.8)] border-none rounded-full px-8 md:px-12 py-3 md:py-4 cursor-pointer no-underline inline-block transition-all duration-300 shadow-[0_4px_12px_rgba(233,195,205,0.3)] hover:bg-[rgba(233,195,205,1)] hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(233,195,205,0.4)] text-center"
              >
                {{ $t('hero.buttons.diaries') }}
              </router-link>
            </div>
          </div>
          
          <!-- Right Content: Hero Image -->
          <div class="flex items-center justify-center relative">
            <img 
              src="@/assets/home/hero/hero.svg" 
              alt="Hero Products" 
              class="w-full h-auto max-w-[500px] lg:max-w-[800px] animate-float"
            />
          </div>
          
        </div>
        
        <!-- Trust Badges Section -->
        <div class="flex flex-wrap justify-center lg:justify-between gap-4 md:gap-6 lg:gap-10 mt-8 md:mt-12">
          <div 
            v-for="badge in trustBadges" 
            :key="badge.key"
            class="relative bg-white/30 backdrop-blur-[10px] border-2 border-white/50 rounded-full px-6 md:px-8 lg:px-12 py-3 md:py-4 lg:py-6 cursor-pointer transition-all duration-300 flex-1 min-w-[180px] md:min-w-[220px] flex items-center justify-center hover:bg-white/50 hover:border-white/80 hover:-translate-y-1 hover:shadow-[0_8px_20px_rgba(0,0,0,0.1)]"
            @mouseenter="showTooltip(badge.key)"
            @mouseleave="hideTooltip(badge.key)"
          >
            <span class="font-poppins text-base md:text-lg lg:text-xl font-medium text-black/80 whitespace-nowrap text-center">{{ $t(`hero.trustBadges.${badge.key}.title`) }}</span>
            
            <!-- Tooltip -->
            <transition name="tooltip-fade">
              <div 
                v-if="activeTooltip === badge.key" 
                class="absolute bottom-[calc(100%+12px)] left-1/2 -translate-x-1/2 bg-white border-2 border-black/10 rounded-xl px-5 md:px-7 py-4 md:py-5 shadow-[0_8px_24px_rgba(0,0,0,0.15)] min-w-[220px] md:min-w-[280px] max-w-[280px] md:max-w-[320px] z-10 after:content-[''] after:absolute after:top-full after:left-1/2 after:-translate-x-1/2 after:border-8 after:border-transparent after:border-t-white"
              >
                <p class="font-poppins text-sm md:text-[0.9375rem] leading-relaxed text-black/80 m-0 text-center">
                  {{ $t(`hero.trustBadges.${badge.key}.tooltip`) }}
                </p>
              </div>
            </transition>
          </div>
        </div>
        
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useI18nStore } from '@/stores/modules/i18nStore'

// Store
const i18nStore = useI18nStore()

// Trust badges configuration
const trustBadges = [
  { key: 'discreetShipping' },
  { key: 'privateGifting' },
  { key: 'securePayments' },
  { key: 'trustedWorldwide' }
]

// Tooltip state
const activeTooltip = ref(null)

const showTooltip = (key) => {
  activeTooltip.value = key
}

const hideTooltip = (key) => {
  if (activeTooltip.value === key) {
    activeTooltip.value = null
  }
}
</script>

<style scoped>
/* Floating Animation */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.animate-float {
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.15));
  animation: float 6s ease-in-out infinite;
}

/* Tooltip Fade Animation */
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(5px);
}

.tooltip-fade-enter-to,
.tooltip-fade-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>

