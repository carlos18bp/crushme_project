/**
 * Wishlist Store for CrushMe e-commerce application
 * Manages wishlists, wishlist items, and favorites
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  create_request, 
  update_request, 
  delete_request,
  patch_request
} from '@/services/request_http.js';
import { WISHLIST_PRIORITIES } from '@/utils/constants.js';

export const useWishlistStore = defineStore('wishlist', () => {
  // State
  const wishlists = ref([]);
  const currentWishlist = ref(null);
  const publicWishlists = ref([]);
  const favoriteWishlists = ref([]);
  
  const isLoading = ref(false);
  const isLoadingWishlist = ref(false);
  const isUpdating = ref(false);
  const error = ref(null);

  // Getters
  const totalWishlists = computed(() => wishlists.value.length);

  const activeWishlists = computed(() => 
    wishlists.value.filter(wishlist => wishlist.is_active)
  );

  const publicUserWishlists = computed(() => 
    activeWishlists.value.filter(wishlist => wishlist.is_public)
  );

  const privateWishlists = computed(() => 
    activeWishlists.value.filter(wishlist => !wishlist.is_public)
  );

  const hasWishlists = computed(() => wishlists.value.length > 0);

  const totalWishlistValue = computed(() => {
    return wishlists.value.reduce((total, wishlist) => total + parseFloat(wishlist.total_value || 0), 0);
  });

  const totalWishlistItems = computed(() => {
    return wishlists.value.reduce((total, wishlist) => total + (wishlist.total_items || 0), 0);
  });

  // Actions

  /**
   * Fetch user's wishlists
   */
  async function fetchWishlists() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('wishlists/');
      wishlists.value = response.data.wishlists || [];
      return { success: true, data: wishlists.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch wishlists';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Fetch wishlist by ID
   * @param {number} wishlistId - Wishlist ID
   */
  async function fetchWishlist(wishlistId) {
    isLoadingWishlist.value = true;
    error.value = null;

    try {
      const response = await get_request(`wishlists/${wishlistId}/`);
      currentWishlist.value = response.data.wishlist;
      return { success: true, data: response.data.wishlist };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch wishlist';
      currentWishlist.value = null;
      return { success: false, error: error.value };
    } finally {
      isLoadingWishlist.value = false;
    }
  }

  /**
   * Create new wishlist
   * @param {Object} wishlistData - Wishlist data
   * @param {string} wishlistData.name - Wishlist name
   * @param {string} wishlistData.description - Wishlist description
   * @param {boolean} wishlistData.is_public - Public visibility
   */
  async function createWishlist(wishlistData) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request('wishlists/create/', wishlistData);
      
      const newWishlist = response.data.wishlist;
      wishlists.value.unshift(newWishlist);
      
      return { 
        success: true, 
        message: response.data.message,
        data: newWishlist 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to create wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Update wishlist
   * @param {number} wishlistId - Wishlist ID
   * @param {Object} updateData - Update data
   */
  async function updateWishlist(wishlistId, updateData) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await update_request(`wishlists/${wishlistId}/update/`, updateData);
      
      const updatedWishlist = response.data.wishlist;
      
      // Update in list
      const index = wishlists.value.findIndex(w => w.id === wishlistId);
      if (index !== -1) {
        wishlists.value[index] = updatedWishlist;
      }
      
      // Update current if it's the same
      if (currentWishlist.value?.id === wishlistId) {
        currentWishlist.value = updatedWishlist;
      }
      
      return { 
        success: true, 
        message: response.data.message,
        data: updatedWishlist 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to update wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Delete wishlist
   * @param {number} wishlistId - Wishlist ID
   */
  async function deleteWishlist(wishlistId) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request(`wishlists/${wishlistId}/delete/`);
      
      // Remove from list
      wishlists.value = wishlists.value.filter(w => w.id !== wishlistId);
      
      // Clear current if it's the same
      if (currentWishlist.value?.id === wishlistId) {
        currentWishlist.value = null;
      }
      
      return { 
        success: true, 
        message: response.data.message 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to delete wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Add product to wishlist
   * @param {number} wishlistId - Wishlist ID
   * @param {number} productId - Product ID
   * @param {string} notes - Optional notes
   * @param {string} priority - Priority level
   */
  async function addProductToWishlist(wishlistId, productId, notes = '', priority = 'medium') {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request(`wishlists/${wishlistId}/add-product/`, {
        product_id: productId,
        notes,
        priority
      });
      
      const updatedWishlist = response.data.wishlist;
      
      // Update in list
      const index = wishlists.value.findIndex(w => w.id === wishlistId);
      if (index !== -1) {
        wishlists.value[index] = updatedWishlist;
      }
      
      // Update current if it's the same
      if (currentWishlist.value?.id === wishlistId) {
        currentWishlist.value = updatedWishlist;
      }
      
      return { 
        success: true, 
        message: response.data.message,
        data: updatedWishlist 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to add product to wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Remove product from wishlist
   * @param {number} wishlistId - Wishlist ID
   * @param {number} productId - Product ID
   */
  async function removeProductFromWishlist(wishlistId, productId) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request(`wishlists/${wishlistId}/remove-product/${productId}/`);
      
      const updatedWishlist = response.data.wishlist;
      
      // Update in list
      const index = wishlists.value.findIndex(w => w.id === wishlistId);
      if (index !== -1) {
        wishlists.value[index] = updatedWishlist;
      }
      
      // Update current if it's the same
      if (currentWishlist.value?.id === wishlistId) {
        currentWishlist.value = updatedWishlist;
      }
      
      return { 
        success: true, 
        message: response.data.message,
        data: updatedWishlist 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to remove product from wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Update wishlist item
   * @param {number} wishlistId - Wishlist ID
   * @param {number} itemId - Item ID
   * @param {Object} updateData - Update data
   */
  async function updateWishlistItem(wishlistId, itemId, updateData) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await update_request(`wishlists/${wishlistId}/items/${itemId}/update/`, updateData);
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.item 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to update wishlist item';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Fetch public wishlist by UUID
   * @param {string} uuid - Wishlist UUID
   */
  async function fetchPublicWishlist(uuid) {
    isLoadingWishlist.value = true;
    error.value = null;

    try {
      const response = await get_request(`wishlists/public/${uuid}/`);
      return { success: true, data: response.data.wishlist };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch public wishlist';
      return { success: false, error: error.value };
    } finally {
      isLoadingWishlist.value = false;
    }
  }

  /**
   * Search public wishlists
   */
  async function searchPublicWishlists() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('wishlists/public/');
      publicWishlists.value = response.data.wishlists || [];
      return { success: true, data: publicWishlists.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to search public wishlists';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Add wishlist to favorites
   * @param {number} wishlistId - Wishlist ID
   */
  async function favoriteWishlist(wishlistId) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request(`wishlists/${wishlistId}/favorite/`, {});
      return { 
        success: true, 
        message: response.data.message 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to favorite wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Remove wishlist from favorites
   * @param {number} wishlistId - Wishlist ID
   */
  async function unfavoriteWishlist(wishlistId) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request(`wishlists/${wishlistId}/unfavorite/`);
      
      // Remove from favorites list
      favoriteWishlists.value = favoriteWishlists.value.filter(
        fav => fav.wishlist.id !== wishlistId
      );
      
      return { 
        success: true, 
        message: response.data.message 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to unfavorite wishlist';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Fetch favorite wishlists
   */
  async function fetchFavoriteWishlists() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('wishlists/favorites/');
      favoriteWishlists.value = response.data.favorite_wishlists || [];
      return { success: true, data: favoriteWishlists.value };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch favorite wishlists';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update wishlist shipping information
   * @param {number} wishlistId - Wishlist ID
   * @param {Object} shippingData - Shipping data
   */
  async function updateWishlistShipping(wishlistId, shippingData) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await patch_request(`wishlists/${wishlistId}/shipping/`, shippingData);
      
      const updatedWishlist = response.data.wishlist;
      
      // Update in list
      const index = wishlists.value.findIndex(w => w.id === wishlistId);
      if (index !== -1) {
        wishlists.value[index] = updatedWishlist;
      }
      
      // Update current if it's the same
      if (currentWishlist.value?.id === wishlistId) {
        currentWishlist.value = updatedWishlist;
      }
      
      return { 
        success: true, 
        message: response.data.message,
        data: updatedWishlist 
      };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to update shipping info';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Get wishlist by ID from current wishlists
   * @param {number} wishlistId - Wishlist ID
   */
  function getWishlistById(wishlistId) {
    return wishlists.value.find(wishlist => wishlist.id === wishlistId) || null;
  }

  /**
   * Check if product is in any wishlist
   * @param {number} productId - Product ID
   */
  function isProductInWishlist(productId) {
    return wishlists.value.some(wishlist => 
      wishlist.items?.some(item => item.product.id === productId)
    );
  }

  /**
   * Get priority label
   * @param {string} priority - Priority value
   */
  function getPriorityLabel(priority) {
    const priorityObj = WISHLIST_PRIORITIES.find(p => p.value === priority);
    return priorityObj ? priorityObj.label : priority;
  }

  /**
   * Get priority color
   * @param {string} priority - Priority value
   */
  function getPriorityColor(priority) {
    const priorityObj = WISHLIST_PRIORITIES.find(p => p.value === priority);
    return priorityObj ? priorityObj.color : 'text-gray-500';
  }

  /**
   * Clear current wishlist
   */
  function clearCurrentWishlist() {
    currentWishlist.value = null;
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Get wishlist statistics
   */
  function getWishlistStatistics() {
    return {
      total: totalWishlists.value,
      active: activeWishlists.value.length,
      public: publicUserWishlists.value.length,
      private: privateWishlists.value.length,
      total_value: totalWishlistValue.value,
      total_items: totalWishlistItems.value,
      favorites: favoriteWishlists.value.length
    };
  }

  return {
    // State
    wishlists,
    currentWishlist,
    publicWishlists,
    favoriteWishlists,
    isLoading,
    isLoadingWishlist,
    isUpdating,
    error,
    
    // Getters
    totalWishlists,
    activeWishlists,
    publicUserWishlists,
    privateWishlists,
    hasWishlists,
    totalWishlistValue,
    totalWishlistItems,
    
    // Actions
    fetchWishlists,
    fetchWishlist,
    createWishlist,
    updateWishlist,
    deleteWishlist,
    addProductToWishlist,
    removeProductFromWishlist,
    updateWishlistItem,
    fetchPublicWishlist,
    searchPublicWishlists,
    favoriteWishlist,
    unfavoriteWishlist,
    fetchFavoriteWishlists,
    updateWishlistShipping,
    getWishlistById,
    isProductInWishlist,
    getPriorityLabel,
    getPriorityColor,
    clearCurrentWishlist,
    clearError,
    getWishlistStatistics
  };
});
