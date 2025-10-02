<template>
  <div class="home-view">
    <!-- Background Image -->
    <div class="home-background">
      <img 
        src="@/assets/backgrounds/hero_bg.png" 
        alt="Home Background" 
        class="background-image"
      />
    </div>
    
    <!-- Content -->
    <div class="home-content">
      <!-- Navbar -->
      <Navbar />
      
      <!-- Hero Section -->
      <Hero />
      
      <!-- Trending Products Section -->
      <TrendingProducts />
      
      <!-- FAQ Section -->
      <FAQ />
      
      <!-- Footer -->
      <Footer />
    </div>
  </div>
</template>

<script setup>
import Navbar from '@/components/shared/Navbar.vue'
import Hero from '@/components/home/Hero.vue'
import TrendingProducts from '@/components/products/TrendingProducts.vue'
import FAQ from '@/components/shared/FAQ.vue'
import Footer from '@/components/shared/Footer.vue'
</script>

<style scoped>
.home-view {
  width: 100%;
  overflow-x: hidden;
  position: relative;
}

/* Background Image */
.home-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 0;
  pointer-events: none;
}

.background-image {
  width: 100%;
  height: auto;
  display: block;
}

/* Content Container */
.home-content {
  position: relative;
  z-index: 1;
}
</style>
