<template>
  <div class="you-may-know">
    <!-- Title -->
    <h2 class="component-title">You may know</h2>
    
    <!-- Users List -->
    <div class="users-list">
      <div 
        v-for="(user, index) in users" 
        :key="index"
        class="user-item"
      >
        <!-- Avatar -->
        <div class="user-avatar">
          <img 
            :src="user.avatar" 
            :alt="user.name"
            class="avatar-img"
          />
        </div>
        
        <!-- User Info -->
        <div class="user-info">
          <h3 class="user-name">{{ user.name }}</h3>
          <p class="user-description">{{ user.description }}</p>
        </div>
        
        <!-- Watch Button -->
        <button class="watch-button">
          <span class="plus-icon">+</span>
          Watch
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Mock users data
const users = ref([
  {
    name: 'Wade Warren',
    description: 'Informative text here',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200'
  },
  {
    name: 'Bessie Cooper',
    description: 'Informative text here',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200'
  },
  {
    name: 'Darrell Steward',
    description: 'Informative text here',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200'
  },
  {
    name: 'Eleanor Pena',
    description: 'Informative text here',
    avatar: 'https://images.unsplash.com/photo-1488716820095-cbe80883c496?w=200'
  }
])
</script>

<style scoped>
/* Container */
.you-may-know {
  background: white;
  border-radius: 1rem;
  padding: 32px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Title */
.component-title {
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 700;
  color: #11181E;
  margin: 0 0 24px 0;
}

/* Users List */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* User Item */
.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
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

.user-name {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #11181E;
  margin: 0 0 2px 0;
}

.user-description {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  color: #64748b;
  margin: 0;
}

/* Watch Button */
.watch-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: #11181E;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.watch-button:hover {
  background: #e2e8f0;
}

.plus-icon {
  font-size: 1.125rem;
  font-weight: 600;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .you-may-know {
    padding: 24px;
  }
  
  .component-title {
    font-size: 1.25rem;
  }
  
  .watch-button {
    padding: 6px 16px;
    font-size: 0.8125rem;
  }
}
</style>

