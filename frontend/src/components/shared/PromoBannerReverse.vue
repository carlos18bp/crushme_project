<template>
  <div class="promo-banner-container my-16">
    <div class="promo-banner">
      <!-- Push Pins -->
      <img 
        :src="randomPin1" 
        alt="Pin" 
        class="push-pin pin-top-left"
      />
      <img 
        :src="randomPin2" 
        alt="Pin" 
        class="push-pin pin-top-right"
      />
      
      <!-- Content -->
      <div class="banner-content">
        <!-- Text Section (Left) -->
        <div class="text-section">
          <p 
            class="font-poppins text-xl md:text-2xl lg:text-3xl leading-relaxed mb-10"
            style="color: rgba(0, 0, 0, 0.72); font-weight: 300;"
          >
            {{ description }}
          </p>
          
          <!-- Buttons -->
          <div class="buttons-section flex flex-col sm:flex-row gap-4">
            <button 
              v-if="primaryButton"
              @click="$emit('primary-click')"
              class="btn-primary"
            >
              {{ primaryButton.text }}
            </button>
            
            <button 
              v-if="secondaryButton"
              @click="$emit('secondary-click')"
              class="btn-secondary"
            >
              {{ secondaryButton.text }}
            </button>
          </div>
        </div>
        
        <!-- Image Section (Right) with Title -->
        <div class="image-section" v-if="image">
          <h3 
            v-if="title" 
            class="font-comfortaa text-brand-dark text-3xl md:text-4xl lg:text-5xl font-bold mb-8 text-right"
          >
            {{ title }}
          </h3>
          <img 
            :src="image.src" 
            :alt="image.alt || 'Banner image'"
            class="banner-image"
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
.promo-banner-container {
  display: flex;
  justify-content: center;
  padding: 0 1rem;
}

.promo-banner {
  position: relative;
  background: rgba(66, 142, 255, 0.2); /* #428EFF con 20% opacidad */
  border: 3px solid #11181E;
  border-radius: 1rem;
  padding: 3.5rem 4rem; /* Más largo y espacioso */
  max-width: 1400px; /* Aún más ancho */
  width: 100%;
  transform: rotate(1.5deg); /* Rotación invertida */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.banner-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
}

@media (min-width: 768px) {
  .banner-content {
    grid-template-columns: 1fr 1fr;
    gap: 5rem; /* Aún más espacio entre columnas */
  }
}

.push-pin {
  position: absolute;
  width: 64px; /* Mucho más grandes */
  height: 64px;
  z-index: 10;
}

.pin-top-left {
  top: -16px; /* Ajustado para pins más grandes */
  left: 30px;
  transform: rotate(-15deg);
}

.pin-top-right {
  top: -16px; /* Ajustado para pins más grandes */
  right: 30px;
  transform: rotate(25deg);
}

.btn-primary {
  background: #E9C3CD; /* brand-pink-light */
  color: white;
  font-family: 'Comfortaa', cursive;
  font-weight: 600;
  padding: 1.25rem 3rem; /* Botones más grandes */
  border-radius: 2rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: capitalize;
  letter-spacing: 0.3px;
  font-size: 1.25rem; /* Texto más grande */
}

.btn-primary:hover {
  background: #D89AB2;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #E9C3CD; /* brand-pink-light */
  color: white;
  font-family: 'Comfortaa', cursive;
  font-weight: 600;
  padding: 1.25rem 3rem; /* Botones más grandes */
  border-radius: 2rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: capitalize;
  letter-spacing: 0.3px;
  font-size: 1.25rem; /* Texto más grande */
}

.btn-secondary:hover {
  background: #D89AB2;
  transform: translateY(-2px);
}

.banner-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  max-height: 400px; /* Aumentar altura máxima de la imagen */
}

.image-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* Force fonts */
h3 {
  font-family: 'Comfortaa', cursive !important;
}

p {
  font-family: 'Poppins', sans-serif !important;
}

/* Mobile adjustments */
@media (max-width: 768px) {
  .promo-banner {
    padding: 2.5rem 2rem; /* Más espacioso en móvil también */
    transform: rotate(0.5deg); /* Rotación invertida en móvil también */
  }
  
  .banner-content {
    text-align: center;
  }
  
  .pin-top-left {
    left: 15px;
    top: -12px; /* Ajustado para móvil */
  }
  
  .pin-top-right {
    right: 15px;
    top: -12px; /* Ajustado para móvil */
  }
}
</style>

