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
   * Add WooCommerce product to wishlist
   * @param {number} wishlistId - Wishlist ID
   * @param {number} woocommerceProductId - WooCommerce Product ID
   * @param {string} notes - Optional notes
   * @param {string} priority - Priority level
   */
  async function addWooCommerceProductToWishlist(wishlistId, woocommerceProductId, notes = '', priority = 'medium') {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request(`wishlists/${wishlistId}/add-woocommerce-product/`, {
        woocommerce_product_id: woocommerceProductId,
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
   * Remove WooCommerce product from wishlist
   * @param {number} wishlistId - Wishlist ID
   * @param {number} woocommerceProductId - WooCommerce Product ID
   */
  async function removeWooCommerceProductFromWishlist(wishlistId, woocommerceProductId) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await delete_request(`wishlists/${wishlistId}/remove-woocommerce-product/${woocommerceProductId}/`);
      
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
   * Refresh all products in wishlist from WooCommerce
   * @param {number} wishlistId - Wishlist ID
   */
  async function refreshWishlistProducts(wishlistId) {
    isUpdating.value = true;
    error.value = null;

    try {
      const response = await create_request(`wishlists/${wishlistId}/refresh-products/`, {});
      
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
        updated_count: response.data.updated_count,
        failed_count: response.data.failed_count,
        data: updatedWishlist 
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to refresh products';
      return { success: false, error: error.value };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Fetch public wishlist by UUID
   * @param {string} uuid - Wishlist UUID
   */
  async function fetchPublicWishlistByUUID(uuid) {
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
   * Fetch public wishlist by username and ID
   * @param {string} username - User's username
   * @param {number} wishlistId - Wishlist ID
   */
  async function fetchPublicWishlistByUsername(username, wishlistId) {
    isLoadingWishlist.value = true;
    error.value = null;

    try {
      const response = await get_request(`wishlists/@${username}/${wishlistId}/`);
      return { success: true, data: response.data.wishlist };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch public wishlist';
      return { success: false, error: error.value };
    } finally {
      isLoadingWishlist.value = false;
    }
  }

  /**
   * Fetch all public wishlists by username
   * @param {string} username - User's username
   */
  async function fetchWishlistsByUsername(username) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request(`wishlists/user/${username}/`);
      
      if (response.data.success) {
        return { 
          success: true, 
          data: response.data.wishlists || [],
          user: {
            username: response.data.username,
            fullName: response.data.user_full_name,
            totalWishlists: response.data.total_wishlists
          },
          message: response.data.message
        };
      } else {
        return { 
          success: false, 
          error: response.data.message || 'User has no public wishlists'
        };
      }
    } catch (err) {
      error.value = err.response?.data?.message || err.response?.data?.error || 'Failed to fetch user wishlists';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
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
   * Check if WooCommerce product is in any wishlist
   * @param {number} woocommerceProductId - WooCommerce Product ID
   */
  function isWooCommerceProductInWishlist(woocommerceProductId) {
    return wishlists.value.some(wishlist => 
      wishlist.items?.some(item => item.woocommerce_product_id === woocommerceProductId)
    );
  }

  /**
   * Get wishlists containing a specific WooCommerce product
   * @param {number} woocommerceProductId - WooCommerce Product ID
   */
  function getWishlistsWithProduct(woocommerceProductId) {
    return wishlists.value.filter(wishlist => 
      wishlist.items?.some(item => item.woocommerce_product_id === woocommerceProductId)
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
    addWooCommerceProductToWishlist,
    removeWooCommerceProductFromWishlist,
    refreshWishlistProducts,
    fetchPublicWishlistByUUID,
    fetchPublicWishlistByUsername,
    fetchWishlistsByUsername,
    searchPublicWishlists,
    favoriteWishlist,
    unfavoriteWishlist,
    fetchFavoriteWishlists,
    updateWishlistShipping,
    getWishlistById,
    isWooCommerceProductInWishlist,
    getWishlistsWithProduct,
    getPriorityLabel,
    getPriorityColor,
    clearCurrentWishlist,
    clearError,
    getWishlistStatistics
  };
});
