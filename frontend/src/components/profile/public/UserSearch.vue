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
        placeholder="Search by @username"
        class="search-input"
      />
    </div>
    
    <!-- Users List -->
    <div class="users-list">
      <div 
        v-for="(user, index) in filteredUsers" 
        :key="index"
        class="user-item"
        :class="{ 'selected': user.selected }"
      >
        <!-- Avatar -->
        <div class="user-avatar">
          <img 
            :src="user.avatar" 
            :alt="user.username"
            class="avatar-img"
          />
        </div>
        
        <!-- User Info -->
        <div class="user-info">
          <div class="username-container">
            <span class="username">{{ user.username }}</span>
            <span v-if="user.role" class="user-role">• {{ user.role }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Search query
const searchQuery = ref('')

// Mock users data
const users = ref([
  {
    username: '@maryla',
    role: 'Webcammer',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200',
    selected: false
  },
  {
    username: '@jhonbi',
    role: '',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200',
    selected: false
  },
  {
    username: '@guiller89',
    role: '',
    avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200',
    selected: true
  }
])

// Filtered users based on search
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query)
  )
})
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

/* Responsive adjustments */
@media (max-width: 640px) {
  .user-search {
    padding: 24px;
  }
  
  .search-input {
    font-size: 0.875rem;
  }
}
</style>

