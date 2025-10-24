<template>
  <div class="verification-view">
    <!-- Background -->
    <div class="background-container">
      <div class="background-overlay"></div>
    </div>

    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="light" />

    <!-- Verification Form Container -->
    <div class="verification-container">
      <div class="verification-card">
        <!-- Welcome Message -->
        <div class="welcome-section">
          <h2 class="welcome-title">{{ $t('verification.title') }}</h2>
          <p class="welcome-subtitle">{{ $t('verification.subtitle') }}</p>
        </div>

        <!-- Verification Form -->
        <form @submit.prevent="handleVerification" class="verification-form">
          <!-- Code Input -->
          <div class="code-input-container">
            <input
              v-for="(digit, index) in codeDigits"
              :key="index"
              :ref="el => codeInputs[index] = el"
              v-model="codeDigits[index]"
              type="text"
              maxlength="1"
              :placeholder="$t('verification.codePlaceholder')"
              class="code-input"
              @input="handleCodeInput(index, $event)"
              @keydown="handleKeyDown(index, $event)"
              @paste="handlePaste($event)"
              required
            />
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="isLoading || !isCodeComplete"
          >
            <span v-if="!isLoading">{{ $t('verification.verifyButton') }}</span>
            <span v-else class="loading-spinner">
              <svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.25"/>
                <path d="M4 12C4 16.4183 7.58172 20 12 20V12H4Z" fill="currentColor"/>
              </svg>
              {{ $t('verification.verifyingButton') }}
            </span>
          </button>
        </form>

        <!-- Resend link -->
        <div class="resend-section">
          <span class="resend-text">{{ $t('verification.didntReceive') }}</span>
          <button 
            @click="handleResend" 
            class="resend-link"
            :disabled="isResending || resendCooldown > 0"
          >
            <span v-if="resendCooldown > 0">{{ resendCooldown }}s</span>
            <span v-else-if="!isResending">{{ $t('verification.resend') }}</span>
            <span v-else>{{ $t('verification.resendingButton') }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
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

// Code input refs
const codeInputs = ref([])

// Reactive form data
const codeDigits = reactive(['', '', '', ''])

// Component state
const isLoading = ref(false)
const isResending = ref(false)
const resendCooldown = ref(0)
let resendInterval = null

// Computed
const isCodeComplete = computed(() => {
  return codeDigits.every(digit => digit.length === 1)
})

const verificationCode = computed(() => {
  return codeDigits.join('')
})

// Methods
const handleCodeInput = (index, event) => {
  const value = event.target.value
  
  // Only allow numbers
  if (!/^\d*$/.test(value)) {
    codeDigits[index] = ''
    return
  }
  
  codeDigits[index] = value
  
  // Auto-focus next input
  if (value && index < 3) {
    codeInputs.value[index + 1]?.focus()
  }
}

const handleKeyDown = (index, event) => {
  // Handle backspace
  if (event.key === 'Backspace' && !codeDigits[index] && index > 0) {
    codeInputs.value[index - 1]?.focus()
  }
  
  // Handle arrow keys
  if (event.key === 'ArrowLeft' && index > 0) {
    codeInputs.value[index - 1]?.focus()
  }
  
  if (event.key === 'ArrowRight' && index < 3) {
    codeInputs.value[index + 1]?.focus()
  }
}

const handlePaste = (event) => {
  event.preventDefault()
  const pastedData = event.clipboardData.getData('text')
  const digits = pastedData.replace(/\D/g, '').slice(0, 4).split('')
  
  digits.forEach((digit, index) => {
    if (index < 4) {
      codeDigits[index] = digit
    }
  })
  
  // Focus the next empty input or the last one
  const nextEmptyIndex = codeDigits.findIndex(digit => !digit)
  const focusIndex = nextEmptyIndex !== -1 ? nextEmptyIndex : 3
  codeInputs.value[focusIndex]?.focus()
}

const validateCode = () => {
  if (!isCodeComplete.value) {
    showError(t('verification.validation.codeRequired'))
    return false
  }
  
  if (verificationCode.value.length !== 4) {
    showError(t('verification.validation.codeLength'))
    return false
  }
  
  return true
}

const handleVerification = async () => {
  isLoading.value = true
  
  try {
    // Validate code
    if (!validateCode()) {
      return
    }

    // Get email from route params or query
    const email = route.query.email || route.params.email

    // Call auth store verification method
    const result = await authStore.verifyEmail({
      email: email,
      verification_code: verificationCode.value
    })

    if (result.success) {
      // Redirect to confirmation page
      router.push({
        path: `/${i18nStore.locale}/confirmation`,
        query: {
          title: t('verification.success.title'),
          message: t('verification.success.message'),
          primaryActionText: t('verification.success.actionButton'),
          primaryActionRoute: `/${i18nStore.locale}/profile`,
          autoRedirect: 'true',
          redirectDelay: '3',
          redirectTo: `/${i18nStore.locale}/profile`
        }
      })
    } else {
      // Handle verification errors
      let errorMessage = t('verification.errors.verificationFailed')
      
      if (result.error?.includes('invalid') || result.error?.includes('Invalid')) {
        errorMessage = t('verification.errors.invalidCode')
      } else if (result.error?.includes('expired') || result.error?.includes('Expired')) {
        errorMessage = t('verification.errors.codeExpired')
      } else {
        errorMessage += result.error
      }
      
      showError(errorMessage)
      
      // Clear the code inputs on error
      codeDigits.forEach((_, index) => {
        codeDigits[index] = ''
      })
      codeInputs.value[0]?.focus()
    }

  } catch (error) {
    console.error('Verification error:', error)
    showError(t('verification.errors.verificationFailed') + (error.message || 'Error desconocido'))
    
    // Clear the code inputs on error
    codeDigits.forEach((_, index) => {
      codeDigits[index] = ''
    })
    codeInputs.value[0]?.focus()
    
  } finally {
    isLoading.value = false
  }
}

const handleResend = async () => {
  isResending.value = true
  
  try {
    // Get email from route params or query
    const email = route.query.email || route.params.email

    // Call auth store resend method
    const result = await authStore.resendVerificationCode(email)
    
    if (result.success) {
      showSuccess(t('verification.resendSuccess'))
      
      // Start cooldown
      startResendCooldown()
    } else {
      showError(t('verification.errors.resendFailed') + result.error)
    }
    
  } catch (error) {
    console.error('Resend error:', error)
    showError(t('verification.errors.resendFailed') + (error.message || 'Error desconocido'))
  } finally {
    isResending.value = false
  }
}

const startResendCooldown = () => {
  resendCooldown.value = 60 // 60 seconds cooldown
  
  resendInterval = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(resendInterval)
    }
  }, 1000)
}

// Lifecycle
onMounted(() => {
  // Focus first input
  codeInputs.value[0]?.focus()
})

onUnmounted(() => {
  if (resendInterval) {
    clearInterval(resendInterval)
  }
})
</script>

<style scoped>
.verification-view {
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
.verification-container {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.verification-card {
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
  margin: 0 0 0.5rem 0;
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
.verification-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Code Input */
.code-input-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 1rem;
}

.code-input {
  width: 60px;
  height: 60px;
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  outline: none;
  color: #11181E;
}

.code-input::placeholder {
  color: #D1D5DB;
  font-weight: 400;
}

.code-input:focus {
  outline: none;
  border-color: #DA9DFF;
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
  background: white;
  transform: scale(1.05);
}

.code-input:not(:placeholder-shown) {
  border-color: #10B981;
  background: rgba(16, 185, 129, 0.05);
}

/* Submit Button */
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
  opacity: 0.5;
  cursor: not-allowed;
}

/* Resend Section */
.resend-section {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #E5E7EB;
  font-family: 'Comfortaa', cursive;
}

.resend-text {
  color: #6B7280;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.resend-btn {
  background: none;
  border: none;
  color: #DA9DFF;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  transition: color 0.3s ease;
  display: inline-flex;
  align-items: center;
}

.resend-btn:hover:not(:disabled) {
  color: #BF5E81;
}

.resend-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 480px) {
  .verification-container {
    padding: 0.5rem;
  }
  
  .verification-card {
    padding: 1.5rem 1.25rem;
    max-width: 100%;
  }
  
  .welcome-title {
    font-size: 1.3rem;
  }
  
  .welcome-subtitle {
    font-size: 0.9rem;
  }
  
  .code-input-container {
    gap: 0.75rem;
  }
  
  .code-input {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }
}

@media (max-width: 360px) {
  .code-input-container {
    gap: 0.5rem;
  }
  
  .code-input {
    width: 45px;
    height: 45px;
    font-size: 1.1rem;
  }
  
  .submit-btn {
    padding: 0.875rem;
    font-size: 0.95rem;
  }
}
</style>
