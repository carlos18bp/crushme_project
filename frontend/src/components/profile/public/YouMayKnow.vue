<template>
  <div class="you-may-know">
    <!-- Title -->
    <h2 class="component-title">{{ $t('diaries.youMayKnow.title') }}</h2>
    
    <!-- Loading State -->
    <div v-if="isLocalLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ $t('diaries.youMayKnow.loading') }}</p>
    </div>
    
    <!-- Error State -->
    <div v-else-if="localError" class="error-state">
      <p class="error-text">{{ localError }}</p>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="crushes.length === 0" class="empty-state">
      <p class="empty-text">{{ $t('diaries.youMayKnow.noCrushes') }}</p>
    </div>
    
    <!-- Users List -->
    <div v-else class="users-list">
      <div 
        v-for="crush in crushes" 
        :key="crush.id"
        class="user-item"
        @click="navigateToCrush(crush.username)"
      >
        <!-- Avatar -->
        <div class="user-avatar">
          <img 
            :src="crush.profile_picture_url || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200'" 
            :alt="crush.username"
            class="avatar-img"
          />
        </div>
        
        <!-- User Info -->
        <div class="user-info">
          <h3 class="user-name">@{{ crush.username }}</h3>
          <p class="user-description">
            <span class="crush-dot"></span>
            <span class="crush-text">Crush</span>
          </p>
        </div>
        
        <!-- Watch Button -->
        <button class="watch-button" @click.stop="navigateToCrush(crush.username)">
          {{ $t('diaries.youMayKnow.viewProfile') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCrushStore } from '@/stores'
import { useI18nStore } from '@/stores/modules/i18nStore'

const router = useRouter()
const crushStore = useCrushStore()
const i18nStore = useI18nStore()

// Local loading state (no usar el global para evitar conflictos)
const isLocalLoading = ref(false)
const localError = ref(null)

// Get first 5 crushes from the list
const crushes = computed(() => crushStore.crushList.slice(0, 5))

// Load crushes on mount - only if not already loaded
onMounted(async () => {
  // Evitar cargar si ya hay crushes en el store
  if (crushStore.crushList.length > 0) {
    console.log('✅ Crushes ya cargados, usando caché')
    return
  }

  isLocalLoading.value = true
  localError.value = null
  
  try {
    await crushStore.fetchCrushList(5, 0)
    console.log('✅ Crushes loaded in YouMayKnow')
  } catch (error) {
    console.error('❌ Error loading crushes:', error)
    localError.value = error.message || 'Error al cargar crushes'
  } finally {
    isLocalLoading.value = false
  }
})

// Navigate to crush profile
const navigateToCrush = (username) => {
  console.log('🔍 Navegando al perfil de crush:', username)
  
  // Navegar a la URL del crush
  const currentLang = i18nStore.locale
  router.push(`/${currentLang}/diaries/@${username}`)
  
  // Scroll suave hacia arriba para ver el perfil
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
/* Container - Mobile First */
.you-may-know {
  background: white;
  border-radius: 1rem;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media (min-width: 640px) {
  .you-may-know {
    padding: 24px;
  }
}

@media (min-width: 1024px) {
  .you-may-know {
    padding: 32px;
  }
}

/* Title - Mobile First */
.component-title {
  font-family: 'Comfortaa', cursive;
  font-size: 1.125rem;
  font-weight: 700;
  color: #11181E;
  margin: 0 0 16px 0;
}

@media (min-width: 640px) {
  .component-title {
    font-size: 1.25rem;
    margin: 0 0 20px 0;
  }
}

@media (min-width: 1024px) {
  .component-title {
    font-size: 1.5rem;
    margin: 0 0 24px 0;
  }
}

/* Users List - Mobile First */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

@media (min-width: 640px) {
  .users-list {
    gap: 16px;
  }
}

@media (min-width: 1024px) {
  .users-list {
    gap: 20px;
  }
}

/* User Item */
.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.user-item:hover {
  background: #f8fafc;
}

/* Avatar - Mobile First */
.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: #f1f5f9;
}

@media (min-width: 640px) {
  .user-avatar {
    width: 44px;
    height: 44px;
  }
}

@media (min-width: 1024px) {
  .user-avatar {
    width: 48px;
    height: 48px;
  }
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* User Info */
.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #11181E;
  margin: 0 0 2px 0;
}

@media (min-width: 640px) {
  .user-name {
    font-size: 0.875rem;
  }
}

@media (min-width: 1024px) {
  .user-name {
    font-size: 0.9375rem;
  }
}

.user-description {
  font-family: 'Poppins', sans-serif;
  font-size: 0.75rem;
  color: #FF3FD5;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (min-width: 640px) {
  .user-description {
    font-size: 0.8125rem;
    gap: 6px;
  }
}

.crush-dot {
  width: 6px;
  height: 6px;
  background-color: #FF3FD5;
  border-radius: 50%;
  flex-shrink: 0;
}

.crush-text {
  color: #FF3FD5;
}

/* Watch Button - Mobile First */
.watch-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.75rem;
  font-weight: 500;
  color: #11181E;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

@media (min-width: 640px) {
  .watch-button {
    gap: 6px;
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 0.8125rem;
  }
}

@media (min-width: 1024px) {
  .watch-button {
    padding: 8px 20px;
    font-size: 0.875rem;
  }
}

.watch-button:hover {
  background: #e2e8f0;
}

.plus-icon {
  font-size: 1.125rem;
  font-weight: 600;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top-color: #FF3FD5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

/* Error State */
.error-state {
  padding: 20px;
  text-align: center;
}

.error-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #dc2626;
  margin: 0;
}

/* Empty State */
.empty-state {
  padding: 20px;
  text-align: center;
}

.empty-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0;
}

/* Additional responsive tweaks */
@media (max-width: 480px) {
  .you-may-know {
    padding: 16px;
  }
  
  .component-title {
    font-size: 1rem;
    margin: 0 0 12px 0;
  }
  
  .users-list {
    gap: 10px;
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
  }
  
  .watch-button {
    padding: 5px 10px;
    font-size: 0.7rem;
  }
}
</style>




