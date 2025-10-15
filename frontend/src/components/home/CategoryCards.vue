<template>
    <div class="min-h-screen bg-white py-20 px-8">
      <div class="max-w-[1600px] mx-auto">
        <!-- Título principal -->
        <h1 class="text-4xl md:text-5xl font-bold mb-12 text-gray-800">
          {{ $t('categories.title') }} 🎀
        </h1>
  
        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center items-center py-20">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
          <span class="ml-4 text-gray-600">{{ $t('categories.loading') }}</span>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="text-center py-20">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <button @click="retryLoadCategories" class="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors">
            {{ $t('categories.retry') }}
          </button>
        </div>

        <!-- Grid de categorías -->
        <div v-else-if="categories.length > 0" class="grid grid-cols-3 gap-6">
          <!-- Primera fila: 2 columnas + 1 columna -->
          <div
            v-for="(category, index) in categories"
            :key="category.id"
            @click="handleCategoryClick(category)"
            class="bg-white border-4 border-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer hover:scale-105"
            :class="getGridClasses(index)"
          >
            <div class="p-6 pb-4">
              <h2 class="text-2xl font-semibold text-gray-700 flex items-center gap-2">
                {{ category.title }}
              </h2>
            </div>
            <div class="relative flex justify-end h-64 w-full overflow-hidden bg-gray-100">
                <img
                    :src="category.image"
                    :alt="category.title"
                    class="h-full max-h-64 object-cover"
                    @error="handleImageError"
                />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-20">
          <p class="text-gray-600">{{ $t('categories.noCategories') }}</p>
        </div>
      </div>
    </div>
  </template>

  <style scoped>
  /* Responsive Design */
  @media (max-width: 1200px) {
    .min-h-screen {
      padding-left: 2rem;
      padding-right: 2rem;
    }
  }

  @media (max-width: 768px) {
    .min-h-screen {
      padding: 3rem 1.5rem;
    }

    h1 {
      font-size: 2.5rem;
    }
  }

  @media (max-width: 480px) {
    .min-h-screen {
      padding: 2rem 1rem;
    }

    h1 {
      font-size: 2rem;
    }
  }
  </style>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useProductStore } from '@/stores/modules/productStore'
  import { useRouter } from 'vue-router'
  import { useI18nStore } from '@/stores/modules/i18nStore'

  // Stores
  const productStore = useProductStore()
  const router = useRouter()
  const i18nStore = useI18nStore()

  // Estado local
  const isLoading = ref(false)
  const error = ref(null)

  // Datos dinámicos desde el store
  const themes = computed(() => productStore.wooThemes || [])

  // Mapear temas a formato de categorías con imágenes reales del backend
  const categories = computed(() => {
    return themes.value.slice(0, 4).map(theme => {
      // Usar imagen real del backend si está disponible, sino fallback a placeholder
      const imageUrl = theme.first_product_image ||
                      `https://via.placeholder.com/400x300/${getThemeColor(theme.theme)}/FFFFFF?text=${encodeURIComponent(theme.name)}`;

      return {
        id: theme.theme,
        title: theme.name,
        image: imageUrl,
        slug: theme.theme,
        icon: theme.icon || '📦' // Icono por defecto si no viene
      }
    })
  })

  // Función para obtener colores para cada tema
  const getThemeColor = (themeSlug) => {
    const colors = {
      'juguetes': 'FF69B4',
      'lenceria': '4A6FA5',
      'accesorios': 'E9C3CD',
      'ropa-interior': 'DDA0DD',
      'default': '9D51FF'
    }
    return colors[themeSlug] || colors.default
  }

  // Función para manejar clic en categoría
  const handleCategoryClick = async (category) => {
    try {
      // Primero cargar productos de la categoría usando el nuevo endpoint
      const result = await productStore.fetchProductsByCategorySlug(category.slug, 20, 1)

      if (result.success) {
        // Si se cargaron productos exitosamente, navegar a la página de productos
        const currentLang = i18nStore.locale
        router.push({
          name: `Products-${currentLang}`,
          query: { category: category.slug }
        })
      } else {
        console.error('Error loading category products:', result.error)
        // Navegar de todas formas para mostrar el error en la página de productos
        const currentLang = i18nStore.locale
        router.push({
          name: `Products-${currentLang}`,
          query: { category: category.slug }
        })
      }
    } catch (err) {
      console.error('Error navigating to category:', err)
      // Navegar de todas formas incluso si hay error
      const currentLang = i18nStore.locale
      router.push({
        name: `Products-${currentLang}`,
        query: { category: category.slug }
      })
    }
  }

  // Función para obtener clases CSS del grid según el índice
  const getGridClasses = (index) => {
    const gridClasses = [
      'col-span-2', // Primera posición: 2 columnas
      'col-span-1', // Segunda posición: 1 columna
      'col-span-1', // Tercera posición: 1 columna
      'col-span-2'  // Cuarta posición: 2 columnas
    ]
    return gridClasses[index] || 'col-span-1'
  }

  // Función para reintentar cargar categorías
  const retryLoadCategories = async () => {
    isLoading.value = true
    error.value = null

    try {
      // Usar la nueva función del store para categorías destacadas con imágenes reales
      const result = await productStore.fetchFeaturedCategories()
      if (!result.success) {
        throw new Error(result.error || 'Error loading featured categories')
      }
    } catch (err) {
      error.value = err.message || 'Error loading categories'
      console.error('Error loading themes:', err)
    } finally {
      isLoading.value = false
    }
  }

  // Cargar categorías destacadas con imágenes reales del backend
  onMounted(async () => {
    // Solo cargar si no hay temas ya cargados
    if (themes.value.length === 0) {
      isLoading.value = true
      error.value = null

      try {
        // Usar la nueva función del store para categorías destacadas con imágenes reales
        const result = await productStore.fetchFeaturedCategories()
        if (!result.success) {
          throw new Error(result.error || 'Error loading featured categories')
        }
      } catch (err) {
        error.value = err.message || 'Error loading categories'
        console.error('Error loading themes:', err)
      } finally {
        isLoading.value = false
      }
    }
  })
  </script>