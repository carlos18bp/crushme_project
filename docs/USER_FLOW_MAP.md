# Mapa de flujos de usuario de CrushMe

**Fecha de corte:** 2026-08-20  
**Registro ejecutable:** `frontend/e2e/flow-definitions.json`  
**Estado:** plataforma E2E inicial; cierre funcional pendiente en la ola 4

## Roles

- **Guest:** visitante sin cuenta; puede explorar, contactar, registrarse y
  comprar o regalar mediante checkout de invitado.
- **User:** cuenta verificada; ademas administra carrito, perfil, favoritos,
  pedidos y wishlists.
- **Crush:** usuario con estado de verificacion aprobado o en tramite; publica
  perfil, recibe regalos y consulta actividad asociada.
- **Gift buyer:** guest o user que entra desde una wishlist publica y debe
  conservar destinatario, productos y direccion durante el pago.
- **Staff:** operador autenticado en Django Admin para pedidos y solicitudes de
  verificacion.

## Convenciones

- Cada ID representa una interaccion observable, no la mera existencia de una
  ruta.
- Los outcomes son `success`, `error`, `failure` y `display`.
- Un `display` califica solo si la prueba llega por navegacion real y valida
  datos del escenario, no solo visibilidad generica.
- Las integraciones externas se simulan en E2E. PayPal y Wompi usan sandbox;
  SMTP, WooCommerce remoto y servicios de traduccion nunca reciben trafico.
- Sincronizacion WooCommerce, traduccion batch y webhooks son contratos de
  backend sin una accion directa de navegador; se cubren con pytest/integracion.
- La configuracion rechaza `crushme.com.co` y `www.crushme.com.co`. Staging
  remoto exige opt-in y es read-only salvo autorizacion adicional explicita.

## Guest

| Modulo | Interacciones registradas |
|---|---|
| Publico | `public-home`, `public-about`, `public-terms`, `public-privacy`, `public-contact-submit`, `public-faq-toggle` |
| Navegacion | `navigation-locale-switch`, `navigation-mobile-menu`, `navigation-not-found` |
| Autenticacion | `auth-register`, `auth-verify-email`, `auth-resend-verification`, `auth-login`, `auth-forgot-password`, `auth-reset-password`, `auth-protected-redirect` |
| Catalogo | `catalog-browse`, `catalog-filter-sort`, `catalog-search`, `catalog-product-detail`, `catalog-product-variation`, `catalog-trending-navigation` |
| Carrito | `cart-open`, `cart-add`, `cart-quantity-update`, `cart-remove`, `cart-checkout-validation` |
| Checkout | `checkout-guest-identify`, `checkout-shipping-details`, `checkout-discount`, `checkout-paypal`, `checkout-wompi`, `checkout-payment-status` |
| Descubrimiento | `diaries-random-crush`, `diaries-public-profile`, `diaries-user-search`, `reviews-display`, `pricing-currency-display` |

## User

Ademas de los flujos publicos, catalogo y checkout compartidos, una cuenta
verificada ejecuta estas interacciones:

| Modulo | Interacciones registradas |
|---|---|
| Sesion | `auth-guest-redirect`, `auth-logout` |
| Wishlists | `wishlist-create`, `wishlist-edit-delete`, `wishlist-item-manage`, `wishlist-public-share`, `wishlist-favorite`, `wishlist-direct-gift` |
| Perfil | `profile-dashboard`, `profile-update`, `profile-upload`, `profile-crush-verification`, `profile-favorites`, `profile-order-history`, `profile-gifts`, `profile-feed` |
| Reviews | `reviews-create`, `reviews-manage` |

## Crush

La persona Crush comparte los flujos de User. Sus diferencias observables se
concentran en `profile-crush-verification`, `diaries-public-profile`,
`wishlist-public-share`, `profile-gifts` y `profile-feed`: estado de
verificacion, perfil publico, listas publicadas, regalos recibidos y actividad.

## Gift Buyer

El recorrido inicia navegando a `wishlist-public-share`, continua por
`wishlist-direct-gift` y `checkout-gift-recipient`, y termina en
`checkout-paypal` o `checkout-wompi` mas `checkout-payment-status`. Las pruebas
deben demostrar que el servidor conserva el destinatario y recalcula importe,
moneda, descuento y envio sin confiar en valores del cliente.

## Staff

| Modulo | Interacciones registradas |
|---|---|
| Admin | `admin-login`, `admin-order-management`, `admin-crush-verification` |

La ejecucion E2E de staff usa un usuario determinista no compartido con
produccion. Las tareas CLI de sincronizacion, backups y traduccion no se
clasifican como flujos de navegador.

## E2E Coverage Index

| Modulo | Flujos | Outcomes | P1 | P2 | Estado inicial |
|---|---:|---:|---:|---:|---|
| Publico | 6 | 10 | 0 | 2 | `public-terms:display` cubierto |
| Navegacion | 3 | 5 | 0 | 1 | `navigation-not-found:display` cubierto |
| Auth | 9 | 20 | 5 | 3 | `auth-login:success,error` cubiertos |
| Catalogo | 6 | 18 | 3 | 2 | `catalog-browse:display` cubierto |
| Carrito | 5 | 13 | 3 | 2 | Pendiente |
| Checkout | 7 | 21 | 6 | 1 | Pendiente |
| Wishlists | 6 | 20 | 4 | 2 | Pendiente |
| Perfil | 8 | 23 | 4 | 3 | Pendiente |
| Diaries | 3 | 10 | 1 | 2 | Pendiente |
| Reviews | 3 | 8 | 0 | 2 | Pendiente |
| Pricing | 1 | 2 | 1 | 0 | Pendiente |
| Admin | 3 | 8 | 0 | 3 | Pendiente |
| **Total** | **60** | **158** | **27** | **23** | **5 outcomes iniciales** |

La ola 4 debe atender primero los outcomes P1 faltantes de checkout, carrito,
wishlist publica/regalos, autenticacion y perfil. Ningun flujo pendiente se
marca `expectedSpecs: 0`; por tanto el reporte conserva la deuda visible.
