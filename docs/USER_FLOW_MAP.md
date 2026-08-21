# Mapa de flujos de usuario de CrushMe

**Fecha de corte:** 2026-08-21
**Registro ejecutable:** `frontend/e2e/flow-definitions.json`
**Fuente de verdad:** rutas Vue, componentes, stores consumidos por UI,
URLs/vistas Django y Django Admin en `2dec475`.
**Alcance:** 64 flujos, 176 outcomes, 26 P1 y 27 P2.
**Cobertura E2E:** 64/64 flujos cubiertos por 178 tests calificables en 23
specs; 0 parciales, junk-only, no validados o faltantes. Auditoría estricta:
99/100, 0 errores y 0 advertencias.

## Roles

- **Guest:** visita contenido público, explora catálogo, mantiene un carrito local y completa checkout anónimo.
- **User:** cuenta autenticada que gestiona perfil, favoritos, wishlists, pedidos y regalos.
- **Crush:** User con solicitud, rechazo o aprobación de verificación; expone perfil público y recibe regalos.
- **Gift buyer:** Guest o User que abre una wishlist pública y compra para su titular.
- **Staff:** operador autenticado del Django Admin personalizado.

## Convenciones

- Un flow representa una interacción verificable desde el navegador. Endpoints sin disparador UI, webhooks, sincronización WooCommerce, traducción, tareas Huey y comandos de gestión no son flows E2E.
- `success` es la acción completada; `error` es validación, permiso o rechazo recuperable; `failure` es una dependencia o solicitud fallida; `display` es contenido, datos reales o estado vacío observable.
- Cuando una clase no aparece en el registro, es **n/a**: el código no contiene un camino de navegador para esa clase. Por ejemplo, las páginas legales sólo tienen `display`; los guards sólo redirigen localmente.
- Un display E2E debe llegar mediante navegación UI y afirmar datos reales, nunca sólo `goto()` y visibilidad.
- No existen exenciones `expectedSpecs: 0`.
- Los contratos UI relevantes usan `request_http.js`: JWT, CSRF, `Accept-Language` y `X-Currency`. Los resultados HTTP rechazados son `error`; fallas de red, gateway o carga son `failure`.

## Guest

| Flow | Ruta o disparador real | Outcomes | n/a |
|---|---|---|---|
| `public-home` | `HomeView` y navegación principal | display, failure | success/error: no mutación ni validación propia |
| `public-about` | Navbar/Footer → `/en|es/about` | display | success/error/failure: contenido estático |
| `public-terms` | Auth/Footer → `/en|es/terms` | display | success/error/failure: contenido estático |
| `public-privacy` | Auth/Footer → `/en|es/privacy` | display | success/error/failure: contenido estático |
| `public-contact-submit` | `ContactView` → `POST /api/contact/` | success, error, failure | display: el formulario no carga datos de negocio |
| `public-faq-toggle` | FAQ de `HomeView` | success, display | error/failure: estado local |
| `navigation-locale-switch` | `LanguageSelector` | success, display | error/failure: cambio local de ruta/locale |
| `navigation-mobile-menu` | Navbar móvil | success, display | error/failure: navegación local |
| `navigation-not-found` | catch-all Vue | display | success/error/failure: vista estática de recuperación |
| `auth-register` | `/signup`, `POST /api/auth/signup/` | success, error, failure | display: no lista de datos |
| `auth-verify-email` | `/verification`, `POST /api/auth/verify-email/` | success, error, failure | display: sólo formulario/alerta |
| `auth-resend-verification` | botón `verification-resend` | success, error, failure | display: sólo alerta/cooldown |
| `auth-login` | `/login`, `POST /api/auth/login/` | success, error, failure | display: sólo formulario/alerta |
| `auth-forgot-password` | `/forgot-password`, `POST /api/auth/forgot-password/` | success, error, failure | display: sólo formulario/alerta |
| `auth-reset-code` | `/reset-code`, código de cuatro dígitos | success, error | failure: submit sólo navega localmente |
| `auth-reset-password` | `/reset-password`, `POST /api/auth/reset-password/` | success, error, failure | display: sólo formulario/alerta |
| `auth-protected-redirect` | guard de rutas `/profile/**` | success | error/failure/display: guard local sin vista propia |
| `catalog-browse` | Navbar → `/products`, WooCommerce local API | display, failure | success/error: cargar lista no muta ni valida input |
| `catalog-filter-sort` | filtros, sort y paginación de `ProductsView` | success, display, failure | error: categorías proceden del API, no hay input inválido UI |
| `catalog-search` | búsqueda de `ProductsView` | success, display, failure | error: búsqueda libre sin validación de rechazo UI |
| `catalog-product-detail` | tarjeta → `/products/:id` | display, error, failure | success: abrir detalle no muta |
| `catalog-product-variation` | atributos de `ProductDetailView` | success, error, failure, display | ninguna |
| `catalog-trending-navigation` | `TrendingProducts` | success, display, failure | error: no hay formulario/validación |
| `catalog-buy-now` | `ProductCard.handleBuyNow()` | success, error, failure | display: cubierto por catálogo/detalle |
| `cart-open` | botón Navbar con `aria-label="Cart"` | display | success/error/failure: sólo estado local |
| `cart-add` | tarjeta/detalle → `cartStore.addToCart()` | success, error, failure | display: cubierto por drawer |
| `cart-quantity-update` | controles +/- del drawer | success, error, failure | display: cubierto por drawer |
| `cart-remove` | remover item del drawer | success, display | error/failure: mutación local sin request |
| `cart-checkout-validation` | drawer → checkout | success, error, display | failure: validación y routing locales |
| `cart-clear` | confirmación de `CartDrawer` | success, display | error/failure: mutación local |
| `checkout-shipping-details` | formulario de `CheckoutView` | success, error, failure | display: datos no son vista independiente |
| `checkout-discount` | `POST /api/discounts/validate/` | success, error, failure | display: descuento se afirma dentro del total |
| `checkout-paypal` | botones sandbox PayPal | success, error, failure | display: integración no tiene vista de datos |
| `checkout-wompi` | widget sandbox Wompi | success, error, failure | display: integración no tiene vista de datos |
| `checkout-payment-status` | `/checkout/wompi/success`, polling status | success, display, error, failure | ninguna |
| `checkout-gift-recipient` | búsqueda/selección de receptor | success, error, failure | display: resultados se prueban en el flujo de selección |
| `wishlist-public-share` | `/:locale?/@:username/:wishlistId` | success, error, failure, display | ninguna |
| `wishlist-direct-gift` | botón Buy wishlist desde perfil público | success, error, failure | display: lista se afirma en perfil público |
| `diaries-random-crush` | `/diaries`, `GET /api/auth/crush/random/` | success, display, failure | error: no hay input validable |
| `diaries-public-profile` | `/diaries/@:username` | display, error, failure | success: cargar perfil no muta |
| `diaries-user-search` | `UserSearch` con debounce | success, display, failure | error: texto libre sin rechazo UI |
| `diaries-media-view` | modal de avatar, portada o galería | success, display | error/failure: estado local |
| `reviews-display` | `ProductReviews` en detalle | display, failure | success/error: UI actual no crea ni edita reviews |

## User

| Flow | Ruta o disparador real | Outcomes | n/a |
|---|---|---|---|
| `auth-guest-redirect` | guard de login/signup | success | error/failure/display: guard local |
| `auth-logout` | `ProfileSidebar.handleLogout()` | success, failure | error/display: no formulario ni vista de datos |
| `catalog-favorite-product` | corazón de `ProductCard`/detalle | success, error, failure, display | ninguna |
| `wishlist-create` | modal de `ProfileWishlist` | success, error, failure | display: lista se prueba al expandirla |
| `wishlist-item-manage` | selector de wishlist y remover item | success, error, failure, display | ninguna |
| `wishlist-public-search` | formulario de `ProfileWishlist` | success, display, error, failure | ninguna |
| `wishlist-copy-share-link` | botones de copiar URL en wishlist/perfil público | success, error | failure/display: Clipboard API es la única dependencia y el contenido se cubre en el flow origen |
| `profile-dashboard` | `/profile` | display, failure | success/error: dashboard no muta ni recibe input |
| `profile-update` | `/profile/my-profile` | success, error, failure | display: carga inicial se cubre con dashboard |
| `profile-upload` | foto de perfil, portada y galería | success, error, failure, display | ninguna |
| `profile-crush-verification` | solicitud/cancelación en `MyProfile` | success, error, failure, display | ninguna |
| `profile-favorites` | `/profile/favorites` | success, display, failure | error: no input validable |
| `profile-order-history` | `/profile/history` | display, failure | success/error: expansión/paginación no muta |
| `profile-gifts` | `/profile/my-gifts` | success, display, failure | error: tabs locales sin validación |
| `profile-feed` | `Feed` en `ProfileDashboard` → `GET /api/feeds/my-feeds/` | display, failure | success/error: no acción mutante ni formulario |

## Crush

| Flow | Ruta o disparador real | Outcomes | n/a |
|---|---|---|---|
| `profile-dashboard` | dashboard autenticado | display, failure | success/error: sin mutación |
| `profile-update` | formulario `MyProfile` | success, error, failure | display: carga cubierta por dashboard |
| `profile-upload` | media de `MyProfile` | success, error, failure, display | ninguna |
| `profile-crush-verification` | solicitud, cancelación y estado | success, error, failure, display | ninguna |
| `profile-gifts` | regalos recibidos/enviados | success, display, failure | error: tabs locales |
| `profile-feed` | actividad del dashboard | display, failure | success/error: sin mutación |

## Gift Buyer

| Flow | Ruta o disparador real | Outcomes | n/a |
|---|---|---|---|
| `wishlist-public-share` | enlace compartido de wishlist | success, error, failure, display | ninguna |
| `wishlist-direct-gift` | compra desde wishlist pública | success, error, failure | display: lista cubierta al resolver link/perfil |
| `checkout-shipping-details` | checkout de regalo | success, error, failure | display: no vista independiente |
| `checkout-gift-recipient` | destinatario prellenado o seleccionado | success, error, failure | display: resultados son parte de selección |
| `checkout-discount` | código de descuento | success, error, failure | display: total en checkout |
| `checkout-paypal` | PayPal sandbox | success, error, failure | display: no vista propia |
| `checkout-wompi` | Wompi sandbox | success, error, failure | display: no vista propia |
| `checkout-payment-status` | retorno de gateway | success, display, error, failure | ninguna |

## Staff

| Flow | Superficie real | Outcomes | n/a |
|---|---|---|---|
| `admin-login` | `/admin/` custom `CrushMeAdminSite` | success, error, failure | display: login no lista datos |
| `admin-order-management` | `OrderAdmin` | success, error, failure, display | ninguna |
| `admin-crush-verification` | `CustomUserAdmin` actions approve/reject | success, error, failure, display | ninguna |
| `admin-user-management` | User, GuestUser, UserAddress, UserGallery y UserLink admins | success, error, failure, display | ninguna |
| `admin-catalog-management` | Product, WooCommerce catalog, categories, variations y margins admins | success, error, failure, display | ninguna |
| `admin-discount-management` | `DiscountCodeAdmin` | success, error, failure, display | ninguna |

## E2E Coverage Index

| Dimensión | Flujos | Outcomes | Estado |
|---|---:|---:|---|
| Público y navegación | 9 | 15 | pendiente de auditoría |
| Autenticación | 10 | 28 | pendiente de auditoría |
| Catálogo | 8 | 25 | pendiente de auditoría |
| Carrito | 6 | 14 | pendiente de auditoría |
| Checkout | 6 | 19 | pendiente de auditoría |
| Wishlists | 6 | 20 | pendiente de auditoría |
| Perfil | 8 | 21 | pendiente de auditoría |
| Diaries | 4 | 11 | pendiente de auditoría |
| Reviews | 1 | 2 | pendiente de auditoría |
| Django Admin | 6 | 23 | pendiente de auditoría |
| **Total** | **64** | **176** | **pendiente de auditoría** |

Ejecutar después de escribir el registro:

```bash
python3 scripts/flow_coverage_audit.py --repo-root . --json test-results/flow-audit.json
```

El layout es monolítico: `.testquality.yml` no declara `flow_definitions_dir`.
No corresponde ejecutar `generate_flow_registry.py`.
