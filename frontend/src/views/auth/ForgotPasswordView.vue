<template>
  <div class="forgot-password-view">
    <!-- Background -->
    <div class="background-container">
      <div class="background-overlay"></div>
    </div>

    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="light" />

    <!-- Forgot Password Form Container -->
    <div class="forgot-password-container">
      <div class="forgot-password-card">
        <!-- Welcome Message -->
        <div class="welcome-section">
          <h2 class="welcome-title">{{ $t('forgotPassword.title') }}</h2>
          <p class="welcome-subtitle">{{ $t('forgotPassword.subtitle') }}</p>
        </div>

        <!-- Forgot Password Form -->
        <form @submit.prevent="handleForgotPassword" class="forgot-password-form">
          <!-- Email Input -->
          <div class="input-group">
            <input
              v-model="form.email"
              type="email"
              :placeholder="$t('forgotPassword.emailPlaceholder')"
              class="form-input"
              required
            />
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">{{ $t('forgotPassword.sendButton') }}</span>
            <span v-else class="loading-spinner">
              <svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.25"/>
                <path d="M4 12C4 16.4183 7.58172 20 12 20V12H4Z" fill="currentColor"/>
              </svg>
              {{ $t('forgotPassword.sendingButton') }}
            </span>
          </button>
        </form>

        <!-- Back to login link -->
        <div class="back-to-login">
          <router-link :to="`/${i18nStore.locale}/login`" class="back-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ $t('forgotPassword.backToLogin') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/modules/authStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useAlert } from '@/composables/useAlert'
import LanguageSelector from '@/components/shared/LanguageSelector.vue'

const router = useRouter()
const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = useI18n()
const { showError } = useAlert()

// Reactive form data
const form = reactive({
  email: ''
})

// Component state
const isLoading = ref(false)

// Methods
const validateForm = () => {
  // Check email is provided
  if (!form.email) {
    showError(t('forgotPassword.validation.emailRequired'))
    return false
  }

  // Check email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    showError(t('forgotPassword.validation.validEmail'))
    return false
  }

  return true
}

const handleForgotPassword = async () => {
  isLoading.value = true
  
  try {
    // Validate form
    if (!validateForm()) {
      return
    }

    // Call auth store forgot password method
    const result = await authStore.forgotPassword(form.email.trim())

    if (result.success) {
      // Redirect to reset code verification page
      router.push({
        path: `/${i18nStore.locale}/reset-code`,
        query: {
          email: form.email.trim()
        }
      })
    } else {
      // Handle forgot password errors
      let errorMessage = t('forgotPassword.errors.sendFailed')
      
      if (result.error?.includes('not found') || result.error?.includes('does not exist')) {
        errorMessage = t('forgotPassword.errors.emailNotFound')
      } else if (result.error?.includes('too many') || result.error?.includes('429')) {
        errorMessage = t('forgotPassword.errors.tooManyRequests')
      } else {
        errorMessage += result.error
      }
      
      showError(errorMessage)
    }

  } catch (error) {
    console.error('Forgot password error:', error)
    showError(t('forgotPassword.errors.sendFailed') + (error.message || 'Error desconocido'))
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.forgot-password-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  font-family: 'Comfortaa', cursive;
  overflow: hidden;
}

/* Background */
.background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.background-overlay {
  width: 100%;
  height: 100%;
  background-image: url('@/assets/backgrounds/background_1.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.background-overlay::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(1px);
}

/* Main Container */
.forgot-password-container {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.forgot-password-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 2rem 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Welcome Section */
.welcome-section {
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-title {
  font-family: 'Comfortaa', cursive;
  font-weight: 600;
  font-size: 1.5rem;
  color: #11181E;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.welcome-subtitle {
  font-family: 'Comfortaa', cursive;
  font-weight: 400;
  font-size: 1rem;
  color: #6B7280;
  margin: 0;
  line-height: 1.5;
}

/* Form */
.forgot-password-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  font-family: 'Comfortaa', cursive;
  font-size: 0.95rem;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  outline: none;
}

.form-input::placeholder {
  color: #9CA3AF;
  font-weight: 400;
}

.form-input:focus {
  border-color: #DA9DFF;
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
  background: white;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #DA9DFF;
  color: white;
  border: none;
  border-radius: 12px;
  font-family: 'Comfortaa', cursive;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(218, 157, 255, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Back to Login */
.back-to-login {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #E5E7EB;
  font-family: 'Comfortaa', cursive;
}

.back-link {
  color: #BF5E81;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.back-link:hover {
  color: #D689A2;
  transform: translateX(-2px);
}

.back-link svg {
  transition: all 0.2s ease;
}

.back-link:hover svg {
  transform: translateX(-2px);
}

/* Responsive Design */
@media (max-width: 480px) {
  .forgot-password-container {
    padding: 0.5rem;
  }
  
  .forgot-password-card {
    padding: 1.5rem 1.25rem;
    max-width: 100%;
  }
  
  .welcome-title {
    font-size: 1.3rem;
  }
  
  .welcome-subtitle {
    font-size: 0.9rem;
  }
}

@media (max-width: 360px) {
  .form-input {
    padding: 0.875rem 1rem;
    font-size: 0.9rem;
  }
  
  .submit-btn {
    padding: 0.875rem;
    font-size: 0.95rem;
  }
}
</style>
