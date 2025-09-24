/**
 * Constants for CrushMe e-commerce application
 * Centralized configuration values
 */

// API Configuration
export const API_BASE_URL = 'http://localhost:8000/api';

// Local Storage Keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
  CART: 'cart',
  THEME: 'theme'
};

// Product Categories
export const PRODUCT_CATEGORIES = [
  { value: 'electronics', label: 'Electronics' },
  { value: 'clothing', label: 'Clothing' },
  { value: 'books', label: 'Books' },
  { value: 'home_garden', label: 'Home & Garden' },
  { value: 'sports', label: 'Sports & Outdoors' },
  { value: 'toys', label: 'Toys & Games' },
  { value: 'beauty', label: 'Beauty & Personal Care' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'food', label: 'Food & Beverages' },
  { value: 'health', label: 'Health & Wellness' },
  { value: 'jewelry', label: 'Jewelry & Accessories' },
  { value: 'music', label: 'Music & Instruments' },
  { value: 'art', label: 'Art & Crafts' },
  { value: 'office', label: 'Office Supplies' },
  { value: 'pet', label: 'Pet Supplies' },
  { value: 'other', label: 'Other' }
];

// Order Status
export const ORDER_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing', 
  SHIPPED: 'shipped',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled',
  REFUNDED: 'refunded'
};

// Order Status Labels
export const ORDER_STATUS_LABELS = {
  [ORDER_STATUS.PENDING]: 'Pending',
  [ORDER_STATUS.PROCESSING]: 'Processing',
  [ORDER_STATUS.SHIPPED]: 'Shipped', 
  [ORDER_STATUS.DELIVERED]: 'Delivered',
  [ORDER_STATUS.CANCELLED]: 'Cancelled',
  [ORDER_STATUS.REFUNDED]: 'Refunded'
};

// Wishlist Item Priorities
export const WISHLIST_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'text-gray-500' },
  { value: 'medium', label: 'Medium', color: 'text-blue-500' },
  { value: 'high', label: 'High', color: 'text-red-500' }
];

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PRODUCTS: '/products',
  PRODUCT_DETAIL: '/products/:id',
  CART: '/cart',
  CHECKOUT: '/checkout',
  ORDERS: '/orders',
  ORDER_DETAIL: '/orders/:id',
  PROFILE: '/profile',
  WISHLISTS: '/wishlists',
  WISHLIST_DETAIL: '/wishlists/:id',
  WISHLIST_PUBLIC: '/wishlists/public/:uuid',
  SEARCH: '/search'
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
};

// Validation Rules
export const VALIDATION = {
  EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE_REGEX: /^\(\d{3}\) \d{3}-\d{4}$/,
  PASSWORD_MIN_LENGTH: 8
};

// Toast/Alert Types
export const ALERT_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error', 
  WARNING: 'warning',
  INFO: 'info'
};

// Theme Options
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark'
};

// Image Placeholders
export const PLACEHOLDERS = {
  PRODUCT_IMAGE: 'https://via.placeholder.com/300x300?text=Product+Image',
  USER_AVATAR: 'https://via.placeholder.com/100x100?text=User',
  NO_IMAGE: 'https://via.placeholder.com/150x150?text=No+Image'
};

// Responsive Breakpoints (matching Tailwind)
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  '2XL': 1536
};

// Loading States
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error'
};

// Cart Settings
export const CART_SETTINGS = {
  MAX_QUANTITY: 99,
  MIN_QUANTITY: 1
};

// Search Settings
export const SEARCH_SETTINGS = {
  MIN_QUERY_LENGTH: 2,
  DEBOUNCE_DELAY: 300
};
