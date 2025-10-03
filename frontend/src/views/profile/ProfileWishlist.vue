<template>
  <div class="py-6">
    <div class="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            {{ searchedUser ? `@${searchedUser.username}${$t('profile.wishlist.usersWishlists')}` : $t('profile.wishlist.myWishlists') }}
          </h1>
          <p v-if="searchedUser" class="text-sm text-gray-600 mt-1">
            {{ searchedUser.fullName }} · {{ searchedUser.totalWishlists }} {{ searchedUser.totalWishlists !== 1 ? $t('profile.wishlist.publicWishlistsPlural') : $t('profile.wishlist.publicWishlists') }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button v-if="searchedUser" @click="clearSearch" class="flex items-center gap-2 px-4 py-2 border-2 border-gray-400 text-gray-700 bg-white rounded-full text-sm font-medium hover:bg-gray-100 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            {{ $t('profile.wishlist.backToMyWishlists') }}
          </button>
          <button @click="goToShop" class="flex items-center gap-2 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-sm font-medium hover:bg-brand-pink-medium hover:text-white transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
            {{ $t('profile.wishlist.goToShop') }}
          </button>
          <button v-if="!searchedUser" @click="showCreateModal = true" :disabled="wishlistStore.isUpdating" class="flex items-center gap-2 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-sm font-medium hover:bg-brand-pink-medium hover:text-white transition-colors disabled:opacity-50">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
            {{ $t('profile.wishlist.create') }}
          </button>
        </div>
      </div>

      <!-- Search -->
      <div class="mb-6">
        <form @submit.prevent="searchByUsername" class="relative max-w-md">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </div>
          <input 
            v-model="searchQuery" 
            type="text" 
            :placeholder="$t('profile.wishlist.searchPlaceholder')" 
            class="block w-full pl-10 pr-20 py-2.5 border border-gray-300 rounded-lg bg-white placeholder-gray-500 focus:ring-2 focus:ring-brand-pink-medium focus:border-transparent text-sm" 
          />
          <button 
            type="submit" 
            class="absolute inset-y-0 right-0 flex items-center pr-3 text-brand-pink-medium hover:text-brand-pink-dark font-medium text-sm"
            :disabled="!searchQuery.trim()"
          >
            {{ $t('profile.wishlist.search') }}
          </button>
        </form>
      </div>

      <!-- Loading -->
      <div v-if="wishlistStore.isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-pink-medium"></div>
      </div>

      <!-- Error -->
      <div v-else-if="wishlistStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-sm text-red-800">{{ wishlistStore.error }}</p>
      </div>

      <!-- Wishlists -->
      <div v-else-if="filteredWishlists.length > 0" class="space-y-4">
        <div v-for="wishlist in filteredWishlists" :key="wishlist.id" class="wishlist-card border-2 border-gray-900 rounded-2xl overflow-hidden">
          <div class="p-6">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ wishlist.name }}</h3>
                <p class="text-sm text-gray-600 mb-2">{{ wishlist.description || $t('profile.wishlist.noDescription') }}</p>
                <p class="text-xs text-gray-500">
                  {{ wishlist.total_items }} {{ $t('profile.wishlist.items') }} · ${{ wishlist.total_value?.toFixed(2) || '0.00' }} · 
                  <span v-if="wishlist.is_public">{{ $t('profile.wishlist.public') }}</span>
                  <span v-else>{{ $t('profile.wishlist.private') }}</span>
                </p>
              </div>
              <div class="flex items-center gap-2 ml-4">
                <button v-if="wishlist.is_public" @click="copyWishlistLink(wishlist)" :disabled="copyingId === wishlist.id" class="flex items-center gap-2 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-xs font-medium hover:bg-brand-pink-medium hover:text-white transition-colors whitespace-nowrap disabled:opacity-50">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
                  {{ copyingId === wishlist.id ? $t('profile.wishlist.copied') : $t('profile.wishlist.copyWishlistLink') }}
                </button>
                <button @click="buyWishlist(wishlist)" class="px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-xs font-medium hover:bg-brand-pink-medium hover:text-white transition-colors whitespace-nowrap">{{ searchedUser ? $t('profile.wishlist.buyWishlist') : $t('profile.wishlist.buyMyWishlist') }}</button>
                <button @click="toggleWishlist(wishlist.id)" class="p-2 hover:bg-gray-100 rounded-full transition-colors">
                  <svg class="w-5 h-5 text-gray-600 transition-transform" :class="{ 'rotate-180': expandedWishlists.includes(wishlist.id) }" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Products -->
          <div v-if="expandedWishlists.includes(wishlist.id)" class="px-6 pb-6">
            <!-- Loading products -->
            <div v-if="loadingWishlistId === wishlist.id" class="flex justify-center py-8">
              <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-brand-pink-medium"></div>
            </div>
            
            <!-- Products grid -->
            <div v-else-if="getWishlistProducts(wishlist.id).length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="item in getWishlistProducts(wishlist.id)" :key="item.id" class="relative">
                <!-- Remove button (solo para mis wishlists) -->
                <button 
                  v-if="!searchedUser"
                  @click="removeProduct(wishlist.id, item.woocommerce_product_id)"
                  class="absolute top-2 right-2 z-10 bg-white hover:bg-red-600 text-gray-600 hover:text-white rounded-full p-1.5 shadow-md transition-colors"
                  :title="$t('profile.wishlist.removeFromWishlist')"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                
                <!-- Product Card -->
                <ProductCard
                  v-if="item.product_info"
                  :product="formatProductForCard(item)"
                  @navigate-to-product="navigateToProduct"
                  @add-to-cart="handleAddToCart"
                />
                
                <!-- Notes only -->
                <div v-if="item.notes" class="mt-2">
                  <p class="text-xs text-gray-600 italic">💭 {{ item.notes }}</p>
                </div>
              </div>
            </div>
            
            <!-- Empty state -->
            <div v-else class="text-sm text-gray-500 text-center py-8">
              <svg class="w-16 h-16 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p>{{ $t('profile.wishlist.noProductsYet') }}</p>
              <button 
                @click="goToShop" 
                class="mt-3 text-brand-pink-medium hover:text-brand-pink-dark font-medium text-sm"
              >
                {{ $t('profile.wishlist.browseProducts') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else class="text-center py-12">
        <ClipboardDocumentListIcon class="mx-auto h-16 w-16 text-gray-400" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">{{ $t('profile.wishlist.noWishlistsYet') }}</h3>
        <p class="mt-2 text-sm text-gray-500">{{ $t('profile.wishlist.createFirstWishlist') }}</p>
        <button @click="showCreateModal = true" class="mt-4 inline-flex items-center gap-2 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-full text-sm font-medium hover:bg-brand-pink-medium hover:text-white transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" /></svg>
          {{ $t('profile.wishlist.createWishlist') }}
        </button>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-white/40 backdrop-blur-md flex items-center justify-center z-50" @click.self="showCreateModal = false">
      <div class="bg-white rounded-2xl p-6 max-w-md w-full mx-4">
        <h2 class="text-xl font-bold text-gray-900 mb-4">{{ $t('profile.wishlist.createWishlistTitle') }}</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('profile.wishlist.name') }}</label>
            <input v-model="newWishlist.name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-pink-medium focus:border-transparent" :placeholder="$t('profile.wishlist.namePlaceholder')" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('profile.wishlist.description') }}</label>
            <textarea v-model="newWishlist.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-pink-medium focus:border-transparent" :placeholder="$t('profile.wishlist.descriptionPlaceholder')"></textarea>
          </div>
          <div class="flex items-center">
            <input v-model="newWishlist.is_public" type="checkbox" id="is_public" class="h-4 w-4 text-brand-pink-medium focus:ring-brand-pink-medium border-gray-300 rounded" />
            <label for="is_public" class="ml-2 text-sm text-gray-700">{{ $t('profile.wishlist.makePublic') }}</label>
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showCreateModal = false" class="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 bg-white rounded-lg hover:bg-gray-100 transition-colors">{{ $t('profile.wishlist.cancel') }}</button>
          <button @click="createWishlist" :disabled="!newWishlist.name || wishlistStore.isUpdating" class="flex-1 px-4 py-2 border-2 border-brand-pink-medium text-brand-pink-medium bg-white rounded-lg hover:bg-brand-pink-medium hover:text-white transition-colors disabled:opacity-50">{{ wishlistStore.isUpdating ? $t('profile.wishlist.creating') : $t('profile.wishlist.create') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ClipboardDocumentListIcon } from '@heroicons/vue/24/outline'
import { useWishlistStore } from '@/stores/modules/wishlistStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import ProductCard from '@/components/products/ProductCard.vue'

const router = useRouter()
const wishlistStore = useWishlistStore()
const i18nStore = useI18nStore()
const { t } = useI18n()

const searchQuery = ref('')
const expandedWishlists = ref([])
const showCreateModal = ref(false)
const copyingId = ref(null)
const loadingWishlistId = ref(null)
const loadedWishlistDetails = ref({}) // Cache de wishlists con detalles cargados
const newWishlist = ref({ name: '', description: '', is_public: false })
const searchedUser = ref(null) // Info del usuario buscado
const searchedWishlists = ref([]) // Wishlists del usuario buscado

const filteredWishlists = computed(() => {
  // Si estamos viendo wishlists de otro usuario, mostrar esas
  if (searchedUser.value) {
    return searchedWishlists.value
  }
  // Si no, mostrar las propias
  return wishlistStore.wishlists
})

const toggleWishlist = async (id) => {
  const index = expandedWishlists.value.indexOf(id)
  
  if (index > -1) {
    // Collapse
    expandedWishlists.value.splice(index, 1)
  } else {
    // Expand - cargar detalles completos si no están cargados
    expandedWishlists.value.push(id)
    
    if (!loadedWishlistDetails.value[id]) {
      loadingWishlistId.value = id
      try {
        let result
        
        // Si estamos viendo wishlists de otro usuario, usar el endpoint público
        if (searchedUser.value) {
          result = await wishlistStore.fetchPublicWishlistByUsername(searchedUser.value.username, id)
        } else {
          // Si no, usar el endpoint privado
          result = await wishlistStore.fetchWishlist(id)
        }
        
        if (result.success) {
          loadedWishlistDetails.value[id] = result.data
        }
      } catch (err) {
        console.error('Error loading wishlist details:', err)
      } finally {
        loadingWishlistId.value = null
      }
    }
  }
}

// Get products from loaded wishlist details
const getWishlistProducts = (wishlistId) => {
  const detailedWishlist = loadedWishlistDetails.value[wishlistId]
  if (detailedWishlist && detailedWishlist.items) {
    return detailedWishlist.items
  }
  
  // Fallback to basic list
  const wishlist = wishlistStore.wishlists.find(w => w.id === wishlistId)
  return wishlist?.items || []
}

// Format product data for ProductCard component
const formatProductForCard = (item) => {
  // item.product_info contiene toda la info actualizada de WooCommerce
  return {
    id: item.woocommerce_product_id,
    name: item.product_name,
    price: item.product_price,
    images: item.product_info?.images || [{ src: item.product_image }],
    stock_status: item.product_info?.stock_status || 'instock',
    ...item.product_info
  }
}

const navigateToProduct = (productId) => {
  router.push({ name: `ProductDetail-${i18nStore.locale}`, params: { id: productId } })
}

const handleAddToCart = (product) => {
  console.log('Product added to cart from wishlist:', product)
  // El ProductCard ya maneja esto internamente
}

const createWishlist = async () => {
  const result = await wishlistStore.createWishlist(newWishlist.value)
  if (result.success) {
    showCreateModal.value = false
    newWishlist.value = { name: '', description: '', is_public: false }
  }
}

const copyWishlistLink = async (wishlist) => {
  if (!wishlist.public_url) return
  try {
    await navigator.clipboard.writeText(wishlist.public_url)
    copyingId.value = wishlist.id
    setTimeout(() => copyingId.value = null, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const buyWishlist = (wishlist) => {
  alert('Buy wishlist functionality coming soon!')
}

const removeProduct = async (wishlistId, woocommerceProductId) => {
  if (!confirm(t('profile.wishlist.confirmRemove'))) return
  
  const result = await wishlistStore.removeWooCommerceProductFromWishlist(wishlistId, woocommerceProductId)
  
  if (result.success) {
    // Actualizar los detalles cargados
    const detailsResult = await wishlistStore.fetchWishlist(wishlistId)
    if (detailsResult.success) {
      loadedWishlistDetails.value[wishlistId] = detailsResult.data
    }
  }
}

const goToShop = () => {
  router.push({ name: `Products-${i18nStore.locale}` })
}

const searchByUsername = async () => {
  if (!searchQuery.value.trim()) return
  
  // Limpiar el @ si lo escribió
  let username = searchQuery.value.trim()
  if (username.startsWith('@')) {
    username = username.substring(1)
  }
  
  if (!username) return
  
  const result = await wishlistStore.fetchWishlistsByUsername(username)
  
  if (result.success) {
    searchedUser.value = result.user
    searchedWishlists.value = result.data
    // Mapear los campos de la respuesta del endpoint al formato que usa la vista
    searchedWishlists.value = result.data.map(wishlist => ({
      id: wishlist.id,
      name: wishlist.title || wishlist.name,
      description: wishlist.description,
      total_items: wishlist.items_count || wishlist.total_items || 0,
      total_value: wishlist.total_value || 0,
      is_public: true,
      public_url: wishlist.public_url,
      shareable_path: wishlist.shareable_path,
      created_at: wishlist.created_at,
      user_username: username
    }))
  }
}

const clearSearch = async () => {
  searchQuery.value = ''
  searchedUser.value = null
  searchedWishlists.value = []
  expandedWishlists.value = []
  loadedWishlistDetails.value = {}
  // Recargar mis wishlists
  await wishlistStore.fetchWishlists()
}

onMounted(async () => {
  await wishlistStore.fetchWishlists()
})
</script>

<style scoped>
.wishlist-card {
  background: rgba(255, 63, 213, 0.2);
}
</style>

