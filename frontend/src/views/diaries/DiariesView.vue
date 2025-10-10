<template>
  <div class="diaries-view">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="min-h-screen bg-brand-pink-lighter pt-32 pb-16">
      <div class="container mx-auto px-4">
        <!-- Loading State -->
        <div v-if="crushStore.isLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">{{ $t('diaries.publicProfile.loading') }}</p>
        </div>

        <!-- Error State -->
        <div v-else-if="crushStore.error" class="error-container">
          <p class="error-text">{{ crushStore.error }}</p>
          <button @click="loadRandomCrush" class="retry-button">{{ $t('diaries.publicProfile.retry') }}</button>
        </div>

        <!-- Content -->
        <div v-else class="diaries-grid">
          <!-- First Component: Public Profile (2 columns) -->
          <div class="profile-column">
            <PublicProfile :profile-data="profileData" />
          </div>
          
          <!-- Other Components (2 columns) -->
          <div class="other-columns">
            <!-- User Search component -->
            <UserSearch />
            
            <!-- You may know component -->
            <YouMayKnow />
          </div>
        </div>
      </div>
    </main>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCrushStore } from '@/stores'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'
import PublicProfile from '@/components/profile/public/PublicProfile.vue'
import YouMayKnow from '@/components/profile/public/YouMayKnow.vue'
import UserSearch from '@/components/profile/public/UserSearch.vue'

const crushStore = useCrushStore()
const { t } = useI18n()

// Mapear los datos del API al formato que espera PublicProfile
const profileData = computed(() => {
  const crush = crushStore.randomCrush
  if (!crush) return null

  return {
    avatar: crush.profile_picture_url || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
    coverImage: crush.cover_image_url || null, // Cover image del usuario
    name: crush.username,
    username: `@${crush.username}`,
    biography: crush.about || t('diaries.publicProfile.defaultBiography'),
    links: crush.links?.map(link => ({
      label: link.platform,
      color: '#C77DFF',
      url: link.url
    })) || [],
    state: crush.current_status || 'Online',
    notes: crush.note || '',
    gallery: crush.gallery_photos?.map(photo => photo.image) || [],
    wishlists: crush.public_wishlists || [] // Wishlists públicas del usuario
  }
})

// Cargar crush aleatorio cuando se inicializa el componente
async function loadRandomCrush() {
  try {
    await crushStore.fetchRandomCrush()
    console.log('✅ Crush aleatorio cargado en DiariesView')
  } catch (error) {
    console.error('❌ Error cargando crush aleatorio:', error)
  }
}

onMounted(() => {
  loadRandomCrush()
})
</script>

<style scoped>
/* Container styles */
.container {
  max-width: 1600px;
  margin: 0 auto;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #C77DFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #6b7280;
}

/* Error State */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 20px;
}

.error-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #ef4444;
  text-align: center;
}

.retry-button {
  padding: 12px 32px;
  background: #C77DFF;
  color: white;
  border: none;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: #a855f7;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.retry-button:active {
  transform: translateY(0);
}

/* Diaries Grid - 4 columns layout */
.diaries-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  align-items: start;
}

/* Profile Column - spans 2 columns */
.profile-column {
  grid-column: span 2;
}

/* Other Columns - spans 2 columns */
.other-columns {
  grid-column: span 2;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .diaries-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .profile-column,
  .other-columns {
    grid-column: span 1;
  }
}

@media (max-width: 640px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
  
  .diaries-grid {
    gap: 16px;
  }
}
</style>

