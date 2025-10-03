<template>
  <div class="py-6">
    <div class="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            {{ $t('profile.favorites.title') || 'Mis Favoritos' }}
          </h1>
          <p class="text-sm text-gray-600 mt-1">
            {{ totalFavorites }} {{ totalFavorites !== 1 ? ($t('profile.favorites.productsPlural') || 'productos favoritos') : ($t('profile.favorites.products') || 'producto favorito') }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <!-- Refresh button -->
          <button 
            v-if="hasFavorites"
            @click="refreshFavorites" 
            :disabled="profileStore.isLoadingFavorites"
            class="flex items-center gap-2 px-4 py-2 border-2 border-gray-400 text-gray-700 bg-white rounded-full text-sm font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
            :title="$t('profile.favorites.refresh') || 'Actualizar'">
            <svg class="w-4 h-4" :class="{ 'animate-spin': profileStore.isLoadingFavorites }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ $t('profile.favorites.refresh') || 'Actualizar' }}
          </button>
          
          <!-- Go to shop button -->
          <button 
            @click="goToShop" 
            class="flex items-center gap-2 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-sm font-medium hover:bg-brand-pink-medium hover:text-white transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            {{ $t('profile.favorites.goToShop') || 'Ir a la tienda' }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="profileStore.isLoadingFavorites && !profileStore.hasFavorites" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-pink-medium"></div>
      </div>

      <!-- Error -->
      <div v-else-if="profileStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-sm text-red-800">{{ profileStore.error }}</p>
      </div>

      <!-- Products Grid -->
      <div v-else-if="hasFavorites" class="space-y-6">
        <!-- Grid: 2 cards por fila -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="favorite in favoriteProducts" :key="favorite.id" class="relative">
            <!-- Remove button -->
            <button 
              @click="removeFavorite(favorite.woocommerce_product_id)"
              class="absolute top-2 right-2 z-10 bg-white hover:bg-red-600 text-gray-600 hover:text-white rounded-full p-1.5 shadow-md transition-colors"
              :title="$t('profile.favorites.removeFromFavorites') || 'Eliminar de favoritos'">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <!-- Product Card -->
            <ProductCard
              :product="formatProductForCard(favorite)"
              :is-in-favorites="true"
              @navigate-to-product="navigateToProduct"
              @favorite-updated="handleFavoriteUpdated"
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">
          {{ $t('profile.favorites.noFavoritesYet') || 'No tienes productos favoritos' }}
        </h3>
        <p class="mt-2 text-sm text-gray-500">
          {{ $t('profile.favorites.addFavoritesMessage') || 'Empieza a agregar productos que te gusten a tus favoritos' }}
        </p>
        <button 
          @click="goToShop" 
          class="mt-4 inline-flex items-center gap-2 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-sm font-medium hover:bg-brand-pink-medium hover:text-white transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
          {{ $t('profile.favorites.browseProducts') || 'Explorar productos' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useProfileStore } from '@/stores/modules/profileStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import ProductCard from '@/components/products/ProductCard.vue'

const router = useRouter()
const profileStore = useProfileStore()
const i18nStore = useI18nStore()
const { t } = useI18n()

// Computed
const favoriteProducts = computed(() => profileStore.favoriteProducts)
const hasFavorites = computed(() => profileStore.hasFavorites)
const totalFavorites = computed(() => profileStore.totalFavorites)

// Format product data for ProductCard component
const formatProductForCard = (favorite) => {
  return {
    id: favorite.woocommerce_product_id,
    name: favorite.product_name,
    price: favorite.product_price,
    images: favorite.product_image ? [{ src: favorite.product_image }] : [],
    stock_status: favorite.is_in_stock ? 'instock' : 'outofstock',
    slug: favorite.product_slug
  }
}

// Navigate to product detail
const navigateToProduct = (productId) => {
  router.push({ name: `ProductDetail-${i18nStore.locale}`, params: { id: productId } })
}

// Handle favorite updated from ProductCard
const handleFavoriteUpdated = async ({ productId, isFavorited }) => {
  if (!isFavorited) {
    // Reload favorites after removal
    await profileStore.fetchFavoriteProducts()
  }
}

// Remove favorite
const removeFavorite = async (woocommerceProductId) => {
  if (!confirm(t('profile.favorites.confirmRemove') || '¿Estás seguro de que deseas eliminar este producto de favoritos?')) {
    return
  }
  
  const result = await profileStore.removeProductFromFavorites(woocommerceProductId)
  
  if (result.success) {
    // The store already updates the local state
    console.log('Producto eliminado de favoritos')
  }
}

// Refresh favorites from WooCommerce
const refreshFavorites = async () => {
  await profileStore.fetchFavoriteProducts(true) // Force refresh
}

// Go to shop
const goToShop = () => {
  router.push({ name: `Products-${i18nStore.locale}` })
}

// Load favorites on mount
onMounted(async () => {
  await profileStore.fetchFavoriteProducts()
})
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>


