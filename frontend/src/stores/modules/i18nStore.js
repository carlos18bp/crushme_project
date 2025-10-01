import { defineStore } from 'pinia'
import { createI18n } from 'vue-i18n'
import axios from 'axios'

// Import auth translations by module
import loginEn from '@/locales/auth/login/en.json'
import loginEs from '@/locales/auth/login/es.json'
import signupEn from '@/locales/auth/signup/en.json'
import signupEs from '@/locales/auth/signup/es.json'
import verificationEn from '@/locales/auth/verification/en.json'
import verificationEs from '@/locales/auth/verification/es.json'
import forgotPasswordEn from '@/locales/auth/forgot-password/en.json'
import forgotPasswordEs from '@/locales/auth/forgot-password/es.json'
import resetCodeEn from '@/locales/auth/reset-code/en.json'
import resetCodeEs from '@/locales/auth/reset-code/es.json'
import resetPasswordEn from '@/locales/auth/reset-password/en.json'
import resetPasswordEs from '@/locales/auth/reset-password/es.json'
import confirmationEn from '@/locales/auth/confirmation/en.json'
import confirmationEs from '@/locales/auth/confirmation/es.json'

// Import products translations
import productsEn from '@/locales/products/en.json'
import productsEs from '@/locales/products/es.json'

// Import cart translations
import cartEn from '@/locales/shared/cart/en.json'
import cartEs from '@/locales/shared/cart/es.json'

// Import navbar translations
import navbarEn from '@/locales/shared/navbar/en.json'
import navbarEs from '@/locales/shared/navbar/es.json'

// Import footer translations
import footerEn from '@/locales/shared/footer/en.json'
import footerEs from '@/locales/shared/footer/es.json'

// Import about us translations
import aboutUsEn from '@/locales/about_us/en.json'
import aboutUsEs from '@/locales/about_us/es.json'

// List of countries where Spanish is the primary language
const spanishSpeakingCountries = [
  'AR', 'BO', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GQ',
  'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'ES', 'UY', 'VE'
]

// Combine all messages
const messages = {
  en: {
    login: loginEn,
    signup: signupEn,
    verification: verificationEn,
    forgotPassword: forgotPasswordEn,
    resetCode: resetCodeEn,
    resetPassword: resetPasswordEn,
    confirmation: confirmationEn,
    products: productsEn,
    cart: cartEn,
    navbar: navbarEn.navbar,
    aboutUs: aboutUsEn,
    footer: footerEn.footer
  },
  es: {
    login: loginEs,
    signup: signupEs,
    verification: verificationEs,
    forgotPassword: forgotPasswordEs,
    resetCode: resetCodeEs,
    resetPassword: resetPasswordEs,
    confirmation: confirmationEs,
    products: productsEs,
    cart: cartEs,
    navbar: navbarEs.navbar,
    aboutUs: aboutUsEs,
    footer: footerEs.footer
  }
}

export const useI18nStore = defineStore('i18n', {
  state: () => ({
    locale: 'en',
    countryCode: null,
    isInitialized: false
  }),
  actions: {
    setLocale(newLocale) {
      this.locale = newLocale
      i18n.global.locale.value = newLocale
    },
    async detectUserLanguage() {
      try {
        const response = await axios.get('https://ipapi.co/json/')
        this.countryCode = response.data.country_code
        
        // Set Spanish for Spanish-speaking countries, English for others
        const detectedLocale = spanishSpeakingCountries.includes(this.countryCode) ? 'es' : 'en'
        this.setLocale(detectedLocale)
        
        return detectedLocale
      } catch (error) {
        console.error('Error detecting user language:', error)
        // Fallback to English on error
        this.setLocale('en')
        return 'en'
      } finally {
        this.isInitialized = true
      }
    },
    // Initialize language detection when Pinia is available
    async initializeIfNeeded() {
      if (!this.isInitialized) {
        await this.detectUserLanguage()
      }
    }
  },
  persist: true
})

export const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages
})
