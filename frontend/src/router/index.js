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
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('@/views/auth/TermsView.vue')
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('@/views/auth/PrivacyPolicyView.vue')
  },
  
  // Product routes
  {
    path: '/products',
    name: 'Products',
    component: () => import('@/views/products/ProductsView.vue')
  },
  {
    path: '/products/category/:category',
    name: 'ProductsByCategory',
    component: () => import('@/views/products/ProductsView.vue'),
    props: true
  },
  {
    path: '/products/:id',
    name: 'ProductDetail',
    component: () => import('@/views/products/ProductDetailView.vue'),
    props: true
  },
  
  // Shopping cart routes
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/cart/CheckoutView.vue')
  },
  {
    path: '/checkout/wompi/success',
    name: 'WompiSuccess',
    component: () => import('@/views/cart/WompiSuccess.vue')
  },

  
  // User profile routes (protected) - with layout and children
  {
    path: '/profile',
    component: () => import('@/layouts/ProfileLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/profile/ProfileDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'my-profile',
        name: 'MyProfile',
        component: () => import('@/views/profile/MyProfile.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'wishlist',
        name: 'ProfileWishlist',
        component: () => import('@/views/profile/ProfileWishlist.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'favorites',
        name: 'ProfileFavorites',
        component: () => import('@/views/profile/ProfileFavorites.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'my-gifts',
        name: 'MyGifts',
        component: () => import('@/views/profile/MyGifts.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'history',
        name: 'ProfileHistory',
        component: () => import('@/views/profile/ProfileHistory.vue'),
        meta: { requiresAuth: true }
      }
    ]
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
  
  // Diaries pages
  {
    path: '/diaries',
    name: 'Diaries',
    component: () => import('@/views/diaries/DiariesView.vue')
  },
  {
    path: '/diaries/@:username',
    name: 'DiariesUser',
    component: () => import('@/views/diaries/DiariesView.vue'),
    props: true
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
      // Use detected locale if available, otherwise use current locale or default to 'en'
      const targetLocale = i18nStore.detectedLocale || i18nStore.locale || 'en';
      return `/${targetLocale}`;
    }
  },
  
  // ⭐ Wishlist direct checkout routes (with and without language prefix)
  {
    path: '/@:username/:wishlistId',
    name: 'WishlistCheckout',
    component: () => import('@/views/wishlist/WishlistCheckoutRedirect.vue'),
    props: true
  },
  // Localized versions for each language
  ...availableLanguages.map(lang => ({
    path: `/${lang}/@:username/:wishlistId`,
    name: `WishlistCheckout-${lang}`,
    component: () => import('@/views/wishlist/WishlistCheckoutRedirect.vue'),
    props: true
  })),
  
  // Routes for each language
  ...baseRoutes.map(route => {
    // Skip the catch-all route, we'll add it at the end
    if (route.path === '/:pathMatch(.*)*') return null;
    
    return availableLanguages.map(lang => {
      const localizedRoute = {
        ...route,
        path: route.path === '/' ? `/${lang}` : `/${lang}${route.path}`,
        name: route.name ? `${route.name}-${lang}` : undefined
      };
      
      // If route has children, update their names to include language
      if (route.children) {
        localizedRoute.children = route.children.map(child => ({
          ...child,
          name: child.name ? `${child.name}-${lang}` : undefined
        }));
      }
      
      return localizedRoute;
    });
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

// Debug: Log profile routes
console.log('🔍 Profile routes registered:');
routes.forEach(route => {
  if (route.path && route.path.includes('profile')) {
    console.log('  -', route.path, route.name, route.children ? `(${route.children.length} children)` : '');
    if (route.children) {
      route.children.forEach(child => {
        console.log('    └─', child.path, child.name);
      });
    }
  }
});

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const i18nStore = useI18nStore();
  
  console.log('🔍 [Router] Navegación detectada:', {
    to: to.path,
    currentStoreLang: i18nStore.locale
  });
  
  // Try to initialize if needed, but don't block navigation if it fails
  if (!i18nStore.isInitialized) {
    // Fire and forget - don't await
    i18nStore.initializeIfNeeded().catch(err => {
      console.warn('Language detection failed, using default:', err);
    });
  }
  
  // Extract language from URL
  const urlLang = to.path.split('/')[1];
  
  // Handle root path
  if (to.path === '/') {
    next();
    return;
  }
  
  // Check if it's a valid language route
  if (!availableLanguages.includes(urlLang)) {
    // If no language prefix, redirect to current store language or default
    const targetLang = i18nStore.locale || 'en';
    console.log('🔀 [Router] No language in URL, redirecting to:', targetLang);
    next(`/${targetLang}${to.path}`);
    return;
  }
  
  // Set language from URL - NO redirigir automáticamente
  // Esto permite que el usuario navegue en cualquier idioma sin interrupciones
  if (urlLang !== i18nStore.locale) {
    console.log('🌐 [Router] Actualizando idioma del store a:', urlLang);
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
