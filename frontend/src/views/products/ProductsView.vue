<template>
  <div class="products-page">
    <!-- Navbar Component -->
    <Navbar />

    <!-- Main Content -->
    <div class="main-content bg-pink-50 min-h-screen pt-0">
      <div class="container mx-auto px-6 pt-24 pb-6">
        
        <!-- Breadcrumb Dinámico -->
        <div class="breadcrumb mb-8 flex items-center relative z-10 pt-4">
          <button @click="clearAllFilters" class="text-gray-600 hover:text-brand-pink-dark transition-colors">
            {{ $t('products.breadcrumb.home') }}
          </button>
          <span v-if="currentTheme || currentCategory" class="text-gray-400 mx-2">></span>
          <button 
            v-if="currentTheme" 
            @click="onThemeSelect(currentTheme.theme)"
            class="text-gray-600 hover:text-brand-pink-dark transition-colors">
            {{ currentTheme.name }}
          </button>
          <span v-if="currentCategory" class="text-gray-400 mx-2">></span>
          <span v-if="currentCategory" class="text-gray-800 font-medium">
            {{ currentCategory.name }}
          </span>
        </div>

        <div class="flex gap-8 relative z-10">
          <!-- Sidebar Filters -->
          <aside class="sidebar w-80 flex-shrink-0">
            <div class="filters-container bg-white rounded-3xl shadow-sm p-6 border border-gray-100">
              
              <!-- Filters Header -->
              <div class="filters-header mb-6 pb-4 border-b border-gray-200 flex items-center justify-between">
                <h3 class="text-2xl font-semibold text-gray-800">{{ $t('products.filters.title') }}</h3>
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
                </svg>
              </div>

              <!-- Filter Categories -->
              <div class="filter-categories">
                
                <!-- Loading Categories -->
                <div v-if="isLoadingThemes" class="text-center py-4">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-blue-medium mx-auto"></div>
                  <p class="text-gray-600 mt-2">{{ $t('products.filters.loadingCategories') }}</p>
                </div>

                <!-- Themes from WooCommerce (Organized) -->
                <div v-else>
                  <!-- All Products Option -->
                  <div class="filter-item mb-3">
                    <button 
                      @click="clearAllFilters"
                      :class="['filter-button w-full flex items-center justify-between py-3 px-3 text-left transition-colors rounded-lg',
                               !selectedTheme && !selectedCategory ? 'bg-brand-pink-light' : 'hover:bg-gray-50']">
                      <span class="text-gray-700 text-base font-medium">{{ $t('products.filters.allProducts') }}</span>
                      <span v-if="!selectedTheme && !selectedCategory" class="text-brand-pink-dark">✓</span>
                    </button>
                  </div>

                  <!-- Dynamic Themes -->
                  <div v-for="theme in themes" :key="theme.theme" class="filter-item mb-3">
                    <!-- Theme Button -->
                    <button 
                      @click="toggleTheme(theme.theme)"
                      :class="['filter-button w-full flex items-center justify-between py-3 px-3 text-left transition-colors rounded-lg',
                               selectedTheme === theme.theme ? 'bg-brand-pink-light' : 'hover:bg-gray-50']">
                      <div class="flex items-center">
                        <div>
                          <span class="text-gray-800 text-base font-medium">{{ theme.name }}</span>
                          <span class="text-gray-500 text-xs ml-2">({{ theme.total_products }})</span>
                        </div>
                      </div>
                      <svg 
                        :class="['arrow w-5 h-5 text-gray-400 transition-transform',
                                 selectedTheme === theme.theme ? 'rotate-90' : '']" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                      </svg>
                    </button>

                    <!-- Categories dentro del tema (expandible) -->
                    <div v-if="selectedTheme === theme.theme" class="mt-2 ml-4 space-y-2">
                      <!-- Categorías del tema -->
                      <div v-for="category in theme.categories" :key="category.id">
                        <button
                          @click.stop="selectCategory(category.id)"
                          :class="['w-full flex items-center justify-between py-2 px-3 text-left transition-colors rounded-lg text-sm',
                                   selectedCategory === category.id ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100']">
                          <div class="flex items-center">
                            <span>{{ category.name }}</span>
                            <span class="text-gray-400 text-xs ml-2">({{ category.count }})</span>
                          </div>
                          <div class="flex items-center">
                            <span v-if="selectedCategory === category.id" class="text-purple-700 text-sm mr-2">✓</span>
                            <svg 
                              v-if="category.has_subcategories" 
                              :class="['w-4 h-4 text-gray-400 transition-transform',
                                       expandedCategories.has(category.id) ? 'rotate-90' : '']"
                              fill="none" 
                              stroke="currentColor" 
                              viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                          </div>
                        </button>

                        <!-- Subcategorías (si existen) -->
                        <div v-if="category.has_subcategories && expandedCategories.has(category.id)" class="ml-4 mt-1 space-y-1">
                          <button
                            v-for="subcategory in category.subcategories"
                            :key="subcategory.id"
                            @click.stop="selectCategory(subcategory.id)"
                            :class="['w-full flex items-center justify-between py-2 px-3 text-left transition-colors rounded-lg text-sm',
                                     selectedCategory === subcategory.id ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100']">
                            <div class="flex items-center">
                              <span class="text-gray-400 mr-2">└─</span>
                              <span>{{ subcategory.name }}</span>
                              <span class="text-gray-400 text-xs ml-2">({{ subcategory.count }})</span>
                            </div>
                            <span v-if="selectedCategory === subcategory.id" class="text-purple-700 text-sm">✓</span>
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
            
            <!-- Products Header -->
            <div class="products-header flex items-center justify-between mb-8">
              <div>
                <h1 class="text-3xl font-bold text-gray-800 mb-2 flex items-center">
                  <span>{{ pageTitle }}</span>
                </h1>
                <p class="text-gray-600">
                  {{ $t('products.header.showing', { 
                    start: Math.min((currentPage - 1) * productsPerPage + 1, totalProducts), 
                    end: Math.min(currentPage * productsPerPage, totalProducts), 
                    total: totalProducts 
                  }) }}
                </p>
              </div>
              <div class="sort-section flex items-center">
                <span class="text-gray-600 mr-3">{{ $t('products.header.sortBy') }}</span>
                <select 
                  v-model="sortBy"
                  @change="handleSortChange"
                  class="sort-select bg-white border border-gray-300 rounded px-3 py-2 text-gray-700 focus:outline-none focus:border-brand-pink-medium">
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
              <div v-if="isLoading" class="text-center py-12">
                <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-brand-blue-medium mx-auto mb-4"></div>
                <p class="text-gray-600 text-lg">{{ $t('products.loading') }}</p>
              </div>

              <!-- Error State -->
              <div v-else-if="error" class="text-center py-12">
                <div class="text-red-500 mb-4">
                  <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <p class="text-gray-600 text-lg mb-4">{{ error }}</p>
                <button @click="loadProducts" class="bg-brand-blue-medium text-white px-6 py-2 rounded-lg hover:bg-opacity-90 transition-colors">
                  {{ $t('products.retry') }}
                </button>
              </div>

              <!-- No Products State -->
              <div v-else-if="paginatedProducts.length === 0" class="text-center py-12">
                <div class="text-gray-400 mb-4">
                  <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                  </svg>
                </div>
                <p class="text-gray-600 text-lg">{{ $t('products.noProducts') }}</p>
              </div>

              <!-- Products Grid -->
              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <ProductCard
                  v-for="product in paginatedProducts" 
                  :key="product.id"
                  :product="product"
                  :is-in-wishlist="isProductInWishlist(product.id)"
                  :is-in-list="isProductInList(product.id)"
                  :is-in-favorites="isProductInFavorites(product.id)"
                  @navigate-to-product="navigateToProduct"
                  @add-to-cart="addToCart"
                  @toggle-wishlist="toggleWishlist"
                  @toggle-list="toggleProductList"
                  @favorite-updated="handleFavoriteUpdated"
                />
              </div>

              <!-- Pagination -->
              <div v-if="totalProducts > 0" class="flex justify-center items-center mt-12 space-x-4">
                <button 
                  @click="changePage(currentPage - 1)"
                  :disabled="currentPage === 1 || isLoading"
                  class="px-4 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                  {{ $t('products.pagination.previous') }}
                </button>
                
                <div class="flex items-center space-x-2">
                  <span class="text-sm text-gray-600">
                    {{ $t('products.pagination.page') }} {{ currentPage }}
                  </span>
                </div>
                
                <button 
                  @click="changePage(currentPage + 1)"
                  :disabled="displayedProducts.length < productsPerPage || isLoading"
                  class="px-4 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
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
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useProductStore } from '@/stores/modules/productStore'
import { useProfileStore } from '@/stores/modules/profileStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { useCartStore } from '@/stores/modules/cartStore'
import ProductCard from '@/components/products/ProductCard.vue'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'
import { getProductPrice } from '@/utils/priceHelper.js'

// i18n setup
const { t } = useI18n()
const router = useRouter()
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

// ⭐ Total de productos (global o por categoría/tema)
const totalProducts = computed(() => {
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
  } else {
    // Expandir nuevo tema
    selectedTheme.value = themeSlug
    selectedCategory.value = ''
    currentPage.value = 1
    
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
  
  try {
    // Determinar qué cargar según el contexto
    if (selectedCategory.value) {
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

const addToCart = async (product) => {
  console.log('🛒 Agregando al carrito desde ProductsView:', product.name)
  
  try {
    // Obtener el precio correcto del producto (desde short_description)
    const productPrice = getProductPrice(product)
    
    // Preparar opciones del producto
    const options = {
      name: product.name,
      price: productPrice,
      image: product.images?.[0]?.src || null,
      stock_status: product.stock_status,
      variation_id: null // Los productos desde la lista no tienen variación seleccionada
    }
    
    // Llamar al cartStore para agregar el producto
    const result = await cartStore.addToCart(
      product.id,
      1, // cantidad por defecto
      options
    )
    
    if (result.success) {
      console.log('✅ Producto agregado al carrito exitosamente:', product.name)
      console.log('📦 Items en carrito ahora:', cartStore.items.length)
      // Aquí podrías mostrar una notificación de éxito si tienes un sistema de notificaciones
    } else {
      console.error('❌ Error al agregar al carrito:', result.error)
      alert(`Error al agregar ${product.name} al carrito: ${result.error}`)
    }
  } catch (err) {
    console.error('❌ Error inesperado al agregar al carrito:', err)
    alert(`Error inesperado al agregar ${product.name} al carrito`)
  }
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

// Lifecycle
onMounted(async () => {
  // Inicializar catálogo de productos
  await initializeCatalog()
  
  // Cargar IDs de favoritos si el usuario está autenticado
  if (authStore.isLoggedIn) {
    console.log('🔄 Cargando IDs de favoritos...')
    const result = await profileStore.fetchFavoriteProductIds()
    if (result.success) {
      console.log('✅ IDs de favoritos cargados:', result.data.length)
    }
  }
})
</script>

<style scoped>
/* Main Content */
.main-content {
  background-color: #fdf2f8;
  margin-top: -25px; /* Superposición con el navbar */
  position: relative;
}

/* Sidebar */
.sidebar {
  max-width: 320px;
}

.filters-container {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-button {
  border: none;
  background: none;
  font-size: 0.95rem;
  color: #6b7280;
}

.filter-button:hover {
  color: #1f2937;
}

.filter-button:hover .arrow {
  transform: translateX(3px);
}

.arrow {
  transition: transform 0.2s ease;
}

.rotate-90 {
  transform: rotate(90deg);
}

.apply-filter-btn {
  font-size: 0.9rem;
  letter-spacing: 0.025em;
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

/* Products Section */
.products-header h1 {
  font-weight: 700;
  color: #1f2937;
}

.sort-select {
  min-width: 180px;
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

/* Responsive Design */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
  
  .main-content {
    margin-top: -12px; /* Menos superposición en móvil */
  }
  
  .container {
    padding-top: 4rem !important; /* Más espacio en móvil para el navbar */
  }
  
  .sidebar {
    max-width: 100%;
    margin-bottom: 2rem;
  }
  
  .products-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .sort-section {
    width: 100%;
    justify-content: flex-start;
  }
  
  .sort-select {
    min-width: 200px;
  }
  
}

/* Breadcrumb styling */
.breadcrumb {
  backdrop-filter: blur(5px);
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.15);
  margin-left: -1rem;
  margin-right: -1rem;
}

.breadcrumb button {
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

@media (max-width: 1024px) {
  .main-content {
    margin-top: -18px; /* Menos superposición en tablet */
  }
  
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 5rem !important; /* Más espacio en tablet para el navbar */
  }
}
</style>


