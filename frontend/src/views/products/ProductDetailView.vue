<template>
  <div class="product-detail-container">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Main content -->
    <main class="main-content">
  <div class="product-detail-view">
        
        <!-- Loading State -->
        <div v-if="isLoadingProduct" class="loading-container">
          <div class="loading-spinner"></div>
          <p>{{ $t('productDetail.loading') }}</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="error-container">
          <h2>{{ $t('productDetail.error.title') }}</h2>
          <p>{{ error }}</p>
          <button @click="loadProduct" class="retry-btn">
            {{ $t('productDetail.error.retry') }}
          </button>
        </div>
        
        <!-- Product Detail -->
        <div v-else-if="product" class="product-content">
          <div class="product-layout">
            
            <!-- Left Side: Image Gallery -->
            <div class="product-gallery">
              <!-- Thumbnail selector con carousel -->
              <div class="thumbnail-selector">
                <!-- Flecha arriba -->
                <button 
                  v-if="productImages.length > maxVisibleThumbnails"
                  @click="scrollThumbnailsUp"
                  :disabled="thumbnailScrollPosition === 0"
                  class="thumbnail-nav-btn thumbnail-nav-up"
                >
                  ▲
                </button>
                
                <!-- Contenedor de thumbnails -->
                <div class="thumbnail-list" ref="thumbnailList">
                  <div 
                    v-for="(image, index) in productImages" 
                    :key="index"
                    class="thumbnail"
                    :class="{ active: selectedImageIndex === index }"
                    @click="selectImage(index)"
                  >
                    <img :src="image.src" :alt="`${product.name} - imagen ${index + 1}`" />
                  </div>
                </div>
                
                <!-- Flecha abajo -->
                <button 
                  v-if="productImages.length > maxVisibleThumbnails"
                  @click="scrollThumbnailsDown"
                  :disabled="thumbnailScrollPosition >= productImages.length - maxVisibleThumbnails"
                  class="thumbnail-nav-btn thumbnail-nav-down"
                >
                  ▼
                </button>
              </div>
              
              <!-- Main image -->
              <div class="main-image-container">
                <img 
                  :src="selectedImage" 
                  :alt="product.name" 
                  class="main-image"
                />
              </div>
            </div>
            
            <!-- Right Side: Product Information -->
            <div class="product-info">
              <!-- Product Title -->
              <h1 class="product-title">{{ product.name }}</h1>
              
              <!-- Short Description (debajo del título) -->
              <div v-if="cleanShortDescription" class="product-short-description">
                <p v-html="cleanShortDescription"></p>
              </div>
              
              <!-- Reviews (Real data or hardcoded fallback) -->
              <div class="product-reviews">
                <div class="stars">
                  <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.floor(currentRating) }">★</span>
                  <span v-if="currentRating > 0" class="rating-text">{{ currentRating.toFixed(1) }}/5</span>
                  <span v-if="totalReviews > 0" class="rating-count">({{ totalReviews }} {{ totalReviews === 1 ? $t('productReviews.review') : $t('productReviews.reviews') }})</span>
                  <span v-else class="rating-count">({{ $t('productReviews.reviewCount.none') }})</span>
                </div>
              </div>
              
              <!-- Price -->
              <div class="product-price">
                <span class="current-price">{{ displayPrice }}</span>
                <span v-if="product.on_sale && product.regular_price !== product.price" class="regular-price">
                  ${{ product.regular_price }}
                </span>
                <span v-if="product.on_sale" class="sale-badge">{{ $t('productDetail.saleBadge') }}</span>
              </div>
              
              <!-- Description (solo si no hay short_description o si es diferente) -->
              <div v-if="showFullDescription" class="product-description">
                <div v-html="product.description"></div>
              </div>
              
              <!-- ⭐ NUEVO: Selectores de Variaciones (para productos variables) -->
              <div v-if="isProductVariable && variationAttributes.length > 0" class="product-options-container">
                <div v-for="attr in variationAttributes" :key="attr.id" class="product-options">
                  <h4>{{ translateAttributeName(attr.name) }}</h4>
                  <div class="attribute-selector">
                    <button 
                      v-for="option in attr.options" 
                      :key="option"
                      class="attribute-option"
                      :class="{ active: selectedAttributes[attr.name] === option }"
                      @click="selectAttribute(attr.name, option)"
                    >
                      {{ option }}
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- Selectable Attributes (multiple options) - Solo para productos simples -->
              <div v-if="!isProductVariable" v-for="attr in selectableAttributes" :key="attr.id" class="product-options">
                <h4>{{ translateAttributeName(attr.name) }}</h4>
                <div class="attribute-selector">
                  <button 
                    v-for="option in attr.options" 
                    :key="option"
                    class="attribute-option"
                    :class="{ active: selectedAttributes[attr.name] === option }"
                    @click="selectAttribute(attr.name, option)"
                  >
                    {{ option }}
                  </button>
                </div>
              </div>
              
              <!-- Quantity and Actions -->
              <div class="product-actions">
                <!-- Quantity Selector -->
                <div class="quantity-selector">
                  <button @click="decreaseQuantity" :disabled="quantity <= 1 || isAddingToCart" class="quantity-btn">-</button>
                  <input v-model.number="quantity" type="number" min="1" max="99" class="quantity-input" :disabled="isAddingToCart" />
                  <button @click="increaseQuantity" :disabled="quantity >= 99 || isAddingToCart" class="quantity-btn">+</button>
                </div>
                
                <!-- Action Buttons -->
                <button 
                  @click="addToCart" 
                  :disabled="!isStockAvailable || isAddingToCart"
                  class="add-to-cart-btn"
                  :class="{ 'success': addToCartSuccess }"
                >
                  <span v-if="isAddingToCart" class="loading-text">⏳</span>
                  <span v-else-if="addToCartSuccess">✓ {{ $t('productDetail.addedToCart') }}</span>
                  <span v-else>{{ $t('productDetail.addToCart') }}</span>
                </button>
                <button 
                  @click="handleAddToWishlist" 
                  :disabled="!isStockAvailable"
                  class="add-to-wishlist-btn"
                >
                  {{ $t('productDetail.addToWishlist') }}
                </button>
              </div>
              
              <!-- Wishlist Selector Modal -->
              <WishlistSelector
                :show="showWishlistSelector"
                :product-id="product.id"
                @close="showWishlistSelector = false"
                @added="handleWishlistAdded"
                @create-wishlist="handleCreateWishlist"
              />
              
              <!-- Error Message -->
              <div v-if="addToCartError" class="cart-error-message">
                {{ addToCartError }}
              </div>
              
              <!-- Informative Attributes (read only) -->
              <div v-for="attr in informativeAttributes" :key="attr.id" class="product-options">
                <h4>{{ translateAttributeName(attr.name) }}</h4>
                <div class="attribute-info">
                  <span class="info-value">{{ attr.options.join(', ') }}</span>
                </div>
              </div>
            </div>
            
          </div>
        </div>
        
        <!-- No Product Found -->
        <div v-else class="not-found-container">
          <h2>{{ $t('productDetail.notFound.title') }}</h2>
          <p>{{ $t('productDetail.notFound.message', { id: productId }) }}</p>
        </div>
        
      </div>
      
      <!-- Product Reviews Section -->
      <ProductReviews :product-id="productId" />
      
      <!-- Trending Products Section -->
      <TrendingProducts />
      
      <!-- FAQ Section -->
      <FAQ />
    </main>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useProductStore } from '@/stores/modules/productStore'
import { useCartStore } from '@/stores/modules/cartStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useReviewStore } from '@/stores/modules/reviewStore'
import { getFormattedProductPrice, getProductPrice, isSimpleProduct } from '@/utils/priceHelper.js'
import { get_request } from '@/services/request_http.js'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'
import FAQ from '@/components/shared/FAQ.vue'
import WishlistSelector from '@/components/wishlists/WishlistSelector.vue'
import TrendingProducts from '@/components/products/TrendingProducts.vue'
import ProductReviews from '@/components/products/ProductReviews.vue'

// Props
defineProps({
  id: {
    type: String,
    required: true
  }
})

// Router and Store
const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const productStore = useProductStore()
const cartStore = useCartStore()
const authStore = useAuthStore()
const i18nStore = useI18nStore()
const reviewStore = useReviewStore()

// Reactive data
const selectedImageIndex = ref(0)
const selectedAttributes = ref({})
const quantity = ref(1)
const isAddingToCart = ref(false)
const addToCartSuccess = ref(false)
const addToCartError = ref(null)
const thumbnailScrollPosition = ref(0)
const maxVisibleThumbnails = ref(5)
const thumbnailList = ref(null)
const showWishlistSelector = ref(false)

// ⭐ NUEVO: Stock en tiempo real
const realTimeStock = ref(null)
const isCheckingStock = ref(false)
const stockCheckInterval = ref(null)

// Computed properties
const productId = computed(() => route.params.id)
const product = computed(() => productStore.wooCurrentProduct)
const isLoadingProduct = computed(() => productStore.isLoadingWooProduct)
const error = computed(() => productStore.wooError)

// Reviews handling (real data with fallback)
const currentRating = computed(() => {
  // Primero intentar obtener del reviewStore (datos más actualizados)
  if (reviewStore.getAverageRating > 0) {
    return parseFloat(reviewStore.getAverageRating)
  }
  // Luego intentar del producto de WooCommerce
  if (product.value?.average_rating) {
    return parseFloat(product.value.average_rating)
  }
  // Fallback si no hay datos
  return 0
})

// Total de reviews
const totalReviews = computed(() => {
  // Priorizar datos del reviewStore
  if (reviewStore.getTotalReviews > 0) {
    return reviewStore.getTotalReviews
  }
  // Fallback a datos de WooCommerce
  if (product.value?.rating_count) {
    return product.value.rating_count
  }
  return 0
})

// Images handling
// ⭐ Imágenes base del producto (directamente de product.images)
const baseProductImages = computed(() => {
  if (!product.value || !product.value.images || product.value.images.length === 0) {
    return [
      { src: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&h=500&fit=crop&crop=center' },
      { src: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop&crop=center' },
      { src: 'https://images.unsplash.com/photo-1519947486511-46149fa0a254?w=500&h=500&fit=crop&crop=center' }
    ]
  }
  return product.value.images
})

const productImages = computed(() => {
  return displayImages.value
})

const selectedImage = computed(() => {
  return productImages.value[selectedImageIndex.value]?.src || productImages.value[0]?.src
})

// ⭐ Computed: Short description limpia (sin precio para productos simples)
const cleanShortDescription = computed(() => {
  if (!product.value?.short_description) return ''
  
  // Para productos simples, remover el HTML del precio del short_description
  if (isProductSimple.value) {
    // Remover tags que contengan "Precio sugerido" y el precio
    let cleaned = product.value.short_description
    // Remover h5, h4, h3 que contengan precio
    cleaned = cleaned.replace(/<h[3-5][^>]*>.*?(?:Precio sugerido|precio sugerido).*?<\/h[3-5]>/gi, '')
    // Remover spans o divs que contengan solo el precio
    cleaned = cleaned.replace(/<(?:span|div)[^>]*>\s*\$[\d,.]+\s*<\/(?:span|div)>/gi, '')
    
    return cleaned.trim()
  }
  
  return product.value.short_description
})

// Determine if we should show full description
const showFullDescription = computed(() => {
  if (!product.value?.description) return false
  
  // Show full description if there's no short description
  if (!product.value.short_description) return true
  
  // Show full description if it's different from short description
  const shortDesc = product.value.short_description.replace(/<[^>]*>/g, '').trim()
  const fullDesc = product.value.description.replace(/<[^>]*>/g, '').trim()
  
  return shortDesc !== fullDesc && fullDesc.length > shortDesc.length
})

// ⭐ Computed: Determinar si el producto es simple o variable
const isProductSimple = computed(() => {
  return product.value && isSimpleProduct(product.value)
})

// ⭐ NUEVO: Computed para determinar si es producto variable
const isProductVariable = computed(() => {
  return product.value && product.value.type === 'variable'
})

// ⭐ NUEVO: Variación actualmente seleccionada (del store o primera por defecto)
const currentVariation = computed(() => productStore.wooCurrentVariation)

// ⭐ NUEVO: Atributos que generan variaciones
// Ahora el backend incluye 'attributes' con las opciones disponibles
const variationAttributes = computed(() => {
  if (!product.value?.attributes) return []
  
  // El backend ya retorna los atributos correctos para productos variables
  // Invertir el orden de los atributos
  return product.value.attributes.map(attr => ({
    id: attr.slug || attr.name,
    name: attr.name,
    slug: attr.slug,
    options: attr.options || [],
    variation: true
  })).reverse()
})

// ⭐ NUEVO: Variaciones disponibles del producto (viene del backend)
const availableVariations = computed(() => {
  return product.value?.available_variations || []
})

// ⭐ NUEVO: Imágenes a mostrar (variación o producto base)
const displayImages = computed(() => {
  // Si es producto variable y hay variación seleccionada
  if (isProductVariable.value && currentVariation.value) {
    // Prioridad 1: Si la variación tiene múltiples imágenes (del detalle completo)
    if (currentVariation.value.images && currentVariation.value.images.length > 0) {
      console.log('🖼️ [ProductDetail] Usando imágenes múltiples de variación:', currentVariation.value.images.length)
      return currentVariation.value.images
    }
    
    // Prioridad 2: Si la variación tiene una sola imagen
    if (currentVariation.value.image) {
      console.log('🖼️ [ProductDetail] Usando imagen única de variación:', currentVariation.value.image)
      
      // La imagen puede venir como string (URL) o como objeto {src: URL}
      const imageSrc = typeof currentVariation.value.image === 'string' 
        ? currentVariation.value.image 
        : currentVariation.value.image.src
      
      if (imageSrc) {
        return [{
          src: imageSrc,
          thumbnail: imageSrc,
          alt: product.value?.name || 'Product variation'
        }]
      }
    }
  }
  
  // Si no, usar imágenes del producto base
  console.log('🖼️ [ProductDetail] Usando imágenes del producto base')
  return baseProductImages.value
})

// ⭐ Computed: Precio formateado del producto o variación
const displayPrice = computed(() => {
  if (!product.value) return '$0'
  
  // Para productos variables: usar precio de la variación seleccionada
  if (isProductVariable.value && currentVariation.value?.price) {
    const price = parseFloat(currentVariation.value.price)
    console.log(`💰 [ProductDetail] Variación seleccionada - Precio: $${price}`)
    return `$${price.toLocaleString('es-CO')}`
  }
  
  // Para todos los demás casos (simples y fallback): usar campo price directamente
  const price = parseFloat(product.value.price) || 0
  console.log(`💰 [ProductDetail] Precio directo: $${price}`)
  return `$${price.toLocaleString('es-CO')}`
})

// ⭐ Computed: Precio numérico del producto o variación (para cálculos)
const numericPrice = computed(() => {
  if (!product.value) return 0
  
  // Para productos variables: usar precio de la variación seleccionada
  if (isProductVariable.value && currentVariation.value?.price) {
    return parseFloat(currentVariation.value.price) || 0
  }
  
  // Para todos los demás casos: usar campo price directamente
  return parseFloat(product.value.price) || 0
})

// ⭐ NUEVO: Computed para verificar disponibilidad de stock en tiempo real
const isStockAvailable = computed(() => {
  // Para productos variables, verificar stock de la variación seleccionada
  if (isProductVariable.value) {
    // Si hay variación seleccionada, verificar su stock
    if (currentVariation.value) {
      return currentVariation.value.stock_status === 'instock' && 
             (currentVariation.value.stock_quantity === null || currentVariation.value.stock_quantity > 0)
    }
    
    // Si no hay variación seleccionada, buscar en available_variations
    if (availableVariations.value.length > 0) {
      const matchingVariation = findMatchingVariationFromSelected()
      if (matchingVariation) {
        return matchingVariation.in_stock && matchingVariation.stock_quantity > 0
      }
    }
    
    // Sin variación seleccionada, deshabilitar
    return false
  }
  
  // Para productos simples: usar stock en tiempo real
  if (realTimeStock.value && !isProductVariable.value) {
    return realTimeStock.value.available && realTimeStock.value.status === 'instock'
  }
  
  // Fallback: usar stock del producto
  if (product.value) {
    return product.value.stock_status === 'instock' && product.value.in_stock
  }
  
  return false
})

// ⭐ LIMPIADO: Removed old availableColors and availableSizes computed properties
// Now using variationAttributes which gets attributes with variation: true

// Atributos base: excluir Color y Size que se manejan por separado
const otherAttributes = computed(() => {
  if (!product.value?.attributes) return []
  
  return product.value.attributes.filter(attr => {
    const name = attr.name.toLowerCase()
    // Excluir Color y Size porque tienen sus propias secciones dedicadas
    return !name.includes('color') && 
           !name.includes('colour') && 
           !name.includes('cor') && 
           !name.includes('size') && 
           !name.includes('talla') && 
           !name.includes('tamaño')
  })
})

// ⭐ SELECCIONABLES: Usar el campo 'variation' de WooCommerce
// variation === true → Atributo seleccionable (para variaciones del producto)
const selectableAttributes = computed(() => {
  return otherAttributes.value.filter(attr => attr.variation === true)
})

// ⭐ INFORMATIVOS: Usar el campo 'variation' de WooCommerce
// variation === false → Atributo solo informativo (no crea variaciones)
const informativeAttributes = computed(() => {
  return otherAttributes.value.filter(attr => attr.variation === false)
})

// ⭐ NUEVO: Cargar variaciones del producto
const loadVariations = async () => {
  if (!product.value) return
  if (!isProductVariable.value) return
  
  console.log(`🔄 Cargando variaciones para producto ${product.value.id}`)
  
  try {
    const result = await productStore.fetchWooProductVariations(product.value.id, 100, 1)
    
    if (result.success && result.data.length > 0) {
      console.log(`✅ ${result.data.length} variaciones cargadas`)
      
      // ⭐ CARGAR ÚLTIMA VARIACIÓN POR DEFECTO
      const lastVariationId = result.data[result.data.length - 1].id
      console.log(`🎯 Cargando última variación por defecto: ${lastVariationId}`)
      
      await loadVariation(lastVariationId)
    }
  } catch (err) {
    console.error('❌ Error cargando variaciones:', err)
  }
}

// ⭐ NUEVO: Cargar una variación específica
const loadVariation = async (variationId) => {
  if (!product.value) return
  
  console.log(`🔄 Cargando detalle completo de variación ${variationId}`)
  
  try {
    const result = await productStore.fetchWooProductVariation(product.value.id, variationId)
    
    if (result.success && result.data) {
      console.log(`✅ Variación ${variationId} cargada con detalle completo:`, {
        id: result.data.id,
        price: result.data.price,
        stock_quantity: result.data.stock_quantity,
        stock_status: result.data.stock_status,
        image: result.data.image,
        attributes: result.data.attributes
      })
      
      // El store ya actualizó wooCurrentVariation.value
      // Los computed properties (displayPrice, displayImages, isStockAvailable) se actualizan automáticamente
      
      // Reset del índice de imagen cuando cambia la variación
      selectedImageIndex.value = 0
    }
  } catch (err) {
    console.error(`❌ Error cargando variación ${variationId}:`, err)
  }
}

// ⭐ NUEVO: Seleccionar variación basada en atributos seleccionados
const selectVariationByAttributes = async (selectedOptions) => {
  if (!productStore.hasWooVariations) return
  
  console.log('🔍 Buscando variación con atributos:', selectedOptions)
  
  // Buscar variación que coincida con las opciones seleccionadas
  const matchingVariation = productStore.wooProductVariations.find(variation => {
    return variation.attributes.every(attr => {
      const selectedValue = selectedOptions[attr.name]
      return selectedValue === attr.option
    })
  })
  
  if (matchingVariation) {
    console.log(`✅ Variación encontrada: ${matchingVariation.id}`)
    await loadVariation(matchingVariation.id)
  } else {
    console.warn('⚠️ No se encontró variación con esos atributos')
  }
}

// ⭐ NUEVO: Verificar stock en tiempo real
const checkRealTimeStock = async () => {
  if (!productId.value || isCheckingStock.value) return
  
  // ⭐ Si es producto variable, NO consultar stock del padre
  // El stock se maneja por variación individual
  if (isProductVariable.value) {
    console.log('📦 Producto variable detectado - stock se maneja por variación')
    realTimeStock.value = {
      status: 'variable',
      requires_variation_selection: true,
      available: true // Disponible si hay variaciones
    }
    return
  }
  
  isCheckingStock.value = true
  
  try {
    console.log(`📦 Consultando stock en tiempo real para producto ${productId.value}...`)
    const response = await get_request(`products/woocommerce/products/${productId.value}/stock/`)
    
    if (response.data.success) {
      realTimeStock.value = response.data.stock
      console.log('✅ Stock actualizado:', {
        status: realTimeStock.value.status,
        quantity: realTimeStock.value.quantity,
        available: realTimeStock.value.available,
        source: response.data.source
      })
      
      // Actualizar también el producto en el store si es necesario
      if (product.value && !isProductVariable.value) {
        product.value.stock_status = realTimeStock.value.status
        product.value.stock_quantity = realTimeStock.value.quantity
        product.value.in_stock = realTimeStock.value.in_stock
      }
    }
  } catch (err) {
    console.error('❌ Error consultando stock en tiempo real:', err)
    // Usar stock del producto como fallback
    if (product.value) {
      realTimeStock.value = {
        status: product.value.stock_status,
        quantity: product.value.stock_quantity,
        manage_stock: product.value.manage_stock,
        in_stock: product.value.in_stock,
        available: product.value.stock_status === 'instock'
      }
    }
  } finally {
    isCheckingStock.value = false
  }
}

// ⭐ NUEVO: Iniciar polling de stock cada 30 segundos
const startStockPolling = () => {
  // Limpiar intervalo anterior si existe
  if (stockCheckInterval.value) {
    clearInterval(stockCheckInterval.value)
  }
  
  // Consultar stock cada 30 segundos
  stockCheckInterval.value = setInterval(() => {
    checkRealTimeStock()
  }, 30000) // 30 segundos
  
  console.log('⏰ Polling de stock iniciado (cada 30 segundos)')
}

// ⭐ NUEVO: Detener polling de stock
const stopStockPolling = () => {
  if (stockCheckInterval.value) {
    clearInterval(stockCheckInterval.value)
    stockCheckInterval.value = null
    console.log('⏰ Polling de stock detenido')
  }
}

// Methods
// ⭐ NUEVO: Preseleccionar la primera variación disponible
const preselectFirstVariation = async () => {
  if (!isProductVariable.value || availableVariations.value.length === 0) {
    return
  }
  
  console.log('🎯 Preseleccionando primera variación...')
  
  // Obtener la primera variación
  const firstVariation = availableVariations.value[0]
  
  // Preseleccionar los atributos de la primera variación
  selectedAttributes.value = { ...firstVariation.attributes }
  
  console.log('📋 Atributos preseleccionados:', selectedAttributes.value)
  
  // ⭐ PASO 1: Actualizar inmediatamente con datos de available_variations (rápido)
  productStore.setWooCurrentVariation({
    id: firstVariation.id,
    price: firstVariation.price,
    stock_status: firstVariation.in_stock ? 'instock' : 'outofstock',
    stock_quantity: firstVariation.stock_quantity,
    attributes: firstVariation.attributes,
    image: firstVariation.image || null
  })
  
  console.log(`✅ Primera variación preseleccionada: ID ${firstVariation.id}, Precio: $${firstVariation.price}`)
  
  // ⭐ PASO 2: Cargar detalle completo de la variación desde el backend
  await loadVariation(firstVariation.id)
}

const loadProduct = async () => {
  if (!productId.value) return
  
  console.log(`🛍️ Cargando producto ID: ${productId.value}`)
  
  try {
    const result = await productStore.fetchWooProduct(productId.value)
    if (result.success) {
      console.log('✅ Producto cargado:', result.data.name)
      
      // ⭐ Si es producto variable, el backend ya incluye available_variations
      if (result.data.type === 'variable') {
        console.log(`📦 Producto variable con ${result.data.variations_count} variaciones`)
        console.log('✅ available_variations ya incluidas:', result.data.available_variations?.length || 0)
        
        // ⭐ NUEVO: Preseleccionar la primera variación automáticamente
        preselectFirstVariation()
      }
      
      // ⭐ NUEVO: Consultar stock en tiempo real después de cargar el producto
      await checkRealTimeStock()
      
      // ⭐ NUEVO: Iniciar polling de stock
      startStockPolling()
    } else {
      console.error('❌ Error cargando producto:', result.error)
    }
  } catch (err) {
    console.error('❌ Error inesperado:', err)
  }
}

const selectImage = (index) => {
  selectedImageIndex.value = index
}

// ⭐ LIMPIADO: Removed selectColor method - now handled by selectAttribute for variations

const scrollThumbnailsUp = () => {
  if (thumbnailScrollPosition.value > 0) {
    thumbnailScrollPosition.value--
    updateThumbnailScroll()
  }
}

const scrollThumbnailsDown = () => {
  if (thumbnailScrollPosition.value < productImages.value.length - maxVisibleThumbnails.value) {
    thumbnailScrollPosition.value++
    updateThumbnailScroll()
  }
}

const updateThumbnailScroll = () => {
  if (thumbnailList.value) {
    const scrollAmount = thumbnailScrollPosition.value * 78 // 70px thumbnail + 8px gap
    thumbnailList.value.scrollTop = scrollAmount
  }
}

// ⭐ NUEVO: Buscar variación que coincida con atributos seleccionados (usando available_variations)
const findMatchingVariationFromSelected = () => {
  if (!isProductVariable.value || availableVariations.value.length === 0) {
    console.warn('⚠️ No hay producto variable o no hay variaciones disponibles')
    return null
  }
  
  console.log('🔍 Buscando variación con atributos seleccionados:', selectedAttributes.value)
  console.log('📦 Variaciones disponibles:', availableVariations.value)
  
  // Buscar variación que coincida con TODOS los atributos seleccionados
  const match = availableVariations.value.find(variation => {
    console.log(`🔎 Comparando con variación ${variation.id}:`, variation.attributes)
    
    const matches = Object.keys(selectedAttributes.value).every(attrName => {
      const selectedValue = selectedAttributes.value[attrName]
      const variationValue = variation.attributes[attrName]
      
      console.log(`  - Atributo "${attrName}": seleccionado="${selectedValue}", variación="${variationValue}", match=${variationValue === selectedValue}`)
      
      return variationValue === selectedValue
    })
    
    console.log(`  → Variación ${variation.id} ${matches ? '✅ COINCIDE' : '❌ NO coincide'}`)
    return matches
  })
  
  if (match) {
    console.log('✅ Variación encontrada:', match.id)
  } else {
    console.error('❌ No se encontró variación que coincida con:', selectedAttributes.value)
  }
  
  return match
}

const selectAttribute = async (attributeName, option) => {
  // Crear nuevo objeto para asegurar reactividad
  selectedAttributes.value = {
    ...selectedAttributes.value,
    [attributeName]: option
  }
  
  console.log(`🎯 Atributo seleccionado: ${attributeName} = ${option}`)
  console.log('📋 Atributos seleccionados:', selectedAttributes.value)
  
  // ⭐ Si es producto variable, buscar variación en available_variations
  if (isProductVariable.value) {
    const matchingVariation = findMatchingVariationFromSelected()
    
    if (matchingVariation) {
      console.log('✅ Variación encontrada en available_variations:', matchingVariation.id)
      console.log('💰 Precio de variación:', matchingVariation.price)
      console.log('🖼️ Imagen de variación:', matchingVariation.image)
      
      // ⭐ PASO 1: Actualizar inmediatamente con datos de available_variations (rápido)
      productStore.setWooCurrentVariation({
        id: matchingVariation.id,
        price: matchingVariation.price,
        stock_status: matchingVariation.in_stock ? 'instock' : 'outofstock',
        stock_quantity: matchingVariation.stock_quantity,
        attributes: matchingVariation.attributes,
        image: matchingVariation.image || null
      })
      
      // ⭐ PASO 2: Cargar detalle completo de la variación desde el backend
      // Esto trae más información (imágenes adicionales, dimensiones, etc.)
      await loadVariation(matchingVariation.id)
    } else {
      console.warn('⚠️ No se encontró variación con esos atributos')
      productStore.setWooCurrentVariation(null)
    }
  }
}

const translateAttributeName = (attributeName) => {
  const lowerName = attributeName.toLowerCase()
  const translationKey = `productDetail.attributes.${lowerName}`
  
  // Intentar traducir, si no existe la traducción, devolver el nombre original
  const translated = t(translationKey)
  
  // Si la traducción es igual a la clave, significa que no se encontró, devolver original
  return translated === translationKey ? attributeName : translated
}

const increaseQuantity = () => {
  if (quantity.value < 99) quantity.value++
}

const decreaseQuantity = () => {
  if (quantity.value > 1) quantity.value--
}

const addToCart = async () => {
  if (!product.value || isAddingToCart.value) return
  
  // Reset estados
  addToCartSuccess.value = false
  addToCartError.value = null
  isAddingToCart.value = true
  
  try {
    // Preparar opciones del producto
    const options = {
      name: product.value.name,
      price: numericPrice.value, // ⭐ Usa precio correcto: short_description para simple, price para variable
      image: product.value.images?.[0]?.src || null,
      stock_status: product.value.stock_status
    }
    
    // ⭐ Para productos variables: agregar variation_id e imagen de variación
    if (isProductVariable.value && currentVariation.value) {
      options.variation_id = currentVariation.value.id
      // Si la variación tiene imagen, usar esa en lugar de la del producto
      if (currentVariation.value.image?.src) {
        options.image = currentVariation.value.image.src
      }
      console.log(`📦 Producto variable - Variación ID: ${currentVariation.value.id}`)
    }
    
    // Agregar atributos seleccionados
    if (Object.keys(selectedAttributes.value).length > 0) {
      options.attributes = selectedAttributes.value
    }
    
    console.log('🛒 Agregando al carrito:', {
      productId: product.value.id,
      variationId: options.variation_id || null,
      quantity: quantity.value,
      options
    })
    
    // Llamar al cartStore
    const result = await cartStore.addToCart(
      product.value.id,
      quantity.value,
      options
    )
    
    if (result.success) {
      addToCartSuccess.value = true
      console.log('✅ Producto agregado al carrito exitosamente')
      
      // Ocultar mensaje de éxito después de 3 segundos
      setTimeout(() => {
        addToCartSuccess.value = false
      }, 3000)
      
      // Resetear cantidad a 1 después de agregar
      quantity.value = 1
    } else {
      addToCartError.value = result.error || 'Error al agregar al carrito'
      console.error('❌ Error al agregar al carrito:', result.error)
    }
  } catch (err) {
    addToCartError.value = 'Error inesperado al agregar al carrito'
    console.error('❌ Error inesperado:', err)
  } finally {
    isAddingToCart.value = false
  }
}

const handleAddToWishlist = () => {
  // Check if user is authenticated
  if (!authStore.isLoggedIn) {
    // Redirect to login
    router.push({ name: `Login-${i18nStore.locale}` })
    return
  }
  
  // Show wishlist selector
  showWishlistSelector.value = true
}

const handleWishlistAdded = (wishlistId) => {
  console.log(`Product ${product.value.id} added to wishlist ${wishlistId}`)
  // Optionally show a success message
}

const handleCreateWishlist = () => {
  showWishlistSelector.value = false
  router.push({ name: `ProfileWishlist-${i18nStore.locale}` })
}

// Initialize
onMounted(() => {
  loadProduct()
})

// ⭐ NUEVO: Limpiar polling cuando se desmonte el componente
onBeforeUnmount(() => {
  stopStockPolling()
})

// ⭐ NUEVO: Watch para inicializar atributos de variación con primera variación (solo productos variables)
watch(currentVariation, (newVariation) => {
  // Si hay variación nueva, inicializar atributos seleccionados
  if (newVariation && newVariation.attributes && newVariation.attributes.length > 0) {
    console.log('🔄 Inicializando atributos con variación:', newVariation.id)
    
    // Crear nuevo objeto para forzar reactividad
    const newSelectedAttributes = {}
    newVariation.attributes.forEach(attr => {
      newSelectedAttributes[attr.name] = attr.option
      console.log(`✅ Atributo "${attr.name}" = "${attr.option}"`)
    })
    
    // Reemplazar el objeto completo para asegurar reactividad
    selectedAttributes.value = newSelectedAttributes
  }
})

// ⭐ NUEVO: Watch para cambios en productId (navegación entre productos)
watch(productId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log(`🔄 Cambio de producto detectado: ${oldId} → ${newId}`)
    
    // Detener polling anterior
    stopStockPolling()
    
    // Limpiar stock anterior
    realTimeStock.value = null
    
    // Limpiar atributos seleccionados
    selectedAttributes.value = {}
    
    // Limpiar variación actual
    productStore.setWooCurrentVariation(null)
    
    // Cargar nuevo producto
    loadProduct()
  }
})

// Watch for product changes to set default selections
watch(product, (newProduct, oldProduct) => {
  if (newProduct) {
    // ⭐ Si cambió el producto, limpiar variaciones anteriores
    if (oldProduct && newProduct.id !== oldProduct.id) {
      console.log('🔄 Cambio de producto detectado, limpiando variaciones')
      productStore.clearWooVariations()
      selectedAttributes.value = {}
    }
    
    // Reset thumbnail scroll position
    thumbnailScrollPosition.value = 0
    selectedImageIndex.value = 0
    
    // Set default attributes for selectable ones only (solo para productos NO variables)
    if (!isProductVariable.value) {
      const newSelectedAttributes = { ...selectedAttributes.value }
      selectableAttributes.value.forEach(attr => {
        if (attr.options && attr.options.length > 0 && !newSelectedAttributes[attr.name]) {
          newSelectedAttributes[attr.name] = attr.options[0]
        }
      })
      selectedAttributes.value = newSelectedAttributes
    }
  }
}, { immediate: true })
</script>

<style scoped>
.product-detail-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Main Content - Mobile First */
.main-content {
  flex: 1;
  padding-top: 80px; /* Mobile */
  background-color: #fdf2f8;
  padding-bottom: 2rem;
}

@media (min-width: 768px) {
  .main-content {
    padding-top: 90px;
    padding-bottom: 2.5rem;
  }
}

@media (min-width: 1024px) {
  .main-content {
    padding-top: 100px;
    padding-bottom: 3rem;
  }
}

.product-detail-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 0.75rem; /* Mobile */
}

@media (min-width: 640px) {
  .product-detail-view {
    padding: 1.5rem 1rem;
  }
}

@media (min-width: 1024px) {
  .product-detail-view {
    padding: 2rem 1rem;
  }
}

/* Loading and Error States - Mobile First */
.loading-container, .error-container, .not-found-container {
  text-align: center;
  padding: 2.5rem 1rem;
}

@media (min-width: 768px) {
  .loading-container, .error-container, .not-found-container {
    padding: 3.5rem 0;
  }
}

@media (min-width: 1024px) {
  .loading-container, .error-container, .not-found-container {
    padding: 4rem 0;
  }
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #DA9DFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 0.75rem;
}

@media (min-width: 768px) {
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f4f6;
    border-top: 4px solid #DA9DFF;
    margin: 0 auto 1rem;
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background-color: #DA9DFF;
  color: white;
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
}

@media (min-width: 768px) {
  .retry-btn {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
  }
}

.retry-btn:hover {
  background-color: #c084fc;
  transform: translateY(-2px);
}

/* Main Product Layout - Mobile First */
.product-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

@media (min-width: 768px) {
  .product-layout {
    gap: 2.5rem;
    margin-top: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .product-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    margin-top: 2rem;
  }
}

/* Left Side: Image Gallery - Mobile First */
.product-gallery {
  display: flex;
  flex-direction: column-reverse;
  gap: 0.75rem;
  position: static;
  align-self: center;
  height: fit-content;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .product-gallery {
    flex-direction: column-reverse;
    gap: 1rem;
    max-width: 600px;
  }
}

@media (min-width: 1024px) {
  .product-gallery {
    flex-direction: row;
    position: sticky;
    top: 120px;
    align-self: flex-start;
    max-width: none;
    margin: 0;
    z-index: 10;
  }
}

/* Thumbnail Selector - Mobile First */
.thumbnail-selector {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  max-width: none;
  align-items: center;
  justify-content: center;
  width: 100%;
}

@media (min-width: 1024px) {
  .thumbnail-selector {
    flex-direction: column;
    max-width: 80px;
    width: auto;
    justify-content: flex-start;
  }
}

.thumbnail-nav-btn {
  width: 30px;
  height: 60px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.75rem;
  color: #6b7280;
  transition: all 0.3s ease;
  display: none; /* Hidden on mobile */
  align-items: center;
  justify-content: center;
}

@media (min-width: 1024px) {
  .thumbnail-nav-btn {
    display: flex;
    width: 70px;
    height: 30px;
    font-size: 0.875rem;
  }
}

.thumbnail-nav-btn:hover:not(:disabled) {
  background-color: #DA9DFF;
  border-color: #DA9DFF;
  color: white;
  transform: scale(1.05);
}

.thumbnail-nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Thumbnail List - Mobile First */
.thumbnail-list {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  max-height: none;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  padding: 0.25rem 0;
}

.thumbnail-list::-webkit-scrollbar {
  height: 4px;
}

.thumbnail-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.thumbnail-list::-webkit-scrollbar-thumb {
  background: #DA9DFF;
  border-radius: 10px;
}

@media (min-width: 1024px) {
  .thumbnail-list {
    flex-direction: column;
    max-height: 390px;
    max-width: none;
    overflow-x: hidden;
    overflow-y: hidden;
    padding: 0;
  }
  
  .thumbnail-list::-webkit-scrollbar {
    width: 4px;
    height: 0;
  }
}

.thumbnail {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

@media (min-width: 640px) {
  .thumbnail {
    width: 65px;
    height: 65px;
    border-radius: 7px;
  }
}

@media (min-width: 1024px) {
  .thumbnail {
    width: 70px;
    height: 70px;
    border-radius: 8px;
  }
}

.thumbnail.active {
  border-color: #DA9DFF;
  box-shadow: 0 0 0 3px rgba(218, 157, 255, 0.3);
}

.thumbnail:hover {
  transform: scale(1.05);
  border-color: #DA9DFF;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Main Image Container - Mobile First */
.main-image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  aspect-ratio: 1;
  max-height: 300px;
  max-width: 300px;
  margin: 0 auto;
  width: 100%;
}

@media (min-width: 640px) {
  .main-image-container {
    border-radius: 10px;
    padding: 1.25rem;
    max-height: 380px;
    max-width: 380px;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.07);
  }
}

@media (min-width: 1024px) {
  .main-image-container {
    border-radius: 12px;
    padding: 1.5rem;
    max-height: 450px;
    max-width: 450px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

@media (min-width: 1024px) {
  .main-image {
    border-radius: 8px;
  }
}

/* Right Side: Product Information - Mobile First */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

@media (min-width: 768px) {
  .product-info {
    padding: 0.75rem 0;
  }
}

@media (min-width: 1024px) {
  .product-info {
    padding: 1rem 0;
  }
}

.product-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  font-family: 'Comfortaa', sans-serif;
  line-height: 1.2;
}

@media (min-width: 640px) {
  .product-title {
    font-size: 1.75rem;
    line-height: 1.25;
  }
}

@media (min-width: 1024px) {
  .product-title {
    font-size: 2rem;
    line-height: 1.3;
  }
}

/* Short Description - Mobile First */
.product-short-description {
  margin: 0.25rem 0;
}

.product-short-description p {
  color: #6b7280;
  line-height: 1.5;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  margin: 0;
}

@media (min-width: 768px) {
  .product-short-description p {
    font-size: 0.9375rem;
    line-height: 1.6;
  }
}

@media (min-width: 1024px) {
  .product-short-description p {
    font-size: 1rem;
  }
}

/* Reviews */
.product-reviews {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.25rem 0; /* Muy reducido */
}

.stars {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.star {
  font-size: 1rem;
  color: #e5e7eb;
  transition: color 0.2s ease;
}

@media (min-width: 768px) {
  .star {
    font-size: 1.1rem;
  }
}

@media (min-width: 1024px) {
  .star {
    font-size: 1.2rem;
  }
}

.star.filled {
  color: #fbbf24;
}

.rating-text {
  margin-left: 0.5rem;
  color: #6b7280;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
}

@media (min-width: 1024px) {
  .rating-text {
    font-size: 1rem;
  }
}

.rating-count {
  margin-left: 0.25rem;
  color: #9ca3af;
  font-size: 0.8125rem;
  font-family: 'Poppins', sans-serif;
}

@media (min-width: 1024px) {
  .rating-count {
    font-size: 0.9rem;
  }
}

/* Price */
.product-price {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 0.25rem 0; /* Muy reducido */
}

/* Price - Mobile First */
.current-price {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
  font-family: 'Poppins', sans-serif;
}

@media (min-width: 640px) {
  .current-price {
    font-size: 2rem;
  }
}

@media (min-width: 1024px) {
  .current-price {
    font-size: 2.5rem;
  }
}

.regular-price {
  font-size: 1.125rem;
  color: #9ca3af;
  text-decoration: line-through;
  font-family: 'Poppins', sans-serif;
  font-weight: 400;
}

@media (min-width: 640px) {
  .regular-price {
    font-size: 1.25rem;
  }
}

@media (min-width: 1024px) {
  .regular-price {
    font-size: 1.5rem;
  }
}

.sale-badge {
  background-color: #dc2626;
  color: white;
  padding: 0.2rem 0.625rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
}

@media (min-width: 768px) {
  .sale-badge {
    padding: 0.25rem 0.75rem;
    font-size: 0.875rem;
  }
}


/* Description - Mobile First */
.product-description {
  color: #6b7280;
  line-height: 1.5;
  font-family: 'Poppins', sans-serif;
  margin: 0.5rem 0;
  padding-bottom: 0.5rem;
  font-size: 0.875rem;
}

@media (min-width: 768px) {
  .product-description {
    line-height: 1.6;
    font-size: 0.9375rem;
  }
}

@media (min-width: 1024px) {
  .product-description {
    font-size: 1rem;
  }
}

.product-description div {
  color: #6b7280;
  line-height: inherit;
  font-family: 'Poppins', sans-serif;
}

/* Product Options - Mobile First */
.product-options {
  margin: 0.5rem 0;
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.product-options h4 {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-family: 'Comfortaa', sans-serif;
}

@media (min-width: 1024px) {
  .product-options h4 {
    font-size: 1rem;
  }
}

/* Color Selector */
.color-selector {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* Color Option - Mobile First */
.color-option {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (min-width: 640px) {
  .color-option {
    width: 42px;
    height: 42px;
  }
}

@media (min-width: 1024px) {
  .color-option {
    width: 45px;
    height: 45px;
  }
}

.color-option:hover {
  transform: scale(1.1);
  border-color: #c084fc;
  box-shadow: 0 4px 8px rgba(218, 157, 255, 0.3);
}

/* Estado ACTIVO - Contorno elegante y sutil */
.color-option.active {
  border: 3px solid #DA9DFF !important;
  box-shadow: 0 2px 8px rgba(218, 157, 255, 0.4);
  transform: scale(1.05);
}

/* Size Selector */
.size-selector {
  display: flex;
  gap: 0.5rem;
}

/* Size Option - Mobile First */
.size-option {
  padding: 0.625rem 1rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 18px;
  cursor: pointer;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
  color: #6b7280;
  font-size: 0.875rem;
}

@media (min-width: 768px) {
  .size-option {
    padding: 0.75rem 1.25rem;
    border-radius: 20px;
    font-size: 1rem;
  }
}

.size-option:hover {
  border-color: #DA9DFF;
  color: #DA9DFF;
}

.size-option.active {
  background-color: #DA9DFF;
  border-color: #DA9DFF;
  color: white;
}

/* Selectable Attributes */
.attribute-selector {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.attribute-option {
  padding: 0.5rem 0.875rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
  color: #6b7280;
  font-size: 0.8125rem;
}

@media (min-width: 768px) {
  .attribute-option {
    padding: 0.5rem 1rem;
    border-radius: 18px;
    font-size: 0.875rem;
  }
}

.attribute-option:hover {
  border-color: #DA9DFF;
  color: #DA9DFF;
}

.attribute-option.active {
  background-color: #DA9DFF;
  border-color: #DA9DFF;
  color: white;
}

/* Informative Attributes (read-only) */
.attribute-info {
  display: flex;
  align-items: center;
}

.info-value {
  color: #374151;
  font-size: 0.875rem;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
}

@media (min-width: 768px) {
  .info-value {
    font-size: 0.9375rem;
  }
}

@media (min-width: 1024px) {
  .info-value {
    font-size: 1rem;
  }
}

/* Product Actions - Mobile First */
.product-actions {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.75rem;
  margin: 1rem 0;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

@media (min-width: 640px) {
  .product-actions {
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }
}

/* Quantity Selector - Mobile First */
.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0;
  width: 100%;
  border: 2px solid #e5e7eb;
  border-radius: 22px;
  overflow: hidden;
}

@media (min-width: 640px) {
  .quantity-selector {
    width: fit-content;
    border-radius: 25px;
  }
}

.quantity-btn {
  width: 44px;
  height: 44px;
  background: white;
  border: none;
  font-size: 1.125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

@media (min-width: 640px) {
  .quantity-btn {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
}

.quantity-btn:hover:not(:disabled) {
  background-color: #f3f4f6;
  color: #374151;
}

.quantity-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity-input {
  flex: 1;
  height: 44px;
  text-align: center;
  border: none;
  border-left: 1px solid #e5e7eb;
  border-right: 1px solid #e5e7eb;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  color: #374151;
}

@media (min-width: 640px) {
  .quantity-input {
    flex: initial;
    width: 60px;
    height: 40px;
  }
}

.quantity-input:focus {
  outline: none;
}

.add-to-cart-btn {
  flex: 1;
  background-color: #64748b;
  color: white;
  border: none;
  padding: 0.875rem 1.25rem;
  border-radius: 22px;
  font-weight: 600;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
  min-height: 48px;
}

@media (min-width: 640px) {
  .add-to-cart-btn {
    padding: 0.875rem 1.5rem;
    border-radius: 25px;
    font-size: 1rem;
    min-height: 50px;
  }
}

.add-to-cart-btn:hover:not(:disabled) {
  background-color: #475569;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.4);
}

.add-to-cart-btn:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.add-to-cart-btn.success {
  background-color: #DA9DFF; /* Brand purple light */
}

.add-to-cart-btn.success:hover {
  background-color: #c084fc; /* Brand purple hover */
}

.add-to-cart-btn.out-of-stock {
  background-color: #ef4444;
  cursor: not-allowed;
}

.add-to-cart-btn.out-of-stock:hover {
  background-color: #dc2626;
  transform: none;
}

.loading-text {
  display: inline-block;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.cart-error-message {
  background-color: #fee2e2;
  color: #dc2626;
  padding: 0.625rem 0.875rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-family: 'Poppins', sans-serif;
  margin-top: 0.5rem;
  border: 1px solid #fecaca;
}

@media (min-width: 768px) {
  .cart-error-message {
    padding: 0.75rem 1rem;
    border-radius: 8px;
    font-size: 0.875rem;
  }
}

.add-to-wishlist-btn {
  flex: 1;
  background-color: #64748b;
  color: white;
  border: none;
  padding: 0.875rem 1.25rem;
  border-radius: 22px;
  font-weight: 600;
  font-size: 0.9375rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
  min-height: 48px;
}

@media (min-width: 640px) {
  .add-to-wishlist-btn {
    padding: 0.875rem 1.5rem;
    border-radius: 25px;
    font-size: 1rem;
    min-height: 50px;
  }
}

.add-to-wishlist-btn:hover:not(:disabled) {
  background-color: #475569;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(100, 116, 139, 0.4);
}

.add-to-wishlist-btn:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Touch devices optimization */
@media (hover: none) {
  .color-option:hover {
    transform: none;
  }
  
  .size-option:hover {
    border-color: #e5e7eb;
    color: #6b7280;
  }
  
  .attribute-option:hover {
    border-color: #e5e7eb;
    color: #6b7280;
  }
  
  .thumbnail:hover {
    transform: none;
    border-color: transparent;
  }
}

/* Text styling */
p {
  color: #7f8c8d;
  font-family: 'Poppins', sans-serif;
}
</style>
