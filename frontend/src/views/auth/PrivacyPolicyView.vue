<template>
  <div class="privacy-view">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="privacy-main">
      <div class="privacy-container">
        <div class="privacy-content">
          
          <!-- Header -->
          <header class="privacy-header">
            <h1 class="privacy-title">{{ $t('privacy.title') }}</h1>
            <p class="privacy-subtitle">{{ $t('privacy.subtitle') }}</p>
          </header>
          
          <!-- Introduction -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.introduction.title') }}</h2>
            <p class="section-content">{{ $t('privacy.introduction.content') }}</p>
          </section>
          
          <!-- Information Collection -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.informationCollection.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.informationCollection.subtitle') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in informationCollectionItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Automatic Collection -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.automaticCollection.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.automaticCollection.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in automaticCollectionItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Use of Information -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.useOfInformation.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.useOfInformation.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in useOfInformationItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Information Sharing -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.informationSharing.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.informationSharing.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in informationSharingItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Discrete Shipping -->
          <section class="privacy-section highlight">
            <h2 class="section-title">{{ $t('privacy.sections.discreteShipping.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.discreteShipping.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in discreteShippingItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Gift Privacy -->
          <section class="privacy-section highlight">
            <h2 class="section-title">{{ $t('privacy.sections.giftPrivacy.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.giftPrivacy.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in giftPrivacyItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Data Security -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.dataSecurity.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.dataSecurity.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in dataSecurityItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Data Retention -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.dataRetention.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.dataRetention.content') }}</p>
          </section>
          
          <!-- Your Rights -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.yourRights.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.yourRights.content') }}</p>
            <ul class="section-list">
              <li v-for="(item, index) in yourRightsItems" :key="index">
                {{ item }}
              </li>
            </ul>
          </section>
          
          <!-- Age Verification -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.ageVerification.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.ageVerification.content') }}</p>
          </section>
          
          <!-- Third Party Links -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.thirdPartyLinks.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.thirdPartyLinks.content') }}</p>
          </section>
          
          <!-- International -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.international.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.international.content') }}</p>
          </section>
          
          <!-- Changes -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.changes.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.changes.content') }}</p>
          </section>
          
          <!-- Contact -->
          <section class="privacy-section">
            <h2 class="section-title">{{ $t('privacy.sections.contact.title') }}</h2>
            <p class="section-content">{{ $t('privacy.sections.contact.content') }}</p>
            <p class="contact-info">{{ $t('privacy.sections.contact.email') }}</p>
            <p class="contact-info">{{ $t('privacy.sections.contact.support') }}</p>
          </section>
          
          <!-- Commitment -->
          <div class="privacy-commitment">
            <p class="commitment-text">{{ $t('privacy.commitment') }}</p>
          </div>
          
          <!-- Back Button -->
          <div class="privacy-actions">
            <router-link 
              :to="`/${i18nStore.locale}`"
              class="back-button"
            >
              {{ $t('privacy.backButton') }}
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
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useI18nStore } from '@/stores/modules/i18nStore'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'

// Store
const i18nStore = useI18nStore()
const { t } = useI18n()

// Computed properties for arrays - usando índices numéricos
const informationCollectionItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.informationCollection.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.informationCollection.items.${i}`)
    if (item && !item.includes('privacy.sections.informationCollection.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const automaticCollectionItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.automaticCollection.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.automaticCollection.items.${i}`)
    if (item && !item.includes('privacy.sections.automaticCollection.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const useOfInformationItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.useOfInformation.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.useOfInformation.items.${i}`)
    if (item && !item.includes('privacy.sections.useOfInformation.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const informationSharingItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.informationSharing.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.informationSharing.items.${i}`)
    if (item && !item.includes('privacy.sections.informationSharing.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const discreteShippingItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.discreteShipping.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.discreteShipping.items.${i}`)
    if (item && !item.includes('privacy.sections.discreteShipping.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const giftPrivacyItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.giftPrivacy.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.giftPrivacy.items.${i}`)
    if (item && !item.includes('privacy.sections.giftPrivacy.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const dataSecurityItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.dataSecurity.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.dataSecurity.items.${i}`)
    if (item && !item.includes('privacy.sections.dataSecurity.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})

const yourRightsItems = computed(() => {
  const items = []
  let i = 0
  while (t(`privacy.sections.yourRights.items.${i}`, null) !== null) {
    const item = t(`privacy.sections.yourRights.items.${i}`)
    if (item && !item.includes('privacy.sections.yourRights.items')) {
      items.push(item)
      i++
    } else {
      break
    }
  }
  return items
})
</script>

<style scoped>
.privacy-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fdf2f8;
}

.privacy-main {
  flex: 1;
  padding-top: 100px;
  padding-bottom: 4rem;
}

.privacy-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 2rem;
}

.privacy-content {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* Header */
.privacy-header {
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.privacy-title {
  font-family: 'Comfortaa', cursive;
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.privacy-subtitle {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #6b7280;
  font-style: italic;
}

/* Sections */
.privacy-section {
  margin-bottom: 2.5rem;
}

.privacy-section.highlight {
  background: #f0fdf4;
  border-left: 4px solid #10b981;
  padding: 1.5rem;
  border-radius: 8px;
  margin: 2rem 0;
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
  margin-bottom: 1rem;
}

.section-list {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #4b5563;
  line-height: 1.8;
  padding-left: 2rem;
  margin: 1rem 0;
}

.section-list li {
  margin-bottom: 0.5rem;
  text-align: justify;
}

.contact-info {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #6b7280;
  margin: 0.5rem 0;
  font-weight: 500;
}

/* Commitment */
.privacy-commitment {
  background: #eff6ff;
  border-left: 4px solid #DA9DFF;
  padding: 1.5rem;
  margin: 2rem 0;
  border-radius: 8px;
}

.commitment-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #1e40af;
  font-weight: 500;
  margin: 0;
  text-align: center;
}

/* Actions */
.privacy-actions {
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
  .privacy-main {
    padding-top: 80px;
    padding-bottom: 2rem;
  }
  
  .privacy-container {
    padding: 0 1rem;
  }
  
  .privacy-content {
    padding: 2rem 1.5rem;
  }
  
  .privacy-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.25rem;
  }
  
  .section-content {
    font-size: 0.9375rem;
    text-align: left;
  }
  
  .section-list {
    padding-left: 1.5rem;
    font-size: 0.9375rem;
  }
  
  .section-list li {
    text-align: left;
  }
}

@media (max-width: 480px) {
  .privacy-title {
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

