/**
 * Profile Store for CrushMe e-commerce application
 * Manages detailed user profile information including addresses, gallery, and links
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  update_request,
  create_request,
  delete_request,
  isAuthenticated 
} from '@/services/request_http.js';

export const useProfileStore = defineStore('profile', () => {
  // State
  const profile = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const hasProfile = computed(() => !!profile.value);
  
  // User basic info
  const userInfo = computed(() => {
    if (!profile.value) return null;
    return {
      id: profile.value.id,
      email: profile.value.email,
      username: profile.value.username,
      first_name: profile.value.first_name,
      last_name: profile.value.last_name,
      full_name: profile.value.full_name,
      phone: profile.value.phone,
      about: profile.value.about,
      current_status: profile.value.current_status,
      note: profile.value.note,
      date_joined: profile.value.date_joined,
      is_active: profile.value.is_active,
      is_guest_converted: profile.value.is_guest_converted,
      profile_picture: profile.value.profile_picture
    };
  });

  // Addresses
  const addresses = computed(() => profile.value?.addresses || []);
  const defaultAddress = computed(() => 
    addresses.value.find(addr => addr.is_default) || addresses.value[0] || null
  );
  const hasAddresses = computed(() => addresses.value.length > 0);

  // Gallery photos
  const galleryPhotos = computed(() => profile.value?.gallery_photos || []);
  const profilePicture = computed(() => 
    galleryPhotos.value.find(photo => photo.is_profile_picture) || null
  );
  const profilePictureUrl = computed(() => profile.value?.profile_picture_url || null);
  const coverImageUrl = computed(() => profile.value?.cover_image_url || null);
  const hasGalleryPhotos = computed(() => galleryPhotos.value.length > 0);

  // Crush verification
  const isCrush = computed(() => profile.value?.is_crush || false);
  const crushVerificationStatus = computed(() => profile.value?.crush_verification_status || 'none');
  const crushRequestedAt = computed(() => profile.value?.crush_requested_at || null);
  const crushVerifiedAt = computed(() => profile.value?.crush_verified_at || null);
  const crushRejectionReason = computed(() => profile.value?.crush_rejection_reason || null);
  const isCrushVerified = computed(() => isCrush.value && crushVerificationStatus.value === 'approved');
  const canRequestCrushVerification = computed(() => 
    crushVerificationStatus.value === 'none' || crushVerificationStatus.value === 'rejected'
  );
  const hasPendingCrushRequest = computed(() => crushVerificationStatus.value === 'pending');

  // Links
  const links = computed(() => profile.value?.links || []);
  const sortedLinks = computed(() => 
    [...links.value].sort((a, b) => a.order - b.order)
  );
  const hasLinks = computed(() => links.value.length > 0);

  // Guest profile
  const guestProfile = computed(() => profile.value?.guest_profile || null);
  const isGuestConverted = computed(() => profile.value?.is_guest_converted || false);

  // Actions
  
  /**
   * Fetch complete user profile with all related data
   * @returns {Promise<Object>} Result object with success status
   */
  async function fetchProfile() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('auth/profile/');
      
      // Store complete profile data
      profile.value = response.data;
      
      return { success: true, data: response.data };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al obtener el perfil';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update user profile information (basic fields only)
   * @param {Object} profileData - Updated profile data
   * @param {string} [profileData.email] - User email
   * @param {string} [profileData.username] - Username
   * @param {string} [profileData.first_name] - First name
   * @param {string} [profileData.last_name] - Last name
   * @param {string} [profileData.phone] - Phone number
   * @param {string} [profileData.about] - User bio/description
   * @param {string} [profileData.current_status] - Current status
   * @param {string} [profileData.note] - Personal notes
   * @returns {Promise<Object>} Result object with success status
   */
  async function updateProfile(profileData) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await update_request('auth/update_profile/', profileData);
      
      // Update profile with response data (endpoint now returns full profile)
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Perfil actualizado correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar el perfil';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update complete profile with nested data (addresses, links, gallery)
   * @param {Object} profileData - Complete profile data
   * @param {Object} [profileData.basicInfo] - Basic user info
   * @param {Array} [profileData.addresses] - User addresses
   * @param {Array} [profileData.links] - User links
   * @param {Array} [profileData.gallery_photos] - Gallery photos metadata
   * @returns {Promise<Object>} Result object with success status
   */
  async function updateProfileComplete(profileData) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      // Prepare data structure for the endpoint
      const updateData = {
        ...profileData.basicInfo,
        addresses: profileData.addresses || undefined,
        links: profileData.links || undefined,
        gallery_photos: profileData.gallery_photos || undefined
      };

      const response = await update_request('auth/update_profile/', updateData);
      
      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Perfil actualizado correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al actualizar el perfil completo';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Upload gallery images using multipart/form-data
   * @param {Object} uploadData - Upload data
   * @param {File[]} uploadData.images - Array of image files
   * @param {Object} [uploadData.basicInfo] - Optional basic profile data to update
   * @param {Array<Object>} [uploadData.imageMeta] - Metadata for each image (caption, is_profile_picture)
   * @returns {Promise<Object>} Result object with success status
   */
  async function uploadGalleryImages(uploadData) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const formData = new FormData();

      // Add basic info if provided
      if (uploadData.basicInfo) {
        Object.keys(uploadData.basicInfo).forEach(key => {
          if (uploadData.basicInfo[key] !== null && uploadData.basicInfo[key] !== undefined) {
            formData.append(key, uploadData.basicInfo[key]);
          }
        });
      }

      // Add images with their metadata
      uploadData.images.forEach((file, index) => {
        const n = index + 1;
        formData.append(`gallery_image_${n}`, file);
        
        // Add metadata if provided
        if (uploadData.imageMeta && uploadData.imageMeta[index]) {
          const meta = uploadData.imageMeta[index];
          if (meta.caption) {
            formData.append(`gallery_caption_${n}`, meta.caption);
          }
          if (meta.is_profile_picture !== undefined) {
            formData.append(`gallery_is_profile_${n}`, meta.is_profile_picture ? 'true' : 'false');
          }
        }
      });

      // NO establecer Content-Type - el navegador lo maneja con boundary
      const response = await update_request('auth/update_profile/', formData);

      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Imágenes subidas correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al subir imágenes';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Upload profile picture
   * @param {File} file - Profile picture file
   * @returns {Promise<Object>} Result object with success status
   */
  async function uploadProfilePicture(file) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    // Validate file is a File instance
    if (!(file instanceof File)) {
      error.value = 'El archivo no es válido';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('profile_picture', file); // File directo, NO array

      // NO establecer Content-Type - el navegador lo maneja con boundary
      const response = await update_request('auth/update_profile/', formData);

      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Foto de perfil actualizada correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al subir la foto de perfil';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Upload cover image
   * @param {File} file - Cover image file
   * @returns {Promise<Object>} Result object with success status
   */
  async function uploadCoverImage(file) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    // Validate file is a File instance
    if (!(file instanceof File)) {
      error.value = 'El archivo no es válido';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('cover_image', file); // File directo, NO array

      // NO establecer Content-Type - el navegador lo maneja con boundary
      const response = await update_request('auth/update_profile/', formData);

      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Foto de portada actualizada correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al subir la foto de portada';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Upload both profile picture and cover image
   * @param {Object} images - Images object
   * @param {File} [images.profilePicture] - Profile picture file
   * @param {File} [images.coverImage] - Cover image file
   * @returns {Promise<Object>} Result object with success status
   */
  async function uploadProfileImages(images) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    if (!images.profilePicture && !images.coverImage) {
      error.value = 'No se proporcionó ninguna imagen';
      return { success: false, error: error.value };
    }

    // Validate files are File instances
    if (images.profilePicture && !(images.profilePicture instanceof File)) {
      error.value = 'El archivo de foto de perfil no es válido';
      return { success: false, error: error.value };
    }

    if (images.coverImage && !(images.coverImage instanceof File)) {
      error.value = 'El archivo de portada no es válido';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      
      // Añadir solo si existen - Files directos, NO arrays
      if (images.profilePicture) {
        formData.append('profile_picture', images.profilePicture);
      }
      
      if (images.coverImage) {
        formData.append('cover_image', images.coverImage);
      }

      // NO establecer Content-Type - el navegador lo maneja con boundary
      const response = await update_request('auth/update_profile/', formData);

      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Imágenes actualizadas correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al subir las imágenes';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Remove profile picture
   * @returns {Promise<Object>} Result object with success status
   */
  async function removeProfilePicture() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await update_request('auth/profile/update/', {
        profile_picture: null
      });

      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Foto de perfil eliminada correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar la foto de perfil';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Remove cover image
   * @returns {Promise<Object>} Result object with success status
   */
  async function removeCoverImage() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await update_request('auth/profile/update/', {
        cover_image: null
      });

      // Update profile with response data
      profile.value = response.data;
      
      return { 
        success: true, 
        data: response.data,
        message: 'Foto de portada eliminada correctamente'
      };
    } catch (err) {
      error.value = err.response?.data || 'Error al eliminar la foto de portada';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Validate image file before upload
   * @param {File} file - Image file
   * @param {number} maxSize - Maximum file size in bytes (default 5MB)
   * @returns {Object} Validation result
   */
  function validateImageFile(file, maxSize = 5 * 1024 * 1024) {
    const errors = [];
    
    if (!file) {
      errors.push('No se ha seleccionado ningún archivo');
      return { valid: false, errors };
    }
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      errors.push('Formato de imagen no válido. Usa JPG, PNG, GIF o WEBP');
    }
    
    // Validate file size
    if (file.size > maxSize) {
      errors.push(`El archivo excede el tamaño máximo de ${maxSize / 1024 / 1024}MB`);
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Get image URL with cache busting
   * @param {string} url - Image URL
   * @returns {string|null} URL with timestamp parameter
   */
  function getImageUrlWithCacheBusting(url) {
    if (!url) return null;
    const separator = url.includes('?') ? '&' : '?';
    return `${url}${separator}t=${Date.now()}`;
  }

  // ============================================
  // CRUSH VERIFICATION SECTION
  // ============================================

  /**
   * Request Crush verification
   * @returns {Promise<Object>} Result object with success status
   */
  async function requestCrushVerification() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/crush/request-verification/', {});
      
      // Update profile with new verification status
      if (profile.value) {
        profile.value.crush_verification_status = response.data.crush_verification_status;
        profile.value.crush_requested_at = response.data.crush_requested_at;
      }
      
      return { 
        success: true, 
        data: response.data,
        message: response.data.message || 'Solicitud de verificación enviada correctamente'
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al solicitar verificación de Crush';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Cancel Crush verification request
   * @returns {Promise<Object>} Result object with success status
   */
  async function cancelCrushRequest() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/crush/cancel-request/', {});
      
      // Update profile with new verification status
      if (profile.value) {
        profile.value.crush_verification_status = response.data.crush_verification_status;
        profile.value.crush_requested_at = null;
      }
      
      return { 
        success: true, 
        data: response.data,
        message: response.data.message || 'Solicitud de verificación cancelada correctamente'
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al cancelar solicitud de verificación';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get address by ID
   * @param {number} addressId - Address ID
   * @returns {Object|null} Address object or null
   */
  function getAddressById(addressId) {
    return addresses.value.find(addr => addr.id === addressId) || null;
  }

  /**
   * Get gallery photo by ID
   * @param {number} photoId - Photo ID
   * @returns {Object|null} Photo object or null
   */
  function getPhotoById(photoId) {
    return galleryPhotos.value.find(photo => photo.id === photoId) || null;
  }

  /**
   * Get link by ID
   * @param {number} linkId - Link ID
   * @returns {Object|null} Link object or null
   */
  function getLinkById(linkId) {
    return links.value.find(link => link.id === linkId) || null;
  }

  /**
   * Get links by platform
   * @param {string} platform - Platform name (instagram, twitter, etc.)
   * @returns {Array} Array of links for the platform
   */
  function getLinksByPlatform(platform) {
    return links.value.filter(link => link.platform === platform);
  }

  /**
   * Clear profile data
   */
  function clearProfile() {
    profile.value = null;
    error.value = null;
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
  }

  // ============================================
  // FAVORITE PRODUCTS SECTION
  // ============================================

  // State for favorites
  const favoriteProducts = ref([]);
  const favoriteProductIds = ref([]);
  const isLoadingFavorites = ref(false);

  /**
   * Fetch user's favorite products
   * @param {boolean} refresh - Force refresh from WooCommerce
   * @returns {Promise<Object>} Result object with success status
   */
  async function fetchFavoriteProducts(refresh = false) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoadingFavorites.value = true;
    error.value = null;

    try {
      const url = refresh ? 'favorites/products/?refresh=true' : 'favorites/products/';
      const response = await get_request(url);
      
      favoriteProducts.value = response.data.data || [];
      
      return { 
        success: true, 
        data: favoriteProducts.value,
        meta: response.data.meta
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al obtener productos favoritos';
      return { success: false, error: error.value };
    } finally {
      isLoadingFavorites.value = false;
    }
  }

  /**
   * Fetch only favorite product IDs (lightweight)
   * @returns {Promise<Object>} Result object with success status
   */
  async function fetchFavoriteProductIds() {
    if (!isAuthenticated()) {
      return { success: false, error: 'Usuario no autenticado' };
    }

    try {
      const response = await get_request('favorites/products/ids/');
      favoriteProductIds.value = response.data.product_ids || [];
      
      return { 
        success: true, 
        data: favoriteProductIds.value,
        count: response.data.count
      };
    } catch (err) {
      return { success: false, error: err.response?.data?.error };
    }
  }

  /**
   * Add product to favorites
   * @param {number} woocommerceProductId - WooCommerce product ID
   * @returns {Promise<Object>} Result object with success status
   */
  async function addProductToFavorites(woocommerceProductId) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('favorites/products/add/', {
        woocommerce_product_id: woocommerceProductId
      });
      
      // Add to local state
      if (response.data.data) {
        const favoriteData = {
          id: response.data.data.id,
          woocommerce_product_id: response.data.data.woocommerce_product_id,
          product_name: response.data.data.product_data?.name,
          product_price: response.data.data.product_data?.price,
          product_image: response.data.data.product_data?.images?.[0]?.src,
          product_slug: response.data.data.product_data?.slug,
          is_in_stock: response.data.data.product_data?.stock_status === 'instock',
          created_at: response.data.data.created_at
        };
        favoriteProducts.value.unshift(favoriteData);
        favoriteProductIds.value.push(woocommerceProductId);
      }
      
      return { 
        success: true, 
        message: response.data.message,
        data: response.data.data
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al agregar producto a favoritos';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Remove product from favorites
   * @param {number} woocommerceProductId - WooCommerce product ID
   * @returns {Promise<Object>} Result object with success status
   */
  async function removeProductFromFavorites(woocommerceProductId) {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await delete_request(`favorites/products/${woocommerceProductId}/`);
      
      // Remove from local state
      favoriteProducts.value = favoriteProducts.value.filter(
        fav => fav.woocommerce_product_id !== woocommerceProductId
      );
      favoriteProductIds.value = favoriteProductIds.value.filter(
        id => id !== woocommerceProductId
      );
      
      return { 
        success: true, 
        message: response.data.message
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al eliminar producto de favoritos';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Check if a product is in favorites
   * @param {number} woocommerceProductId - WooCommerce product ID
   * @returns {Promise<Object>} Result object with success status
   */
  async function checkProductFavoriteStatus(woocommerceProductId) {
    if (!isAuthenticated()) {
      return { success: false, is_favorited: false };
    }

    try {
      const response = await get_request(`favorites/products/${woocommerceProductId}/status/`);
      return { 
        success: true, 
        is_favorited: response.data.is_favorited
      };
    } catch (err) {
      return { success: false, is_favorited: false };
    }
  }

  /**
   * Check if a product is in favorites (local check)
   * @param {number} woocommerceProductId - WooCommerce product ID
   * @returns {boolean} True if product is in favorites
   */
  function isProductInFavorites(woocommerceProductId) {
    return favoriteProductIds.value.includes(woocommerceProductId);
  }

  /**
   * Refresh all favorite products from WooCommerce
   * @returns {Promise<Object>} Result object with success status
   */
  async function refreshAllFavoriteProducts() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('favorites/products/refresh/', {});
      
      return { 
        success: true, 
        message: response.data.message,
        stats: response.data.stats,
        errors: response.data.errors
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al actualizar productos favoritos';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Clear all favorite products
   * @returns {Promise<Object>} Result object with success status
   */
  async function clearAllFavorites() {
    if (!isAuthenticated()) {
      error.value = 'Usuario no autenticado';
      return { success: false, error: error.value };
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await delete_request('favorites/products/clear/');
      
      // Clear local state
      favoriteProducts.value = [];
      favoriteProductIds.value = [];
      
      return { 
        success: true, 
        message: response.data.message
      };
    } catch (err) {
      error.value = err.response?.data?.error || 'Error al limpiar favoritos';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  // Computed for favorites
  const hasFavorites = computed(() => favoriteProducts.value.length > 0);
  const totalFavorites = computed(() => favoriteProducts.value.length);

  return {
    // State
    profile,
    isLoading,
    error,
    
    // Favorites state
    favoriteProducts,
    favoriteProductIds,
    isLoadingFavorites,
    
    // Getters
    hasProfile,
    userInfo,
    addresses,
    defaultAddress,
    hasAddresses,
    galleryPhotos,
    profilePicture,
    profilePictureUrl,
    coverImageUrl,
    hasGalleryPhotos,
    links,
    sortedLinks,
    hasLinks,
    guestProfile,
    isGuestConverted,
    
    // Crush verification getters
    isCrush,
    crushVerificationStatus,
    crushRequestedAt,
    crushVerifiedAt,
    crushRejectionReason,
    isCrushVerified,
    canRequestCrushVerification,
    hasPendingCrushRequest,
    
    // Favorites getters
    hasFavorites,
    totalFavorites,
    
    // Actions
    fetchProfile,
    updateProfile,
    updateProfileComplete,
    uploadGalleryImages,
    uploadProfilePicture,
    uploadCoverImage,
    uploadProfileImages,
    removeProfilePicture,
    removeCoverImage,
    validateImageFile,
    getImageUrlWithCacheBusting,
    requestCrushVerification,
    cancelCrushRequest,
    getAddressById,
    getPhotoById,
    getLinkById,
    getLinksByPlatform,
    clearProfile,
    clearError,
    
    // Favorites actions
    fetchFavoriteProducts,
    fetchFavoriteProductIds,
    addProductToFavorites,
    removeProductFromFavorites,
    checkProductFavoriteStatus,
    isProductInFavorites,
    refreshAllFavoriteProducts,
    clearAllFavorites
  };
});

