<template>
  <div class="login-view">
    <!-- Background -->
    <div class="background-container">
      <div class="background-overlay"></div>
    </div>

    <!-- Language Selector -->
    <LanguageSelector position="absolute" theme="light" />

    <!-- Login Form Container -->
    <div class="login-container">
      <div class="login-card">
        <!-- Welcome Message -->
        <div class="welcome-section">
          <h2 class="welcome-title">{{ $t('login.title') }}</h2>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <!-- Email Input -->
          <div class="input-group">
            <input
              v-model="form.email"
              type="email"
              :placeholder="$t('login.emailPlaceholder')"
              class="form-input"
              required
            />
          </div>

          <!-- Password Input -->
          <div class="input-group">
            <div class="password-input-container">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="$t('login.passwordPlaceholder')"
                class="form-input password-input"
                required
              />
              <button
                type="button"
                @click="togglePassword"
                class="password-toggle"
              >
                <svg
                  v-if="!showPassword"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg
                  v-else
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M9.88 9.88C9.31 10.45 9 11.2 9 12C9 13.66 10.34 15 12 15C12.8 15 13.55 14.69 14.12 14.12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M10.73 5.08C11.15 5.03 11.57 5 12 5C19 5 23 12 23 12C22.18 13.65 20.69 15.12 18.8 16.17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M6.61 6.61C4.62 7.96 3.1 9.89 2 12C2 12 6 20 12 20C13.26 20 14.44 19.65 15.5 19.07" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="2" y1="2" x2="22" y2="22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Remember me and Forgot password -->
          <div class="form-options">
            <label class="remember-me">
              <input
                v-model="form.rememberMe"
                type="checkbox"
                class="checkbox"
              />
              <span class="checkbox-text">{{ $t('login.rememberMe') }}</span>
            </label>
            <router-link :to="`/${i18nStore.locale}/forgot-password`" class="forgot-password">
              {{ $t('login.forgotPassword') }}
            </router-link>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-btn"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">{{ $t('login.signInButton') }}</span>
            <span v-else class="loading-spinner">
              <svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-opacity="0.25"/>
                <path d="M4 12C4 16.4183 7.58172 20 12 20V12H4Z" fill="currentColor"/>
              </svg>
              {{ $t('login.signingIn') }}
            </span>
          </button>
        </form>

        <!-- Sign up link -->
        <div class="signup-link">
          <span class="signup-text">{{ $t('login.newHere') }}</span>
          <router-link :to="`/${i18nStore.locale}/signup`" class="signup-link-text">
            {{ $t('login.createAccount') }}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
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
import LanguageSelector from '@/components/shared/LanguageSelector.vue'

const router = useRouter()
const authStore = useAuthStore()
const i18nStore = useI18nStore()
const { t } = useI18n()

// Reactive form data
const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

// Component state
const showPassword = ref(false)
const isLoading = ref(false)

// Methods
const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  isLoading.value = true
  
  try {
    // Validate form
    if (!form.email || !form.password) {
      alert(t('login.validation.fillAllFields'))
      return
    }

    // Call auth store login method
    const result = await authStore.login({
      email: form.email,
      password: form.password
    })

    if (result.success) {
      // Redirect to confirmation page
      router.push({
        path: `/${i18nStore.locale}/confirmation`,
        query: {
          title: t('login.success.title'),
          message: t('login.success.message'),
          primaryActionText: t('login.success.actionButton'),
          primaryActionRoute: `/${i18nStore.locale}/profile`,
          autoRedirect: 'true',
          redirectDelay: '3',
          redirectTo: `/${i18nStore.locale}/profile`
        }
      })
    } else {
      // Handle login error
      alert(t('login.errors.loginFailed') + result.error)
    }

  } catch (error) {
    console.error('Login error:', error)
    alert(t('login.errors.loginFailed') + (error.message || 'Error desconocido'))
  } finally {
    isLoading.value = false
  }
}
</script>

<style>
/* Prevent any scroll globally when this view is active */
body {
  overflow: hidden !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
}
</style>

<style scoped>
.login-view {
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
.login-container {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 1.5rem 2rem;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Welcome Section */
.welcome-section {
  text-align: center;
  margin-bottom: 1rem;
}

.welcome-title {
  font-family: 'Comfortaa', cursive;
  font-weight: 500;
  font-size: 1.4rem;
  color: #11181E;
  margin: 0;
  line-height: 1.4;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  border-color: #406582;
  box-shadow: 0 0 0 3px rgba(64, 101, 130, 0.1);
  background: white;
}

/* Password Input */
.password-input-container {
  position: relative;
}

.password-input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6B7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.password-toggle:hover {
  color: #406582;
  background: rgba(64, 101, 130, 0.1);
}

/* Form Options */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.875rem;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-family: 'Comfortaa', cursive;
}

.checkbox {
  margin-right: 0.5rem;
  accent-color: #406582;
}

.checkbox-text {
  color: #6B7280;
  font-weight: 400;
}

.forgot-password {
  color: #BF5E81;
  text-decoration: none;
  font-family: 'Comfortaa', cursive;
  font-weight: 500;
  transition: all 0.2s ease;
}

.forgot-password:hover {
  color: #D689A2;
  text-decoration: underline;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #406582;
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
  background: #2D4A5F;
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(64, 101, 130, 0.3);
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

/* Signup Link */
.signup-link {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #E5E7EB;
  font-family: 'Comfortaa', cursive;
}

.signup-text {
  color: #6B7280;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.signup-link-text {
  color: #BF5E81;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s ease;
}

.signup-link-text:hover {
  color: #D689A2;
  transform: translateX(2px);
}

/* Responsive Design */
@media (max-width: 480px) {
  .login-container {
    padding: 0.5rem;
  }
  
  .login-card {
    padding: 1.5rem 1.25rem;
    max-width: 100%;
  }
  
  .welcome-title {
    font-size: 1.2rem;
  }
  
  .form-options {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
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
