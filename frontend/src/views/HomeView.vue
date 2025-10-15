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
      
      <!-- Notes Section -->
      <NotesSection />
      
      <!-- Promo Banner 1 -->
      <PromoBannerReverse
        :title="$t('ctas.banner1.title')"
        :description="$t('ctas.banner1.description')"
        :primary-button="{ text: $t('ctas.banner1.primaryButton') }"
        :secondary-button="{ text: $t('ctas.banner1.secondaryButton') }"
        :image="{ src: ctaImage, alt: 'Secret Diaries' }"
        @primary-click="handleJoinSecret"
        @secondary-click="handleCreateWishlist"
      />

      <!-- Category Cards Section -->
      <CategoryCards />

      <!-- Promo Banner 2 -->
      <PromoBanner
        :title="$t('ctas.banner2.title')"
        :description="$t('ctas.banner2.description')"
        :primary-button="{ text: $t('ctas.banner2.primaryButton') }"
        :image="{ src: ctaImage2, alt: 'Peek inside diary' }"
        @primary-click="handleExploreDiaries"
      />
      
      <!-- FAQ Section -->
      <FAQ />
      
      <!-- Footer -->
      <Footer />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import Navbar from '@/components/shared/Navbar.vue'
import Hero from '@/components/home/Hero.vue'
import CategoryCards from '@/components/home/CategoryCards.vue'
import TrendingProducts from '@/components/products/TrendingProducts.vue'
import NotesSection from '@/components/home/notes/NotesSection.vue'
import PromoBanner from '@/components/shared/PromoBanner.vue'
import PromoBannerReverse from '@/components/shared/PromoBannerReverse.vue'
import FAQ from '@/components/shared/FAQ.vue'
import Footer from '@/components/shared/Footer.vue'
import ctaImage from '@/assets/home/CTAs/CTA.png'
import ctaImage2 from '@/assets/home/CTAs/CTA2.png'

const router = useRouter()
const i18nStore = useI18nStore()

const handleExploreDiaries = () => {
  // Navegar a explorar diarios/notas
  const currentLang = i18nStore.locale
  router.push({ name: `Diaries-${currentLang}` })
}

const handleJoinSecret = () => {
  // Navegar a login
  const currentLang = i18nStore.locale
  router.push({ name: `Login-${currentLang}` })
}

const handleCreateWishlist = () => {
  // Navegar a wishlist del perfil (protegido, redirige a login si no está autenticado)
  const currentLang = i18nStore.locale
  router.push({ name: `ProfileWishlist-${currentLang}` })
}
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
