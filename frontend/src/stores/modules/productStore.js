/**
 * Product Store for CrushMe e-commerce application
 * Manages products, categories, and search functionality
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { get_request } from '@/services/request_http.js';
import { PRODUCT_CATEGORIES } from '@/utils/constants.js';

export const useProductStore = defineStore('product', () => {
  // State
  const products = ref([]);
  const currentProduct = ref(null);
  const categories = ref([]);
  const featuredProducts = ref([]);
  const searchResults = ref([]);
  const recommendations = ref([]);
  
  // WooCommerce specific state
  const wooProducts = ref([]);
  const wooCategories = ref([]); // Categorías sin organizar (raw)
  const wooThemes = ref([]); // NUEVO: Categorías organizadas por temas (juguetes, lencería, etc.)
  const wooCategoryTree = ref([]); // NUEVO: Árbol jerárquico de categorías
  const wooCurrentProduct = ref(null);
  const wooConnectionStatus = ref(null);
  const selectedTheme = ref(''); // NUEVO: Tema seleccionado
  const selectedSubcategory = ref(''); // NUEVO: Subcategoría seleccionada
  const wooStats = ref(null); // ⭐ NUEVO: Estadísticas globales (total de productos, etc.)
  const trendingProducts = ref([]); // ⭐ NUEVO: Productos en tendencia (8 tops)
  
  const isLoading = ref(false);
  const isLoadingProduct = ref(false);
  const isLoadingSearch = ref(false);
  const isLoadingWoo = ref(false);
  const isLoadingWooProduct = ref(false);
  const isLoadingWooCategories = ref(false);
  const isLoadingWooThemes = ref(false); // NUEVO: Loading para temas organizados
  const isLoadingWooCategoryTree = ref(false); // NUEVO: Loading para árbol de categorías
  const isLoadingTrending = ref(false); // ⭐ NUEVO: Loading para productos en tendencia
  const error = ref(null);
  const wooError = ref(null);
  
  const searchQuery = ref('');
  const selectedCategory = ref('');
  const selectedWooCategory = ref('');

  // Getters
  const activeProducts = computed(() => 
    products.value.filter(product => product.is_active)
  );

  const inStockProducts = computed(() => 
    activeProducts.value.filter(product => product.is_in_stock)
  );

  const productsByCategory = computed(() => {
    if (!selectedCategory.value) return activeProducts.value;
    return activeProducts.value.filter(product => 
      product.category === selectedCategory.value
    );
  });

  const categoriesWithCount = computed(() => {
    return PRODUCT_CATEGORIES.map(category => ({
      ...category,
      count: products.value.filter(p => p.category === category.value && p.is_active).length
    }));
  });

  const hasProducts = computed(() => products.value.length > 0);
  const hasSearchResults = computed(() => searchResults.value.length > 0);

  // WooCommerce getters
  const activeWooProducts = computed(() => 
    wooProducts.value.filter(product => product.status === 'publish')
  );

  const inStockWooProducts = computed(() => 
    activeWooProducts.value.filter(product => product.stock_status === 'instock')
  );

  const wooProductsByCategory = computed(() => {
    if (!selectedWooCategory.value) return activeWooProducts.value;
    return activeWooProducts.value.filter(product => 
      product.categories.some(cat => cat.id === selectedWooCategory.value)
    );
  });

  const wooCategoriesWithCount = computed(() => {
    return wooCategories.value.map(category => ({
      ...category,
      count: wooProducts.value.filter(p => 
        p.categories.some(cat => cat.id === category.id) && p.status === 'publish'
      ).length
    }));
  });

  const hasWooProducts = computed(() => wooProducts.value.length > 0);
  const hasWooCategories = computed(() => wooCategories.value.length > 0);
  const hasWooThemes = computed(() => wooThemes.value.length > 0); // NUEVO
  const hasTrendingProducts = computed(() => trendingProducts.value.length > 0); // ⭐ NUEVO
  const isWooConnected = computed(() => wooConnectionStatus.value === 'OK');

  // NUEVO: Getters para temas organizados
  const wooProductsByTheme = computed(() => {
    if (!selectedTheme.value) return activeWooProducts.value;
    
    // Encontrar el tema seleccionado
    const theme = wooThemes.value.find(t => t.theme === selectedTheme.value);
    if (!theme) return [];
    
    // Obtener todos los IDs de categorías del tema (incluyendo subcategorías)
    const categoryIds = new Set();
    theme.categories.forEach(cat => {
      categoryIds.add(cat.id);
      // Agregar subcategorías si existen
      if (cat.has_subcategories && cat.subcategories) {
        cat.subcategories.forEach(sub => categoryIds.add(sub.id));
      }
    });
    
    // Filtrar productos que pertenezcan a alguna categoría del tema
    return activeWooProducts.value.filter(product =>
      product.categories.some(cat => categoryIds.has(cat.id))
    );
  });

  const wooProductsBySubcategory = computed(() => {
    if (!selectedSubcategory.value) return wooProductsByTheme.value;
    
    return activeWooProducts.value.filter(product =>
      product.categories.some(cat => cat.id === selectedSubcategory.value)
    );
  });

  // NUEVO: Obtener categorías principales de un tema específico
  const getCategoriesByTheme = (themeSlug) => {
    const theme = wooThemes.value.find(t => t.theme === themeSlug);
    return theme ? theme.categories : [];
  };

  // NUEVO: Obtener subcategorías de una categoría específica
  const getSubcategoriesByCategory = (categoryId) => {
    for (const theme of wooThemes.value) {
      const category = theme.categories.find(cat => cat.id === categoryId);
      if (category && category.has_subcategories) {
        return category.subcategories || [];
      }
    }
    return [];
  };

  // Actions

  /**
   * Fetch all products
   */
  async function fetchProducts() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('products/');
      products.value = response.data.products || [];
      return { success: true, data: products.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch products';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch product by ID
   * @param {number} productId - Product ID
   */
  async function fetchProduct(productId) {
    isLoadingProduct.value = true;
    error.value = null;

    try {
      const response = await get_request(`products/${productId}/`);
      currentProduct.value = response.data.product;
      return { success: true, data: response.data.product };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch product';
      currentProduct.value = null;
      return { success: false, error: error.value };
    } finally {
      isLoadingProduct.value = false;
    }
  }

  /**
   * Fetch products by category
   * @param {string} category - Category name
   */
  async function fetchProductsByCategory(category) {
    isLoading.value = true;
    error.value = null;
    selectedCategory.value = category;

    try {
      const response = await get_request(`products/category/?category=${category}`);
      const categoryProducts = response.data.products || [];
      
      // Update products array with category products
      // Remove existing products of this category and add new ones
      products.value = products.value.filter(p => p.category !== category);
      products.value.push(...categoryProducts);
      
      return { success: true, data: categoryProducts };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch category products';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Search products
   * @param {string} query - Search query
   */
  async function searchProducts(query) {
    if (!query || query.length < 2) {
      searchResults.value = [];
      searchQuery.value = '';
      return { success: true, data: [] };
    }

    isLoadingSearch.value = true;
    error.value = null;
    searchQuery.value = query;

    try {
      const response = await get_request(`products/search/?q=${encodeURIComponent(query)}`);
      searchResults.value = response.data.products || [];
      return { success: true, data: searchResults.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Search failed';
      searchResults.value = [];
      return { success: false, error: error.value };
    } finally {
      isLoadingSearch.value = false;
    }
  }

  /**
   * Fetch product categories
   */
  async function fetchCategories() {
    try {
      const response = await get_request('products/categories/');
      categories.value = response.data.categories || [];
      return { success: true, data: categories.value };
    } catch (err) {
      categories.value = PRODUCT_CATEGORIES;
      return { success: true, data: categories.value };
    }
  }

  /**
   * Fetch featured products
   */
  async function fetchFeaturedProducts() {
    try {
      const response = await get_request('products/featured/');
      featuredProducts.value = response.data.featured_products || [];
      return { success: true, data: featuredProducts.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch featured products';
      return { success: false, error: error.value };
    }
  }

  /**
   * Fetch product recommendations
   * @param {number} productId - Product ID for recommendations
   */
  async function fetchRecommendations(productId) {
    try {
      const response = await get_request(`products/${productId}/recommendations/`);
      recommendations.value = response.data.recommendations || [];
      return { success: true, data: recommendations.value };
    } catch (err) {
      recommendations.value = [];
      return { success: false, error: err.response?.data?.error || 'Failed to fetch recommendations' };
    }
  }

  /**
   * Get product by ID from current products
   * @param {number} productId - Product ID
   */
  function getProductById(productId) {
    return products.value.find(product => product.id === productId) || null;
  }

  /**
   * Clear search results
   */
  function clearSearch() {
    searchResults.value = [];
    searchQuery.value = '';
  }

  /**
   * Clear selected category
   */
  function clearCategory() {
    selectedCategory.value = '';
  }

  /**
   * Clear current product
   */
  function clearCurrentProduct() {
    currentProduct.value = null;
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Set loading state
   * @param {boolean} loading - Loading state
   */
  function setLoading(loading) {
    isLoading.value = loading;
  }

  /**
   * Filter products by price range
   * @param {number} minPrice - Minimum price
   * @param {number} maxPrice - Maximum price
   */
  function filterByPriceRange(minPrice, maxPrice) {
    let filtered = activeProducts.value;
    
    if (minPrice !== null && minPrice !== undefined) {
      filtered = filtered.filter(product => product.price >= minPrice);
    }
    
    if (maxPrice !== null && maxPrice !== undefined) {
      filtered = filtered.filter(product => product.price <= maxPrice);
    }
    
    return filtered;
  }

  /**
   * Sort products by criteria
   * @param {string} sortBy - Sort criteria (name, price, date)
   * @param {string} order - Sort order (asc, desc)
   */
  function sortProducts(productList, sortBy = 'name', order = 'asc') {
    const sorted = [...productList].sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'date':
          comparison = new Date(a.created_at) - new Date(b.created_at);
          break;
        default:
          comparison = 0;
      }
      
      return order === 'desc' ? -comparison : comparison;
    });
    
    return sorted;
  }

  // ========== WOOCOMMERCE ACTIONS ==========

  /**
   * Test WooCommerce connection
   */
  async function testWooConnection() {
    isLoadingWoo.value = true;
    wooError.value = null;

    try {
      const response = await get_request('products/woocommerce/test/');
      wooConnectionStatus.value = response.data.connection_status;
      return { success: true, data: response.data };
    } catch (err) {
      wooError.value = err.response?.data?.error || 'Failed to test WooCommerce connection';
      wooConnectionStatus.value = 'ERROR';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWoo.value = false;
    }
  }

  /**
   * Fetch products from WooCommerce
   * @param {object} options - Fetch options
   * @param {number} options.categoryId - Category ID filter
   * @param {number} options.perPage - Products per page (max 100)
   * @param {number} options.page - Page number
   */
  async function fetchWooProducts({ categoryId = null, perPage = 10, page = 1 } = {}) {
    isLoadingWoo.value = true;
    wooError.value = null;

    try {
      let url = `products/woocommerce/products/?per_page=${perPage}&page=${page}`;
      if (categoryId) {
        url += `&category_id=${categoryId}`;
      }

      const response = await get_request(url);
      const products = response.data.data || [];
      
      // ⭐ SIEMPRE reemplazar productos al cambiar de página (no apilar)
      wooProducts.value = products;
      
      return { 
        success: true, 
        data: products,
        pagination: response.data.pagination_info
      };
    } catch (err) {
      wooError.value = err.response?.data?.error || 'Failed to fetch WooCommerce products';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWoo.value = false;
    }
  }

  /**
   * Fetch products from WooCommerce by category
   * @param {number} categoryId - Category ID
   * @param {number} perPage - Products per page
   * @param {number} page - Page number
   */
  async function fetchWooProductsByCategory(categoryId, perPage = 10, page = 1) {
    selectedWooCategory.value = categoryId;
    return await fetchWooProducts({ categoryId, perPage, page });
  }

  /**
   * Fetch categories from WooCommerce (sin organizar)
   * @param {object} options - Fetch options
   * @param {number} options.perPage - Categories per page
   * @param {number} options.page - Page number
   */
  async function fetchWooCategories({ perPage = 100, page = 1 } = {}) {
    isLoadingWooCategories.value = true;
    wooError.value = null;

    try {
      const response = await get_request(`products/woocommerce/categories/?per_page=${perPage}&page=${page}`);
      
      // Si es la primera página, reemplazar; si no, agregar
      if (page === 1) {
        wooCategories.value = response.data.data || [];
      } else {
        wooCategories.value.push(...(response.data.data || []));
      }
      
      return { 
        success: true, 
        data: response.data.data || [],
        pagination: response.data.pagination_info
      };
    } catch (err) {
      wooError.value = err.response?.data?.error || 'Failed to fetch WooCommerce categories';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWooCategories.value = false;
    }
  }

  /**
   * ⭐ NUEVO: Fetch organized categories by themes from WooCommerce
   * Obtiene las categorías organizadas en 6 temas principales:
   * - juguetes (🎮)
   * - lenceria (👗)
   * - lubricantes (💧)
   * - bondage (⛓️)
   * - bienestar (🌿)
   * - marcas (🏷️)
   * - ofertas (💰)
   */
  async function fetchWooOrganizedCategories() {
    isLoadingWooThemes.value = true;
    wooError.value = null;

    try {
      const response = await get_request('products/woocommerce/categories/organized/');

      // 🔥 DEBUG: Ver respuesta completa del backend
      console.log('🚀 RESPUESTA COMPLETA DEL BACKEND:', {
        status: response.status,
        data: response.data,
        headers: response.headers,
        fullResponse: response
      });

      console.log('📊 DATOS DE TEMAS RECIBIDOS:', response.data.data);
      console.log('🔢 TOTAL DE CATEGORÍAS:', response.data.total_categories);

      wooThemes.value = response.data.data || [];

      return {
        success: true,
        data: response.data.data || [],
        total_categories: response.data.total_categories || 0
      };
    } catch (err) {
      // 🔥 DEBUG: Ver error completo del backend
      console.error('❌ ERROR EN LLAMADA AL BACKEND:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data,
        fullError: err
      });

      wooError.value = err.response?.data?.error || 'Failed to fetch organized WooCommerce categories';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWooThemes.value = false;
    }
  }

  /**
   * ⭐ NUEVO: Fetch category tree from WooCommerce
   * Obtiene el árbol jerárquico completo de categorías (padre-hijos)
   */
  async function fetchWooCategoryTree() {
    isLoadingWooCategoryTree.value = true;
    wooError.value = null;

    try {
      const response = await get_request('products/woocommerce/categories/tree/');
      
      wooCategoryTree.value = response.data.data || [];
      
      return { 
        success: true, 
        data: response.data.data || [],
        total: response.data.total || 0
      };
    } catch (err) {
      wooError.value = err.response?.data?.error || 'Failed to fetch WooCommerce category tree';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWooCategoryTree.value = false;
    }
  }

  /**
   * Fetch specific product from WooCommerce
   * @param {number} productId - WooCommerce product ID
   */
  async function fetchWooProduct(productId) {
    isLoadingWooProduct.value = true;
    wooError.value = null;

    try {
      const response = await get_request(`products/woocommerce/products/${productId}/`);
      
      // Verificar si la respuesta del backend es exitosa
      if (response.data.success) {
        const productData = response.data.data;
        wooCurrentProduct.value = productData;
        return { success: true, data: productData };
      } else {
        wooError.value = response.data.error || 'Error desconocido del backend';
        wooCurrentProduct.value = null;
        return { success: false, error: wooError.value };
      }
      
    } catch (err) {
      // Intentar extraer el error del backend si está disponible
      let errorMessage = 'Failed to fetch WooCommerce product';
      if (err.response?.data) {
        if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        }
      }
      
      wooError.value = errorMessage;
      wooCurrentProduct.value = null;
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWooProduct.value = false;
    }
  }

  /**
   * Get WooCommerce product by ID from current products
   * @param {number} productId - WooCommerce product ID
   */
  function getWooProductById(productId) {
    return wooProducts.value.find(product => product.id === productId) || null;
  }

  /**
   * Filter WooCommerce products by price range
   * @param {number} minPrice - Minimum price
   * @param {number} maxPrice - Maximum price
   */
  function filterWooByPriceRange(minPrice, maxPrice) {
    let filtered = activeWooProducts.value;
    
    if (minPrice !== null && minPrice !== undefined) {
      filtered = filtered.filter(product => parseFloat(product.price) >= minPrice);
    }
    
    if (maxPrice !== null && maxPrice !== undefined) {
      filtered = filtered.filter(product => parseFloat(product.price) <= maxPrice);
    }
    
    return filtered;
  }

  /**
   * Sort WooCommerce products by criteria
   * @param {Array} productList - Products to sort
   * @param {string} sortBy - Sort criteria (name, price, date)
   * @param {string} order - Sort order (asc, desc)
   */
  function sortWooProducts(productList, sortBy = 'name', order = 'asc') {
    const sorted = [...productList].sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.name.localeCompare(b.name);
          break;
        case 'price':
          comparison = parseFloat(a.price) - parseFloat(b.price);
          break;
        case 'date':
          comparison = new Date(a.date_created) - new Date(b.date_created);
          break;
        case 'popularity':
          comparison = a.total_sales - b.total_sales;
          break;
        case 'rating':
          comparison = parseFloat(a.average_rating) - parseFloat(b.average_rating);
          break;
        default:
          comparison = 0;
      }
      
      return order === 'desc' ? -comparison : comparison;
    });
    
    return sorted;
  }

  /**
   * Clear WooCommerce selected category
   */
  function clearWooCategory() {
    selectedWooCategory.value = '';
  }

  /**
   * Clear WooCommerce current product
   */
  function clearWooCurrentProduct() {
    wooCurrentProduct.value = null;
  }

  /**
   * Clear WooCommerce error state
   */
  function clearWooError() {
    wooError.value = null;
  }

  /**
   * Clear featured categories (wooThemes)
   */
  function clearFeaturedCategories() {
    wooThemes.value = [];
  }

  /**
   * Set WooCommerce loading state
   * @param {boolean} loading - Loading state
   */
  function setWooLoading(loading) {
    isLoadingWoo.value = loading;
  }

  // ========== NUEVAS FUNCIONES PARA TEMAS Y SUBCATEGORÍAS ==========

  /**
   * ⭐ NUEVO: Seleccionar un tema
   * @param {string} themeSlug - Slug del tema (juguetes, lenceria, lubricantes, etc.)
   */
  function selectTheme(themeSlug) {
    selectedTheme.value = themeSlug;
    selectedSubcategory.value = ''; // Limpiar subcategoría al cambiar tema
  }

  /**
   * ⭐ NUEVO: Seleccionar una subcategoría
   * @param {number} categoryId - ID de la categoría/subcategoría
   */
  function selectSubcategory(categoryId) {
    selectedSubcategory.value = categoryId;
  }

  /**
   * ⭐ NUEVO: Limpiar selección de tema
   */
  function clearTheme() {
    selectedTheme.value = '';
    selectedSubcategory.value = '';
  }

  /**
   * ⭐ NUEVO: Limpiar selección de subcategoría
   */
  function clearSubcategory() {
    selectedSubcategory.value = '';
  }

  /**
   * ⭐ NUEVO: Obtener tema por slug
   * @param {string} themeSlug - Slug del tema
   * @returns {object|null} Objeto del tema o null
   */
  function getThemeBySlug(themeSlug) {
    return wooThemes.value.find(theme => theme.theme === themeSlug) || null;
  }

  /**
   * ⭐ NUEVO: Obtener categoría por ID (busca en todos los temas)
   * @param {number} categoryId - ID de la categoría
   * @returns {object|null} Objeto de la categoría o null
   */
  function getCategoryById(categoryId) {
    for (const theme of wooThemes.value) {
      // Buscar en categorías principales
      const category = theme.categories.find(cat => cat.id === categoryId);
      if (category) return category;
      
      // Buscar en subcategorías
      for (const cat of theme.categories) {
        if (cat.has_subcategories && cat.subcategories) {
          const subcategory = cat.subcategories.find(sub => sub.id === categoryId);
          if (subcategory) return subcategory;
        }
      }
    }
    return null;
  }

  /**
   * ⭐ NUEVO: Obtener productos de un tema con paginación optimizada
   * @param {string} themeSlug - Slug del tema
   * @param {number} perPage - Productos por página (recomendado: 20)
   * @param {number} page - Número de página
   */
  async function fetchProductsByTheme(themeSlug, perPage = 20, page = 1) {
    const theme = getThemeBySlug(themeSlug);
    if (!theme) {
      return { success: false, error: 'Tema no encontrado' };
    }

    // Si el tema tiene una categoría principal (is_main: true), usar esa
    const mainCategory = theme.categories.find(cat => cat.is_main);
    if (mainCategory) {
      return await fetchWooProducts({ 
        categoryId: mainCategory.id, 
        perPage, 
        page 
      });
    }

    // Si no, cargar productos de la primera categoría
    if (theme.categories.length > 0) {
      return await fetchWooProducts({ 
        categoryId: theme.categories[0].id, 
        perPage, 
        page 
      });
    }

    return { success: false, error: 'No hay categorías en este tema' };
  }

  /**
   * ⭐ NUEVO: Obtener estadísticas globales de WooCommerce
   * Total de productos, categorías, top categorías, etc.
   */
  async function fetchWooStats() {
    isLoadingWoo.value = true;
    wooError.value = null;

    try {
      const response = await get_request('products/woocommerce/stats/');
      wooStats.value = response.data.data || null;
      
      return { 
        success: true, 
        data: response.data.data || null
      };
    } catch (err) {
      wooError.value = err.response?.data?.error || 'Failed to fetch WooCommerce stats';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWoo.value = false;
    }
  }

  /**
   * ⭐ NUEVO: Obtener productos en tendencia (8 tops) desde WooCommerce
   * Retorna los 8 productos más populares ordenados por:
   * Popularidad = (total_sales × 10) + (average_rating × 5) + rating_count
   * Solo incluye productos con stock disponible
   */
  async function fetchWooTrendingProducts() {
    isLoadingTrending.value = true;
    wooError.value = null;

    try {
      const response = await get_request('products/woocommerce/products/trending/');
      const products = response.data.data || [];

      trendingProducts.value = products;

      return {
        success: true,
        data: products,
        total_products: response.data.total_products || 0,
        message: response.data.message
      };
    } catch (err) {
      wooError.value = err.response?.data?.error || 'Failed to fetch trending products';
      trendingProducts.value = [];
      return { success: false, error: wooError.value };
    } finally {
      isLoadingTrending.value = false;
    }
  }

  /**
   * ⭐ NUEVO: Obtener 4 categorías destacadas aleatorias desde WooCommerce
   * Obtiene categorías principales con la imagen del primer producto disponible
   */
  async function fetchFeaturedCategories() {
    isLoadingWooThemes.value = true;
    wooError.value = null;

    try {
      const response = await get_request('products/woocommerce/categories/featured-random/');

      // 🔥 DEBUG: Ver respuesta completa del backend
      console.log('🚀 RESPUESTA FEATURED CATEGORIES:', {
        status: response.status,
        data: response.data,
        headers: response.headers,
        fullResponse: response
      });

      const featuredCategories = response.data.data || [];

      // Almacenar en wooThemes para compatibilidad con componentes existentes
      wooThemes.value = featuredCategories.map(cat => ({
        theme: cat.slug,
        name: cat.name,
        icon: cat.icon,
        first_product_image: cat.first_product_image,
        category_id: cat.category_id
      }));

      return {
        success: true,
        data: featuredCategories,
        total_selected: response.data.total_selected || 0,
        message: response.data.message
      };
    } catch (err) {
      // 🔥 DEBUG: Ver error completo del backend
      console.error('❌ ERROR EN FEATURED CATEGORIES:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data,
        fullError: err
      });

      wooError.value = err.response?.data?.error || 'Failed to fetch featured categories';
      return { success: false, error: wooError.value };
    } finally {
      isLoadingWooThemes.value = false;
    }
  }

  /**
   * ⭐ NUEVO: Obtener productos por slug de categoría desde WooCommerce
   * @param {string} categorySlug - Slug de la categoría (ej: 'juguetes', 'lenceria')
   * @param {number} perPage - Productos por página (default: 20)
   * @param {number} page - Número de página (default: 1)
   */
  async function fetchProductsByCategorySlug(categorySlug, perPage = 20, page = 1) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request(`products/category/?category=${encodeURIComponent(categorySlug)}&per_page=${perPage}&page=${page}`);

      // 🔥 DEBUG: Ver respuesta completa del backend
      console.log('🚀 RESPUESTA PRODUCTS BY CATEGORY SLUG:', {
        status: response.status,
        data: response.data,
        categorySlug,
        perPage,
        page
      });

      const categoryProducts = response.data.products || [];

      return {
        success: true,
        data: categoryProducts,
        pagination: response.data.pagination_info,
        total_products: response.data.total_products || 0
      };
    } catch (err) {
      // 🔥 DEBUG: Ver error completo del backend
      console.error('❌ ERROR EN PRODUCTS BY CATEGORY SLUG:', {
        message: err.message,
        response: err.response,
        categorySlug,
        fullError: err
      });

      error.value = err.response?.data?.error || 'Failed to fetch category products';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * ⭐ NUEVO: Carga inicial optimizada - PRIMERO categorías, DESPUÉS productos
   * Secuencia optimizada para evitar demoras innecesarias
   */
  async function initializeWooCommerce() {
    try {
      // ⚡ SKIPEADO: Test de conexión (demora ~2.5s innecesarios)
      // TODO: Reactivar en futuro si es necesario para debugging

      // 2. ⭐ ESPERAR a que las categorías se carguen completamente ANTES de productos
      const themesResult = await fetchWooOrganizedCategories();
      
      if (!themesResult.success) {
        return { success: false, error: 'Error cargando categorías - No se pueden cargar productos sin categorías' };
      }

      // 3. ⭐ Solo DESPUÉS de tener categorías, cargar productos (reducido a 9)
      const productsResult = await fetchWooProducts({ 
        perPage: 9, 
        page: 1 
      });

      // 4. ⭐ Cargar estadísticas EN BACKGROUND después de mostrar productos
      fetchWooStats();

      return { 
        success: true, 
        themes: themesResult.data,
        products: productsResult.data || [],
        total_categories: themesResult.total_categories,
        stats: null // Se cargarán después
      };
    } catch (err) {
      wooError.value = err.message || 'Error inicializando WooCommerce';
      return { success: false, error: wooError.value };
    }
  }

  return {
    // State
    products,
    currentProduct,
    categories,
    featuredProducts,
    searchResults,
    recommendations,
    isLoading,
    isLoadingProduct,
    isLoadingSearch,
    error,
    searchQuery,
    selectedCategory,
    
    // WooCommerce State
    wooProducts,
    wooCategories,
    wooThemes, // ⭐ NUEVO
    wooCategoryTree, // ⭐ NUEVO
    wooCurrentProduct,
    wooConnectionStatus,
    wooStats, // ⭐ NUEVO: Estadísticas globales
    trendingProducts, // ⭐ NUEVO: Productos en tendencia (8 tops)
    isLoadingWoo,
    isLoadingWooProduct,
    isLoadingWooCategories,
    isLoadingWooThemes, // ⭐ NUEVO
    isLoadingWooCategoryTree, // ⭐ NUEVO
    isLoadingTrending, // ⭐ NUEVO: Loading para productos en tendencia
    wooError,
    selectedWooCategory,
    selectedTheme, // ⭐ NUEVO
    selectedSubcategory, // ⭐ NUEVO
    
    // Getters
    activeProducts,
    inStockProducts,
    productsByCategory,
    categoriesWithCount,
    hasProducts,
    hasSearchResults,
    
    // WooCommerce Getters
    activeWooProducts,
    inStockWooProducts,
    wooProductsByCategory,
    wooCategoriesWithCount,
    hasWooProducts,
    hasWooCategories,
    hasWooThemes, // ⭐ NUEVO
    hasTrendingProducts, // ⭐ NUEVO
    isWooConnected,
    wooProductsByTheme, // ⭐ NUEVO
    wooProductsBySubcategory, // ⭐ NUEVO
    getCategoriesByTheme, // ⭐ NUEVO
    getSubcategoriesByCategory, // ⭐ NUEVO
    
    // Actions
    fetchProducts,
    fetchProduct,
    fetchProductsByCategory,
    searchProducts,
    fetchCategories,
    fetchFeaturedProducts,
    fetchRecommendations,
    getProductById,
    clearSearch,
    clearCategory,
    clearCurrentProduct,
    clearError,
    setLoading,
    filterByPriceRange,
    sortProducts,
    
    // WooCommerce Actions
    testWooConnection,
    fetchWooProducts,
    fetchWooProductsByCategory,
    fetchWooCategories,
    fetchWooOrganizedCategories, // ⭐ NUEVO
    fetchWooCategoryTree, // ⭐ NUEVO
    fetchWooStats, // ⭐ NUEVO: Estadísticas globales
    fetchWooTrendingProducts, // ⭐ NUEVO: Productos en tendencia (8 tops)
    fetchFeaturedCategories, // ⭐ NUEVO: Categorías destacadas aleatorias
    fetchProductsByCategorySlug, // ⭐ NUEVO: Productos por slug de categoría
    fetchWooProduct,
    getWooProductById,
    filterWooByPriceRange,
    sortWooProducts,
    clearWooCategory,
    clearWooCurrentProduct,
    clearWooError,
    clearFeaturedCategories, // ⭐ NUEVO: Limpiar categorías destacadas
    setWooLoading,
    
    // ⭐ NUEVAS ACCIONES PARA TEMAS
    selectTheme,
    selectSubcategory,
    clearTheme,
    clearSubcategory,
    getThemeBySlug,
    getCategoryById,
    fetchProductsByTheme,
    initializeWooCommerce
  };
});
