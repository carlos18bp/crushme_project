# Frontend Rules — CrushMe

## Stack And Scope
- **Vue 3.5 + Vite 7 SPA** (no Nuxt, no SSR).
- The codebase is **JavaScript** (not TypeScript-first).
- State management: **Pinia 3** (Options API) + **`pinia-plugin-persistedstate`** for localStorage persistence.
- Routing: **vue-router 4** with locale prefixes (`/en/...`, `/es/...`).
- HTTP: **Axios** wrapped by **two clients** (see Project Conventions).
- i18n: **vue-i18n 9.14** with `src/locales/{en,es}.json`.
- Styling: **Tailwind 4** + **Flowbite 3** + **Headless UI** + **Heroicons**.
- Animations: **GSAP 3.13**, **Framer-Motion**.
- Tests: **Jest** for unit, **Playwright** for E2E.

## Project Conventions
- **Pinia stores use the Options API pattern** (`{ state, getters, actions }`). Do not rewrite to `setup()` style.
- **Persisted state**: relevant slices (auth tokens, cart, currency, language) persist to localStorage via `pinia-plugin-persistedstate`.
- **Two HTTP clients, never mix**:
  - **Content/admin flows** → `frontend/src/services/request_http.js` (Axios with CSRF cookie).
  - **Platform/auth (JWT) flows** → `frontend/src/composables/usePlatformApi.js` (Axios with JWT interceptors).
  - A given store either talks to the public catalog or the authenticated platform — never both.
- **Filename conventions**:
  - Pinia stores → camelCase (`authStore.js`, `productStore.js`, `cartStore.js`).
  - Components → PascalCase (`HomeView.vue`, `LoginView.vue`).
  - Composables → camelCase with `use` prefix (`usePlatformApi.js`).
  - Stores live under `src/stores/modules/`.
- **Bilingual content**: product/blog text is **already translated server-side** at WooCommerce sync time (via `argostranslate`). The frontend just picks up the localized field — do not translate client-side.
- **UI strings** (buttons, labels, errors) must go through `vue-i18n` — never hardcode user-facing text.
- **Currency**: the `currencyStore` tracks COP/USD. The platform HTTP client injects an `x-currency` header (a custom CORS-allowed header) so the backend returns prices in the right currency.

## UX And Routing
- vue-router 4 with locale prefixes. Active locale comes from the `i18nStore`.
- Top-level routes: `/`, `/login`, `/signup`, `/products`, `/products/:id`, `/checkout`, `/profile/*`, `/about`, `/contact`, `/diaries/@{username}`.
- For Playwright and async UI work, prefer **role-based locators** and **explicit element waits**.
- Do **not** use `networkidle` for Vite flows — the HMR WebSocket prevents it from settling.
- For SPA-heavy routes, keep `test.setTimeout(60_000)` in E2E specs.

## Commands
- Dev server: `cd frontend && npm run dev` (Vite, default :5173)
- Unit tests (Jest): `cd frontend && npm test -- path/to/file.spec.js`
- E2E (Playwright): `cd frontend && npx playwright test e2e/path/to/spec.js`
- Use `E2E_REUSE_SERVER=1` if Vite dev server is already running.
- Build: `cd frontend && npm run build` (emits to `../backend/static/frontend/`)

## Testing Rules
- Never run the full frontend unit or E2E suite.
- Maximum 20 tests per batch and 3 commands per cycle.
- Assert user-visible behavior, not implementation details.
- Use stable locators in E2E and avoid brittle text matches when a role or `data-testid` exists.
