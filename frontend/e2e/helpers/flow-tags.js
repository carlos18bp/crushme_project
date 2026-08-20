/** Canonical flow IDs. The registry sync check reads this block directly. */
export const FlowIds = Object.freeze({
  publicHome: 'public-home',
  publicAbout: 'public-about',
  publicTerms: 'public-terms',
  publicPrivacy: 'public-privacy',
  publicContactSubmit: 'public-contact-submit',
  publicFaqToggle: 'public-faq-toggle',
  navigationLocaleSwitch: 'navigation-locale-switch',
  navigationMobileMenu: 'navigation-mobile-menu',
  navigationNotFound: 'navigation-not-found',
  authRegister: 'auth-register',
  authVerifyEmail: 'auth-verify-email',
  authResendVerification: 'auth-resend-verification',
  authLogin: 'auth-login',
  authForgotPassword: 'auth-forgot-password', // pragma: allowlist secret
  authResetPassword: 'auth-reset-password', // pragma: allowlist secret
  authProtectedRedirect: 'auth-protected-redirect',
  authGuestRedirect: 'auth-guest-redirect',
  authLogout: 'auth-logout',
  catalogBrowse: 'catalog-browse',
  catalogFilterSort: 'catalog-filter-sort',
  catalogSearch: 'catalog-search',
  catalogProductDetail: 'catalog-product-detail',
  catalogProductVariation: 'catalog-product-variation',
  catalogTrendingNavigation: 'catalog-trending-navigation',
  cartOpen: 'cart-open',
  cartAdd: 'cart-add',
  cartQuantityUpdate: 'cart-quantity-update',
  cartRemove: 'cart-remove',
  cartCheckoutValidation: 'cart-checkout-validation',
  checkoutGuestIdentify: 'checkout-guest-identify',
  checkoutShippingDetails: 'checkout-shipping-details',
  checkoutDiscount: 'checkout-discount',
  checkoutPaypal: 'checkout-paypal',
  checkoutWompi: 'checkout-wompi',
  checkoutPaymentStatus: 'checkout-payment-status',
  checkoutGiftRecipient: 'checkout-gift-recipient',
  wishlistCreate: 'wishlist-create',
  wishlistEditDelete: 'wishlist-edit-delete',
  wishlistItemManage: 'wishlist-item-manage',
  wishlistPublicShare: 'wishlist-public-share',
  wishlistFavorite: 'wishlist-favorite',
  wishlistDirectGift: 'wishlist-direct-gift',
  profileDashboard: 'profile-dashboard',
  profileUpdate: 'profile-update',
  profileUpload: 'profile-upload',
  profileCrushVerification: 'profile-crush-verification',
  profileFavorites: 'profile-favorites',
  profileOrderHistory: 'profile-order-history',
  profileGifts: 'profile-gifts',
  profileFeed: 'profile-feed',
  diariesRandomCrush: 'diaries-random-crush',
  diariesPublicProfile: 'diaries-public-profile',
  diariesUserSearch: 'diaries-user-search',
  reviewsDisplay: 'reviews-display',
  reviewsCreate: 'reviews-create',
  reviewsManage: 'reviews-manage',
  pricingCurrencyDisplay: 'pricing-currency-display',
  adminLogin: 'admin-login',
  adminOrderManagement: 'admin-order-management',
  adminCrushVerification: 'admin-crush-verification',
});

export function flowTags(id, module, priority) {
  return [`@flow:${id}`, `@module:${module}`, `@priority:${priority}`];
}

export const AUTH_LOGIN = flowTags(FlowIds.authLogin, 'auth', 'P1');
export const AUTH_REGISTER = flowTags(FlowIds.authRegister, 'auth', 'P1');
export const PUBLIC_HOME = flowTags(FlowIds.publicHome, 'public', 'P2');
export const PUBLIC_TERMS = flowTags(FlowIds.publicTerms, 'public', 'P3');
export const CATALOG_BROWSE = flowTags(FlowIds.catalogBrowse, 'catalog', 'P1');
export const NAVIGATION_NOT_FOUND = flowTags(
  FlowIds.navigationNotFound,
  'navigation',
  'P3',
);
