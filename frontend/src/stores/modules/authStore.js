/**
 * Authentication Store for CrushMe e-commerce application
 * Manages user authentication state and related actions
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  get_request, 
  create_request, 
  update_request,
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
  const username = computed(() => user.value?.username || '');

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
        clearTokens();
        localStorage.removeItem(STORAGE_KEYS.USER);
      }
    }
  }

  /**
   * Login user with username and password
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.username - Username
   * @param {string} credentials.password - User password
   */
  async function login(credentials) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/login/', credentials);
      
      if (response.data.access && response.data.user) {
        // Store tokens
        setTokens(response.data.access, response.data.refresh);
        
        // Store user data
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        
        return { success: true, data: response.data };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data?.non_field_errors?.[0] || err.response?.data?.error || 'Login failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Register new user
   * @param {Object} userData - Registration data
   * @param {string} userData.email - User email
   * @param {string} userData.username - Username
   * @param {string} userData.password - User password
   * @param {string} userData.password_confirm - Password confirmation
   */
  async function register(userData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/signup/', userData);
      
      // Signup returns message and requires_verification, not tokens
      return { 
        success: true, 
        data: response.data,
        requiresVerification: response.data.requires_verification 
      };
    } catch (err) {
      error.value = err.response?.data || 'Registration failed';
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
      // Silent error handling
    } finally {
      // Clear local state regardless of API call result
      user.value = null;
      clearTokens();
      localStorage.removeItem(STORAGE_KEYS.USER);
    }
  }

  /**
   * Verify email with verification code
   * @param {Object} verifyData - Verification data
   * @param {string} verifyData.email - User email
   * @param {string} verifyData.verification_code - 4-digit verification code
   */
  async function verifyEmail(verifyData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/verify-email/', verifyData);
      
      if (response.data.access && response.data.user) {
        // Store tokens after successful verification
        setTokens(response.data.access, response.data.refresh);
        
        // Store user data
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        
        return { success: true, data: response.data };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data?.verification_code?.[0] || err.response?.data?.non_field_errors?.[0] || 'Email verification failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Resend verification code
   * @param {string} email - User email
   */
  async function resendVerificationCode(email) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/resend-verification/', { email });
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to resend verification code';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
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
      
      // Profile endpoint returns user data directly
      user.value = response.data;
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data));
      return { success: true, data: response.data };
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
      const response = await update_request('auth/update_profile/', profileData);
      
      if (response.data.user) {
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        return { success: true, data: response.data.user, message: response.data.message };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data || 'Profile update failed';
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
      const response = await create_request('auth/update_password/', passwordData);
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data || 'Password change failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Send password reset code (forgot password)
   * @param {string} email - User email
   */
  async function forgotPassword(email) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/forgot-password/', { email });
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data?.error || 'Failed to send reset code';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Reset password with code (single endpoint)
   * @param {Object} resetData - Password reset data
   * @param {string} resetData.email - User email
   * @param {string} resetData.reset_code - 4-digit reset code
   * @param {string} resetData.new_password - New password
   * @param {string} resetData.new_password_confirm - New password confirmation
   */
  async function resetPassword(resetData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/reset-password/', resetData);
      return { success: true, message: response.data.message };
    } catch (err) {
      error.value = err.response?.data || 'Password reset failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Guest checkout
   * @param {Object} guestData - Guest checkout data
   */
  async function guestCheckout(guestData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/guest_checkout/', guestData);
      return { success: true, data: response.data };
    } catch (err) {
      error.value = err.response?.data || 'Guest checkout failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Check username availability
   * @param {string} username - Username to check
   */
  async function checkUsername(username) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/check_username/', { username });
      return { success: true, data: response.data };
    } catch (err) {
      error.value = err.response?.data || 'Username check failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Check guest profile
   * @param {string} email - Email to check for guest profile
   */
  async function checkGuest(email) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/check_guest/', { email });
      return { success: true, data: response.data };
    } catch (err) {
      error.value = err.response?.data || 'Guest check failed';
      return { success: false, error: error.value };
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Google OAuth login
   * @param {string} googleToken - Google OAuth token
   */
  async function googleLogin(googleToken) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await create_request('auth/google_login/', { google_token: googleToken });
      
      if (response.data.access && response.data.user) {
        // Store tokens
        setTokens(response.data.access, response.data.refresh);
        
        // Store user data
        user.value = response.data.user;
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.data.user));
        
        return { success: true, data: response.data };
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      error.value = err.response?.data || 'Google login failed';
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
    username,
    
    // Actions
    login,
    register,
    verifyEmail,
    resendVerificationCode,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    guestCheckout,
    checkUsername,
    checkGuest,
    googleLogin,
    clearError,
    initializeAuth
  };
});
