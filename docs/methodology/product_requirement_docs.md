# Product Requirements - CrushMe

## Vision

CrushMe is a bilingual (ES/EN) e-commerce and wishlist-sharing platform.
Verified "crush" profiles can receive gifted wishlists from other users. The
platform bridges Colombian and international markets through COP/USD pricing
and Wompi/PayPal payments.

Modernization must preserve this business model and its public contracts. It
may strengthen implementation, testing, security, and operations without
turning the project into a different product or creating a second runtime.

## Core Features

### 1. User Authentication And Profiles

- Email-based registration with the custom `User` model.
- JWT authentication with 15-minute access tokens, 7-day refresh tokens,
  rotation, blacklist, serialized refresh, and explicit logout revocation.
- Crush verification workflow through `is_crush`,
  `crush_verification_status`, and `crush_verified_at`.
- Guest checkout through session-bound `GuestUser` records.

### 2. Product Catalog

- Products and variants mirrored from WooCommerce.
- Category pricing overrides through `CategoryPriceMargin`.
- Product galleries through the vendored `django_attachments` app.
- Offline ES/EN translation at synchronization time through a CPU-only local
  engine, cached in `TranslatedContent`.

### 3. Cart, Wishlists, And Gifting

- Frontend cart persistence plus server-side cart and price validation.
- UUID-based public and shareable wishlists.
- Anonymous gifting without mandatory registration.
- Favorite wishlists and public diary/profile pages.

### 4. Orders And Payments

- PayPal for USD and Wompi for COP.
- A server-generated `PaymentSession` is the authority for products, variants,
  shipping, discounts, currency, amount, and gateway identifiers.
- Captures and webhooks must match durable payment state before changing an
  order.
- Completed local orders can be forwarded to WooCommerce.

### 5. Bilingual And Multi-Currency Experience

- Locale-prefixed `/en/` and `/es/` routes with Vue I18n UI strings.
- `currencyStore` tracks COP/USD and the shared HTTP client sends `X-Currency`.
- Backend content is translated and priced before the frontend renders it.

### 6. Reviews, Contact, And Feed

- Product reviews and ratings.
- Persisted contact requests.
- User activity feed.

## Non-Functional Requirements

- **Availability**: production is the single runtime at `crushme.com.co` and
  `www.crushme.com.co`.
- **Compatibility**: preserve function-based DRF views, API payloads, locale
  routes, the single Axios client, and existing payment/business behavior.
- **Security**: no reachable critical/high dependency finding; explicit
  integration modes; server-side totals; throttling; signature checks; upload
  content, size, pixel, and count limits; no active secrets in source.
- **Data safety**: fresh database/media backup and tested restore before every
  runtime-changing wave; fake-data and E2E tooling must reject production.
- **Testing**: partitioned backend, frontend-unit, E2E, lint, quality, and
  MySQL-specific CI gates with hermetic settings.
- **Performance**: Redis cache DB 1, Huey queue DB 2, conditional Silk, and at
  least 30 percent measured production headroom before lifecycle promotion.
- **Translation safety**: production inference is CPU-only, offline, isolated
  from web/worker cgroups, integrity-verified, and must not load Torch/CUDA.
