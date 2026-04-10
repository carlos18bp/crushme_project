# Frontend Rules — Vue 3 + Vite + Pinia (CrushMe)

## Stack

- **Vue 3.5.13** (`<script setup>`-style components OK; **Pinia stores must use Options API** — see below)
- **Vite 7** as the dev server and bundler
- **Pinia 3.0.3** + **`pinia-plugin-persistedstate`** for state management (Options API + localStorage persistence)
- **Vue Router 4.5.1** with locale prefixes (`/en/...`, `/es/...`)
- **Axios 1.12.2** wrapped by **two HTTP clients**:
  - `src/services/request_http.js` — content/admin flows (CSRF cookie injected)
  - `src/composables/usePlatformApi.js` — platform/auth flows (JWT interceptors)
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
- Use **Options API in Pinia stores** (`{ state, getters, actions }`) — this is a project invariant.

## Naming Conventions

- **Pinia store files**: camelCase (`authStore.js`, `productStore.js`, `cartStore.js`, `orderStore.js`, `wishlistStore.js`, `profileStore.js`, `paymentStore.js`, `currencyStore.js`, `i18nStore.js`, `crushStore.js`).
- **Component files**: PascalCase (`HomeView.vue`, `LoginView.vue`, `ProductDetailView.vue`).
- **Composables**: camelCase with `use` prefix (`usePlatformApi.js`).
- Stores live under `src/stores/modules/`.

## State Management — Pinia (Options API + persisted)

- **Always Options API**:
  ```javascript
  import { defineStore } from 'pinia'

  export const useCartStore = defineStore('cart', {
    state: () => ({ items: [], totalCop: 0, totalUsd: 0 }),
    getters: { itemCount: (state) => state.items.length },
    actions: {
      addItem(product, quantity) { /* ... */ }
    },
    persist: true  // pinia-plugin-persistedstate
  })
  ```
- **Persisted state**: relevant slices (auth tokens, cart, currency, language) persist to `localStorage` automatically via `pinia-plugin-persistedstate`.
- **Do not use `setup()` style stores** unless explicitly asked.

## HTTP — Two clients, never mix

This codebase has **two HTTP clients** because the backend has a dual auth scheme:

| Use case | Client | Auth |
|----------|--------|------|
| Public catalog, products, blog, content | `src/services/request_http.js` | CSRF cookie |
| Auth (login/signup/profile), wishlists, orders, JWT-protected endpoints | `src/composables/usePlatformApi.js` | JWT (Bearer) |

- **Never call `fetch()` or raw `axios` directly** in stores or components. Always use one of the two wrappers.
- **Never mix the two clients in the same store/feature.** Choose one based on whether the endpoint requires JWT or not.

## Routing — vue-router 4 with locale prefixes

- Routes are declared in `src/router/index.js`.
- The router uses **locale prefixes** (`/en/...`, `/es/...`) — the active locale comes from the `i18nStore` Pinia store.
- Top-level routes: `/`, `/login`, `/signup`, `/products`, `/products/:id`, `/checkout`, `/profile/*`, `/about`, `/contact`, `/diaries/@{username}`.

## i18n — vue-i18n 9.14

- Locale files live in `src/locales/` (`en.json`, `es.json`).
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
- The backend respects a custom **`x-currency` header** (CORS-allowed). The platform HTTP client injects it from the active store.
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
- Do **not** convert Pinia stores to `setup()` style.
- Do **not** call `fetch()` or raw `axios` outside of `request_http.js` / `usePlatformApi.js`.
- Do **not** mix `request_http.js` and `usePlatformApi.js` in the same store.
- Do **not** translate product/blog content client-side — it's already translated at sync time.
- Do **not** introduce TypeScript-first patterns into JS files.
