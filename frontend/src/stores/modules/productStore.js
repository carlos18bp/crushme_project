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
  
  const isLoading = ref(false);
  const isLoadingProduct = ref(false);
  const isLoadingSearch = ref(false);
  const error = ref(null);
  
  const searchQuery = ref('');
  const selectedCategory = ref('');

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
      console.warn('Failed to fetch categories from API, using local constants');
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
    
    // Getters
    activeProducts,
    inStockProducts,
    productsByCategory,
    categoriesWithCount,
    hasProducts,
    hasSearchResults,
    
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
    sortProducts
  };
});
