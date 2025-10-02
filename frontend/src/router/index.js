/**
 * Vue Router configuration for CrushMe e-commerce application
 * Simple routing configuration with basic guards and i18n support
 */
import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated } from '@/services/request_http.js';
import { useI18nStore } from '@/stores/modules/i18nStore';

// Available languages
const availableLanguages = ['en', 'es'];

// Base routes without language prefix
const baseRoutes = [
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
    path: '/signup',
    name: 'SignUp', 
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/verification',
    name: 'Verification',
    component: () => import('@/views/auth/VerificationView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPasswordView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/reset-code',
    name: 'ResetCode',
    component: () => import('@/views/auth/ResetCodeView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/auth/ResetPasswordView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/confirmation',
    name: 'Confirmation',
    component: () => import('@/views/auth/ConfirmationView.vue')
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
  
  // About Us page
  {
    path: '/about',
    name: 'AboutUs',
    component: () => import('@/views/AboutUsView.vue')
  },
  
  // Contact page
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('@/views/ContactView.vue')
  },
  
  // Error handling
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
];

// Generate localized routes
const routes = [
  // Root redirect
  {
    path: '/',
    redirect: to => {
      const i18nStore = useI18nStore();
      return `/${i18nStore.locale}`;
    }
  },
  
  // Routes for each language
  ...baseRoutes.map(route => {
    // Skip the catch-all route, we'll add it at the end
    if (route.path === '/:pathMatch(.*)*') return null;
    
    return availableLanguages.map(lang => ({
      ...route,
      path: route.path === '/' ? `/${lang}` : `/${lang}${route.path}`,
      name: `${route.name}-${lang}`
    }));
  }).flat().filter(Boolean),
  
  // Catch-all route for 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Si hay una posición guardada (cuando usas botones de navegador), úsala
    if (savedPosition) {
      return savedPosition;
    }
    // Si la ruta tiene un hash (#), navega a ese elemento
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      };
    }
    // Por defecto, vuelve al inicio de la página
    return { top: 0, left: 0, behavior: 'smooth' };
  }
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const i18nStore = useI18nStore();
  
  // Extract language from URL
  const urlLang = to.path.split('/')[1];
  
  // Handle root path
  if (to.path === '/') {
    next();
    return;
  }
  
  // Check if it's a valid language route
  if (!availableLanguages.includes(urlLang)) {
    // If no language prefix, redirect to current language
    const currentLang = i18nStore.locale;
    next(`/${currentLang}${to.path}`);
    return;
  }
  
  // Set language if different from current
  if (urlLang !== i18nStore.locale) {
    i18nStore.setLocale(urlLang);
  }
  
  // Handle authentication
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ name: `Login-${urlLang}`, query: { redirect: to.fullPath } });
  } else if (to.meta.requiresGuest && isAuthenticated()) {
    next({ name: `Home-${urlLang}` });
  } else {
    next();
  }
});

export default router;
