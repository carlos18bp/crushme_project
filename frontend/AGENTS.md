# Frontend Rules — Vue 3 + Vite + Pinia (CrushMe)

## Stack

- **Vue 3.5.13** (`<script setup>`-style components OK)
- **Vite 7** as the dev server and bundler
- **Pinia 3.0.3** + **`pinia-plugin-persistedstate`** for state management (mixed API styles + localStorage persistence)
- **Vue Router 4.5.1** with locale prefixes (`/en/...`, `/es/...`)
- **Axios 1.12.2** wrapped by a **single HTTP client**: `src/services/request_http.js` (CSRF + JWT + auto-refresh)
- **vue-i18n 9.14.5** for EN/ES localization
- **Tailwind CSS 4.1.13** + **Flowbite 3.1.2**
- **Headless UI Vue 1.7.23**, **Heroicons 2.2**, **Bootstrap Icons 1.13**
- **GSAP 3.13** for animations
- **SweetAlert2 11.23**, **country-state-city 3.2** for forms
- **Tests**: Jest (unit) + Playwright (E2E)

This is a **Vue 3 + Vite SPA** — **NOT Nuxt**. There is no SSR.

## Code Style and Structure

- The codebase is **JavaScript**, not TypeScript-first.
- Use Composition API in components when adding new ones.
- Most Pinia stores use the **setup/Composition API** (`defineStore('name', () => { ... })`). A few (i18nStore, reviewStore, contactStore) use the **Options API**. Match the style of the store you're editing.

## Naming Conventions

- **Pinia store files**: camelCase (`authStore.js`, `productStore.js`, `cartStore.js`, `orderStore.js`, `wishlistStore.js`, `profileStore.js`, `paymentStore.js`, `currencyStore.js`, `i18nStore.js`, `crushStore.js`, `reviewStore.js`, `contactStore.js`).
- **Component files**: PascalCase (`HomeView.vue`, `LoginView.vue`, `ProductDetailView.vue`).
- **Composables**: camelCase with `use` prefix (`useAlert.js`, `useCart.js`, `useCheckout.js`, `useNotifications.js`).
- Stores live under `src/stores/modules/`.

## State Management — Pinia (mixed API styles + persisted)

- Most stores use the **setup/Composition API**:
  ```javascript
  import { defineStore } from 'pinia'
  import { ref, computed } from 'vue'

  export const useCartStore = defineStore('cart', () => {
    const items = ref([])
    const itemCount = computed(() => items.value.length)
    function addItem(product, quantity) { /* ... */ }
    return { items, itemCount, addItem }
  })
  ```
- A few stores (i18nStore, reviewStore, contactStore) use the **Options API** (`{ state, getters, actions }`).
- **Persisted state**: relevant slices (auth tokens, cart, currency, language) persist to `localStorage` automatically via `pinia-plugin-persistedstate`.
- Match the style of the store you're editing.

## HTTP — Single client with CSRF + JWT

All API requests go through **`src/services/request_http.js`** — a single Axios wrapper that:
- Sends `X-CSRFToken` (from cookie) and `Authorization: Bearer` (from localStorage) headers on every request
- Injects `Accept-Language` and `X-Currency` headers from the i18n and currency stores
- Handles automatic JWT refresh on 401 responses (retries the original request with a new token)
- Exports: `get_request`, `create_request`, `update_request`, `patch_request`, `delete_request`, `upload_request`

- **Never call `fetch()` or raw `axios` directly** in stores or components. Always use the `request_http.js` helpers.

## Routing — vue-router 4 with locale prefixes

- Routes are declared in `src/router/index.js`.
- The router uses **locale prefixes** (`/en/...`, `/es/...`) — the active locale comes from the `i18nStore` Pinia store.
- Top-level routes: `/`, `/login`, `/signup`, `/products`, `/products/:id`, `/checkout`, `/profile/*`, `/about`, `/contact`, `/diaries/@{username}`.

## i18n — vue-i18n 9.14

- Locale files live in `src/locales/` organized by domain (e.g., `auth/login/{en,es}.json`, `products/{en,es}.json`, `shared/{en,es}.json`).
- The `i18nStore` Pinia store toggles the active locale.
- **Never hardcode user-facing strings** — everything goes through `t('key')`.
- **Product/blog content from the backend is already translated** at WooCommerce sync time via `argostranslate`. The frontend just picks up the localized field — do not translate it again client-side.

## UI and Styling — Tailwind 4 + Flowbite

### Class Ordering
Layout → position → spacing → sizing → typography → visual → interactive.

### Responsive
Mobile-first. Breakpoint order: `sm:` → `md:` → `lg:` → `xl:` → `2xl:`.

### `@apply`
Use `@apply` only for base component styles that repeat 5+ times. Prefer utility classes inline.

### Avoid
- Never use `style=""` when a Tailwind class exists.
- Avoid arbitrary values (`text-[#1a1a2e]`); define design tokens in `tailwind.config.js`.
- No `!important` (`!` prefix) unless overriding third-party styles.

## Currency Handling

- The `currencyStore` Pinia store tracks the active currency (COP for Wompi, USD for PayPal).
- The backend respects a custom **`x-currency` header** (CORS-allowed). `request_http.js` injects it from the `currencyStore` on every request.
- Prices come back from the backend already converted; do not convert client-side.

## Component Patterns

- Pages live in `src/views/`. They are thin and call `store.init()` or `store.fetchSomething()` on mount.
- Reusable components live in `src/components/`.
- Layouts (e.g., `ProfileLayout`) live in `src/layouts/`.

## Testing — Jest + Playwright

### Jest (unit)
- Test files in `frontend/test/` with `.spec.js` extension.
- Run: `cd frontend && npm test -- path/to/file.spec.js`
- Use `@vue/test-utils` and prefer `data-testid` and role-based queries.

### Playwright (E2E)
- Specs in `frontend/e2e/`.
- Run: `cd frontend && npx playwright test e2e/path/to/spec.js`
- Use `E2E_REUSE_SERVER=1` when Vite dev server is already running.
- **Selector hierarchy**: `getByRole` > `getByTestId` > `locator('[data-testid=...]')`.
- **No `waitForTimeout()`** — use `toBeVisible()`, `waitForResponse()`, `waitForURL()`.
- **No `networkidle`** with Vite HMR — it never settles. Use `domcontentloaded` + element waits.

## What NOT to do

- Do **not** introduce Nuxt or any SSR layer.
- Do **not** call `fetch()` or raw `axios` outside of `request_http.js`.
- Do **not** translate product/blog content client-side — it's already translated at sync time.
- Do **not** introduce TypeScript-first patterns into JS files.
