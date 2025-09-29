<template>
  <div class="confirmation-view">
    <!-- Background overlay -->
    <div class="background-overlay"></div>
    
    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="transparent" />
    
    <!-- Content container -->
    <div class="confirmation-content">
      <div class="confirmation-card">
        <!-- Success icon -->
        <div class="success-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="12" fill="#10B981"/>
            <path d="M8 12.5l2.5 2.5L16 9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        
        <!-- Title -->
        <h1 class="confirmation-title">{{ title }}</h1>
        
        <!-- Message -->
        <p class="confirmation-message">{{ message }}</p>
        
        <!-- Additional info if provided -->
        <p v-if="subtitle" class="confirmation-subtitle">{{ subtitle }}</p>
        
        <!-- Action buttons -->
        <div class="confirmation-actions">
          <button 
            v-if="primaryAction"
            @click="handlePrimaryAction"
            class="btn btn-primary"
          >
            {{ primaryAction.text }}
          </button>
          
          <button 
            v-if="secondaryAction"
            @click="handleSecondaryAction"
            class="btn btn-secondary"
          >
            {{ secondaryAction.text }}
          </button>
        </div>
        
        <!-- Auto redirect countdown if enabled -->
        <div v-if="autoRedirect && countdown > 0" class="countdown">
          {{ $t('confirmation.redirecting', { seconds: countdown }) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useI18nStore } from '@/stores/modules/i18nStore'
import LanguageSelector from '@/components/shared/LanguageSelector.vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const i18nStore = useI18nStore()

// Props que pueden ser pasados via query params o props
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: null
  },
  primaryAction: {
    type: Object,
    default: null
    // Expected format: { text: 'Continue', route: '/dashboard' }
  },
  secondaryAction: {
    type: Object,
    default: null
    // Expected format: { text: 'Go Back', route: '/previous' }
  },
  autoRedirect: {
    type: Boolean,
    default: false
  },
  redirectDelay: {
    type: Number,
    default: 5
  },
  redirectTo: {
    type: String,
    default: '/'
  }
})

// Reactive data
const countdown = ref(props.redirectDelay)
let countdownInterval = null

// Get data from query params if not provided as props
const title = ref(props.title || route.query.title || t('confirmation.defaultTitle'))
const message = ref(props.message || route.query.message || t('confirmation.defaultMessage'))
const subtitle = ref(props.subtitle || route.query.subtitle || null)

// Parse actions from query params if not provided as props
const primaryAction = ref(props.primaryAction || (route.query.primaryActionText ? {
  text: route.query.primaryActionText,
  route: route.query.primaryActionRoute || `/${i18nStore.locale}`
} : {
  text: t('confirmation.continue'),
  route: `/${i18nStore.locale}`
}))

const secondaryAction = ref(props.secondaryAction || (route.query.secondaryActionText ? {
  text: route.query.secondaryActionText,
  route: route.query.secondaryActionRoute || `/${i18nStore.locale}`
} : null))

// Handle actions
const handlePrimaryAction = () => {
  if (primaryAction.value?.route) {
    router.push(primaryAction.value.route)
  }
}

const handleSecondaryAction = () => {
  if (secondaryAction.value?.route) {
    router.push(secondaryAction.value.route)
  }
}

// Auto redirect functionality
const startCountdown = () => {
  if (props.autoRedirect || route.query.autoRedirect === 'true') {
    countdownInterval = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        const redirectRoute = props.redirectTo || route.query.redirectTo || `/${i18nStore.locale}`
        router.push(redirectRoute)
      }
    }, 1000)
  }
}

// Lifecycle
onMounted(() => {
  startCountdown()
})

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})
</script>

<style scoped>
.confirmation-view {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('@/assets/backgrounds/background_1.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
}

.background-overlay::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
}

.confirmation-content {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 500px;
}

.confirmation-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.success-icon {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.confirmation-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1rem;
  animation: slideUp 0.6s ease-out 0.2s both;
}

.confirmation-message {
  font-size: 1.1rem;
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.6;
  animation: slideUp 0.6s ease-out 0.3s both;
}

.confirmation-subtitle {
  font-size: 0.9rem;
  color: #9ca3af;
  margin-bottom: 2rem;
  animation: slideUp 0.6s ease-out 0.4s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirmation-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
  animation: slideUp 0.6s ease-out 0.5s both;
}

.btn {
  padding: 0.875rem 2rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: transparent;
  color: #6b7280;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  transform: translateY(-1px);
}

.countdown {
  font-size: 0.875rem;
  color: #9ca3af;
  margin-top: 1rem;
  animation: slideUp 0.6s ease-out 0.6s both;
}

/* Responsive design */
@media (min-width: 640px) {
  .confirmation-actions {
    flex-direction: row;
    justify-content: center;
  }
  
  .confirmation-card {
    padding: 4rem 3rem;
  }
}

@media (max-width: 480px) {
  .confirmation-view {
    padding: 1rem;
  }
  
  .confirmation-card {
    padding: 2rem 1.5rem;
  }
  
  .confirmation-title {
    font-size: 1.5rem;
  }
  
  .confirmation-message {
    font-size: 1rem;
  }
}
</style>
