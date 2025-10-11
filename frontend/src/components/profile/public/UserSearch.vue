<template>
  <div class="user-search">
    <!-- Search Input -->
    <div class="search-container">
      <svg class="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM18 18l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <input 
        v-model="searchQuery"
        type="text" 
        :placeholder="$t('diaries.userSearch.placeholder')"
        class="search-input"
      />
    </div>
    
    <!-- Loading State -->
    <div v-if="crushStore.isSearching" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">{{ $t('diaries.userSearch.searching') }}</p>
    </div>
    
    <!-- Empty State (No query) -->
    <div v-else-if="!searchQuery.trim()" class="empty-state">
      <svg class="empty-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
      <p class="empty-text">{{ $t('diaries.userSearch.startTyping') }}</p>
    </div>
    
    <!-- No Results -->
    <div v-else-if="crushStore.searchResults.length === 0" class="empty-state">
      <svg class="empty-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="15" y1="9" x2="9" y2="15"></line>
        <line x1="9" y1="9" x2="15" y2="15"></line>
      </svg>
      <p class="empty-text">{{ $t('diaries.userSearch.noResults') }}</p>
    </div>
    
    <!-- Users List -->
    <div v-else class="users-list">
      <div 
        v-for="user in crushStore.searchResults" 
        :key="user.id"
        class="user-item"
        @click="navigateToProfile(user.username)"
      >
        <!-- Avatar -->
        <div class="user-avatar">
          <img 
            :src="user.profile_picture_url || 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200'" 
            :alt="user.username"
            class="avatar-img"
          />
        </div>
        
        <!-- User Info -->
        <div class="user-info">
          <div class="username-container">
            <span class="username">@{{ user.username }}</span>
            <span v-if="user.is_crush" class="crush-label">
              <span class="crush-dot"></span>
              Crush
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCrushStore } from '@/stores'
import { useI18nStore } from '@/stores/modules/i18nStore'

const router = useRouter()
const crushStore = useCrushStore()
const i18nStore = useI18nStore()

// Search query
const searchQuery = ref('')
let searchTimeout = null

// Watch search query with debounce
watch(searchQuery, (newQuery) => {
  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // Clear search if query is empty
  if (!newQuery.trim()) {
    crushStore.clearSearch()
    return
  }
  
  // Debounce search (300ms)
  searchTimeout = setTimeout(async () => {
    try {
      await crushStore.searchUsers(newQuery.trim(), 10)
    } catch (error) {
      console.error('Error searching users:', error)
    }
  }, 300)
})

// Navigate to user profile
const navigateToProfile = (username) => {
  console.log('🔍 Navegando al perfil de:', username)
  
  // Limpiar búsqueda después de seleccionar
  searchQuery.value = ''
  crushStore.clearSearch()
  
  // Navegar a la URL del usuario
  const currentLang = i18nStore.locale
  router.push(`/${currentLang}/diaries/@${username}`)
  
  // Scroll suave hacia arriba para ver el perfil
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<style scoped>
/* Container */
.user-search {
  background: white;
  border-radius: 1rem;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Search Container */
.search-container {
  position: relative;
  margin-bottom: 24px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  color: #11181E;
  background: white;
  transition: all 0.2s ease;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  outline: none;
  border-color: #C77DFF;
  box-shadow: 0 0 0 3px rgba(199, 125, 255, 0.1);
}

/* Users List */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* User Item */
.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-item:hover {
  background: #f8fafc;
}

.user-item.selected {
  background: #e0f2fe;
  border: 1px solid #38bdf8;
}

/* Avatar */
.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: #f1f5f9;
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

.username-container {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.username {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #11181E;
}

.user-role {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 400;
  color: #64748b;
}

/* Crush Label */
.crush-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 400;
  color: #FF3FD5;
}

.crush-dot {
  width: 6px;
  height: 6px;
  background-color: #FF3FD5;
  border-radius: 50%;
  flex-shrink: 0;
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
  border-top-color: #C77DFF;
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

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
}

.empty-icon {
  color: #cbd5e1;
  stroke-width: 1.5;
}

.empty-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #94a3b8;
  text-align: center;
  margin: 0;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .user-search {
    padding: 24px;
  }
  
  .search-input {
    font-size: 0.875rem;
  }
  
  .username {
    font-size: 0.875rem;
  }
  
  .crush-label {
    font-size: 0.875rem;
  }
  
  .crush-dot {
    width: 5px;
    height: 5px;
  }
}
</style>




