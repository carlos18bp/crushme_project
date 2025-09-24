/**
 * Authentication Store for CrushMe e-commerce application
 * Manages user authentication state and related actions
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  create_request, 
  setTokens, 
  clearTokens, 
  isAuthenticated 
} from '@/services/request_http.js';
import { STORAGE_KEYS } from '@/utils/constants.js';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const isLoggedIn = computed(() => !!user.value && isAuthenticated());
  const userFullName = computed(() => user.value?.full_name || '');
  const userEmail = computed(() => user.value?.email || '');
  const userId = computed(() => user.value?.id || null);

  // Actions
  
  /**
   * Initialize auth state from localStorage
   */
  function initializeAuth() {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
    if (storedUser && isAuthenticated()) {
      try {
        user.value = JSON.parse(storedUser);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        clearTokens();
        localStorage.removeItem(STORAGE_KEYS.USER);
      }
    }
  }

  /**
   * Login user with email and password
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.email - User email
   * @param {string} credentials.password - User password
   */
  async function login(credentials) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/signin/', credentials);
      
      if (response.data.tokens && response.data.user) {
        // Store tokens
        setTokens(response.data.tokens.access, response.data.tokens.refresh);
        
        // Store user data
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        
        return { success: true, data: response.data };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Register new user
   * @param {Object} userData - Registration data
   * @param {string} userData.email - User email
   * @param {string} userData.first_name - User first name
   * @param {string} userData.last_name - User last name
   * @param {string} userData.password - User password
   * @param {string} userData.password_confirm - Password confirmation
   */
  async function register(userData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/signup/', userData);
      
      if (response.data.tokens && response.data.user) {
        // Store tokens
        setTokens(response.data.tokens.access, response.data.tokens.refresh);
        
        // Store user data
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        
        return { success: true, data: response.data };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Registration failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Logout user
   */
  async function logout() {
    try {
      // Call logout endpoint (optional, since JWT is stateless)
      await create_request('auth/logout/', {});
    } catch (err) {
      console.warn('Logout request failed:', err);
    } finally {
      // Clear local state regardless of API call result
      user.value = null;
      clearTokens();
      localStorage.removeItem(STORAGE_KEYS.USER);
    }
  }

  /**
   * Get current user profile
   */
  async function fetchProfile() {
    if (!isAuthenticated()) return { success: false, error: 'Not authenticated' };

    isLoading.value = true;
    error.value = null;

    try {
      const response = await get_request('auth/profile/');
      
      if (response.data.user) {
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        return { success: true, data: response.data.user };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to fetch profile';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update user profile
   * @param {Object} profileData - Updated profile data
   */
  async function updateProfile(profileData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/profile/update/', profileData);
      
      if (response.data.user) {
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        return { success: true, data: response.data.user };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Profile update failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Change user password
   * @param {Object} passwordData - Password change data
   * @param {string} passwordData.current_password - Current password
   * @param {string} passwordData.new_password - New password
   * @param {string} passwordData.new_password_confirm - New password confirmation
   */
  async function changePassword(passwordData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/password/change/', passwordData);
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Password change failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Send password reset code
   * @param {string} email - User email
   */
  async function sendPasswordResetCode(email) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/password/reset/send/', { email });
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Failed to send reset code';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Reset password with code
   * @param {Object} resetData - Password reset data
   * @param {string} resetData.email - User email
   * @param {string} resetData.passcode - Reset code
   * @param {string} resetData.new_password - New password
   * @param {string} resetData.new_password_confirm - New password confirmation
   */
  async function resetPassword(resetData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/password/reset/verify/', resetData);
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data?.details || err.response?.data?.error || 'Password reset failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Clear error state
   */
  function clearError() {
    error.value = null;
  }

  // Initialize auth state on store creation
  initializeAuth();

  return {
    // State
    user,
    isLoading,
    error,
    
    // Getters
    isLoggedIn,
    userFullName,
    userEmail,
    userId,
    
    // Actions
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    sendPasswordResetCode,
    resetPassword,
    clearError,
    initializeAuth
  };
});
