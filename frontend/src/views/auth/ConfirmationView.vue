<template>
  <div class="confirmation-view">
    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="light" />
    
    <!-- Content container -->
    <div class="confirmation-content">
      <!-- Title with emoji -->
      <h1 class="confirmation-title">{{ title }} 😍</h1>
      
      <!-- Auto redirect countdown if enabled -->
      <div v-if="autoRedirect && countdown > 0" class="countdown">
        {{ $t('confirmation.redirecting', { seconds: countdown }) }}
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
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden;
  font-family: 'Comfortaa', cursive;
  /* Gradiente suave de rosa a azul claro */
  background: linear-gradient(135deg, 
    #FFE5F0 0%, 
    #F5E6F7 25%, 
    #E6F2FF 50%, 
    #D4E8F5 75%, 
    #C7E0ED 100%
  );
}

.confirmation-content {
  position: relative;
  z-index: 2;
  width: 100%;
  text-align: center;
  animation: fadeInScale 0.8s ease-out;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.confirmation-title {
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 400;
  color: #2c3e50;
  margin: 0;
  line-height: 1.4;
  letter-spacing: -0.02em;
}

.countdown {
  font-family: 'Comfortaa', cursive;
  font-size: 0.875rem;
  color: #7f8c8d;
  margin-top: 1.5rem;
  font-weight: 300;
  opacity: 0.8;
}

/* Responsive design */
@media (min-width: 360px) {
  .confirmation-title {
    font-size: 1.75rem;
  }
}

@media (min-width: 480px) {
  .confirmation-view {
    padding: 2rem;
  }
  
  .confirmation-title {
    font-size: 2rem;
  }
  
  .countdown {
    font-size: 0.9rem;
    margin-top: 2rem;
  }
}

@media (min-width: 768px) {
  .confirmation-title {
    font-size: 2.5rem;
  }
  
  .countdown {
    font-size: 1rem;
  }
}
</style>
