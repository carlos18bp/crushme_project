<template>
  <div class="products-page">
    <!-- Navbar Component -->
    <Navbar />

    <!-- Main Content -->
    <div class="main-content bg-pink-50 min-h-screen pt-20">
      <div class="container mx-auto px-4 md:px-5 lg:px-6 pt-20 md:pt-22 lg:pt-24 pb-4 md:pb-5 lg:pb-6">

        <div class="flex flex-col lg:flex-row gap-4 md:gap-6 lg:gap-8 relative z-10">
          <!-- Sidebar Filters -->
          <aside class="sidebar w-full lg:w-80 flex-shrink-0">
            <div class="filters-container bg-white rounded-2xl md:rounded-3xl shadow-sm p-4 md:p-5 lg:p-6 border border-gray-100">
              
              <!-- Filters Header -->
              <div class="filters-header mb-4 md:mb-5 lg:mb-6 pb-3 md:pb-4 border-b border-gray-200">
                <div class="flex items-center justify-between mb-3 md:mb-0">
                  <h3 class="text-lg md:text-xl lg:text-2xl font-semibold text-gray-800">{{ $t('products.filters.title') }}</h3>
                  <button 
                    @click="toggleCategoriesMenu" 
                    class="lg:hidden text-gray-600 hover:text-brand-pink-dark transition-colors">
                    <svg 
                      :class="['w-6 h-6 transition-transform', isCategoriesMenuOpen ? 'rotate-180' : '']"
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Filter Categories -->
              <div :class="['filter-categories', { 'hidden lg:block': !isCategoriesMenuOpen }]">
                
                <!-- Loading Categories -->
                <div v-if="isLoadingThemes" class="text-center py-3 md:py-4">
                  <div class="animate-spin rounded-full h-7 w-7 md:h-8 md:w-8 border-b-2 border-brand-blue-medium mx-auto"></div>
                  <p class="text-gray-600 mt-2 text-sm md:text-base">{{ $t('products.filters.loadingCategories') }}</p>
                </div>

                <!-- Themes from WooCommerce (Organized) -->
                <div v-else>
                  <!-- All Products Option -->
                  <div class="filter-item mb-2 md:mb-3">
                    <button 
                      @click="clearAllFilters"
                      :class="['filter-button w-full flex items-center justify-between py-2.5 md:py-3 px-2.5 md:px-3 text-left transition-colors rounded-lg',
                               !selectedTheme && !selectedCategory ? 'bg-brand-pink-light' : 'hover:bg-gray-50']">
                      <span class="text-gray-700 text-sm md:text-base font-medium">{{ $t('products.filters.allProducts') }}</span>
                      <span v-if="!selectedTheme && !selectedCategory" class="text-brand-pink-dark">✓</span>
                    </button>
                  </div>

                  <!-- Dynamic Themes -->
                  <div v-for="theme in themes" :key="theme.theme" class="filter-item mb-2 md:mb-3">
                    <!-- Theme Button -->
                    <button 
                      @click="toggleTheme(theme.theme)"
                      :class="['filter-button w-full flex items-center justify-between py-2.5 md:py-3 px-2.5 md:px-3 text-left transition-colors rounded-lg',
                               selectedTheme === theme.theme ? 'bg-brand-pink-light' : 'hover:bg-gray-50']">
                      <div class="flex items-center">
                        <div>
                          <span class="text-gray-800 text-sm md:text-base font-medium">{{ theme.name }}</span>
                          <span class="text-gray-500 text-xs ml-1.5 md:ml-2">({{ theme.total_products }})</span>
                        </div>
                      </div>
                      <svg 
                        :class="['arrow w-4 h-4 md:w-5 md:h-5 text-gray-400 transition-transform',
                                 selectedTheme === theme.theme ? 'rotate-90' : '']" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                    </button>

                    <!-- Categories dentro del tema (expandible) -->
                    <div v-if="selectedTheme === theme.theme" class="mt-1.5 md:mt-2 ml-3 md:ml-4 space-y-1.5 md:space-y-2">
                      <!-- Categorías del tema -->
                      <div v-for="category in theme.categories" :key="category.id">
                        <button
                          @click.stop="selectCategory(category.id)"
                          :class="['w-full flex items-center justify-between py-1.5 md:py-2 px-2.5 md:px-3 text-left transition-colors rounded-lg text-xs md:text-sm',
                                   selectedCategory === category.id ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100']">
                          <div class="flex items-center">
                            <span>{{ category.name }}</span>
                            <span class="text-gray-400 text-xs ml-1.5 md:ml-2">({{ category.count }})</span>
                          </div>
                          <div class="flex items-center">
                            <span v-if="selectedCategory === category.id" class="text-purple-700 text-xs md:text-sm mr-1.5 md:mr-2">✓</span>
                            <svg 
                              v-if="category.has_subcategories" 
                              :class="['w-3.5 h-3.5 md:w-4 md:h-4 text-gray-400 transition-transform',
                                       expandedCategories.has(category.id) ? 'rotate-90' : '']"
                              fill="none" 
                              stroke="currentColor" 
                              viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                          </div>
                        </button>

                        <!-- Subcategorías (si existen) -->
                        <div v-if="category.has_subcategories && expandedCategories.has(category.id)" class="ml-3 md:ml-4 mt-1 space-y-1">
                          <button
                            v-for="subcategory in category.subcategories"
                            :key="subcategory.id"
                            @click.stop="selectCategory(subcategory.id)"
                            :class="['w-full flex items-center justify-between py-1.5 md:py-2 px-2.5 md:px-3 text-left transition-colors rounded-lg text-xs md:text-sm',
                                     selectedCategory === subcategory.id ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100']">
                            <div class="flex items-center">
                              <span class="text-gray-400 mr-1.5 md:mr-2 text-xs">└─</span>
                              <span>{{ subcategory.name }}</span>
                              <span class="text-gray-400 text-xs ml-1.5 md:ml-2">({{ subcategory.count }})</span>
                            </div>
                            <span v-if="selectedCategory === subcategory.id" class="text-purple-700 text-xs md:text-sm">✓</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </aside>

          <!-- Products Section -->
          <main class="products-section flex-1">
            
            <!-- Search Bar -->
            <div class="search-bar mb-4 md:mb-6">
              <div class="relative">
                <input
                  v-model="searchQuery"
                  @input="handleSearchInput"
                  @keyup.enter="performSearch"
                  type="text"
                  placeholder="Buscar productos..."
                  class="w-full px-4 py-2.5 md:py-3 pl-11 md:pl-12 pr-10 md:pr-12 border-2 border-gray-200 rounded-xl md:rounded-2xl focus:outline-none focus:border-brand-purple-light focus:ring-2 focus:ring-brand-purple-light focus:ring-opacity-20 transition-all text-sm md:text-base"
                />
                <svg 
                  class="absolute left-3 md:left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 md:w-6 md:h-6 text-gray-400"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <button
                  v-if="searchQuery"
                  @click="clearSearch"
                  class="absolute right-3 md:right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
                  <svg class="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              <p v-if="isSearching" class="text-sm text-gray-500 mt-2">{{ $t('products.searching') || 'Buscando...' }}</p>
            </div>

            <!-- Products Header -->
            <div class="products-header flex flex-col md:flex-row items-start md:items-center justify-between mb-4 md:mb-6 lg:mb-8 gap-3 md:gap-4">
              <div>
                <h1 class="text-xl md:text-2xl lg:text-3xl font-bold text-gray-800 mb-1.5 md:mb-2 flex items-center">
                  <span>{{ pageTitle }}</span>
                </h1>
                <p class="text-sm md:text-base text-gray-600">
                  {{ $t('products.header.showing', { 
                    start: Math.min((currentPage - 1) * productsPerPage + 1, totalProducts), 
                    end: Math.min(currentPage * productsPerPage, totalProducts), 
                    total: totalProducts 
                  }) }}
                </p>
              </div>
              <div class="sort-section flex items-center w-full md:w-auto">
                <span class="text-gray-600 mr-2 md:mr-3 text-sm md:text-base">{{ $t('products.header.sortBy') }}</span>
                <select 
                  v-model="sortBy"
                  @change="handleSortChange"
                  class="sort-select bg-white border border-gray-300 rounded px-2.5 md:px-3 py-1.5 md:py-2 text-sm md:text-base text-gray-700 focus:outline-none focus:border-brand-pink-medium flex-1 md:flex-initial">
                  <option value="mostPopular">{{ $t('products.header.sortOptions.mostPopular') }}</option>
                  <option value="priceLowHigh">{{ $t('products.header.sortOptions.priceLowHigh') }}</option>
                  <option value="priceHighLow">{{ $t('products.header.sortOptions.priceHighLow') }}</option>
                  <option value="newest">{{ $t('products.header.sortOptions.newest') }}</option>
                  <option value="bestRating">{{ $t('products.header.sortOptions.bestRating') }}</option>
                </select>
              </div>
            </div>

            <!-- Products Grid -->
            <div class="products-grid">
              
              <!-- Loading State -->
              <div v-if="isLoading" class="text-center py-8 md:py-10 lg:py-12">
                <div class="animate-spin rounded-full h-12 w-12 md:h-14 md:w-14 lg:h-16 lg:w-16 border-b-2 border-brand-blue-medium mx-auto mb-3 md:mb-4"></div>
                <p class="text-gray-600 text-base md:text-lg">{{ $t('products.loading') }}</p>
              </div>

              <!-- Error State -->
              <div v-else-if="error" class="text-center py-8 md:py-10 lg:py-12">
                <div class="text-red-500 mb-3 md:mb-4">
                  <svg class="w-12 h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <p class="text-gray-600 text-base md:text-lg mb-3 md:mb-4">{{ error }}</p>
                <button @click="loadProducts" class="bg-brand-blue-medium text-white px-4 md:px-6 py-1.5 md:py-2 rounded-lg hover:bg-opacity-90 transition-colors text-sm md:text-base">
                  {{ $t('products.retry') }}
                </button>
              </div>

              <!-- No Products State -->
              <div v-else-if="paginatedProducts.length === 0" class="text-center py-8 md:py-10 lg:py-12">
                <div class="text-gray-400 mb-3 md:mb-4">
                  <svg class="w-12 h-12 md:w-14 md:h-14 lg:w-16 lg:h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                  </svg>
                </div>
                <p class="text-gray-600 text-base md:text-lg">{{ $t('products.noProducts') }}</p>
              </div>

              <!-- Products Grid -->
              <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-5 lg:gap-6">
                <ProductCard
                  v-for="product in paginatedProducts" 
                  :key="product.id"
                  :product="product"
                  :is-in-wishlist="isProductInWishlist(product.id)"
                  :is-in-list="isProductInList(product.id)"
                  :is-in-favorites="isProductInFavorites(product.id)"
                  @navigate-to-product="navigateToProduct"
                  @toggle-wishlist="toggleWishlist"
                  @toggle-list="toggleProductList"
                  @favorite-updated="handleFavoriteUpdated"
                />
              </div>

              <!-- Pagination -->
              <div v-if="totalProducts > 0" class="flex justify-center items-center mt-8 md:mt-10 lg:mt-12 space-x-2 md:space-x-4">
                <button 
                  @click="changePage(currentPage - 1)"
                  :disabled="currentPage === 1 || isLoading"
                  class="px-3 md:px-4 py-1.5 md:py-2 border border-gray-300 rounded-lg text-sm md:text-base text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                  {{ $t('products.pagination.previous') }}
                </button>
                
                <div class="flex items-center space-x-1 md:space-x-2">
                  <span class="text-xs md:text-sm text-gray-600">
                    {{ $t('products.pagination.page') }} {{ currentPage }}
                  </span>
                </div>
                
                <button 
                  @click="changePage(currentPage + 1)"
                  :disabled="displayedProducts.length < productsPerPage || isLoading"
                  class="px-3 md:px-4 py-1.5 md:py-2 border border-gray-300 rounded-lg text-sm md:text-base text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                  {{ $t('products.pagination.next') }}
                </button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useProductStore } from '@/stores/modules/productStore'
import { useProfileStore } from '@/stores/modules/profileStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { useCartStore } from '@/stores/modules/cartStore'
import ProductCard from '@/components/products/ProductCard.vue'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'

// i18n setup
const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const i18nStore = useI18nStore()

// Store setup
const productStore = useProductStore()
const profileStore = useProfileStore()
const authStore = useAuthStore()
const cartStore = useCartStore()

// Reactive data
const selectedTheme = ref('') // Tema seleccionado (juguetes, lenceria, etc.)
const selectedCategory = ref('') // Categoría/subcategoría seleccionada
const expandedCategories = ref(new Set()) // Categorías con subcategorías expandidas
const sortBy = ref('mostPopular')
const currentPage = ref(1)
const productsPerPage = ref(9) // ⭐ Cambiado a 9 productos por página
const wishlistProducts = ref(new Set())
const listProducts = ref(new Set())
const isCategoriesMenuOpen = ref(false) // ⭐ NUEVO: Estado del menú de categorías en mobile
const searchQuery = ref('') // ⭐ NUEVO: Query de búsqueda
const isSearching = ref(false) // ⭐ NUEVO: Estado de búsqueda
const searchResultsCount = ref(null) // ⭐ NUEVO: Cantidad de resultados
const activeSearchQuery = ref('') // ⭐ NUEVO: Query de búsqueda activa (para paginación)
const searchPagination = ref(null) // ⭐ NUEVO: Datos de paginación de búsqueda

// Computed properties from store
const themes = computed(() => productStore.wooThemes)
const isLoading = computed(() => productStore.isLoadingWoo)
const isLoadingThemes = computed(() => productStore.isLoadingWooThemes)
const error = computed(() => productStore.wooError)
const connectionStatus = computed(() => productStore.isWooConnected)
const stats = computed(() => productStore.wooStats) // ⭐ Estadísticas globales

// Computed: Tema actual
const currentTheme = computed(() => {
  if (!selectedTheme.value) return null
  return productStore.getThemeBySlug(selectedTheme.value)
})

// Computed: Categoría actual
const currentCategory = computed(() => {
  if (!selectedCategory.value) return null
  return productStore.getCategoryById(selectedCategory.value)
})

// Computed: Título de la página
const pageTitle = computed(() => {
  if (currentCategory.value) {
    return currentCategory.value.name
  }
  if (currentTheme.value) {
    return currentTheme.value.name
  }
  return t('products.title')
})

// ⭐ NUEVA LÓGICA: Productos directamente del store (ya vienen paginados del backend)
const displayedProducts = computed(() => {
  const products = productStore.wooProducts
  
  // Ordenar localmente si es necesario
  const sorted = [...products]
  
  switch (sortBy.value) {
    case 'mostPopular':
      return sorted.sort((a, b) => (b.total_sales || 0) - (a.total_sales || 0))
    case 'priceLowHigh':
      return sorted.sort((a, b) => parseFloat(a.price) - parseFloat(b.price))
    case 'priceHighLow':
      return sorted.sort((a, b) => parseFloat(b.price) - parseFloat(a.price))
    case 'newest':
      return sorted.sort((a, b) => new Date(b.date_created) - new Date(a.date_created))
    case 'bestRating':
      return sorted.sort((a, b) => parseFloat(b.average_rating || 0) - parseFloat(a.average_rating || 0))
    default:
      return sorted
  }
})

// ⭐ Total de productos (global o por categoría/tema/búsqueda)
const totalProducts = computed(() => {
  // Si hay una búsqueda activa, usar el total de resultados de búsqueda
  if (activeSearchQuery.value && searchPagination.value) {
    return searchPagination.value.total_results || 0
  }
  
  // Si hay una categoría seleccionada, usar su total
  if (selectedCategory.value) {
    const category = productStore.getCategoryById(selectedCategory.value)
    return category?.count || 0
  }
  
  // Si hay un tema seleccionado, usar su total
  if (selectedTheme.value) {
    const theme = productStore.getThemeBySlug(selectedTheme.value)
    return theme?.total_products || 0
  }
  
  // Si no hay filtros, usar el total global de estadísticas
  if (stats.value?.totals?.products) {
    return stats.value.totals.products
  }
  
  // Fallback: contar productos cargados
  return displayedProducts.value.length
})

const totalPages = computed(() => Math.ceil(totalProducts.value / productsPerPage.value))
const paginatedProducts = computed(() => displayedProducts.value)

// Methods

/**
 * ⭐ Inicialización optimizada: PRIMERO categorías, DESPUÉS productos
 */
const initializeCatalog = async () => {
  try {
    console.log('🚀 Inicializando catálogo...')
    
    // ⭐ Usar la función optimizada del store que carga categorías ANTES que productos
    const result = await productStore.initializeWooCommerce()
    
    if (result.success) {
      console.log('✅ Catálogo inicializado:', {
        themes: result.themes?.length || 0,
        products: result.products?.length || 0,
        totalCategories: result.total_categories || 0
      })
    } else {
      console.error('❌ Error inicializando catálogo:', result.error)
    }
  } catch (error) {
    console.error('Error al inicializar catálogo:', error)
  }
}

/**
 * Toggle de tema: Expande/colapsa el tema
 */
const toggleTheme = (themeSlug) => {
  if (selectedTheme.value === themeSlug) {
    // Si es el mismo tema, colapsarlo
    selectedTheme.value = ''
    selectedCategory.value = ''
    updateURL()
  } else {
    // Expandir nuevo tema
    selectedTheme.value = themeSlug
    selectedCategory.value = ''
    currentPage.value = 1
    
    // Actualizar URL
    updateURL()
    
    // Cargar productos del tema
    loadThemeProducts(themeSlug)
  }
}

/**
 * Seleccionar tema (sin toggle)
 */
const onThemeSelect = async (themeSlug) => {
  selectedTheme.value = themeSlug
  selectedCategory.value = ''
  currentPage.value = 1
  
  // Actualizar URL
  updateURL()
  
  await loadThemeProducts(themeSlug)
}

/**
 * ⭐ Cargar productos de un tema (solo 9)
 */
const loadThemeProducts = async (themeSlug) => {
  try {
    const result = await productStore.fetchProductsByTheme(themeSlug, 9, 1)
    if (result.success) {
      console.log(`✅ Productos de ${themeSlug} cargados:`, result.data.length)
    }
  } catch (error) {
    console.error('Error cargando productos del tema:', error)
  }
}

/**
 * ⭐ Seleccionar categoría/subcategoría (solo 9 productos)
 */
const selectCategory = async (categoryId) => {
  selectedCategory.value = categoryId
  currentPage.value = 1
  
  // Expandir categoría si tiene subcategorías
  const category = productStore.getCategoryById(categoryId)
  if (category?.has_subcategories) {
    if (expandedCategories.value.has(categoryId)) {
      expandedCategories.value.delete(categoryId)
    } else {
      expandedCategories.value.add(categoryId)
    }
    // Forzar actualización reactiva
    expandedCategories.value = new Set(expandedCategories.value)
  }
  
  // Actualizar URL
  updateURL()
  
  // ⭐ Cargar solo 9 productos de la categoría
  try {
    const result = await productStore.fetchWooProductsByCategory(categoryId, 9, 1)
    if (result.success) {
      console.log(`✅ Productos de categoría ${categoryId} cargados:`, result.data.length)
    }
  } catch (error) {
    console.error('Error cargando productos de categoría:', error)
  }
}

/**
 * ⭐ Limpiar todos los filtros y cargar primeros 9 productos
 */
const clearAllFilters = async () => {
  selectedTheme.value = ''
  selectedCategory.value = ''
  expandedCategories.value.clear()
  currentPage.value = 1
  productStore.clearTheme()
  productStore.clearSubcategory()
  
  // Actualizar URL (limpiar query params)
  updateURL()
  
  console.log('🔄 Limpiando filtros, cargando productos generales...')
  // Cargar primeros 9 productos sin filtros
  const result = await productStore.fetchWooProducts({ perPage: 9, page: 1 })
  if (result.success) {
    console.log('✅ Productos generales cargados:', result.data.length)
  }
}

const handleSortChange = (event) => {
  sortBy.value = event.target.value
  currentPage.value = 1 // Reset to first page when sorting
}

/**
 * ⭐ NUEVO: Cambiar de página - Carga 9 productos de esa página
 */
const changePage = async (newPage) => {
  if (newPage < 1) return
  
  console.log(`📄 PAGINATION DEBUG - Cambiando a página ${newPage}, productos actuales en store:`, productStore.wooProducts.length)
  
  currentPage.value = newPage
  
  // Actualizar URL con nueva página
  updateURL()
  
  try {
    // Si hay una búsqueda activa, paginar en los resultados de búsqueda
    if (activeSearchQuery.value) {
      console.log(`📄 PAGINATION DEBUG - Cargando página ${newPage} de búsqueda: "${activeSearchQuery.value}"`)
      const result = await productStore.searchWooProducts(activeSearchQuery.value, newPage)
      if (result.success) {
        searchPagination.value = result.pagination
        searchResultsCount.value = result.pagination?.total_results || result.data.length
      }
    }
    // Determinar qué cargar según el contexto
    else if (selectedCategory.value) {
      // Cargar página de categoría específica
      console.log(`📄 PAGINATION DEBUG - Cargando página ${newPage} de categoría ${selectedCategory.value}`)
      await productStore.fetchWooProductsByCategory(selectedCategory.value, 9, newPage)
    } else if (selectedTheme.value) {
      // Cargar página de tema
      console.log(`📄 PAGINATION DEBUG - Cargando página ${newPage} de tema ${selectedTheme.value}`)
      await productStore.fetchProductsByTheme(selectedTheme.value, 9, newPage)
    } else {
      // Cargar página de todos los productos
      console.log(`📄 PAGINATION DEBUG - Cargando página ${newPage} de todos los productos`)
      await productStore.fetchWooProducts({ perPage: 9, page: newPage })
    }
    
    console.log(`📄 PAGINATION DEBUG - Después de cargar página ${newPage}, productos en store:`, productStore.wooProducts.length)
    console.log(`📄 PAGINATION DEBUG - IDs de productos cargados:`, productStore.wooProducts.map(p => `${p.id}-${p.name?.substring(0, 15)}`))
    
    // Scroll al inicio de la lista de productos
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (error) {
    console.error('Error cambiando de página:', error)
  }
}

const navigateTo = (routeName) => {
  const currentLang = i18nStore.locale
  router.push({ name: `${routeName}-${currentLang}` })
}

const navigateToProduct = (productId) => {
  const currentLang = i18nStore.locale
  router.push({ name: `ProductDetail-${currentLang}`, params: { id: productId } })
}

const toggleWishlist = (productId) => {
  if (wishlistProducts.value.has(productId)) {
    wishlistProducts.value.delete(productId)
  } else {
    wishlistProducts.value.add(productId)
  }
  // Force reactivity update
  wishlistProducts.value = new Set(wishlistProducts.value)
}

const toggleProductList = (productId) => {
  if (listProducts.value.has(productId)) {
    listProducts.value.delete(productId)
  } else {
    listProducts.value.add(productId)
  }
  // Force reactivity update
  listProducts.value = new Set(listProducts.value)
}

const isProductInWishlist = (productId) => {
  return wishlistProducts.value.has(productId)
}

const isProductInList = (productId) => {
  return listProducts.value.has(productId)
}

const isProductInFavorites = (productId) => {
  return profileStore.isProductInFavorites(productId)
}

const handleFavoriteUpdated = async ({ productId, isFavorited }) => {
  console.log(`Producto ${productId} ${isFavorited ? 'agregado a' : 'eliminado de'} favoritos`)
  // La actualización ya se maneja en el store, no necesitamos hacer nada más aquí
}

const loadMoreProducts = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// Watch para actualizar el store cuando cambian las selecciones locales
watch(selectedTheme, (newTheme) => {
  if (newTheme) {
    productStore.selectTheme(newTheme)
  }
})

watch(selectedCategory, (newCategory) => {
  if (newCategory) {
    productStore.selectSubcategory(newCategory)
  }
})

/**
 * ⭐ NUEVO: Actualizar URL con query params
 */
const updateURL = () => {
  const query = {}
  
  // Agregar tema si existe
  if (selectedTheme.value) {
    query.theme = selectedTheme.value
  }
  
  // Agregar categoría si existe
  if (selectedCategory.value) {
    query.category = selectedCategory.value
  }
  
  // Agregar página si no es la primera
  if (currentPage.value > 1) {
    query.page = currentPage.value
  }
  
  // Actualizar URL sin recargar la página
  router.replace({ 
    name: route.name, 
    query 
  })
}

/**
 * ⭐ NUEVO: Restaurar estado desde URL
 */
const restoreFromURL = async () => {
  const { theme, category, page } = route.query
  
  console.log('🔍 Restaurando estado desde URL:', { theme, category, page })
  
  // Restaurar página
  if (page) {
    currentPage.value = parseInt(page) || 1
  }
  
  // Restaurar tema
  if (theme) {
    selectedTheme.value = theme
    console.log('🔍 Tema restaurado:', theme)
  }
  
  // Restaurar categoría
  if (category) {
    const categoryId = parseInt(category)
    selectedCategory.value = categoryId
    console.log('🔍 Categoría restaurada:', categoryId)
    
    // Cargar productos de la categoría con la página correcta
    const result = await productStore.fetchWooProductsByCategory(categoryId, 9, currentPage.value)
    if (result.success) {
      console.log(`✅ Productos de categoría ${categoryId} cargados (página ${currentPage.value}):`, result.data.length)
    }
  } else if (theme) {
    // Si solo hay tema, cargar productos del tema
    const result = await productStore.fetchProductsByTheme(theme, 9, currentPage.value)
    if (result.success) {
      console.log(`✅ Productos de tema ${theme} cargados (página ${currentPage.value}):`, result.data.length)
    }
  } else if (page) {
    // Si solo hay página, cargar todos los productos de esa página
    const result = await productStore.fetchWooProducts({ perPage: 9, page: currentPage.value })
    if (result.success) {
      console.log(`✅ Productos generales cargados (página ${currentPage.value}):`, result.data.length)
    }
  }
}

// Función para manejar parámetros de consulta iniciales (DEPRECATED - usar restoreFromURL)
const handleInitialQuery = async () => {
  // Esta función ahora es manejada por restoreFromURL
  await restoreFromURL()
}

/**
 * ⭐ NUEVO: Toggle del menú de categorías en mobile
 */
const toggleCategoriesMenu = () => {
  isCategoriesMenuOpen.value = !isCategoriesMenuOpen.value
}

/**
 * ⭐ NUEVO: Manejar input de búsqueda (debounce)
 */
let searchTimeout = null
const handleSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim().length >= 2) {
      performSearch()
    } else if (searchQuery.value.trim().length === 0) {
      clearSearch()
    }
  }, 500) // Esperar 500ms después de que el usuario deje de escribir
}

/**
 * ⭐ NUEVO: Realizar búsqueda de productos
 */
const performSearch = async () => {
  const query = searchQuery.value.trim()
  
  if (query.length < 2) {
    return
  }

  isSearching.value = true
  searchResultsCount.value = null
  
  // Limpiar filtros de categoría al buscar
  selectedTheme.value = ''
  selectedCategory.value = ''
  currentPage.value = 1
  
  console.log('🔍 Buscando productos:', query)
  
  try {
    const result = await productStore.searchWooProducts(query, 1)
    
    if (result.success) {
      activeSearchQuery.value = query // Guardar query activa para paginación
      searchPagination.value = result.pagination
      searchResultsCount.value = result.pagination?.total_results || result.data.length
      console.log(`✅ Búsqueda completada: ${result.pagination?.total_results || result.data.length} productos encontrados (página 1 de ${result.pagination?.total_pages || 1})`)
    } else {
      console.error('❌ Error en búsqueda:', result.error)
      searchResultsCount.value = 0
      activeSearchQuery.value = ''
      searchPagination.value = null
    }
  } catch (error) {
    console.error('❌ Error inesperado en búsqueda:', error)
    searchResultsCount.value = 0
    activeSearchQuery.value = ''
    searchPagination.value = null
  } finally {
    isSearching.value = false
  }
}

/**
 * ⭐ NUEVO: Limpiar búsqueda y restaurar productos
 */
const clearSearch = async () => {
  searchQuery.value = ''
  searchResultsCount.value = null
  isSearching.value = false
  activeSearchQuery.value = '' // Limpiar query activa
  searchPagination.value = null // Limpiar paginación de búsqueda
  
  // Recargar productos generales
  console.log('🔄 Limpiando búsqueda, cargando productos generales...')
  await clearAllFilters()
}

// Lifecycle
onMounted(async () => {
  // Inicializar catálogo de productos
  await initializeCatalog()

  // Restaurar estado desde URL (tema, categoría, página)
  await restoreFromURL()

  // Cargar IDs de favoritos si el usuario está autenticado
  if (authStore.isLoggedIn) {
    console.log('🔄 Cargando IDs de favoritos...')
    const result = await profileStore.fetchFavoriteProductIds()
    if (result.success) {
      console.log('✅ IDs de favoritos cargados:', result.data.length)
    }
  }
  
  // En mobile, cerrar el menú de categorías por defecto
  if (window.innerWidth < 1024) {
    isCategoriesMenuOpen.value = false
  } else {
    isCategoriesMenuOpen.value = true
  }
})
</script>

<style scoped>
/* Main Content - Mobile First */
.main-content {
  background-color: #fdf2f8;
  margin-top: -15px; /* Superposición con el navbar en mobile */
  position: relative;
}

@media (min-width: 768px) {
  .main-content {
    margin-top: -20px;
  }
}

@media (min-width: 1024px) {
  .main-content {
    margin-top: -25px;
  }
}

/* Sidebar - Mobile First */
.sidebar {
  max-width: 100%;
}

@media (min-width: 1024px) {
  .sidebar {
    max-width: 320px;
  }
}

.filters-container {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-button {
  border: none;
  background: none;
  font-size: 0.875rem;
  color: #6b7280;
}

@media (min-width: 768px) {
  .filter-button {
    font-size: 0.9rem;
  }
}

@media (min-width: 1024px) {
  .filter-button {
    font-size: 0.95rem;
  }
}

.filter-button:hover {
  color: #1f2937;
}

.filter-button:hover .arrow {
  transform: translateX(2px);
}

@media (min-width: 768px) {
  .filter-button:hover .arrow {
    transform: translateX(3px);
  }
}

.arrow {
  transition: transform 0.2s ease;
}

.rotate-90 {
  transform: rotate(90deg);
}

.apply-filter-btn {
  font-size: 0.8125rem;
  letter-spacing: 0.025em;
}

@media (min-width: 768px) {
  .apply-filter-btn {
    font-size: 0.875rem;
  }
}

@media (min-width: 1024px) {
  .apply-filter-btn {
    font-size: 0.9rem;
  }
}

/* Theme buttons */
.filter-item .filter-button {
  transition: all 0.2s ease;
}

.filter-item .filter-button:hover {
  background-color: #f9fafb;
}

/* Category indicators */
.bg-purple-100 {
  background-color: #ede9fe;
}

.text-purple-700 {
  color: #7c3aed;
}

.text-purple-600 {
  color: #9333ea;
}

.hover\:bg-purple-50:hover {
  background-color: #faf5ff;
}

/* Products Section - Mobile First */
.products-header h1 {
  font-weight: 700;
  color: #1f2937;
}

.sort-select {
  min-width: auto;
}

@media (min-width: 640px) {
  .sort-select {
    min-width: 160px;
  }
}

@media (min-width: 768px) {
  .sort-select {
    min-width: 180px;
  }
}


/* Line clamp utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Responsive Design - Mobile First */
.nav-menu {
  display: flex;
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
}

/* Breadcrumb styling - Mobile First */
.breadcrumb {
  backdrop-filter: blur(5px);
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.15);
  margin-left: -0.5rem;
  margin-right: -0.5rem;
  font-size: 0.875rem;
}

@media (min-width: 640px) {
  .breadcrumb {
    padding: 0.625rem 0.875rem;
    border-radius: 0.625rem;
    margin-left: -0.75rem;
    margin-right: -0.75rem;
    font-size: 0.9375rem;
  }
}

@media (min-width: 1024px) {
  .breadcrumb {
    padding: 0.75rem 1rem;
    border-radius: 0.75rem;
    margin-left: -1rem;
    margin-right: -1rem;
    font-size: 1rem;
  }
}

.breadcrumb button {
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Search Bar Styles */
.search-bar input {
  transition: all 0.3s ease;
}

.search-bar input:focus {
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.2);
}

/* Category Menu Toggle for Mobile */
@media (min-width: 1024px) {
  .filter-categories {
    display: block !important;
  }
}
</style>


