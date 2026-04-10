# Product Requirements — CrushMe

## Vision
CrushMe is a bilingual (ES/EN) e-commerce + wishlist-sharing platform. Verified "crush" profiles can receive gifted wishlists from other users. The platform bridges Colombian and international markets through dual-currency (COP/USD) and dual-payment (Wompi/PayPal) support.

## Core Features

### 1. User Authentication & Profiles
- Email-based registration with custom User model (email-as-username)
- JWT authentication (30d access, 60d refresh, rotation + blacklist)
- Crush verification workflow: users can request verification to become "crushes" eligible for gifted wishlists (`is_crush`, `crush_verification_status`, `crush_verified_at`)
- Guest checkout via `GuestUser` model (session-based, no registration required)

### 2. Product Catalog (WooCommerce Mirror)
- Products mirrored from a remote WooCommerce store via `sync_woocommerce` command
- Local models: `WooCommerceProduct`, `WooCommerceProductVariation`
- Category-based price margins via `CategoryPriceMargin`
- Product images and galleries via `django_attachments`
- All product text translated offline at sync time (ES/EN) via `argostranslate` → cached in `TranslatedContent`

### 3. Shopping Cart
- Cart persisted to localStorage on the frontend (`cartStore`)
- Backend `Cart` and `CartItem` models for server-side validation at checkout

### 4. Wishlists (Public & Shareable)
- Users create wishlists with items from the product catalog
- Each `WishList` has a UUID-based public share URL
- Anonymous visitors can view and gift wishlist items without an account
- `FavoriteWishList` lets users bookmark other people's wishlists

### 5. Orders & Checkout
- Dual payment gateways:
  - **PayPal** for international payments (USD)
  - **Wompi** for Colombian payments (COP)
- Webhook endpoints update `Order.status` based on payment events
- Order tracking via `OrderTracking` model
- Orders can be forwarded to WooCommerce via `woocommerce_order_service`

### 6. Reviews & Ratings
- Product reviews with text and images (`Review`, `ReviewImage`)

### 7. User Diaries / Public Profiles
- Public-facing user diary pages at `/diaries/@{username}`

### 8. Bilingual UI
- Frontend: `vue-i18n` locale files organized by domain (auth, products, shared, etc.)
- Backend: product content pre-translated at WooCommerce sync time
- Locale-prefixed routing: `/en/...` and `/es/...`

### 9. Multi-Currency
- COP (Colombian Peso) for Wompi payments
- USD for PayPal payments
- `currencyStore` tracks active currency, `request_http.js` injects `X-Currency` header
- Backend `CurrencyMiddleware` reads the header

### 10. Contact & Feed
- Contact form with `ContactMessage` model
- Feed system for user activity

## Non-Functional Requirements
- **Domain**: crushme.com.co / www.crushme.com.co
- **Memory limit**: 650M (PyTorch installed but unused)
- **Bilingual**: ES primary, EN secondary
- **Performance**: Redis cache (db 1), django-silk profiling (conditional)
- **Backups**: Weekly via Huey task + django-dbbackup
