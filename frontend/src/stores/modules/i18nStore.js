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
import termsEn from '@/locales/auth/terms/en.json'
import termsEs from '@/locales/auth/terms/es.json'
import privacyEn from '@/locales/auth/privacy/en.json'
import privacyEs from '@/locales/auth/privacy/es.json'

// Import products translations
import productsEn from '@/locales/products/en.json'
import productsEs from '@/locales/products/es.json'

// Import product detail translations
import productDetailEn from '@/locales/products/product-detail/en.json'
import productDetailEs from '@/locales/products/product-detail/es.json'

// Import product reviews translations
import productReviewsEn from '@/locales/products/reviews/en.json'
import productReviewsEs from '@/locales/products/reviews/es.json'

// Import cart translations
import cartEn from '@/locales/shared/cart/en.json'
import cartEs from '@/locales/shared/cart/es.json'

// Import navbar translations
import navbarEn from '@/locales/shared/navbar/en.json'
import navbarEs from '@/locales/shared/navbar/es.json'

// Import footer translations
import footerEn from '@/locales/shared/footer/en.json'
import footerEs from '@/locales/shared/footer/es.json'

// Import FAQ translations
import faqEn from '@/locales/shared/faq/en.json'
import faqEs from '@/locales/shared/faq/es.json'

// Import about us translations
import aboutUsEn from '@/locales/about_us/en.json'
import aboutUsEs from '@/locales/about_us/es.json'

// Import contact translations
import contactEn from '@/locales/contact/en.json'
import contactEs from '@/locales/contact/es.json'

// Import diaries translations
import diariesEn from '@/locales/diaries/en.json'
import diariesEs from '@/locales/diaries/es.json'
import publicProfileEn from '@/locales/diaries/public-profile/en.json'
import publicProfileEs from '@/locales/diaries/public-profile/es.json'
import userSearchEn from '@/locales/diaries/user-search/en.json'
import userSearchEs from '@/locales/diaries/user-search/es.json'
import youMayKnowEn from '@/locales/diaries/you-may-know/en.json'
import youMayKnowEs from '@/locales/diaries/you-may-know/es.json'

// Import alerts translations
import alertsEn from '@/locales/alerts/en.json'
import alertsEs from '@/locales/alerts/es.json'

// Import home translations
import heroEn from '@/locales/home/hero/en.json'
import heroEs from '@/locales/home/hero/es.json'
import trendingEn from '@/locales/home/trending/en.json'
import trendingEs from '@/locales/home/trending/es.json'
import notesEn from '@/locales/home/notes/en.json'
import notesEs from '@/locales/home/notes/es.json'
import ctasEn from '@/locales/home/ctas/en.json'
import ctasEs from '@/locales/home/ctas/es.json'
import categoriesEn from '@/locales/home/categories/en.json'
import categoriesEs from '@/locales/home/categories/es.json'

// Import profile translations
import profileSidebarEn from '@/locales/profile/sidebar/en.json'
import profileSidebarEs from '@/locales/profile/sidebar/es.json'
import profileDashboardEn from '@/locales/profile/dashboard/en.json'
import profileDashboardEs from '@/locales/profile/dashboard/es.json'
import profileFormEn from '@/locales/profile/form/en.json'
import profileFormEs from '@/locales/profile/form/es.json'
import profileWishlistEn from '@/locales/profile/wishlist/en.json'
import profileWishlistEs from '@/locales/profile/wishlist/es.json'
import profileFavoritesEn from '@/locales/profile/favorites/en.json'
import profileFavoritesEs from '@/locales/profile/favorites/es.json'

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
    terms: termsEn,
    privacy: privacyEn,
    products: productsEn,
    productDetail: productDetailEn,
    productReviews: productReviewsEn,
    cart: cartEn,
    navbar: navbarEn.navbar,
    aboutUs: aboutUsEn,
    contact: contactEn,
    diaries: {
      ...diariesEn,
      publicProfile: publicProfileEn,
      userSearch: userSearchEn,
      youMayKnow: youMayKnowEn
    },
    alerts: alertsEn,
    footer: footerEn.footer,
    faq: faqEn,
    hero: heroEn,
    trending: trendingEn,
    notes: notesEn,
    ctas: ctasEn,
    categories: categoriesEn,
    profileSidebar: profileSidebarEn,
    profileDashboard: profileDashboardEn,
    profile: {
      form: profileFormEn,
      wishlist: profileWishlistEn,
      favorites: profileFavoritesEn
    }
  },
  es: {
    login: loginEs,
    signup: signupEs,
    verification: verificationEs,
    forgotPassword: forgotPasswordEs,
    resetCode: resetCodeEs,
    resetPassword: resetPasswordEs,
    confirmation: confirmationEs,
    terms: termsEs,
    privacy: privacyEs,
    products: productsEs,
    productDetail: productDetailEs,
    productReviews: productReviewsEs,
    cart: cartEs,
    navbar: navbarEs.navbar,
    aboutUs: aboutUsEs,
    contact: contactEs,
    diaries: {
      ...diariesEs,
      publicProfile: publicProfileEs,
      userSearch: userSearchEs,
      youMayKnow: youMayKnowEs
    },
    alerts: alertsEs,
    footer: footerEs.footer,
    faq: faqEs,
    hero: heroEs,
    trending: trendingEs,
    notes: notesEs,
    ctas: ctasEs,
    categories: categoriesEs,
    profileSidebar: profileSidebarEs,
    profileDashboard: profileDashboardEs,
    profile: {
      form: profileFormEs,
      wishlist: profileWishlistEs,
      favorites: profileFavoritesEs
    }
  }
}

export const useI18nStore = defineStore('i18n', {
  state: () => ({
    locale: 'en',
    countryCode: null,
    isInitialized: false,
    detectedLocale: null
  }),
  actions: {
    setLocale(newLocale) {
      this.locale = newLocale
      i18n.global.locale.value = newLocale
    },
    async detectUserLanguage() {
      try {
        // Add timeout to prevent hanging
        const response = await axios.get('https://ipapi.co/json/', {
          timeout: 3000 // 3 seconds timeout
        })
        this.countryCode = response.data.country_code
        
        // Set Spanish for Spanish-speaking countries, English for others
        const detectedLocale = spanishSpeakingCountries.includes(this.countryCode) ? 'es' : 'en'
        this.detectedLocale = detectedLocale
        
        return detectedLocale
      } catch (error) {
        console.warn('Failed to detect user language, using default:', error.message)
        // Fallback to English on error
        this.detectedLocale = 'en'
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
