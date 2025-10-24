<template>
  <div class="reset-code-view">
    <!-- Background -->
    <div class="background-container">
      <div class="background-overlay"></div>
    </div>
    
    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="light" />
    
    <!-- Reset Code Form Container -->
    <div class="reset-code-container">
      <div class="reset-code-card">
        <!-- Welcome Message -->
        <div class="welcome-section">
          <h2 class="welcome-title">{{ $t('resetCode.title') }}</h2>
          <p class="welcome-subtitle">{{ $t('resetCode.subtitle') }}</p>
        </div>
        
        <!-- Reset Code Form -->
        <form @submit.prevent="handleVerification" class="reset-code-form">
          <!-- Code Inputs -->
          <div class="code-inputs">
            <input
              v-for="(digit, index) in code"
              :key="index"
              ref="codeInputs"
              v-model="code[index]"
              type="text"
              maxlength="1"
              inputmode="numeric"
              pattern="[0-9]"
              :placeholder="$t('resetCode.codePlaceholder')"
              class="code-input"
              @input="handleInput($event, index)"
              @keydown="handleKeyDown($event, index)"
              @paste="handlePaste($event, index)"
            />
          </div>
          
          <!-- Verify Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">{{ $t('resetCode.verifyButton') }}</span>
            <span v-else class="loading-spinner">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ $t('resetCode.verifyingButton') }}
            </span>
          </button>
        </form>
        
        <!-- Resend Code Link -->
        <div class="resend-link">
          <span class="resend-text">{{ $t('resetCode.didntReceive') }}</span>
          <button
            @click="resendCode"
            :disabled="isResending || resendCooldown > 0"
            class="resend-btn"
          >
            <span v-if="isResending" class="loading-spinner">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ $t('resetCode.resendingButton') }}
            </span>
            <span v-else-if="resendCooldown > 0">
              {{ resendCooldown }}s
            </span>
            <span v-else>{{ $t('resetCode.resend') }}</span>
          </button>
        </div>
        
        <!-- Back to Forgot Password -->
        <div class="back-link">
          <router-link :to="`/${i18nStore.locale}/forgot-password`" class="back-link-text">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ $t('resetCode.backToForgot') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
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

// Reactive form data
const code = reactive(['', '', '', ''])
const isLoading = ref(false)
const isResending = ref(false)
const resendCooldown = ref(0)
const codeInputs = ref([])

// Get email from query params or route state
const email = ref(route.query.email || '')

// Auto-focus first input on mount
onMounted(async () => {
  await nextTick()
  if (codeInputs.value && codeInputs.value[0]) {
    codeInputs.value[0].focus()
  }
})

// Handle input for code fields
const handleInput = (event, index) => {
  const value = event.target.value.replace(/[^0-9]/g, '')
  
  if (value.length <= 1) {
    code[index] = value
    
    // Move to next input if value is entered and not the last input
    if (value && index < 3) {
      nextTick(() => {
        codeInputs.value[index + 1]?.focus()
      })
    }
  }
}

// Handle key navigation
const handleKeyDown = (event, index) => {
  // Handle backspace
  if (event.key === 'Backspace' && !code[index] && index > 0) {
    nextTick(() => {
      codeInputs.value[index - 1]?.focus()
    })
  }
  
  // Handle arrow keys
  if (event.key === 'ArrowLeft' && index > 0) {
    codeInputs.value[index - 1]?.focus()
  }
  if (event.key === 'ArrowRight' && index < 3) {
    codeInputs.value[index + 1]?.focus()
  }
}

// Handle paste
const handlePaste = (event, index) => {
  event.preventDefault()
  const pastedData = event.clipboardData.getData('text').replace(/[^0-9]/g, '')
  
  for (let i = 0; i < Math.min(pastedData.length, 4 - index); i++) {
    code[index + i] = pastedData[i]
  }
  
  // Focus on the next empty input or the last one
  const nextIndex = Math.min(index + pastedData.length, 3)
  nextTick(() => {
    codeInputs.value[nextIndex]?.focus()
  })
}

// Handle form submission
const handleVerification = async () => {
  // Validation
  const codeString = code.join('')
  
  if (codeString.length !== 4) {
    showError(t('resetCode.validation.codeLength'))
    return
  }
  
  if (!/^\d{4}$/.test(codeString)) {
    showError(t('resetCode.validation.codeRequired'))
    return
  }
  
  // Redirect to reset password with email and code
  // The actual verification will happen in ResetPasswordView
  router.push({
    path: `/${i18nStore.locale}/reset-password`,
    query: {
      email: email.value,
      reset_code: codeString
    }
  })
}

// Resend code
const resendCode = async () => {
  if (resendCooldown.value > 0 || isResending.value) return
  
  isResending.value = true
  
  try {
    const result = await authStore.forgotPassword(email.value)
    
    if (result.success) {
      showSuccess(t('resetCode.resendSuccess'))
      
      // Start cooldown
      resendCooldown.value = 60
      const cooldownInterval = setInterval(() => {
        resendCooldown.value--
        if (resendCooldown.value <= 0) {
          clearInterval(cooldownInterval)
        }
      }, 1000)
    } else {
      showError(t('resetCode.errors.resendFailed') + result.error)
    }
    
  } catch (error) {
    console.error('Resend code failed:', error)
    showError(t('resetCode.errors.resendFailed') + (error.message || 'Unknown error'))
  } finally {
    isResending.value = false
  }
}
</script>

<style scoped>
.reset-code-view {
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

.reset-code-container {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 450px;
  padding: 0 2rem;
}

.reset-code-card {
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

.reset-code-form {
  width: 100%;
}

.code-inputs {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.code-input {
  width: 60px;
  height: 60px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.code-input:focus {
  outline: none;
  border-color: #DA9DFF;
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
  background: white;
}

.code-input:hover {
  border-color: #d1d5db;
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

.resend-link {
  text-align: center;
  margin-bottom: 1.5rem;
}

.resend-text {
  font-size: 0.875rem;
  color: #6b7280;
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
  color: #9ca3af;
  cursor: not-allowed;
  text-decoration: none;
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
  .reset-code-container {
    padding: 0 1rem;
  }
  
  .reset-code-card {
    padding: 2rem 1.5rem;
  }
  
  .welcome-title {
    font-size: 1.5rem;
  }
  
  .code-inputs {
    gap: 0.75rem;
  }
  
  .code-input {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }
}
</style>

