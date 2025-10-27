<template>
  <section class="relative min-h-screen flex items-center pt-[60px]">
    <!-- Video Background -->
    <div class="absolute inset-0 w-full h-full overflow-hidden">
      <video
        ref="videoPlayer"
        class="absolute inset-0 w-full h-full object-cover"
        muted
        playsinline
        @ended="onVideoEnded"
      >
        <source :src="currentVideoSrc" type="video/mp4">
      </video>
    </div>

    <!-- White Overlay (20% opacity) -->
    <div class="absolute inset-0 bg-white opacity-40 z-[1]"></div>

    <!-- Content Container -->
    <div class="relative w-full z-[2]">
      <div class="max-w-[1800px] mx-auto px-6 md:px-12 py-12 md:py-20">
        <div class="flex flex-col items-center justify-center mb-12 md:mb-20 text-center">
          
          <!-- Centered Content: Text and Buttons -->
          <div class="flex flex-col gap-8 md:gap-10 items-center max-w-[900px]">
            <h1 class="font-comfortaa text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal leading-tight text-black m-0">
              {{ $t('hero.title') }}<br>
              {{ $t('hero.titleSecondLine') }} 💕
            </h1>
            
            <p class="font-poppins text-xl md:text-2xl lg:text-3xl font-light leading-relaxed text-black m-0 max-w-[700px]">
              {{ $t('hero.subtitle') }}
            </p>
            
            <!-- Call to Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-5 md:gap-7 w-full sm:w-auto">
              <router-link 
                :to="`/${i18nStore.locale}/products`"
                class="font-poppins text-lg md:text-xl font-medium text-white bg-[#4A6FA5] border-none rounded-full px-10 md:px-16 py-4 md:py-5 cursor-pointer no-underline inline-block transition-all duration-300 shadow-[0_4px_12px_rgba(74,111,165,0.3)] hover:bg-[#3d5a8a] hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(74,111,165,0.4)] text-center"
              >
                {{ $t('hero.buttons.shop') }}
              </router-link>
              
              <router-link 
                :to="`/${i18nStore.locale}/diaries`"
                class="font-poppins text-lg md:text-xl font-medium text-white bg-[rgba(233,195,205,0.8)] border-none rounded-full px-10 md:px-16 py-4 md:py-5 cursor-pointer no-underline inline-block transition-all duration-300 shadow-[0_4px_12px_rgba(233,195,205,0.3)] hover:bg-[rgba(233,195,205,1)] hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(233,195,205,0.4)] text-center"
              >
                {{ $t('hero.buttons.diaries') }}
              </router-link>
            </div>
          </div>
          
        </div>
        
        <!-- Trust Badges Section -->
        <!-- Mobile: Carousel -->
        <div class="block lg:hidden mt-8 md:mt-12">
          <div ref="carouselContainer" class="relative overflow-hidden">
            <div class="flex transition-transform duration-300 ease-in-out" :style="{ transform: `translateX(-${currentSlide * 100}%)` }">
              <div 
                v-for="badge in trustBadges" 
                :key="badge.key"
                class="w-full flex-shrink-0 px-4"
              >
                <div 
                  class="relative bg-white/30 backdrop-blur-[10px] border-2 border-white/50 rounded-full px-6 py-4 cursor-pointer transition-all duration-300 flex items-center justify-center hover:bg-white/50 hover:border-white/80"
                  @click="toggleTooltip(badge.key)"
                >
                  <span class="font-poppins text-base font-medium text-black/80 whitespace-nowrap text-center">{{ $t(`hero.trustBadges.${badge.key}.title`) }}</span>
                  
                  <!-- Tooltip -->
                  <transition name="tooltip-fade">
                    <div 
                      v-if="activeTooltip === badge.key" 
                      class="absolute bottom-[calc(100%+12px)] left-1/2 -translate-x-1/2 bg-white border-2 border-black/10 rounded-xl px-5 py-4 shadow-[0_8px_24px_rgba(0,0,0,0.15)] min-w-[220px] max-w-[280px] z-10 after:content-[''] after:absolute after:top-full after:left-1/2 after:-translate-x-1/2 after:border-8 after:border-transparent after:border-t-white"
                    >
                      <p class="font-poppins text-sm leading-relaxed text-black/80 m-0 text-center">
                        {{ $t(`hero.trustBadges.${badge.key}.tooltip`) }}
                      </p>
                    </div>
                  </transition>
                </div>
              </div>
            </div>
            
            <!-- Carousel indicators -->
            <div class="flex justify-center gap-2 mt-4">
              <button
                v-for="(badge, index) in trustBadges"
                :key="index"
                @click="goToSlide(index)"
                class="w-2 h-2 rounded-full transition-all duration-300"
                :class="currentSlide === index ? 'bg-black/80 w-6' : 'bg-black/30'"
                :aria-label="`Go to slide ${index + 1}`"
              ></button>
            </div>
          </div>
        </div>

        <!-- Desktop: Grid -->
        <div class="hidden lg:flex flex-wrap justify-center lg:justify-between gap-4 md:gap-6 lg:gap-10 mt-8 md:mt-12">
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18nStore } from '@/stores/modules/i18nStore'
import Clip1 from '@/assets/home/hero/Clip1.mp4'
import Clip2 from '@/assets/home/hero/Clip2.mp4'

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

const toggleTooltip = (key) => {
  if (activeTooltip.value === key) {
    activeTooltip.value = null
  } else {
    activeTooltip.value = key
  }
}

// Carousel state
const carouselContainer = ref(null)
const currentSlide = ref(0)

const goToSlide = (index) => {
  currentSlide.value = index
}

// Auto-advance carousel
let carouselInterval = null

onMounted(() => {
  // Iniciar reproducción del primer video
  if (videoPlayer.value) {
    videoPlayer.value.play()
  }

  // Auto-advance carousel every 4 seconds
  carouselInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % trustBadges.length
  }, 4000)
})

// Clean up interval on unmount
onUnmounted(() => {
  if (carouselInterval) {
    clearInterval(carouselInterval)
  }
})

// Video loop logic
const videoPlayer = ref(null)
const videos = [Clip1, Clip2]
let currentVideoIndex = 0
const currentVideoSrc = ref(videos[0])

const onVideoEnded = () => {
  // Cambiar al siguiente video
  currentVideoIndex = (currentVideoIndex + 1) % videos.length
  currentVideoSrc.value = videos[currentVideoIndex]
  
  // Esperar a que el video se cargue y reproducir
  if (videoPlayer.value) {
    videoPlayer.value.load()
    videoPlayer.value.play()
  }
}

onMounted(() => {
  // Iniciar reproducción del primer video
  if (videoPlayer.value) {
    videoPlayer.value.play()
  }
})
</script>

<style scoped>
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

