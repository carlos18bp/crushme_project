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
                  :disabled="product.stock_status === 'outofstock' || isAddingToCart"
                  class="add-to-cart-btn"
                  :class="{ 'success': addToCartSuccess }"
                >
                  <span v-if="isAddingToCart" class="loading-text">⏳</span>
                  <span v-else-if="addToCartSuccess">✓ {{ $t('productDetail.addedToCart') }}</span>
                  <span v-else>{{ $t('productDetail.addToCart') }}</span>
                </button>
                <button 
                  @click="handleAddToWishlist" 
                  :disabled="product.stock_status === 'outofstock'"
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useProductStore } from '@/stores/modules/productStore'
import { useCartStore } from '@/stores/modules/cartStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useReviewStore } from '@/stores/modules/reviewStore'
import { getFormattedProductPrice, getProductPrice, isSimpleProduct } from '@/utils/priceHelper.js'
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

// ⭐ NUEVO: Atributos que generan variaciones (variation: true)
const variationAttributes = computed(() => {
  if (!product.value?.attributes) return []
  
  return product.value.attributes.filter(attr => attr.variation === true)
})

// ⭐ NUEVO: Imágenes a mostrar (variación o producto base)
const displayImages = computed(() => {
  // Si es producto variable y hay variación seleccionada con imagen, usar esa
  if (isProductVariable.value && currentVariation.value?.image?.src) {
    console.log('🖼️ [ProductDetail] Usando imagen de variación')
    return [currentVariation.value.image]
  }
  
  // Si no, usar imágenes del producto base
  console.log('🖼️ [ProductDetail] Usando imágenes del producto base')
  return baseProductImages.value
})

// ⭐ Computed: Precio formateado del producto o variación
const displayPrice = computed(() => {
  if (!product.value) return '$0'
  
  // Para productos simples: extraer precio de short_description
  if (isProductSimple.value) {
    const extractedPrice = getFormattedProductPrice(product.value)
    console.log(`💰 [ProductDetail] Producto simple - Precio extraído: ${extractedPrice}`)
    return extractedPrice
  }
  
  // Para productos variables: usar variación si está seleccionada
  if (isProductVariable.value && currentVariation.value) {
    const variationPrice = getFormattedProductPrice(currentVariation.value)
    console.log(`💰 [ProductDetail] Variación seleccionada - Precio: ${variationPrice}`)
    return variationPrice
  }
  
  // Fallback: precio base del producto
  console.log(`💰 [ProductDetail] Producto variable sin variación - Usando precio base: $${product.value.price}`)
  return `$${product.value.price}`
})

// ⭐ Computed: Precio numérico del producto o variación (para cálculos)
const numericPrice = computed(() => {
  if (!product.value) return 0
  
  // Para productos simples: extraer precio de short_description
  if (isProductSimple.value) {
    return getProductPrice(product.value) || 0
  }
  
  // Para productos variables: usar variación si está seleccionada
  if (isProductVariable.value && currentVariation.value) {
    return getProductPrice(currentVariation.value) || 0
  }
  
  // Fallback: usar product.price
  return parseFloat(product.value.price) || 0
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
      
      // ⭐ CARGAR PRIMERA VARIACIÓN POR DEFECTO
      const firstVariationId = result.data[0].id
      console.log(`🎯 Cargando primera variación por defecto: ${firstVariationId}`)
      
      await loadVariation(firstVariationId)
    }
  } catch (err) {
    console.error('❌ Error cargando variaciones:', err)
  }
}

// ⭐ NUEVO: Cargar una variación específica
const loadVariation = async (variationId) => {
  if (!product.value) return
  
  console.log(`🔄 Cargando variación ${variationId}`)
  
  try {
    const result = await productStore.fetchWooProductVariation(product.value.id, variationId)
    
    if (result.success) {
      console.log(`✅ Variación ${variationId} cargada`)
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

// Methods
const loadProduct = async () => {
  if (!productId.value) return
  
  console.log(`🛍️ Cargando producto ID: ${productId.value}`)
  
  try {
    const result = await productStore.fetchWooProduct(productId.value)
    if (result.success) {
      console.log('✅ Producto cargado:', result.data.name)
      
      // ⭐ Si es producto variable, cargar variaciones automáticamente
      if (result.data.type === 'variable') {
        await loadVariations()
      }
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

const selectAttribute = async (attributeName, option) => {
  // Crear nuevo objeto para asegurar reactividad
  selectedAttributes.value = {
    ...selectedAttributes.value,
    [attributeName]: option
  }
  
  console.log(`🎯 Atributo seleccionado: ${attributeName} = ${option}`)
  
  // ⭐ Si es producto variable, buscar y cargar la variación correspondiente
  if (isProductVariable.value) {
    await selectVariationByAttributes(selectedAttributes.value)
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
    
    // Agregar atributos seleccionados
    if (Object.keys(selectedAttributes.value).length > 0) {
      options.attributes = selectedAttributes.value
    }
    
    console.log('🛒 Agregando al carrito:', {
      productId: product.value.id,
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

.main-content {
  flex: 1;
  padding-top: 100px; /* Más espacio para el navbar */
  background-color: #fdf2f8;
  padding-bottom: 3rem; /* Espacio antes del footer */
}

.product-detail-view {
  max-width: 1600px; /* Aumentado de 1400px para usar más ancho */
  margin: 0 auto;
  padding: 2rem 1rem; /* Reducido padding lateral */
}

/* Loading and Error States */
.loading-container, .error-container, .not-found-container {
  text-align: center;
  padding: 4rem 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #DA9DFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background-color: #DA9DFF;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
}

.retry-btn:hover {
  background-color: #c084fc;
  transform: translateY(-2px);
}

/* Main Product Layout */
.product-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  margin-top: 2rem;
}

/* Left Side: Image Gallery */
.product-gallery {
  display: flex;
  gap: 1rem;
  position: sticky;
  top: 120px; /* Más espacio para el navbar + margen */
  align-self: flex-start;
  height: fit-content;
  z-index: 10; /* Asegurar que esté por encima de otros elementos */
}

.thumbnail-selector {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 80px;
  align-items: center;
}

.thumbnail-nav-btn {
  width: 70px;
  height: 30px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  color: #6b7280;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
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

.thumbnail-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 390px; /* 5 thumbnails * 78px */
  overflow-y: hidden;
  scroll-behavior: smooth;
}

.thumbnail {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  flex-shrink: 0;
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

.main-image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  aspect-ratio: 1;
  max-height: 450px;
  max-width: 450px;
  margin: 0 auto;
}

.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

/* Right Side: Product Information */
.product-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* Reducido aún más para compactar */
  padding: 1rem 0;
}

.product-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0; /* Sin margin */
  font-family: 'Comfortaa', sans-serif;
  line-height: 1.3;
}

/* Short Description */
.product-short-description {
  margin: 0.25rem 0; /* Muy reducido */
}

.product-short-description p {
  color: #6b7280;
  line-height: 1.6;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  margin: 0;
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
  font-size: 1.2rem;
  color: #e5e7eb;
  transition: color 0.2s ease;
}

.star.filled {
  color: #fbbf24;
}

.rating-text {
  margin-left: 0.5rem;
  color: #6b7280;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
}

.rating-count {
  margin-left: 0.25rem;
  color: #9ca3af;
  font-size: 0.9rem;
  font-family: 'Poppins', sans-serif;
}

/* Price */
.product-price {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 0.25rem 0; /* Muy reducido */
}

.current-price {
  font-size: 2.5rem;
  font-weight: 600; /* Reducido de 700 a 600 */
  color: #2c3e50;
  font-family: 'Poppins', sans-serif;
}

.regular-price {
  font-size: 1.5rem;
  color: #9ca3af;
  text-decoration: line-through;
  font-family: 'Poppins', sans-serif;
  font-weight: 400; /* Asegurar peso normal */
}

.sale-badge {
  background-color: #dc2626;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
}

/* Description */
.product-description {
  color: #6b7280;
  line-height: 1.6;
  font-family: 'Poppins', sans-serif;
  margin: 0.5rem 0; /* Muy reducido */
  padding-bottom: 0.5rem; /* Espacio antes de la siguiente sección */
}

.product-description div {
  color: #6b7280;
  line-height: 1.6;
  font-family: 'Poppins', sans-serif;
}

/* Product Options */
.product-options {
  margin: 0.5rem 0; /* Muy reducido */
  padding-top: 0.75rem; /* Muy reducido */
  padding-bottom: 0.75rem; /* Espacio después de cada sección */
  border-top: 1px solid #e5e7eb; /* Línea separadora visible entre secciones */
}

.product-options h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem; /* Reducido */
  font-family: 'Comfortaa', sans-serif; /* Asegurar Comfortaa para títulos */
}

/* Color Selector */
.color-selector {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.color-option {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #e5e7eb;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.size-option {
  padding: 0.75rem 1.25rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 20px; /* Más redondo */
  cursor: pointer;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
  color: #6b7280;
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
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 18px; /* Más redondo */
  cursor: pointer;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
  transition: all 0.3s ease;
  color: #6b7280;
  font-size: 0.875rem;
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
  font-size: 1rem;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
}

/* Product Actions */
.product-actions {
  display: flex;
  flex-direction: row; /* TODOS en la misma fila */
  align-items: center;
  gap: 1rem;
  margin: 1rem 0; /* Muy reducido */
  padding-top: 0.75rem; /* Muy reducido */
  border-top: 1px solid #e5e7eb; /* Línea separadora */
}

/* Quantity Selector */
.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0;
  width: fit-content;
  border: 2px solid #e5e7eb;
  border-radius: 25px; /* Más redondo */
  overflow: hidden;
}

.quantity-btn {
  width: 40px;
  height: 40px;
  background: white;
  border: none;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
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
  width: 60px;
  height: 40px;
  text-align: center;
  border: none;
  border-left: 1px solid #e5e7eb;
  border-right: 1px solid #e5e7eb;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  color: #374151;
}

.quantity-input:focus {
  outline: none;
}

.add-to-cart-btn {
  flex: 1;
  background-color: #64748b;
  color: white;
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 25px; /* Más redondo */
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif; /* Poppins para botones */
  min-height: 50px;
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
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: 'Poppins', sans-serif;
  margin-top: 0.5rem;
  border: 1px solid #fecaca;
}

.add-to-wishlist-btn {
  flex: 1;
  background-color: #64748b;
  color: white;
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 25px; /* Más redondo */
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif; /* Poppins para botones */
  min-height: 50px;
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

/* Responsive Design */
@media (max-width: 1024px) {
  .product-layout {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .product-gallery {
    justify-content: center;
    position: static; /* Disable sticky on tablets */
  }
  
  .thumbnail-selector {
    flex-direction: row;
    max-width: none;
    width: 100%;
    justify-content: center;
  }
  
  .thumbnail-nav-btn {
    display: none; /* Ocultar flechas en tablets */
  }
  
  .thumbnail-list {
    flex-direction: row;
    max-height: none;
    max-width: 500px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.5rem 0;
  }
  
  .thumbnail-list::-webkit-scrollbar {
    height: 6px;
  }
  
  .thumbnail-list::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
  }
  
  .thumbnail-list::-webkit-scrollbar-thumb {
    background: #DA9DFF;
    border-radius: 10px;
  }
}

@media (max-width: 768px) {
  .product-detail-view {
    padding: 1rem 0.5rem; /* Aún menos padding en móviles */
  }
  
  .product-title {
    font-size: 1.5rem;
  }
  
  .current-price {
    font-size: 2rem;
  }
  
  .regular-price {
    font-size: 1.25rem;
  }
  
  .product-actions {
    flex-wrap: wrap; /* Permitir wrap en móviles si es necesario */
    gap: 0.75rem;
  }
  
  .add-to-cart-btn,
  .add-to-wishlist-btn {
    font-size: 0.875rem; /* Texto más pequeño en móviles */
    padding: 0.75rem 1rem;
    flex: 0 1 auto; /* No forzar flex: 1 en móviles */
  }
  
  .main-image-container {
    max-height: 350px;
    max-width: 350px;
    padding: 1rem;
  }
  
  .thumbnail-list {
    max-width: 100%;
  }
  
  .color-option {
    width: 40px;
    height: 40px;
  }
}

/* Text styling */
p {
  color: #7f8c8d;
  font-family: 'Poppins', sans-serif;
}
</style>
