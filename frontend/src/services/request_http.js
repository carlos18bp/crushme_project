/**
 * HTTP Request Service for CrushMe e-commerce application
 * Based on the gym_project implementation with JWT authentication
 * Handles all API communication with the Django backend
 */
import axios from "axios";

/**
 * Get cookie value by name (for CSRF token)
 * @param {string} name - Cookie name
 * @returns {string|null} - Cookie value or null
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Get JWT token from localStorage
 * @returns {string|null} - JWT token or null
 */
function getJWTToken() {
  return localStorage.getItem("access_token");
}

/**
 * Get refresh token from localStorage
 * @returns {string|null} - Refresh token or null
 */
function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

/**
 * Set JWT tokens in localStorage
 * @param {string} accessToken - Access token
 * @param {string} refreshToken - Refresh token
 */
export function setTokens(accessToken, refreshToken) {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

/**
 * Remove JWT tokens from localStorage
 */
export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
}

/**
 * Check if user is authenticated
 * @returns {boolean} - True if authenticated
 */
export function isAuthenticated() {
  return !!getJWTToken();
}

/**
 * Main request function with automatic token refresh
 * @param {string} method - HTTP method
 * @param {string} url - Endpoint URL
 * @param {object} params - Request parameters
 * @param {object} config - Additional Axios config
 * @returns {object} - Response from endpoint
 */
async function makeRequest(method, url, params = {}, config = {}) {
  const startTime = performance.now();
  const fullUrl = `/api/${url}`;
  console.log(`🌐 → HTTP ${method} ${fullUrl}`);
  
  const csrfToken = getCookie("csrftoken");
  const token = getJWTToken();
  
  // Si params es FormData, NO establecer Content-Type (el navegador lo hace con boundary)
  const isFormData = params instanceof FormData;
  
  const headers = {
    ...(!isFormData && { "Content-Type": "application/json" }), // Solo para JSON
    "X-CSRFToken": csrfToken,
    ...(token && { "Authorization": `Bearer ${token}` }),
    ...config.headers
  };

  const requestConfig = {
    ...config,
    headers
  };

  try {
    let response;

    switch (method) {
      case "GET":
        response = await axios.get(fullUrl, requestConfig);
        break;
      case "POST":
        response = await axios.post(fullUrl, params, requestConfig);
        break;
      case "PUT":
        response = await axios.put(fullUrl, params, requestConfig);
        break;
      case "PATCH":
        response = await axios.patch(fullUrl, params, requestConfig);
        break;
      case "DELETE":
        response = await axios.delete(fullUrl, requestConfig);
        break;
      default:
        throw new Error(`Unsupported method: ${method}`);
    }

    const responseTime = performance.now() - startTime;
    const responseSize = JSON.stringify(response.data).length;
    console.log(`🌐 ← HTTP ${method} ${fullUrl} (${responseTime.toFixed(0)}ms, ${responseSize} bytes, status: ${response.status})`);

    return response;
    
  } catch (error) {
    const errorTime = performance.now() - startTime;
    console.error(`🌐 ✗ HTTP ${method} ${fullUrl} ERROR (${errorTime.toFixed(0)}ms):`, error.message);
    
    // Handle 401 errors (token expired) with automatic refresh
    if (error.response?.status === 401 && token) {
      try {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          const refreshResponse = await axios.post('/api/auth/token/refresh/', {
            refresh: refreshToken
          });
          
          const newAccessToken = refreshResponse.data.access;
          localStorage.setItem("access_token", newAccessToken);
          
          // Retry original request with new token
          const newHeaders = {
            ...headers,
            "Authorization": `Bearer ${newAccessToken}`
          };
          
          const retryConfig = { ...requestConfig, headers: newHeaders };
          
          switch (method) {
            case "GET":
              return await axios.get(`/api/${url}`, retryConfig);
            case "POST":
              return await axios.post(`/api/${url}`, params, retryConfig);
            case "PUT":
              return await axios.put(`/api/${url}`, params, retryConfig);
            case "PATCH":
              return await axios.patch(`/api/${url}`, params, retryConfig);
            case "DELETE":
              return await axios.delete(`/api/${url}`, retryConfig);
          }
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        clearTokens();
        console.error("Token refresh failed:", refreshError);
        // You can add router redirect here if needed
        // router.push('/login');
      }
    }

    console.error("Error during request:", error);
    if (error.response) {
      console.error("Response data:", error.response.data);
      console.error("Status code:", error.response.status);
    } else {
      console.error("Request failed without response.");
    }
    throw error;
  }
}

/**
 * GET request with optional responseType
 * @param {string} url - Endpoint URL
 * @param {string} responseType - Axios response type (default: json)
 * @returns {object} - Response from endpoint
 */
export async function get_request(url, responseType = "json") {
  return await makeRequest("GET", url, {}, { responseType });
}

/**
 * POST request (create)
 * @param {string} url - Endpoint URL
 * @param {object} params - Request parameters
 * @returns {object} - Response from endpoint
 */
export async function create_request(url, params) {
  return await makeRequest("POST", url, params);
}

/**
 * PUT request (full update)
 * @param {string} url - Endpoint URL
 * @param {object} params - Request parameters
 * @returns {object} - Response from endpoint
 */
export async function update_request(url, params) {
  return await makeRequest("PUT", url, params);
}

/**
 * PATCH request (partial update)
 * @param {string} url - Endpoint URL
 * @param {object} params - Request parameters
 * @returns {object} - Response from endpoint
 */
export async function patch_request(url, params) {
  return await makeRequest("PATCH", url, params);
}

/**
 * DELETE request
 * @param {string} url - Endpoint URL
 * @returns {object} - Response from endpoint
 */
export async function delete_request(url) {
  return await makeRequest("DELETE", url);
}

/**
 * Upload file request
 * @param {string} url - Endpoint URL
 * @param {FormData} formData - Form data with file
 * @returns {object} - Response from endpoint
 */
export async function upload_request(url, formData) {
  return await makeRequest("POST", url, formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
}

// Configure axios defaults
// NOTE: No configurar baseURL para que use el proxy de Vite (vite.config.js)
// El proxy redirige /api/* a http://localhost:8000/api/*
// axios.defaults.baseURL = 'http://localhost:8000';
axios.defaults.timeout = 10000;

// Add response interceptor for global error handling
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.warn("Authentication failed - redirecting to login");
    } else if (error.response?.status >= 500) {
      // Server error
      console.error("Server error:", error.response.status);
    }
    return Promise.reject(error);
  }
);
