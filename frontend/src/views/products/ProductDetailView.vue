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
              <div v-if="product.short_description" class="product-short-description">
                <p v-html="product.short_description"></p>
              </div>
              
              <!-- Reviews (Real data or hardcoded fallback) -->
              <div class="product-reviews">
                <div class="stars">
                  <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= Math.floor(currentRating) }">★</span>
                  <span class="rating-text">{{ currentRating }}/5</span>
                  <span v-if="product.rating_count > 0" class="rating-count">({{ product.rating_count }} {{ $t('productDetail.reviews') }})</span>
                </div>
              </div>
              
              <!-- Price -->
              <div class="product-price">
                <span class="current-price">${{ product.price }}</span>
                <span v-if="product.on_sale && product.regular_price !== product.price" class="regular-price">
                  ${{ product.regular_price }}
                </span>
                <span v-if="product.on_sale" class="sale-badge">{{ $t('productDetail.saleBadge') }}</span>
              </div>
              
              <!-- Description (solo si no hay short_description o si es diferente) -->
              <div v-if="showFullDescription" class="product-description">
                <div v-html="product.description"></div>
              </div>
              
              <!-- Color Options (from product attributes) -->
              <div v-if="availableColors.length > 0" class="product-options">
                <h4>{{ $t('productDetail.selectColor') }}</h4>
                <div class="color-selector">
                  <div 
                    v-for="(color, index) in availableColors" 
                    :key="index"
                    class="color-option"
                    :class="{ active: selectedColor?.name === color.name }"
                    :style="{ backgroundColor: color.value || color.defaultColor }"
                    @click="selectColor(color)"
                    :title="color.name"
                  ></div>
                </div>
              </div>
              
              <!-- Size Options (from product attributes) -->
              <div v-if="availableSizes.length > 0" class="product-options">
                <h4>{{ $t('productDetail.selectSize') }}</h4>
                <div class="size-selector">
                  <button 
                    v-for="size in availableSizes" 
                    :key="size"
                    class="size-option"
                    :class="{ active: selectedSize === size }"
                    @click="selectedSize = size"
                  >
                    {{ size }}
                  </button>
                </div>
              </div>
              
              <!-- Selectable Attributes (multiple options) -->
              <div v-for="attr in selectableAttributes" :key="attr.id" class="product-options">
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
                  @click="addToWishlist" 
                  :disabled="product.stock_status === 'outofstock'"
                  class="add-to-wishlist-btn"
                >
                  {{ $t('productDetail.addToWishlist') }}
                </button>
              </div>
              
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
      
      <!-- FAQ Section -->
      <FAQ />
    </main>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useProductStore } from '@/stores/modules/productStore'
import { useCartStore } from '@/stores/modules/cartStore'
import Navbar from '@/components/shared/Navbar.vue'
import Footer from '@/components/shared/Footer.vue'
import FAQ from '@/components/shared/FAQ.vue'

// Props
defineProps({
  id: {
    type: String,
    required: true
  }
})

// Router and Store
const route = useRoute()
const { t } = useI18n()
const productStore = useProductStore()
const cartStore = useCartStore()

// Reactive data
const selectedImageIndex = ref(0)
const selectedColor = ref(null)
const selectedSize = ref('')
const selectedAttributes = ref({})
const quantity = ref(1)
const isAddingToCart = ref(false)
const addToCartSuccess = ref(false)
const addToCartError = ref(null)
const thumbnailScrollPosition = ref(0)
const maxVisibleThumbnails = ref(5)
const thumbnailList = ref(null)

// Computed properties
const productId = computed(() => route.params.id)
const product = computed(() => productStore.wooCurrentProduct)
const isLoadingProduct = computed(() => productStore.isLoadingWooProduct)
const error = computed(() => productStore.wooError)

// Reviews handling (real data with fallback)
const currentRating = computed(() => {
  if (product.value?.average_rating) {
    return parseFloat(product.value.average_rating)
  }
  return 4.5 // Fallback hardcoded rating
})

// Images handling
const productImages = computed(() => {
  if (!product.value?.images || product.value.images.length === 0) {
    return [
      { src: 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&h=500&fit=crop&crop=center' },
      { src: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&h=500&fit=crop&crop=center' },
      { src: 'https://images.unsplash.com/photo-1519947486511-46149fa0a254?w=500&h=500&fit=crop&crop=center' }
    ]
  }
  return product.value.images
})

const selectedImage = computed(() => {
  return productImages.value[selectedImageIndex.value]?.src || productImages.value[0]?.src
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

// Extract attributes from product data
const availableColors = computed(() => {
  if (!product.value?.attributes) return []
  
  const colorAttr = product.value.attributes.find(attr => 
    attr.name.toLowerCase().includes('color') || 
    attr.name.toLowerCase().includes('colour') ||
    attr.name.toLowerCase().includes('cor')
  )
  
  if (!colorAttr || !colorAttr.options) return []
  
  // Map color names to hex values (fallback colors)
  const colorMap = {
    'red': '#dc2626', 'rojo': '#dc2626',
    'blue': '#2563eb', 'azul': '#2563eb',
    'green': '#16a34a', 'verde': '#16a34a',
    'black': '#1f2937', 'negro': '#1f2937',
    'white': '#f9fafb', 'blanco': '#f9fafb',
    'yellow': '#eab308', 'amarillo': '#eab308',
    'purple': '#9333ea', 'morado': '#9333ea',
    'pink': '#ec4899', 'rosa': '#ec4899',
    'orange': '#ea580c', 'naranja': '#ea580c',
    'gray': '#6b7280', 'gris': '#6b7280'
  }
  
  return colorAttr.options.map(colorName => ({
    name: colorName,
    value: colorMap[colorName.toLowerCase()] || '#6b7280',
    defaultColor: '#6b7280'
  }))
})

const availableSizes = computed(() => {
  if (!product.value?.attributes) return []
  
  const sizeAttr = product.value.attributes.find(attr => 
    attr.name.toLowerCase().includes('size') || 
    attr.name.toLowerCase().includes('talla') ||
    attr.name.toLowerCase().includes('tamaño')
  )
  
  return sizeAttr?.options || []
})

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

// Methods
const loadProduct = async () => {
  if (!productId.value) return
  
  console.log(`🛍️ Cargando producto ID: ${productId.value}`)
  
  try {
    const result = await productStore.fetchWooProduct(productId.value)
    if (result.success) {
      console.log('✅ Producto cargado:', result.data.name)
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

const selectColor = (color) => {
  selectedColor.value = color
  console.log('Color seleccionado:', color.name)
}

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

const selectAttribute = (attributeName, option) => {
  selectedAttributes.value[attributeName] = option
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
      price: parseFloat(product.value.price),
      image: product.value.images?.[0]?.src || null,
      stock_status: product.value.stock_status
    }
    
    // Agregar atributos seleccionados
    if (selectedColor.value) {
      options.color = selectedColor.value.name
    }
    
    if (selectedSize.value) {
      options.size = selectedSize.value
    }
    
    // Agregar otros atributos
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

const addToWishlist = () => {
  console.log('Adding to wishlist:', {
    product: product.value.name,
    productId: product.value.id
  })
  // TODO: Implement wishlist functionality
}

// Initialize
onMounted(() => {
  loadProduct()
})

// Watch for product changes to set default selections
watch(product, (newProduct) => {
  if (newProduct) {
    // Reset thumbnail scroll position
    thumbnailScrollPosition.value = 0
    selectedImageIndex.value = 0
    
    // Set default color selection
    if (availableColors.value.length > 0 && !selectedColor.value) {
      selectedColor.value = availableColors.value[0]
    }
    
    // Set default size selection
    if (availableSizes.value.length > 0 && !selectedSize.value) {
      // Try to select 'Large' or 'Medium' as default, otherwise first option
      const preferredSizes = ['Large', 'L', 'Medium', 'M']
      const defaultSize = availableSizes.value.find(size => 
        preferredSizes.some(preferred => size.toLowerCase().includes(preferred.toLowerCase()))
      ) || availableSizes.value[0]
      selectedSize.value = defaultSize
    }
    
    // Set default attributes for selectable ones only
    selectableAttributes.value.forEach(attr => {
      if (attr.options && attr.options.length > 0 && !selectedAttributes.value[attr.name]) {
        selectedAttributes.value[attr.name] = attr.options[0]
      }
    })
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
