<template>
  <div class="diaries-view">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main Content -->
    <main class="min-h-screen bg-brand-pink-lighter pt-32 pb-16">
      <div class="container mx-auto px-4">
        <!-- 4 Column Grid Layout -->
        <div class="diaries-grid">
          <!-- First Component: Public Profile (2 columns) -->
          <div class="profile-column">
            <PublicProfile />
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
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'
import PublicProfile from '@/components/profile/public/PublicProfile.vue'
import YouMayKnow from '@/components/profile/public/YouMayKnow.vue'
import UserSearch from '@/components/profile/public/UserSearch.vue'
</script>

<style scoped>
/* Container styles */
.container {
  max-width: 1600px;
  margin: 0 auto;
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

