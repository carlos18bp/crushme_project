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
/* Container - Mobile First */
.user-search {
  background: white;
  border-radius: 1rem;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media (min-width: 640px) {
  .user-search {
    padding: 24px;
  }
}

@media (min-width: 1024px) {
  .user-search {
    padding: 32px;
  }
}

/* Search Container - Mobile First */
.search-container {
  position: relative;
  margin-bottom: 16px;
}

@media (min-width: 640px) {
  .search-container {
    margin-bottom: 20px;
  }
}

@media (min-width: 1024px) {
  .search-container {
    margin-bottom: 24px;
  }
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
  width: 18px;
  height: 18px;
}

@media (min-width: 640px) {
  .search-icon {
    left: 14px;
    width: 19px;
    height: 19px;
  }
}

@media (min-width: 1024px) {
  .search-icon {
    left: 16px;
    width: 20px;
    height: 20px;
  }
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  color: #11181E;
  background: white;
  transition: all 0.2s ease;
}

@media (min-width: 640px) {
  .search-input {
    padding: 11px 14px 11px 44px;
    border-radius: 11px;
    font-size: 0.875rem;
  }
}

@media (min-width: 1024px) {
  .search-input {
    padding: 12px 16px 12px 48px;
    border-radius: 12px;
    font-size: 0.9375rem;
  }
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  outline: none;
  border-color: #C77DFF;
  box-shadow: 0 0 0 3px rgba(199, 125, 255, 0.1);
}

/* Users List - Mobile First */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

@media (min-width: 640px) {
  .users-list {
    gap: 4px;
  }
}

/* User Item - Mobile First */
.user-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

@media (min-width: 640px) {
  .user-item {
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
  }
}

.user-item:hover {
  background: #f8fafc;
}

.user-item.selected {
  background: #e0f2fe;
  border: 1px solid #38bdf8;
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

.username-container {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.username {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #11181E;
}

@media (min-width: 640px) {
  .username {
    font-size: 0.875rem;
  }
}

@media (min-width: 1024px) {
  .username {
    font-size: 0.9375rem;
  }
}

.user-role {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  font-weight: 400;
  color: #64748b;
}

@media (min-width: 640px) {
  .user-role {
    font-size: 0.875rem;
  }
}

@media (min-width: 1024px) {
  .user-role {
    font-size: 0.9375rem;
  }
}

/* Crush Label - Mobile First */
.crush-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.75rem;
  font-weight: 400;
  color: #FF3FD5;
}

@media (min-width: 640px) {
  .crush-label {
    gap: 5px;
    font-size: 0.8125rem;
  }
}

@media (min-width: 1024px) {
  .crush-label {
    gap: 6px;
    font-size: 0.9375rem;
  }
}

.crush-dot {
  width: 5px;
  height: 5px;
  background-color: #FF3FD5;
  border-radius: 50%;
  flex-shrink: 0;
}

@media (min-width: 1024px) {
  .crush-dot {
    width: 6px;
    height: 6px;
  }
}

/* Loading State - Mobile First */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 16px;
  gap: 10px;
}

@media (min-width: 640px) {
  .loading-state {
    padding: 35px 18px;
    gap: 11px;
  }
}

@media (min-width: 1024px) {
  .loading-state {
    padding: 40px 20px;
    gap: 12px;
  }
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid #f3f4f6;
  border-top-color: #C77DFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@media (min-width: 640px) {
  .loading-spinner {
    width: 30px;
    height: 30px;
  }
}

@media (min-width: 1024px) {
  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f4f6;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
}

@media (min-width: 1024px) {
  .loading-text {
    font-size: 0.875rem;
  }
}

/* Empty State - Mobile First */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 16px;
  gap: 10px;
}

@media (min-width: 640px) {
  .empty-state {
    padding: 35px 18px;
    gap: 11px;
  }
}

@media (min-width: 1024px) {
  .empty-state {
    padding: 40px 20px;
    gap: 12px;
  }
}

.empty-icon {
  color: #cbd5e1;
  stroke-width: 1.5;
  width: 40px;
  height: 40px;
}

@media (min-width: 640px) {
  .empty-icon {
    width: 44px;
    height: 44px;
  }
}

@media (min-width: 1024px) {
  .empty-icon {
    width: 48px;
    height: 48px;
  }
}

.empty-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  color: #94a3b8;
  text-align: center;
  margin: 0;
}

@media (min-width: 1024px) {
  .empty-text {
    font-size: 0.875rem;
  }
}

/* Additional responsive tweaks */
@media (max-width: 480px) {
  .user-search {
    padding: 16px;
  }
  
  .search-container {
    margin-bottom: 12px;
  }
  
  .search-input {
    padding: 9px 10px 9px 36px;
    font-size: 0.75rem;
  }
  
  .search-icon {
    left: 10px;
    width: 16px;
    height: 16px;
  }
  
  .user-item {
    padding: 8px;
    gap: 8px;
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
  }
  
  .username {
    font-size: 0.75rem;
  }
  
  .crush-label {
    font-size: 0.7rem;
  }
  
  .crush-dot {
    width: 4px;
    height: 4px;
  }
}
</style>





