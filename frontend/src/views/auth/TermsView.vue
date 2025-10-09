<template>
  <div class="terms-view">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="terms-main">
      <div class="terms-container">
        <div class="terms-content">
          
          <!-- Header -->
          <header class="terms-header">
            <h1 class="terms-title">{{ $t('terms.title') }}</h1>
            <p class="terms-subtitle">{{ $t('terms.subtitle') }}</p>
          </header>
          
          <!-- Introduction -->
          <section class="terms-section">
            <h2 class="section-title">{{ $t('terms.introduction.title') }}</h2>
            <p class="section-content">{{ $t('terms.introduction.content') }}</p>
          </section>
          
          <!-- All Sections -->
          <section 
            v-for="section in sections" 
            :key="section"
            class="terms-section"
          >
            <h2 class="section-title">{{ $t(`terms.sections.${section}.title`) }}</h2>
            <p class="section-content">{{ $t(`terms.sections.${section}.content`) }}</p>
          </section>
          
          <!-- Agreement -->
          <div class="terms-agreement">
            <p class="agreement-text">{{ $t('terms.agreement') }}</p>
          </div>
          
          <!-- Back Button -->
          <div class="terms-actions">
            <router-link 
              :to="`/${i18nStore.locale}`"
              class="back-button"
            >
              {{ $t('terms.backButton') }}
            </router-link>
          </div>
          
        </div>
      </div>
    </main>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { useI18nStore } from '@/stores/modules/i18nStore'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'

// Store
const i18nStore = useI18nStore()

// Section keys for v-for
const sections = [
  'acceptance',
  'ageRequirement',
  'accountSecurity',
  'products',
  'gifting',
  'privacy',
  'payments',
  'prohibitedUse',
  'intellectualProperty',
  'disclaimer',
  'limitation',
  'termination',
  'changes',
  'contact'
]
</script>

<style scoped>
.terms-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fdf2f8;
}

.terms-main {
  flex: 1;
  padding-top: 100px;
  padding-bottom: 4rem;
}

.terms-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

.terms-content {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* Header */
.terms-header {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.terms-title {
  font-family: 'Comfortaa', cursive;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.terms-subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #6b7280;
  font-style: italic;
}

/* Sections */
.terms-section {
  margin-bottom: 2.5rem;
}

.section-title {
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
}

.section-content {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #4b5563;
  line-height: 1.8;
  text-align: justify;
}

/* Agreement */
.terms-agreement {
  background: #eff6ff;
  border-left: 4px solid #DA9DFF;
  padding: 1.5rem;
  margin: 2rem 0;
  border-radius: 8px;
}

.agreement-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #1e40af;
  font-weight: 500;
  margin: 0;
}

/* Actions */
.terms-actions {
  display: flex;
  justify-content: center;
  margin-top: 3rem;
}

.back-button {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: #DA9DFF;
  padding: 0.875rem 2rem;
  border-radius: 25px;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(218, 157, 255, 0.3);
}

.back-button:hover {
  background: #c084fc;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(218, 157, 255, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .terms-main {
    padding-top: 80px;
    padding-bottom: 2rem;
  }
  
  .terms-container {
    padding: 0 1rem;
  }
  
  .terms-content {
    padding: 2rem 1.5rem;
  }
  
  .terms-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.25rem;
  }
  
  .section-content {
    font-size: 0.9375rem;
    text-align: left;
  }
}

@media (max-width: 480px) {
  .terms-title {
    font-size: 1.75rem;
  }
  
  .section-title {
    font-size: 1.125rem;
  }
  
  .back-button {
    width: 100%;
    text-align: center;
  }
}
</style>

