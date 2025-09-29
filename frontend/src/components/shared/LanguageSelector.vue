<template>
  <div class="language-selector" :class="positionClass">
    <button 
      @click="changeLanguage('en')"
      :class="{ 'active': i18nStore.locale === 'en' }"
      class="lang-btn"
      :title="'English'"
    >
      EN
    </button>
    <button 
      @click="changeLanguage('es')"
      :class="{ 'active': i18nStore.locale === 'es' }"
      class="lang-btn"
      :title="'Español'"
    >
      ES
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'

const props = defineProps({
  position: {
    type: String,
    default: 'fixed', // 'fixed', 'relative', 'absolute'
    validator: (value) => ['fixed', 'relative', 'absolute'].includes(value)
  },
  size: {
    type: String,
    default: 'normal', // 'small', 'normal', 'large'
    validator: (value) => ['small', 'normal', 'large'].includes(value)
  },
  theme: {
    type: String,
    default: 'light', // 'light', 'dark', 'transparent'
    validator: (value) => ['light', 'dark', 'transparent'].includes(value)
  }
})

const router = useRouter()
const i18nStore = useI18nStore()

// Computed class for positioning
const positionClass = computed(() => {
  return `position-${props.position} size-${props.size} theme-${props.theme}`
})

const changeLanguage = (locale) => {
  i18nStore.setLocale(locale)
  
  // Get current route without language prefix
  const currentPath = router.currentRoute.value.path
  const pathWithoutLang = currentPath.substring(3) // Remove /en or /es
  
  // Navigate to the same route but with new language
  router.push(`/${locale}${pathWithoutLang}`)
}
</script>

<style scoped>
.language-selector {
  display: flex;
  gap: 0.5rem;
  z-index: 50;
}

/* Position variants */
.position-fixed {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
}

.position-absolute {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
}

.position-relative {
  position: relative;
}

/* Size variants */
.size-small .lang-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  border-radius: 6px;
}

.size-normal .lang-btn {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  border-radius: 8px;
}

.size-large .lang-btn {
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border-radius: 10px;
}

/* Base button styles */
.lang-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(64, 101, 130, 0.3);
  font-family: 'Comfortaa', cursive;
  font-weight: 600;
  color: #406582;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  outline: none;
}

.lang-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: #406582;
  transform: translateY(-1px);
}

.lang-btn.active {
  background: #406582;
  color: white;
  border-color: #406582;
}

/* Theme variants */
.theme-light .lang-btn {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(64, 101, 130, 0.3);
  color: #406582;
}

.theme-light .lang-btn:hover {
  background: rgba(255, 255, 255, 1);
  border-color: #406582;
}

.theme-light .lang-btn.active {
  background: #406582;
  color: white;
  border-color: #406582;
}

.theme-dark .lang-btn {
  background: rgba(17, 24, 30, 0.9);
  border-color: rgba(164, 193, 208, 0.3);
  color: #A4C1D0;
}

.theme-dark .lang-btn:hover {
  background: rgba(17, 24, 30, 1);
  border-color: #A4C1D0;
}

.theme-dark .lang-btn.active {
  background: #A4C1D0;
  color: #11181E;
  border-color: #A4C1D0;
}

.theme-transparent .lang-btn {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.theme-transparent .lang-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.theme-transparent .lang-btn.active {
  background: rgba(255, 255, 255, 0.9);
  color: #406582;
  border-color: rgba(255, 255, 255, 0.9);
}

/* Responsive design */
@media (max-width: 480px) {
  .position-fixed,
  .position-absolute {
    top: 1rem;
    right: 1rem;
  }
  
  .size-normal .lang-btn {
    padding: 0.4rem 0.6rem;
    font-size: 0.7rem;
  }
  
  .size-large .lang-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
  }
}

@media (max-width: 360px) {
  .size-small .lang-btn {
    padding: 0.2rem 0.4rem;
    font-size: 0.7rem;
  }
  
  .size-normal .lang-btn {
    padding: 0.3rem 0.5rem;
    font-size: 0.65rem;
  }
}
</style>
