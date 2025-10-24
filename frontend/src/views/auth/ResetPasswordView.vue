<template>
  <div class="reset-password-view">
    <!-- Background -->
    <div class="background-container">
      <div class="background-overlay"></div>
    </div>
    
    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="light" />
    
    <!-- Reset Password Form Container -->
    <div class="reset-password-container">
      <div class="reset-password-card">
        <!-- Welcome Message -->
        <div class="welcome-section">
          <h2 class="welcome-title">{{ $t('resetPassword.title') }}</h2>
          <p class="welcome-subtitle">{{ $t('resetPassword.subtitle') }}</p>
        </div>
        
        <!-- Reset Password Form -->
        <form @submit.prevent="handleResetPassword" class="reset-password-form">
          <!-- New Password Input -->
          <div class="input-group">
            <div class="password-input-container">
              <input
                v-model="form.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                :placeholder="$t('resetPassword.newPasswordPlaceholder')"
                class="form-input password-input"
                required
                minlength="8"
                autocomplete="new-password"
              />
              <button
                type="button"
                @click="toggleNewPassword"
                class="password-toggle"
              >
                <svg v-if="showNewPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Confirm Password Input -->
          <div class="input-group">
            <div class="password-input-container">
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                :placeholder="$t('resetPassword.confirmPasswordPlaceholder')"
                class="form-input password-input"
                required
                autocomplete="new-password"
              />
              <button
                type="button"
                @click="toggleConfirmPassword"
                class="password-toggle"
              >
                <svg v-if="showConfirmPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Password Strength Indicator -->
          <div class="password-strength" v-if="form.newPassword">
            <div class="strength-label">{{ getPasswordStrengthLabel() }}</div>
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :class="getPasswordStrengthClass()"
                :style="{ width: getPasswordStrengthWidth() }"
              ></div>
            </div>
          </div>
          
          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">{{ $t('resetPassword.updateButton') }}</span>
            <span v-else class="loading-spinner">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ $t('resetPassword.updatingButton') }}
            </span>
          </button>
        </form>
        
        <!-- Back to Code Verification -->
        <div class="back-link">
          <router-link :to="`/${i18nStore.locale}/reset-code?email=${email.value}`" class="back-link-text">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ $t('resetPassword.backToCode') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { useAlert } from '@/composables/useAlert'
import LanguageSelector from '@/components/shared/LanguageSelector.vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const i18nStore = useI18nStore()
const authStore = useAuthStore()
const { showError, showSuccess } = useAlert()

// Get params from query
const email = ref(route.query.email || '')
const resetCode = ref(route.query.reset_code || '')

// Reactive form data
const form = reactive({
  newPassword: '',
  confirmPassword: ''
})

const isLoading = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// Password visibility toggles
const toggleNewPassword = () => {
  showNewPassword.value = !showNewPassword.value
}

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

// Password strength validation
const passwordStrength = computed(() => {
  const password = form.newPassword
  let score = 0
  
  if (password.length >= 8) score++
  if (password.match(/[a-z]/)) score++
  if (password.match(/[A-Z]/)) score++
  if (password.match(/[0-9]/)) score++
  if (password.match(/[^a-zA-Z0-9]/)) score++
  
  return score
})

const getPasswordStrengthLabel = () => {
  const strength = passwordStrength.value
  if (strength < 2) return 'Weak'
  if (strength < 4) return 'Medium'
  return 'Strong'
}

const getPasswordStrengthClass = () => {
  const strength = passwordStrength.value
  if (strength < 2) return 'strength-weak'
  if (strength < 4) return 'strength-medium'
  return 'strength-strong'
}

const getPasswordStrengthWidth = () => {
  return `${(passwordStrength.value / 5) * 100}%`
}

// Form validation
const validateForm = () => {
  if (!form.newPassword || !form.confirmPassword) {
    showError(t('resetPassword.validation.fillAllFields'))
    return false
  }
  
  if (form.newPassword.length < 8) {
    showError(t('resetPassword.validation.passwordLength'))
    return false
  }
  
  if (form.newPassword !== form.confirmPassword) {
    showError(t('resetPassword.validation.passwordsMatch'))
    return false
  }
  
  if (passwordStrength.value < 3) {
    showError(t('resetPassword.validation.passwordStrength'))
    return false
  }
  
  return true
}

// Handle form submission
const handleResetPassword = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  try {
    // Call auth store to reset password
    const result = await authStore.resetPassword({
      email: email.value,
      reset_code: resetCode.value,
      new_password: form.newPassword,
      new_password_confirm: form.confirmPassword
    })
    
    if (result.success) {
      // On success, redirect to confirmation with success message
      router.push({
        path: `/${i18nStore.locale}/confirmation`,
        query: {
          title: t('resetPassword.success.title'),
          message: t('resetPassword.success.message'),
          primaryActionText: t('resetPassword.success.actionButton'),
          primaryActionRoute: `/${i18nStore.locale}/login`
        }
      })
    } else {
      // Handle reset password errors
      let errorMessage = t('resetPassword.errors.updateFailed')
      
      if (result.error?.reset_code) {
        errorMessage = t('resetPassword.errors.invalidToken')
      } else if (result.error?.new_password) {
        errorMessage = t('resetPassword.errors.weakPassword')
      } else if (typeof result.error === 'string') {
        errorMessage += result.error
      } else {
        errorMessage += 'Error desconocido'
      }
      
      showError(errorMessage)
    }
    
  } catch (error) {
    console.error('Password reset failed:', error)
    showError(t('resetPassword.errors.updateFailed') + (error.message || 'Unknown error'))
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.reset-password-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Comfortaa', sans-serif;
}

.background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/backgrounds/background_1.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(250, 243, 243, 0.3) 0%, rgba(218, 157, 255, 0.2) 50%, rgba(164, 193, 208, 0.3) 100%);
  backdrop-filter: blur(8px);
}

.reset-password-container {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 450px;
  padding: 0 2rem;
}

.reset-password-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2.5rem 2rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
}

.welcome-section {
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.welcome-subtitle {
  font-size: 1rem;
  color: #6b7280;
  line-height: 1.5;
  margin: 0;
}

.reset-password-form {
  width: 100%;
}

.input-group {
  margin-bottom: 1.5rem;
}

.password-input-container {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 1rem 3rem 1rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  color: #1f2937;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #DA9DFF;
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
  background: white;
}

.form-input:hover {
  border-color: #d1d5db;
}

.form-input::placeholder {
  color: #9ca3af;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  transition: color 0.3s ease;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  color: #4b5563;
}

.password-strength {
  margin-bottom: 1.5rem;
}

.strength-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.strength-bar {
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 2px;
}

.strength-weak {
  background: #ef4444;
}

.strength-medium {
  background: #f59e0b;
}

.strength-strong {
  background: #10b981;
}

.submit-btn {
  width: 100%;
  background: #DA9DFF;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(218, 157, 255, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-link {
  text-align: center;
}

.back-link-text {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.3s ease;
}

.back-link-text:hover {
  color: #4b5563;
}

/* Responsive */
@media (max-width: 480px) {
  .reset-password-container {
    padding: 0 1rem;
  }
  
  .reset-password-card {
    padding: 2rem 1.5rem;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .form-input {
    padding: 0.875rem 2.5rem 0.875rem 0.875rem;
  }
}
</style>

