/**
 * Crush Store for CrushMe e-commerce application
 * Manages public Crush profiles and exploration features
 * All endpoints are public (no authentication required)
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { get_request } from '@/services/request_http.js';

export const useCrushStore = defineStore('crush', () => {
  // State
  const crushProfile = ref(null);
  const randomCrush = ref(null);
  const randomSevenCrushes = ref([]);
  const crushList = ref([]);
  const searchResults = ref([]);
  const pagination = ref({
    total: 0,
    offset: 0,
    limit: 50,
    count: 0
  });
  const isLoading = ref(false);
  const isSearching = ref(false);
  const error = ref(null);

  // Getters
  const hasCrushProfile = computed(() => !!crushProfile.value);
  const hasRandomCrush = computed(() => !!randomCrush.value);
  const hasRandomSevenCrushes = computed(() => randomSevenCrushes.value.length > 0);
  const hasCrushList = computed(() => crushList.value.length > 0);
  const hasSearchResults = computed(() => searchResults.value.length > 0);
  
  const currentPage = computed(() => Math.floor(pagination.value.offset / pagination.value.limit) + 1);
  const totalPages = computed(() => Math.ceil(pagination.value.total / pagination.value.limit));
  const hasNextPage = computed(() => (pagination.value.offset + pagination.value.count) < pagination.value.total);
  const hasPrevPage = computed(() => pagination.value.offset > 0);

  // Actions

  /**
   * Get public profile by username
   * Endpoint: GET /api/auth/public/@{username}/
   * @param {string} username - Username to fetch
   * @returns {Promise<Object>} - User profile data
   */
  async function fetchPublicProfile(username) {
    isLoading.value = true;
    error.value = null;
    crushProfile.value = null;

    try {
      console.log(`🎯 Fetching public profile for: @${username}`);
      const response = await get_request(`auth/public/@${username}/`);
      
      if (response.data.success) {
        crushProfile.value = response.data.data;
        console.log(`✅ Profile loaded:`, crushProfile.value);
        return crushProfile.value;
      } else {
        throw new Error(response.data.error || 'Failed to fetch profile');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching profile';
      error.value = errorMessage;
      console.error('❌ Error fetching public profile:', errorMessage);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get one random Crush with full profile
   * Endpoint: GET /api/auth/crush/random/
   * @returns {Promise<Object>} - Random Crush profile
   */
  async function fetchRandomCrush() {
    isLoading.value = true;
    error.value = null;
    randomCrush.value = null;

    try {
      console.log('🎲 Fetching random Crush...');
      const response = await get_request('auth/crush/random/');
      
      if (response.data.success) {
        randomCrush.value = response.data.data;
        console.log(`✅ Random Crush loaded:`, randomCrush.value);
        return randomCrush.value;
      } else {
        throw new Error(response.data.error || 'Failed to fetch random Crush');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching random Crush';
      error.value = errorMessage;
      console.error('❌ Error fetching random Crush:', errorMessage);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get 7 random Crushes for carousel/grid
   * Endpoint: GET /api/auth/crush/random-7/
   * @returns {Promise<Array>} - Array of 7 random Crushes
   */
  async function fetchRandomSevenCrushes() {
    isLoading.value = true;
    error.value = null;
    randomSevenCrushes.value = [];

    try {
      console.log('🎠 Fetching 7 random Crushes for carousel...');
      const response = await get_request('auth/crush/random-7/');
      
      if (response.data.success) {
        randomSevenCrushes.value = response.data.results;
        console.log(`✅ ${response.data.count} Crushes loaded for carousel`);
        return randomSevenCrushes.value;
      } else {
        throw new Error(response.data.error || 'Failed to fetch random Crushes');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching random Crushes';
      error.value = errorMessage;
      console.error('❌ Error fetching random 7 Crushes:', errorMessage);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get paginated list of all Crushes
   * Endpoint: GET /api/auth/crush/list/?limit={limit}&offset={offset}
   * @param {Object} params - Pagination parameters
   * @param {number} params.limit - Number of results per page (default: 50, max: 100)
   * @param {number} params.offset - Number of results to skip (default: 0)
   * @returns {Promise<Array>} - Array of Crushes
   */
  async function fetchCrushList({ limit = 50, offset = 0 } = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      console.log(`📋 Fetching Crush list (limit: ${limit}, offset: ${offset})...`);
      
      // Build URL with query parameters
      const params = new URLSearchParams();
      params.append('limit', limit);
      params.append('offset', offset);
      const url = `auth/crush/list/?${params.toString()}`;
      
      const response = await get_request(url);
      
      if (response.data.success) {
        crushList.value = response.data.results;
        pagination.value = {
          total: response.data.total,
          offset: response.data.offset,
          limit: response.data.limit,
          count: response.data.count
        };
        console.log(`✅ ${response.data.count} Crushes loaded (${response.data.total} total)`);
        return crushList.value;
      } else {
        throw new Error(response.data.error || 'Failed to fetch Crush list');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Error fetching Crush list';
      error.value = errorMessage;
      console.error('❌ Error fetching Crush list:', errorMessage);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Search users by username
   * Endpoint: GET /api/auth/search/?q={query}&limit={limit}
   * @param {Object} params - Search parameters
   * @param {string} params.query - Search query (username)
   * @param {number} params.limit - Maximum number of results (default: 20, max: 50)
   * @returns {Promise<Array>} - Array of matching users
   */
  async function searchUsers(query, limit = 20) {
    if (!query || !query.trim()) {
      searchResults.value = [];
      return [];
    }

    isSearching.value = true;
    error.value = null;

    try {
      console.log(`🔍 Searching users: "${query}" (limit: ${limit})...`);
      
      // Build URL with query parameters
      const params = new URLSearchParams();
      params.append('q', query.trim());
      params.append('limit', limit);
      const url = `auth/search/?${params.toString()}`;
      
      const response = await get_request(url);
      
      if (response.data.success) {
        searchResults.value = response.data.results;
        console.log(`✅ ${response.data.count} users found`);
        return searchResults.value;
      } else {
        throw new Error(response.data.error || 'Search failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Error searching users';
      error.value = errorMessage;
      console.error('❌ Error searching users:', errorMessage);
      searchResults.value = [];
      throw err;
    } finally {
      isSearching.value = false;
    }
  }

  /**
   * Navigate to next page in Crush list
   * @returns {Promise<Array>} - Next page of Crushes
   */
  async function nextPage() {
    if (!hasNextPage.value) {
      console.warn('⚠️ No next page available');
      return crushList.value;
    }
    
    const nextOffset = pagination.value.offset + pagination.value.limit;
    return await fetchCrushList({ 
      limit: pagination.value.limit, 
      offset: nextOffset 
    });
  }

  /**
   * Navigate to previous page in Crush list
   * @returns {Promise<Array>} - Previous page of Crushes
   */
  async function prevPage() {
    if (!hasPrevPage.value) {
      console.warn('⚠️ No previous page available');
      return crushList.value;
    }
    
    const prevOffset = Math.max(0, pagination.value.offset - pagination.value.limit);
    return await fetchCrushList({ 
      limit: pagination.value.limit, 
      offset: prevOffset 
    });
  }

  /**
   * Navigate to specific page in Crush list
   * @param {number} page - Page number (1-indexed)
   * @returns {Promise<Array>} - Crushes for the specified page
   */
  async function goToPage(page) {
    const pageNumber = Math.max(1, Math.min(page, totalPages.value));
    const newOffset = (pageNumber - 1) * pagination.value.limit;
    return await fetchCrushList({ 
      limit: pagination.value.limit, 
      offset: newOffset 
    });
  }

  /**
   * Clear search results
   */
  function clearSearch() {
    searchResults.value = [];
    error.value = null;
    console.log('🧹 Search results cleared');
  }

  /**
   * Clear all Crush data
   */
  function clearAll() {
    crushProfile.value = null;
    randomCrush.value = null;
    randomSevenCrushes.value = [];
    crushList.value = [];
    searchResults.value = [];
    pagination.value = {
      total: 0,
      offset: 0,
      limit: 50,
      count: 0
    };
    error.value = null;
    console.log('🧹 All Crush data cleared');
  }

  /**
   * Get default avatar URL for fallback
   * @returns {string} - Default avatar URL
   */
  function getDefaultAvatar() {
    return '/default-avatar.png';
  }

  /**
   * Get profile picture URL with fallback
   * @param {Object} user - User object
   * @returns {string} - Profile picture URL or default
   */
  function getProfilePicture(user) {
    return user?.profile_picture_url || getDefaultAvatar();
  }

  return {
    // State
    crushProfile,
    randomCrush,
    randomSevenCrushes,
    crushList,
    searchResults,
    pagination,
    isLoading,
    isSearching,
    error,

    // Getters
    hasCrushProfile,
    hasRandomCrush,
    hasRandomSevenCrushes,
    hasCrushList,
    hasSearchResults,
    currentPage,
    totalPages,
    hasNextPage,
    hasPrevPage,

    // Actions
    fetchPublicProfile,
    fetchRandomCrush,
    fetchRandomSevenCrushes,
    fetchCrushList,
    searchUsers,
    nextPage,
    prevPage,
    goToPage,
    clearSearch,
    clearAll,
    getDefaultAvatar,
    getProfilePicture
  };
});



