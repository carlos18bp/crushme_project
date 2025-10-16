<template>
  <section class="relative py-8 md:py-12 lg:py-16 bg-transparent">
    <div class="w-full">
      <div class="max-w-[1800px] mx-auto px-6 md:px-12 py-8 md:py-12 lg:py-16">
        
        <!-- Header Section -->
        <div class="mb-8 md:mb-12">
          <!-- Row 1: Title -->
          <div class="mb-4 md:mb-6">
            <h2 class="font-comfortaa text-2xl md:text-3xl lg:text-4xl font-bold text-black m-0 leading-tight whitespace-pre-line">
              {{ $t('trending.title') }} ✨
            </h2>
          </div>
          
          <!-- Row 2: Subtitle - aligned right -->
          <div class="mb-3 md:mb-4 flex justify-start lg:justify-end">
            <p class="font-comfortaa text-lg md:text-xl lg:text-[1.75rem] font-normal text-black/70 m-0 leading-relaxed max-w-full lg:max-w-[65%] text-left lg:text-right">
              {{ $t('trending.subtitle') }}
            </p>
          </div>
          
          <!-- Row 3: Button - aligned right -->
          <div class="flex justify-start lg:justify-end">
            <router-link 
              :to="`/${i18nStore.locale}/products`"
              class="font-comfortaa text-base md:text-lg lg:text-[1.375rem] font-semibold text-white bg-[#4A6FA5] border-none rounded-full px-6 md:px-8 lg:px-12 py-3 md:py-4 lg:py-[1.125rem] cursor-pointer no-underline inline-block transition-all duration-300 shadow-[0_4px_12px_rgba(74,111,165,0.3)] whitespace-nowrap hover:bg-[#3d5a8a] hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(74,111,165,0.4)] w-full sm:w-auto text-center"
            >
              {{ $t('trending.button') }} 🔥
            </router-link>
          </div>
        </div>
        
        <!-- Loading State -->
        <div v-if="productStore.isLoadingTrending" class="flex flex-col items-center justify-center py-12 md:py-16 gap-4">
          <div class="w-12 h-12 border-4 border-[rgba(74,111,165,0.2)] border-t-[#4A6FA5] rounded-full animate-spin"></div>
          <p class="font-poppins text-base text-black/60">{{ $t('trending.loading') }}</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="productStore.wooError" class="flex items-center justify-center py-12 md:py-16">
          <p class="font-poppins text-base md:text-lg text-red-500 text-center">{{ $t('trending.error') }}</p>
        </div>
        
        <!-- No Products State -->
        <div v-else-if="!productStore.hasTrendingProducts" class="flex items-center justify-center py-12 md:py-16">
          <p class="font-poppins text-base md:text-lg text-black/50 text-center">{{ $t('trending.noProducts') }}</p>
        </div>
        
        <!-- Products Carousel -->
        <div v-else class="relative flex items-center gap-2 md:gap-4">
          <!-- Navigation Button - Left -->
          <button 
            @click="scrollLeft" 
            class="hidden md:flex absolute top-1/2 -translate-y-1/2 z-10 left-[-12px] lg:left-[-24px] w-9 h-9 lg:w-12 lg:h-12 rounded-full bg-white border-2 border-black/10 text-[#4A6FA5] items-center justify-center cursor-pointer transition-all duration-300 shadow-[0_4px_12px_rgba(0,0,0,0.1)] hover:bg-[#4A6FA5] hover:text-white hover:scale-110 hover:shadow-[0_6px_20px_rgba(74,111,165,0.3)] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isAtStart"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 lg:w-6 lg:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          
          <!-- Carousel Container -->
          <div 
            ref="carouselRef" 
            class="flex-1 overflow-x-auto overflow-y-hidden scroll-smooth [-webkit-overflow-scrolling:touch] [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden py-4 mx-0 md:mx-9 lg:mx-12"
            @scroll="handleScroll"
          >
            <div class="flex gap-4 md:gap-6 p-2">
              <div 
                v-for="product in productStore.trendingProducts" 
                :key="product.id"
                class="flex-[0_0_85%] sm:flex-[0_0_calc((100%-1.5rem)/2)] md:flex-[0_0_calc((100%-3rem)/3)] lg:flex-[0_0_calc((100%-4.5rem)/4)] min-w-[220px] sm:min-w-[240px] md:min-w-[260px] lg:min-w-[280px] max-w-[280px] sm:max-w-[300px] md:max-w-[320px] lg:max-w-[380px]"
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
            class="hidden md:flex absolute top-1/2 -translate-y-1/2 z-10 right-[-12px] lg:right-[-24px] w-9 h-9 lg:w-12 lg:h-12 rounded-full bg-white border-2 border-black/10 text-[#4A6FA5] items-center justify-center cursor-pointer transition-all duration-300 shadow-[0_4px_12px_rgba(0,0,0,0.1)] hover:bg-[#4A6FA5] hover:text-white hover:scale-110 hover:shadow-[0_6px_20px_rgba(74,111,165,0.3)] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="isAtEnd"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 lg:w-6 lg:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
/* Deep selectors para ProductCard - asegurar altura consistente */
:deep(.product-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.product-info) {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

:deep(.product-title) {
  min-height: 3rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}
</style>

