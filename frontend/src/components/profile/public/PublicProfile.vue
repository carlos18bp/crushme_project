<template>
  <div class="public-profile">
    <!-- Header with gradient background -->
    <div class="profile-header">
      <div class="header-gradient"></div>
      
      <!-- Avatar -->
      <div class="avatar-container">
        <img 
          :src="profileData.avatar" 
          :alt="profileData.name"
          class="avatar-image"
        />
      </div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content">
      <!-- Username -->
      <div class="profile-info">
        <h1 class="profile-username">{{ profileData.username }}</h1>
      </div>

      <!-- Biography -->
      <div class="biography-section">
        <h3 class="section-title">Biography</h3>
        <div class="biography-text">
          {{ profileData.biography }}
        </div>
      </div>

      <!-- Three Column Grid: Links, State, Notes -->
      <div class="three-column-grid">
        <!-- My Links -->
        <div class="links-section">
          <h3 class="section-title">My Links</h3>
          <div class="links-buttons">
            <button 
              v-for="(link, index) in profileData.links" 
              :key="index"
              class="link-button"
              :style="{ backgroundColor: link.color }"
            >
              {{ link.label }}
            </button>
          </div>
        </div>

        <!-- My State -->
        <div class="info-card">
          <h3 class="section-title">My state</h3>
          <p class="info-text">{{ profileData.state }}</p>
        </div>

        <!-- Notes -->
        <div class="info-card">
          <h3 class="section-title">Notes</h3>
          <p class="info-text">{{ profileData.notes }}</p>
        </div>
      </div>

      <!-- Gallery -->
      <div class="gallery-section">
        <h3 class="section-title">Gallery</h3>
        <div class="gallery-grid">
          <div 
            v-for="(image, index) in profileData.gallery" 
            :key="index"
            class="gallery-item"
          >
            <img 
              :src="image" 
              :alt="`Gallery image ${index + 1}`"
              class="gallery-image"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Mock profile data - esto luego vendrá de props o API
const profileData = ref({
  avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
  name: 'Mary Jackson',
  username: '@username',
  biography: `Hi! I'm [Your Name], a friendly, upbeat webcam model who loves good conversation, cozy vibes, and a touch of playful energy. On my shows you'll find smiles, laughter, and a welcoming space where we can relax, chat, and enjoy the moment together. I'm into [interests: gaming/fitness/cosplay/music], so don't be shy about asking questions or sharing what you love too.

I value respect and positive energy. Please be polite, keep requests within platform rules, and remember I don't do meetups—everything stays online and between consenting adults (18+). Tips and requests help me create more content and upgrade my setup, and I'm always grateful for your support.

Schedule: [Days/Times] ([Timezone]).
What to expect: friendly chats, playful banter, themed outfits, and interactive goals.
Support: follows, tips, and kind words mean the world—thank you!
Hit follow, turn on notifications, and say hi when you join. Let's make great memories together. 💫`,
  links: [
    { label: 'Instagram', color: '#C77DFF' },
    { label: 'Facebook', color: '#C77DFF' },
    { label: 'Stream', color: '#C77DFF' }
  ],
  state: 'Sweet smiles, playful vibes—come say hi ✨',
  notes: `Welcome to my room! This is a respectful, 18+ space. I don't do meetups or off-platform chats, and I follow site rules. Tips and kind words keep the show going and help upgrade my setup. Custom requests? Ask first and be polite. Schedule: [Days/Times, Timezone]. Thanks for being sweet and supportive! 💫`,
  gallery: [
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400',
    'https://images.unsplash.com/photo-1488716820095-cbe80883c496?w=400',
    'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400',
    'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400',
    'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400',
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400',
    'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
    'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400'
  ]
})
</script>

<style scoped>
/* Container */
.public-profile {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

/* Header Section */
.profile-header {
  position: relative;
  width: 100%;
  height: 200px;
}

.header-gradient {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, 
    #60a5fa 0%,    /* blue-400 */
    #a78bfa 25%,   /* violet-400 */
    #f472b6 50%,   /* pink-400 */
    #fb7185 75%,   /* rose-400 */
    #ef4444 100%   /* red-500 */
  );
}

/* Avatar */
.avatar-container {
  position: absolute;
  bottom: -40px;
  left: 32px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid white;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Profile Content */
.profile-content {
  padding: 56px 32px 32px 32px;
}

/* Profile Info */
.profile-info {
  margin-bottom: 24px;
}

.profile-username {
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 700;
  color: #11181E;
  margin: 0;
}

/* Section Titles */
.section-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #11181E;
  margin: 0 0 12px 0;
}

/* Biography Section */
.biography-section {
  margin-bottom: 24px;
}

.biography-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #475569;
  white-space: pre-line;
}

/* Three Column Grid: Links, State, Notes */
.three-column-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

/* Links Section */
.links-section {
  display: flex;
  flex-direction: column;
}

.links-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-button {
  width: 100%;
  padding: 12px 24px;
  border: none;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.link-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.link-button:active {
  transform: translateY(0);
}

/* Info Card */
.info-card {
  display: flex;
  flex-direction: column;
}

.info-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #475569;
  margin: 0;
}

/* Gallery Section */
.gallery-section {
  margin-bottom: 0;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.gallery-item {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f5f9;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover .gallery-image {
  transform: scale(1.05);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .profile-content {
    padding: 56px 20px 20px 20px;
  }

  .avatar-container {
    left: 20px;
    width: 80px;
    height: 80px;
  }

  .three-column-grid {
    grid-template-columns: 1fr;
  }

  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

