<template>
  <div class="flex justify-center px-4 my-8 md:my-12 lg:my-16">
    <div class="promo-banner relative bg-[rgba(66,142,255,0.2)] border-[3px] border-[#11181E] rounded-2xl p-8 md:p-10 lg:p-14 max-w-[1400px] w-full rotate-[1.5deg] shadow-[0_8px_32px_rgba(0,0,0,0.1)]">
      <!-- Push Pins -->
      <img 
        :src="randomPin1" 
        alt="Pin" 
        class="absolute w-12 h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 z-10 top-[-12px] md:top-[-14px] lg:top-[-16px] left-[20px] md:left-[25px] lg:left-[30px] rotate-[-15deg]"
      />
      <img 
        :src="randomPin2" 
        alt="Pin" 
        class="absolute w-12 h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 z-10 top-[-12px] md:top-[-14px] lg:top-[-16px] right-[20px] md:right-[25px] lg:right-[30px] rotate-[25deg]"
      />
      
      <!-- Content -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 lg:gap-20 items-center">
        <!-- Text Section (Left) -->
        <div class="text-center md:text-left">
          <p 
            class="font-poppins text-lg md:text-xl lg:text-2xl xl:text-3xl leading-relaxed mb-8 md:mb-10 text-black/72 font-light"
          >
            {{ description }}
          </p>
          
          <!-- Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
            <button 
              v-if="primaryButton"
              @click="$emit('primary-click')"
              class="bg-[#E9C3CD] text-white font-comfortaa font-semibold px-8 md:px-10 lg:px-12 py-4 md:py-5 rounded-full border-none cursor-pointer transition-all duration-300 capitalize tracking-wide text-base md:text-lg lg:text-xl hover:bg-[#D89AB2] hover:-translate-y-0.5"
            >
              {{ primaryButton.text }}
            </button>
            
            <button 
              v-if="secondaryButton"
              @click="$emit('secondary-click')"
              class="bg-[#E9C3CD] text-white font-comfortaa font-semibold px-8 md:px-10 lg:px-12 py-4 md:py-5 rounded-full border-none cursor-pointer transition-all duration-300 capitalize tracking-wide text-base md:text-lg lg:text-xl hover:bg-[#D89AB2] hover:-translate-y-0.5"
            >
              {{ secondaryButton.text }}
            </button>
          </div>
        </div>
        
        <!-- Image Section (Right) with Title -->
        <div class="flex flex-col justify-center" v-if="image">
          <h3 
            v-if="title" 
            class="font-comfortaa text-brand-dark text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold mb-6 md:mb-8 text-center md:text-right"
          >
            {{ title }}
          </h3>
          <img 
            :src="image.src" 
            :alt="image.alt || 'Banner image'"
            class="w-full h-auto object-cover max-h-[300px] md:max-h-[350px] lg:max-h-[400px]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Import pins
import pin1 from '@/assets/icons/pins/Push pin.png'
import pin2 from '@/assets/icons/pins/Push pin-1.png'  
import pin3 from '@/assets/icons/pins/Push pin-2.png'
import pin4 from '@/assets/icons/pins/Push pin-3.png'
import pin5 from '@/assets/icons/pins/Push pin-4.png'
import pin6 from '@/assets/icons/pins/Push pin-5.png'
import pin7 from '@/assets/icons/pins/Push pin-6.png'
import pin8 from '@/assets/icons/pins/Push pin-7.png'

// Props
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    required: true
  },
  primaryButton: {
    type: Object,
    default: null
  },
  secondaryButton: {
    type: Object,
    default: null
  },
  image: {
    type: Object,
    default: null
  },
  backgroundColor: {
    type: String,
    default: 'bg-brand-purple-light'
  }
})

// Emits
defineEmits(['primary-click', 'secondary-click'])

// Random pin selection
const pins = [pin1, pin2, pin3, pin4, pin5, pin6, pin7, pin8]

const randomPin1 = computed(() => pins[Math.floor(Math.random() * pins.length)])
const randomPin2 = computed(() => pins[Math.floor(Math.random() * pins.length)])
</script>

<style scoped>
/* Mobile adjustments for rotation - rotated in opposite direction */
@media (max-width: 768px) {
  .promo-banner {
    transform: rotate(0.5deg);
  }
}

/* Ensure fonts */
h3 {
  font-family: 'Comfortaa', cursive !important;
}

p {
  font-family: 'Poppins', sans-serif !important;
}
</style>

