# Mapa de flujos de usuario de CrushMe

**Fecha de corte:** 2026-08-20
**Registro ejecutable:** `frontend/e2e/flow-definitions.json`
**Fase:** QA Fase 1, inventario de flujos desde codigo real
**Alcance:** 56 flujos, 149 outcomes, 25 P1 y 22 P2
**Evidencia actual:** 4 cubiertos, 16 parciales, 36 faltantes, 0 junk-only y 0
sin validar; detalle en `docs/audits/2026-08-20-wave-4-qa.md`

## Roles

- **Guest:** visita contenido publico, explora el catalogo, usa el carrito
  local y completa checkout anonimo.
- **User:** cuenta autenticada que administra perfil, favoritos, wishlists,
  pedidos y regalos.
- **Crush:** User con solicitud o aprobacion de verificacion; expone perfil
  publico y recibe regalos.
- **Gift buyer:** Guest o User que abre una wishlist publica y paga un regalo
  para su titular.
- **Staff:** operador autenticado del Django Admin.

## Convenciones

- Cada ID representa una interaccion observable desde navegador, no la mera
  disponibilidad de un endpoint o metodo de store.
- Los outcomes son `success`, `error`, `failure` y `display`.
- `error` cubre validacion local o respuesta rechazada; `failure` cubre una
  dependencia, carga o servicio no disponible. Flujos puramente estaticos
  solo requieren `display`.
- PayPal y Wompi se ejercitan exclusivamente con sandbox. SMTP, WooCommerce,
  sincronizacion, traduccion y webhooks no son interacciones directas de UI.
- No hay exenciones intencionales `expectedSpecs: 0` registradas.
- Las brechas se conservan visibles y se priorizan por severidad; una prueba
  solo recibe credito cuando ejecuta una interaccion y afirma su outcome.

## Inventario

| Modulo | Flujos | Outcomes | P1 | P2 |
|---|---:|---:|---:|---:|
| Publico | 6 | 10 | 0 | 2 |
| Navegacion | 3 | 5 | 0 | 1 |
| Autenticacion | 9 | 20 | 5 | 3 |
| Catalogo | 7 | 22 | 3 | 3 |
| Carrito | 6 | 15 | 3 | 2 |
| Checkout | 6 | 18 | 5 | 1 |
| Wishlists | 5 | 18 | 4 | 1 |
| Perfil | 7 | 21 | 4 | 3 |
| Diaries | 3 | 10 | 1 | 2 |
| Reviews | 1 | 2 | 0 | 1 |
| Admin | 3 | 8 | 0 | 3 |
| **Total** | **56** | **149** | **25** | **22** |

## Guest

| Modulo | Interacciones registradas |
|---|---|
| Publico | `public-home`, `public-about`, `public-terms`, `public-privacy`, `public-contact-submit`, `public-faq-toggle` |
| Navegacion | `navigation-locale-switch`, `navigation-mobile-menu`, `navigation-not-found` |
| Autenticacion | `auth-register`, `auth-verify-email`, `auth-resend-verification`, `auth-login`, `auth-forgot-password`, `auth-reset-password`, `auth-protected-redirect` |
| Catalogo | `catalog-browse`, `catalog-filter-sort`, `catalog-search`, `catalog-product-detail`, `catalog-product-variation`, `catalog-trending-navigation` |
| Carrito | `cart-open`, `cart-add`, `cart-quantity-update`, `cart-remove`, `cart-checkout-validation`, `cart-clear` |
| Checkout | `checkout-shipping-details`, `checkout-discount`, `checkout-paypal`, `checkout-wompi`, `checkout-payment-status`, `checkout-gift-recipient` |
| Diaries | `diaries-random-crush`, `diaries-public-profile`, `diaries-user-search` |
| Reviews | `reviews-display` |

## User y Crush

| Modulo | Interacciones registradas |
|---|---|
| Sesion | `auth-guest-redirect`, `auth-logout` |
| Catalogo | `catalog-favorite-product` |
| Wishlists | `wishlist-create`, `wishlist-item-manage`, `wishlist-public-share`, `wishlist-direct-gift`, `wishlist-public-search` |
| Perfil | `profile-dashboard`, `profile-update`, `profile-upload`, `profile-crush-verification`, `profile-favorites`, `profile-order-history`, `profile-gifts` |

El flujo de regalo desde wishlist publica resuelve `@username/wishlistId`,
descarta productos no disponibles y redirige con `giftMode`, destinatario e ID
de wishlist; el checkout vuelve a validar datos de envio, descuento, importe y
estado de pago.

## Staff

| Modulo | Interacciones registradas |
|---|---|
| Django Admin | `admin-login`, `admin-order-management`, `admin-crush-verification` |

## Evidencia Sustantiva

- Las rutas reales de checkout, perfil, wishlists y diaries estan en
  `frontend/src/router/index.js:95`, `frontend/src/router/index.js:107` y
  `frontend/src/router/index.js:198`.
- La ruta compartida consulta la wishlist publica, rechaza enlaces invalidos o
  listas vacias, omite items no disponibles y redirige al checkout en
  `frontend/src/views/wishlist/WishlistCheckoutRedirect.vue:60`,
  `frontend/src/views/wishlist/WishlistCheckoutRedirect.vue:71` y
  `frontend/src/views/wishlist/WishlistCheckoutRedirect.vue:123`.
- `wishlist-public-search` cubre el formulario y la consulta de listas publicas
  en `frontend/src/views/profile/ProfileWishlist.vue:32` y
  `frontend/src/views/profile/ProfileWishlist.vue:389`.
- `catalog-favorite-product` cubre el control que redirige guests a login y
  agrega o elimina favoritos en
  `frontend/src/components/products/ProductCard.vue:253`.
- `cart-clear` cubre la confirmacion previa al vaciado del carrito en
  `frontend/src/components/products/CartDrawer.vue:246`.
- Se retiro `checkout-guest-identify`: `guestCheckout()` existe solo como
  metodo de store en `frontend/src/stores/modules/authStore.js:289`, sin
  consumidor UI; el checkout anonimo real usa el formulario de envio.
- Se retiraron `wishlist-edit-delete` y `wishlist-favorite`: los metodos
  persisten en `frontend/src/stores/modules/wishlistStore.js:130` y
  `frontend/src/stores/modules/wishlistStore.js:433`, pero la UI solo crea,
  busca, copia y elimina items (`frontend/src/views/profile/ProfileWishlist.vue:311`).
- Se retiraron `reviews-create` y `reviews-manage`: los botones no tienen
  handler en `frontend/src/components/products/ProductReviews.vue:23` y la
  unica accion de menu permanece como TODO en
  `frontend/src/components/products/ProductReviews.vue:145`.
- Se retiro `pricing-currency-display`: la moneda se detecta por geolocalizacion
  en `frontend/src/stores/modules/currencyStore.js:63`; no existe selector de
  moneda en la UI actual.
- Se retiro `profile-feed`: no hay ruta de perfil para feed
  (`frontend/src/router/index.js:110`); solo persiste una consulta aislada en
  `frontend/src/stores/modules/profileStore.js:912`.
- Se conservan los flujos de Admin: la interfaz esta publicada en
  `backend/crushme_project/urls.py:33`, registra pedidos en
  `backend/crushme_app/admin.py:421` y acciones de aprobacion/rechazo de Crush
  en `backend/crushme_app/admin.py:110` y
  `backend/crushme_app/admin.py:133`.

## Disciplina de Selectores

La disciplina esta presente, pero parcial: hay `data-testid` para login,
terminos, catalogo y tarjetas de producto, por ejemplo
`frontend/src/views/auth/LoginView.vue:25` y
`frontend/src/components/products/ProductCard.vue:2`. Los flujos restantes
deben ampliar `data-testid` o roles accesibles antes de autorizar nuevos E2E.
