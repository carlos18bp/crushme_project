<template>
  <section class="hero-section">
    <!-- Content Container -->
    <div class="hero-container">
      <div class="max-w-[1800px] mx-auto px-12 py-20">
        <div class="hero-content-wrapper">
          
          <!-- Left Content: Text and Buttons -->
          <div class="hero-text-section">
            <h1 class="hero-title">
              {{ $t('hero.title') }}<br>
              {{ $t('hero.titleSecondLine') }} 💕
            </h1>
            
            <p class="hero-subtitle">
              {{ $t('hero.subtitle') }}
            </p>
            
            <!-- Call to Action Buttons -->
            <div class="hero-buttons">
              <router-link 
                :to="`/${i18nStore.locale}/products`"
                class="btn-primary"
              >
                {{ $t('hero.buttons.shop') }}
              </router-link>
              
              <router-link 
                :to="`/${i18nStore.locale}/diaries`"
                class="btn-secondary"
              >
                {{ $t('hero.buttons.diaries') }}
              </router-link>
            </div>
          </div>
          
          <!-- Right Content: Hero Image -->
          <div class="hero-image-section">
            <img 
              src="@/assets/home/hero/hero.svg" 
              alt="Hero Products" 
              class="hero-image"
            />
          </div>
          
        </div>
        
        <!-- Trust Badges Section -->
        <div class="trust-badges">
          <div 
            v-for="badge in trustBadges" 
            :key="badge.key"
            class="trust-badge"
            @mouseenter="showTooltip(badge.key)"
            @mouseleave="hideTooltip(badge.key)"
          >
            <span class="badge-text">{{ $t(`hero.trustBadges.${badge.key}.title`) }}</span>
            
            <!-- Tooltip -->
            <transition name="tooltip-fade">
              <div 
                v-if="activeTooltip === badge.key" 
                class="tooltip"
              >
                <p class="tooltip-text">
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
/* Hero Section Container */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding-top: 60px; /* Compensar altura del navbar */
}

/* Content Container */
.hero-container {
  position: relative;
  width: 100%;
  z-index: 2;
}

/* Content Wrapper - Grid Layout */
.hero-content-wrapper {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 2rem;
  align-items: center;
  margin-bottom: 5rem;
}

/* Left Content Section */
.hero-text-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.hero-title {
  font-family: 'Comfortaa', cursive;
  font-size: 3.5rem;
  font-weight: 400;
  line-height: 1.2;
  color: #000000;
  margin: 0;
}

.hero-subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1.5rem;
  font-weight: 300;
  line-height: 1.6;
  color: #000000;
  margin: 0;
  max-width: 600px;
}

/* Buttons Container */
.hero-buttons {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

/* Primary Button */
.btn-primary {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #FFFFFF;
  background: #4A6FA5;
  border: none;
  border-radius: 50px;
  padding: 1rem 3rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
}

.btn-primary:hover {
  background: #3d5a8a;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 111, 165, 0.4);
}

/* Secondary Button */
.btn-secondary {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: #FFFFFF;
  background: rgba(233, 195, 205, 0.8);
  border: none;
  border-radius: 50px;
  padding: 1rem 3rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(233, 195, 205, 0.3);
}

.btn-secondary:hover {
  background: rgba(233, 195, 205, 1);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(233, 195, 205, 0.4);
}

/* Right Content Section - Hero Image */
.hero-image-section {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.hero-image {
  width: 100%;
  height: auto;
  max-width: 800px;
  filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.15));
  animation: float 6s ease-in-out infinite;
}

/* Floating Animation */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* Trust Badges Section */
.trust-badges {
  display: flex;
  justify-content: space-between;
  gap: 2.5rem;
  flex-wrap: wrap;
  margin-top: 3rem;
  max-width: 100%;
}

.trust-badge {
  position: relative;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-radius: 50px;
  padding: 1.5rem 3rem;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.trust-badge:hover {
  background: rgba(255, 255, 255, 0.5);
  border-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.badge-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.8);
  white-space: nowrap;
  text-align: center;
}

/* Tooltip */
.tooltip {
  position: absolute;
  bottom: calc(100% + 12px);
  left: 50%;
  transform: translateX(-50%);
  background: #FFFFFF;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 1.25rem 1.75rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  max-width: 320px;
  z-index: 10;
}

.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: #FFFFFF;
}

.tooltip-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: rgba(0, 0, 0, 0.8);
  margin: 0;
  text-align: center;
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

/* Responsive Design */
@media (max-width: 1024px) {
  .hero-content-wrapper {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  
  .hero-text-section {
    text-align: center;
    align-items: center;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.25rem;
  }
  
  .hero-buttons {
    justify-content: center;
  }
  
  .hero-image {
    max-width: 500px;
  }
  
  .trust-badges {
    justify-content: center;
    gap: 1.5rem;
  }
  
  .trust-badge {
    flex: 0 1 auto;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding-top: 80px;
  }
  
  .hero-container > div {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1.125rem;
  }
  
  .btn-primary,
  .btn-secondary {
    font-size: 1rem;
    padding: 0.875rem 2rem;
  }
  
  .trust-badges {
    gap: 1rem;
    justify-content: center;
  }
  
  .trust-badge {
    padding: 1rem 2rem;
    min-width: 180px;
  }
  
  .badge-text {
    font-size: 1rem;
  }
  
  .tooltip {
    min-width: 220px;
    max-width: 260px;
    padding: 1rem 1.25rem;
  }
  
  .tooltip-text {
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.75rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
    text-align: center;
  }
  
  .trust-badges {
    flex-direction: column;
    align-items: stretch;
  }
  
  .trust-badge {
    text-align: center;
  }
}
</style>

