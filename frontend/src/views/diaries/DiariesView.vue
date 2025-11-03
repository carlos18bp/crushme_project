<template>
  <div class="diaries-view">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="min-h-screen bg-brand-pink-lighter pt-20 md:pt-28 lg:pt-32 pb-12 md:pb-16">
      <div class="container mx-auto px-4 md:px-6 lg:px-4">
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
          <!-- Mobile Order: Search → YouMayKnow → Profile -->
          <!-- Desktop Order: Profile (2 cols) → Search + YouMayKnow (2 cols) -->
          
          <!-- User Search component - First on mobile -->
          <div class="search-column">
            <UserSearch />
          </div>
          
          <!-- You may know component - Second on mobile -->
          <div class="you-may-know-column">
            <YouMayKnow />
          </div>
          
          <!-- Public Profile - Third on mobile, spans 2 columns on desktop -->
          <div class="profile-column">
            <PublicProfile :profile-data="profileData" />
          </div>
        </div>
      </div>
    </main>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useCrushStore } from '@/stores'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'
import PublicProfile from '@/components/profile/public/PublicProfile.vue'
import YouMayKnow from '@/components/profile/public/YouMayKnow.vue'
import UserSearch from '@/components/profile/public/UserSearch.vue'

// Props (username from route)
const props = defineProps({
  username: {
    type: String,
    default: null
  }
})

const crushStore = useCrushStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// Mapear los datos del API al formato que espera PublicProfile
// Usa crushProfile si está disponible (cuando se selecciona un usuario específico)
// Si no, usa randomCrush (por defecto al cargar la página)
const profileData = computed(() => {
  const crush = crushStore.crushProfile || crushStore.randomCrush
  if (!crush) return null

  return {
    avatar: crush.profile_picture_url || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
    coverImage: crush.cover_image_url || null, // Cover image del usuario
    name: crush.username,
    username: `@${crush.username}`,
    biography: crush.about || t('diaries.publicProfile.defaultBiography'),
    links: crush.links?.map(link => ({
      label: link.title || link.platform,
      color: '#C77DFF',
      url: link.url
    })) || [],
    state: crush.current_status || 'Online',
    notes: crush.note || '',
    gallery: crush.gallery_photos?.map(photo => photo.image) || [],
    wishlists: crush.public_wishlists || [] // Wishlists públicas del usuario
  }
})

// Cargar perfil de usuario específico o crush aleatorio
async function loadProfile() {
  // Obtener username de props o de la ruta
  const username = props.username || route.params.username
  
  if (username) {
    // Si hay un username, cargar ese perfil específico
    try {
      await crushStore.fetchPublicProfile(username)
      console.log(`✅ Perfil de @${username} cargado en DiariesView`)
    } catch (error) {
      console.error(`❌ Error cargando perfil de @${username}:`, error)
    }
  } else {
    // Si no hay username, cargar un crush aleatorio
    try {
      const randomCrush = await crushStore.fetchRandomCrush()
      console.log('✅ Crush aleatorio cargado en DiariesView')
      
      // Actualizar la URL con el username del crush aleatorio
      if (randomCrush && randomCrush.username) {
        const currentLang = route.path.split('/')[1] || 'en'
        router.replace(`/${currentLang}/diaries/@${randomCrush.username}`)
        console.log(`🔗 URL actualizada a: /${currentLang}/diaries/@${randomCrush.username}`)
      }
    } catch (error) {
      console.error('❌ Error cargando crush aleatorio:', error)
    }
  }
}

// Cargar perfil aleatorio cuando se inicializa
async function loadRandomCrush() {
  try {
    await crushStore.fetchRandomCrush()
    console.log('✅ Crush aleatorio cargado en DiariesView')
  } catch (error) {
    console.error('❌ Error cargando crush aleatorio:', error)
  }
}

// Watch para cambios en el username de la ruta
watch(() => route.params.username, (newUsername, oldUsername) => {
  // Solo recargar si el username cambió y es diferente
  if (newUsername && newUsername !== oldUsername) {
    loadProfile()
  }
})

onMounted(() => {
  loadProfile()
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
  min-height: 300px;
  gap: 16px;
}

@media (min-width: 768px) {
  .loading-container {
    min-height: 400px;
    gap: 20px;
  }
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #C77DFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@media (min-width: 768px) {
  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid #f3f4f6;
    border-top: 4px solid #C77DFF;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #6b7280;
}

@media (min-width: 768px) {
  .loading-text {
    font-size: 1rem;
  }
}

/* Error State */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
  padding: 1rem;
}

@media (min-width: 768px) {
  .error-container {
    min-height: 400px;
    gap: 20px;
    padding: 0;
  }
}

.error-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #ef4444;
  text-align: center;
  max-width: 90%;
}

@media (min-width: 768px) {
  .error-text {
    font-size: 1rem;
    max-width: 100%;
  }
}

.retry-button {
  padding: 10px 24px;
  background: #C77DFF;
  color: white;
  border: none;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

@media (min-width: 768px) {
  .retry-button {
    padding: 12px 32px;
    border-radius: 24px;
    font-size: 0.875rem;
  }
}

.retry-button:hover {
  background: #a855f7;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.retry-button:active {
  transform: translateY(0);
}

/* Diaries Grid - Mobile First */
.diaries-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: stretch;
}

@media (min-width: 768px) {
  .diaries-grid {
    gap: 20px;
  }
}

@media (min-width: 1024px) {
  .diaries-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    align-items: start;
  }
}

/* Search Column - First on mobile, right side on desktop */
.search-column {
  width: 100%;
  order: 1;
}

@media (min-width: 1024px) {
  .search-column {
    grid-column: 3 / 5;
    grid-row: 1;
    order: initial;
  }
}

/* You May Know Column - Second on mobile, right side below search on desktop */
.you-may-know-column {
  width: 100%;
  order: 2;
}

@media (min-width: 1024px) {
  .you-may-know-column {
    grid-column: 3 / 5;
    grid-row: 2;
    order: initial;
  }
}

/* Profile Column - Third on mobile, left side (2 cols) on desktop */
.profile-column {
  width: 100%;
  order: 3;
}

@media (min-width: 1024px) {
  .profile-column {
    grid-column: 1 / 3;
    grid-row: 1 / 3;
    order: initial;
  }
}
</style>

