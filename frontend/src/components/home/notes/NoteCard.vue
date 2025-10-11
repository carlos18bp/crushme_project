<template>
  <div 
    class="note-card"
    :class="[`pin-${pinPosition}`, `rotate-${rotationClass}`]"
    :style="{ 
      '--rotation': `${rotation}deg`,
      '--pin-rotation': `${pinRotation}deg`
    }"
  >
    <!-- Pin -->
    <div class="pin" :class="`pin-${pinPosition}`">
      <img :src="pinImage" :alt="`Pin ${pinPosition}`" class="pin-image" />
    </div>

    <!-- Card Content -->
    <div class="card-content">
      <!-- Username -->
      <div class="username">@{{ username }}</div>
      
      <!-- Note Text -->
      <div class="note-text">
        {{ note }}
      </div>
      
      <!-- Status Section (right side) -->
      <div class="status-section">
        <div class="status-label">{{ $t('notes.myStatus') }}</div>
        <div class="status-text">{{ status }}</div>
      </div>
      
      <!-- Go to Diary Button -->
      <button class="diary-button" @click="goToDiary">
        {{ $t('notes.goToDiary') }}
      </button>
    </div>
    
    <!-- Profile Avatar (bottom-left corner) -->
    <div class="profile-avatar">
      <img :src="profilePicture" :alt="username" class="avatar-img" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'

const router = useRouter()
const i18nStore = useI18nStore()

// Props
const props = defineProps({
  username: {
    type: String,
    required: true
  },
  note: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true
  },
  profilePicture: {
    type: String,
    required: true
  }
})

// Importar pins
import pin0 from '@/assets/icons/pins/Push pin.png'
import pin1 from '@/assets/icons/pins/Push pin-1.png'
import pin2 from '@/assets/icons/pins/Push pin-2.png'
import pin3 from '@/assets/icons/pins/Push pin-3.png'
import pin4 from '@/assets/icons/pins/Push pin-4.png'
import pin5 from '@/assets/icons/pins/Push pin-5.png'
import pin6 from '@/assets/icons/pins/Push pin-6.png'
import pin7 from '@/assets/icons/pins/Push pin-7.png'

// Array de pins disponibles
const pins = [pin0, pin1, pin2, pin3, pin4, pin5, pin6, pin7]

// Generar valores aleatorios para cada instancia (solo una vez al crear el componente)
const pinIndex = Math.floor(Math.random() * pins.length)
const pinImage = computed(() => pins[pinIndex])

// Posiciones posibles: left, center, right
const positions = ['left', 'center', 'right']
const pinPosition = positions[Math.floor(Math.random() * positions.length)]

// Rotación aleatoria de la tarjeta (-8 a 8 grados) - generada una sola vez
const rotation = Math.random() * 16 - 8

// Rotación del pin (-15 a 15 grados) - generada una sola vez
const pinRotation = Math.random() * 30 - 15

// Clase de rotación para la tarjeta
const rotationClass = computed(() => {
  if (rotation < -4) return 'left'
  if (rotation > 4) return 'right'
  return 'center'
})

// Navigate to user's diary
const goToDiary = () => {
  const currentLang = i18nStore.locale
  router.push(`/${currentLang}/diaries/@${props.username}`)
}
</script>

<style scoped>
/* Note Card Container */
.note-card {
  position: relative;
  width: 100%;
  max-width: 320px;
  background: rgba(255, 43, 43, 0.16);
  border: 2px solid #000000;
  border-radius: 16px;
  padding: 24px 20px 16px;
  transform: rotate(var(--rotation));
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
}

.note-card:hover {
  transform: rotate(0deg) translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

/* Pin */
.pin {
  position: absolute;
  top: -12px;
  width: 40px;
  height: 40px;
  z-index: 2;
  transform: rotate(var(--pin-rotation));
  transition: transform 0.3s ease;
}

.pin.pin-left {
  left: 20px;
}

.pin.pin-center {
  left: 50%;
  transform: translateX(-50%) rotate(var(--pin-rotation));
}

.pin.pin-right {
  right: 20px;
}

.pin-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

/* Card Content */
.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 30px;
}

/* Username */
.username {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.5);
  letter-spacing: 0.02em;
}

/* Note Text */
.note-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  color: #000000;
  min-height: 120px;
  margin-bottom: 8px;
}

/* Profile Avatar - Bottom Left Corner */
.profile-avatar {
  position: absolute;
  bottom: -15px;
  left: -15px;
  width: 160px;
  height: 160px;
  border-radius: 38px;
  overflow: hidden;
  background: #f1f5f9;
  border: 3px solid #000000;
  z-index: 5;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Status Section */
.status-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
  margin-bottom: 8px;
}

.status-label {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: #000000;
}

.status-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  color: #000000;
}

/* Diary Button */
.diary-button {
  width: 100%;
  padding: 8px 16px;
  background: transparent;
  border: none;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.4);
  text-align: right;
  cursor: pointer;
  transition: color 0.2s ease;
  margin-top: 4px;
}

.diary-button:hover {
  color: rgba(0, 0, 0, 0.7);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .note-card {
    max-width: 280px;
    padding: 20px 16px 12px;
    border-radius: 14px;
  }
  
  .note-text {
    font-size: 0.9375rem;
    min-height: 100px;
  }
  
  .profile-avatar {
    width: 130px;
    height: 130px;
    border-radius: 32px;
    bottom: -12px;
    left: -12px;
    border: 2px solid #000000;
  }
  
  .card-content {
    padding-bottom: 30px;
  }
}
</style>

