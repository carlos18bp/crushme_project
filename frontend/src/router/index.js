/**
 * Vue Router configuration for CrushMe e-commerce application
 * Simple routing configuration with basic guards
 */
import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated } from '@/services/request_http.js';

const routes = [
  // Public routes
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  
  // Authentication routes
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register', 
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresGuest: true }
  },
  
  // Product routes
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/products/ProductsView.vue')
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('@/views/products/ProductDetailView.vue'),
    props: true
  },
  
  // Shopping cart routes
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/cart/CartView.vue')
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/cart/CheckoutView.vue'),
    meta: { requiresAuth: true }
  },
  
  // Order routes (protected)
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('@/views/orders/OrdersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: () => import('@/views/orders/OrderDetailView.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  
  // Wishlist routes (protected)
  {
    path: '/wishlists',
    name: 'Wishlists',
    component: () => import('@/views/wishlists/WishlistsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/wishlists/:id',
    name: 'WishlistDetail',
    component: () => import('@/views/wishlists/WishlistDetailView.vue'),
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/wishlists/public/:uuid',
    name: 'PublicWishlist',
    component: () => import('@/views/wishlists/PublicWishlistView.vue'),
    props: true
  },
  
  // User profile routes (protected)
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/profile/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  
  // Error handling
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Simple authentication guard
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (to.meta.requiresGuest && isAuthenticated()) {
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;
