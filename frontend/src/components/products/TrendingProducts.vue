<template>
  <section class="trending-products-section">
    <div class="trending-container">
      <div class="max-w-[1800px] mx-auto px-12 py-16">
        
        <!-- Header Section -->
        <div class="trending-header mb-12">
          <!-- Row 1: Title -->
          <div class="titles-section mb-6">
            <h2 class="trending-title">
              {{ $t('trending.title') }} ✨
            </h2>
          </div>
          
          <!-- Row 2: Subtitle - aligned right -->
          <div class="subtitle-section mb-4 flex justify-end">
            <p class="trending-subtitle text-right">
              {{ $t('trending.subtitle') }}
            </p>
          </div>
          
          <!-- Row 3: Button - aligned right -->
          <div class="button-section flex justify-end">
            <router-link 
              :to="`/${i18nStore.locale}/products`"
              class="trending-button"
            >
              {{ $t('trending.button') }} 🔥
            </router-link>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="productStore.isLoadingTrending" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">{{ $t('trending.loading') }}</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="productStore.wooError" class="error-state">
          <p class="error-text">{{ $t('trending.error') }}</p>
        </div>
        
        <!-- No Products State -->
        <div v-else-if="!productStore.hasTrendingProducts" class="empty-state">
          <p class="empty-text">{{ $t('trending.noProducts') }}</p>
        </div>
        
        <!-- Products Carousel -->
        <div v-else class="carousel-wrapper">
          <!-- Navigation Button - Left -->
          <button 
            @click="scrollLeft" 
            class="carousel-nav carousel-nav-left"
            :disabled="isAtStart"
            :class="{ 'opacity-50 cursor-not-allowed': isAtStart }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <!-- Carousel Container -->
          <div 
            ref="carouselRef" 
            class="carousel-container"
            @scroll="handleScroll"
          >
            <div class="carousel-track">
              <div 
                v-for="product in productStore.trendingProducts" 
                :key="product.id"
                class="carousel-item"
              >
                <ProductCard 
                  :product="product"
                  :is-in-wishlist="false"
                  :is-in-list="false"
                  @navigate-to-product="navigateToProduct"
                  @toggle-wishlist="handleToggleWishlist"
                  @toggle-list="handleToggleList"
                  @add-to-cart="handleAddToCart"
                />
              </div>
            </div>
          </div>
          
          <!-- Navigation Button - Right -->
          <button 
            @click="scrollRight" 
            class="carousel-nav carousel-nav-right"
            :disabled="isAtEnd"
            :class="{ 'opacity-50 cursor-not-allowed': isAtEnd }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useProductStore } from '@/stores/modules/productStore'
import ProductCard from '@/components/products/ProductCard.vue'

// Stores
const i18nStore = useI18nStore()
const productStore = useProductStore()
const router = useRouter()

// Refs
const carouselRef = ref(null)
const isAtStart = ref(true)
const isAtEnd = ref(false)

// Methods
const navigateToProduct = (productId) => {
  router.push(`/${i18nStore.locale}/products/${productId}`)
}

const handleToggleWishlist = (productId) => {
  console.log('Toggle wishlist:', productId)
  // TODO: Implementar lógica de wishlist
}

const handleToggleList = (productId) => {
  console.log('Toggle list:', productId)
  // TODO: Implementar lógica de lista
}

const handleAddToCart = (product) => {
  console.log('Added to cart:', product)
}

const scrollLeft = () => {
  if (carouselRef.value) {
    carouselRef.value.scrollBy({
      left: -400,
      behavior: 'smooth'
    })
  }
}

const scrollRight = () => {
  if (carouselRef.value) {
    carouselRef.value.scrollBy({
      left: 400,
      behavior: 'smooth'
    })
  }
}

const handleScroll = () => {
  if (carouselRef.value) {
    const { scrollLeft, scrollWidth, clientWidth } = carouselRef.value
    isAtStart.value = scrollLeft === 0
    isAtEnd.value = scrollLeft + clientWidth >= scrollWidth - 10
  }
}

// Lifecycle
onMounted(async () => {
  // Cargar productos en tendencia si no están cargados
  if (!productStore.hasTrendingProducts) {
    await productStore.fetchWooTrendingProducts()
  }
  
  // Verificar posición inicial del scroll
  handleScroll()
})
</script>

<style scoped>
/* Section Container */
.trending-products-section {
  position: relative;
  padding: 4rem 0;
  background: transparent;
}

.trending-container {
  width: 100%;
}

/* Header Section */
.trending-header {
  margin-bottom: 3rem;
}

.titles-section {
  margin-bottom: 1.5rem;
}

.subtitle-section {
  margin-bottom: 1rem;
}

.button-section {
  /* Button row */
}

.trending-title {
  font-family: 'Comfortaa', cursive;
  font-size: 2.5rem;
  font-weight: 700;
  color: #000000;
  margin: 0;
  line-height: 1.2;
  white-space: pre-line;
}

.trending-subtitle {
  font-family: 'Comfortaa', cursive;
  font-size: 1.75rem;
  font-weight: 400;
  color: rgba(0, 0, 0, 0.7);
  margin: 0;
  line-height: 1.5;
  max-width: 65%;
}

.trending-button {
  font-family: 'Comfortaa', cursive;
  font-size: 1.375rem;
  font-weight: 600;
  color: #FFFFFF;
  background: #4A6FA5;
  border: none;
  border-radius: 50px;
  padding: 1.125rem 3rem;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
  white-space: nowrap;
}

.trending-button:hover {
  background: #3d5a8a;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 111, 165, 0.4);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  gap: 1rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(74, 111, 165, 0.2);
  border-top-color: #4A6FA5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: rgba(0, 0, 0, 0.6);
}

/* Error State */
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
}

.error-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  color: #ef4444;
  text-align: center;
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
}

.empty-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  color: rgba(0, 0, 0, 0.5);
  text-align: center;
}

/* Carousel Wrapper */
.carousel-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* Navigation Buttons */
.carousel-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: white;
  border: 2px solid rgba(0, 0, 0, 0.1);
  color: #4A6FA5;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.carousel-nav:hover:not(:disabled) {
  background: #4A6FA5;
  color: white;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 6px 20px rgba(74, 111, 165, 0.3);
}

.carousel-nav:active:not(:disabled) {
  transform: translateY(-50%) scale(0.95);
}

.carousel-nav-left {
  left: -24px;
}

.carousel-nav-right {
  right: -24px;
}

/* Carousel Container */
.carousel-container {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  padding: 1rem 0;
  margin: 0 48px;
}

.carousel-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

/* Carousel Track */
.carousel-track {
  display: flex;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

/* Carousel Item */
.carousel-item {
  flex: 0 0 calc((100% - 4.5rem) / 4); /* 4 tarjetas visibles, 1.5rem gap entre cada una */
  min-width: 280px;
  max-width: 380px;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .trending-title {
    font-size: 2rem;
  }
  
  .trending-subtitle {
    font-size: 1.5rem;
  }
  
  .trending-button {
    font-size: 1.25rem;
    padding: 1rem 2.5rem;
  }
  
  .trending-subtitle {
    max-width: 70%;
  }
  
  .carousel-container {
    margin: 0 36px;
  }
  
  .carousel-nav {
    width: 40px;
    height: 40px;
  }
  
  .carousel-nav-left {
    left: -20px;
  }
  
  .carousel-nav-right {
    right: -20px;
  }
  
  .carousel-item {
    flex: 0 0 calc((100% - 3rem) / 3); /* 3 tarjetas visibles en tablet */
    min-width: 260px;
    max-width: 320px;
  }
}

@media (max-width: 768px) {
  .trending-products-section {
    padding: 2rem 0;
  }
  
  .trending-container > div {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
  
  .trending-title {
    font-size: 1.75rem;
  }
  
  .trending-subtitle {
    font-size: 1.25rem;
    max-width: 100%;
    text-align: left;
  }
  
  .subtitle-section {
    justify-content: flex-start;
  }
  
  .button-section {
    justify-content: flex-start;
  }
  
  .trending-button {
    width: 100%;
    text-align: center;
    font-size: 1.125rem;
  }
  
  .carousel-container {
    margin: 0 28px;
  }
  
  .carousel-nav {
    width: 36px;
    height: 36px;
  }
  
  .carousel-nav-left {
    left: -18px;
  }
  
  .carousel-nav-right {
    right: -18px;
  }
  
  .carousel-item {
    flex: 0 0 calc((100% - 1.5rem) / 2); /* 2 tarjetas visibles en mobile */
    min-width: 240px;
    max-width: 280px;
  }
}

@media (max-width: 768px) {
  /* Ajuste adicional para pantallas medianas */
  .carousel-item {
    flex: 0 0 calc((100% - 1.5rem) / 2);
    min-width: 240px;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .trending-title {
    font-size: 1.5rem;
  }
  
  .trending-subtitle {
    font-size: 1.125rem;
  }
  
  .trending-button {
    font-size: 1rem;
    padding: 0.875rem 2rem;
  }
  
  .carousel-wrapper {
    margin: 0 -1.5rem;
    padding: 0 1.5rem;
  }
  
  .carousel-container {
    margin: 0;
  }
  
  .carousel-nav {
    display: none;
  }
  
  .carousel-item {
    flex: 0 0 85%;
    min-width: 220px;
    max-width: 280px;
  }
  
  .carousel-track {
    gap: 1rem;
  }
}

/* Asegurar que todas las tarjetas tengan la misma altura */
.carousel-item :deep(.product-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.carousel-item :deep(.product-info) {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Fijar altura del título para mantener consistencia */
.carousel-item :deep(.product-title) {
  min-height: 3rem; /* Altura fija para 2 líneas de texto */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}
</style>

