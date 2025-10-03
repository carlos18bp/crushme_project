# Integración WooCommerce - Sistema de Órdenes

## 📋 Resumen

Este documento explica cómo funciona la integración completa entre tu sistema Django y WooCommerce para el manejo de productos y órdenes.

---

## 🏗️ Arquitectura General

```
┌─────────────┐      ┌──────────────┐      ┌────────────────┐
│   Frontend  │ ───▶ │    Django    │ ───▶ │  WooCommerce   │
│   (Simple)  │      │   Backend    │      │      API       │
└─────────────┘      └──────────────┘      └────────────────┘
                            │
                            ├─ Guarda local (formato simple)
                            └─ Transforma y envía (formato WooCommerce)
```

### ✅ **Ventajas de esta Arquitectura:**

1. **Frontend simple**: No cambia, sigue enviando dirección, ciudad, estado, código postal
2. **Backend inteligente**: Hace el mapeo y transformación según el país
3. **Sin productos locales**: Todo viene de WooCommerce API
4. **Parseo automático**: Direcciones colombianas se parsean automáticamente

---

## 📦 Flujo Completo: Producto → Carrito → Orden → WooCommerce

### 1. **Consultar Productos** (WooCommerce → Frontend)

```bash
GET /api/products/woocommerce/products/?per_page=50&page=1
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 2045,
      "name": "Camiseta Básica",
      "price": "50000.00",
      "images": [...]
    }
  ]
}
```

### 2. **Agregar al Carrito**

```bash
POST /api/cart/add-product/
{
  "woocommerce_product_id": 2045,
  "quantity": 2
}
```

**Lo que pasa:**
- Se guarda en `CartItem`:
  - `woocommerce_product_id` = 2045
  - `product_name` = "Camiseta Básica" (snapshot)
  - `unit_price` = 50000.00 (snapshot)
  - `product_image` = URL (snapshot)

### 3. **Crear Orden**

```bash
POST /api/orders/create/
{
  "shipping_address": "Carrera 80 #50-25 Apto 301",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050031",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "notes": "Por favor llamar antes de entregar"
}
```

**Lo que pasa internamente:**

#### A. Se crea orden local:
```python
Order(
  user=usuario_actual,
  email="user@email.com",
  name="Juan Pérez",
  address_line_1="Carrera 80 #50-25 Apto 301",
  city="Medellín",
  state="Antioquia",
  zipcode="050031",
  country="CO",
  phone="+57 300 1234567"
)
```

#### B. Se crean OrderItems:
```python
OrderItem(
  woocommerce_product_id=2045,
  product_name="Camiseta Básica",  # snapshot histórico
  quantity=2,
  unit_price=50000.00
)
```

#### C. Se envía a WooCommerce automáticamente:

**Parseo de dirección colombiana:**
```
Input:  "Carrera 80 #50-25 Apto 301"
Output: {
  "type_address": "Carrera",
  "street_1": "80",
  "street_2": "50",
  "street_3": "25",
  "unit_number": "301",
  "type_property": "Apartamento"
}
```

**Payload a WooCommerce:**
```json
{
  "customer_id": 659,
  "status": "on-hold",
  "billing": {
    "first_name": "CRUSHME",
    "last_name": "Store",
    "company": "ITTESAS",
    "address_1": "Calle Principal",
    "city": "Medellín",
    "state": "ANT",
    "country": "CO",
    "email": "tienda@crushme.com",
    "phone": "1234567891"
  },
  "shipping": {
    "first_name": "Juan",
    "last_name": "Pérez",
    "address_1": "Carrera 80 #50-25 Apto 301",
    "city": "Medellín",
    "state": "ANT",
    "postcode": "050031",
    "country": "CO",
    "phone": "+57 300 1234567"
  },
  "line_items": [
    {
      "product_id": 2045,
      "quantity": 2
    }
  ],
  "meta_data": [
    {"key": "shipping_neighborhood", "value": "Medellín"},
    {"key": "shipping_street_1", "value": "80"},
    {"key": "shipping_street_2", "value": "50"},
    {"key": "shipping_street_3", "value": "25"},
    {"key": "shipping_type_address", "value": "Carrera"},
    {"key": "shipping_type_property", "value": "Apartamento"},
    {"key": "shipping_unit_number", "value": "301"}
  ]
}
```

#### D. Respuesta al Frontend:
```json
{
  "message": "Order created successfully",
  "order": {
    "id": 45,
    "order_number": "ORD123456ABCD1234",
    "status": "pending",
    "total": "100000.00",
    "shipping_address": "Carrera 80 #50-25 Apto 301",
    "shipping_city": "Medellín"
  },
  "woocommerce_integration": {
    "sent": true,
    "woocommerce_order_id": 8765,
    "woocommerce_order_number": "8765"
  }
}
```

---

## 🔧 Componentes Implementados

### 1. **ColombianAddressParser** (Parser de Direcciones)

```python
# Ejemplo de uso:
address = "Carrera 80 #50-25 Apto 301"
parsed = ColombianAddressParser.parse(address)

# Resultado:
{
  'type_address': 'Carrera',
  'street_1': '80',
  'street_2': '50',
  'street_3': '25',
  'unit_number': '301',
  'type_property': 'Apartamento'
}
```

**Soporta:**
- ✅ Carrera, Calle, Avenida, Transversal, Diagonal, etc.
- ✅ Formatos: "Carrera 80 #50-25", "Calle 10 # 20-30"
- ✅ Tipos de propiedad: Apartamento, Casa, Local, Oficina
- ✅ Números de unidad: Apto 301, Casa 5, Local 102

### 2. **WooCommerceOrderService** (Servicio de Envío)

**Archivo:** `crushme_app/services/woocommerce_order_service.py`

**Métodos principales:**
- `send_order(order)`: Envía orden a WooCommerce
- `_build_order_payload(order)`: Construye el JSON para WooCommerce
- `_build_colombian_metadata(order)`: Genera metadata colombiana
- `_get_state_code(state_name)`: Convierte nombres a códigos (Antioquia → ANT)

### 3. **OrderCreateSerializer** (Serializer Corregido)

**Cambios realizados:**
- ✅ Eliminada validación de stock local (no existen productos locales)
- ✅ Usa `woocommerce_product_id` de `CartItem`
- ✅ Mapea campos API → campos de modelo
- ✅ Extrae email y nombre del usuario autenticado

### 4. **OrderItemSerializer** (Serializer Corregido)

**Cambios realizados:**
- ✅ No usa ForeignKey a `Product` local
- ✅ Usa `woocommerce_product_id` directamente
- ✅ Genera objeto `product` desde datos guardados (snapshot histórico)

---

## 🌎 Soporte Multi-País

### Colombia (CO)
- **Parseo automático** de direcciones
- **Metadata completa** con campos colombianos
- **Códigos de departamento** (Antioquia → ANT)

### Otros Países
- **Dirección simple** (se envía tal cual)
- **Sin metadata adicional**
- **Compatible** con formato estándar WooCommerce

---

## ⚙️ Configuración Requerida

### settings.py
```python
WOOCOMMERCE_CONSUMER_KEY = 'ck_xxxxxxxxxxxxxxxxxxxx'
WOOCOMMERCE_CONSUMER_SECRET = 'cs_xxxxxxxxxxxxxxxxxxxx'
WOOCOMMERCE_API_URL = 'https://desarrollo.distrisex.com/wp-json/wc/v3'
```

### Customer ID Fijo
```python
# En woocommerce_order_service.py
STORE_CUSTOMER_ID = 659  # Tu ID de tienda en WooCommerce
```

---

## 🧪 Ejemplos de Prueba

### Ejemplo 1: Dirección Colombiana Simple
```json
{
  "shipping_address": "Calle 50 #45-23",
  "shipping_city": "Bogotá",
  "shipping_state": "Cundinamarca",
  "shipping_postal_code": "110111",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567"
}
```

**Resultado parseado:**
- Tipo: Calle
- Calle 1: 50
- Calle 2: 45
- Calle 3: 23
- Propiedad: Casa (default)

### Ejemplo 2: Dirección con Apartamento
```json
{
  "shipping_address": "Avenida 68 #25-30 Apto 502",
  "shipping_city": "Cali",
  "shipping_state": "Valle del Cauca",
  "shipping_postal_code": "760001",
  "shipping_country": "CO",
  "phone_number": "+57 300 9876543"
}
```

**Resultado parseado:**
- Tipo: Avenida
- Calle 1: 68
- Calle 2: 25
- Calle 3: 30
- Propiedad: Apartamento
- Unidad: 502

### Ejemplo 3: País No Colombiano
```json
{
  "shipping_address": "123 Main Street, Apt 4B",
  "shipping_city": "New York",
  "shipping_state": "NY",
  "shipping_postal_code": "10001",
  "shipping_country": "US",
  "phone_number": "+1 555 1234567"
}
```

**Resultado:** Se envía sin metadata adicional, formato estándar WooCommerce.

---

## 📝 Registro de Logs

El sistema genera logs detallados:

```
✅ Order ORD123456ABCD1234 created locally
✅ Products loaded from cache: woocommerce_products_all_50_1
✅ Order ORD123456ABCD1234 sent to WooCommerce successfully
```

En caso de error:
```
❌ Order ORD123456ABCD1234 created locally but failed to send to WooCommerce: Connection timeout
```

---

## 🔄 Manejo de Errores

### Si WooCommerce falla:
1. **Orden se guarda localmente** ✅
2. **Usuario recibe orden creada**
3. **Se registra error en logs**
4. **Respuesta incluye**: `"woocommerce_integration": {"sent": false, "error": "..."}`

### Puede reintentarse manualmente:
```python
from crushme_app.services.woocommerce_order_service import woocommerce_order_service

order = Order.objects.get(order_number='ORD123456ABCD1234')
result = woocommerce_order_service.send_order(order)
```

---

## ✅ Ventajas de esta Implementación

1. ✅ **Frontend no cambia**: Mantiene estructura simple
2. ✅ **Backend inteligente**: Hace el trabajo pesado
3. ✅ **Multi-país**: Soporta Colombia con detalle y otros países simples
4. ✅ **Robusto**: Si WooCommerce falla, orden se guarda localmente
5. ✅ **Histórico preservado**: OrderItems guardan snapshot del momento de compra
6. ✅ **Extensible**: Fácil agregar parsers para otros países
7. ✅ **Sin migración frontend**: No rompe experiencia de usuario

---

## 🚀 Próximos Pasos Sugeridos

1. **Agregar campo `woocommerce_order_id` al modelo `Order`** para guardar la referencia
2. **Webhook de WooCommerce** para actualizar estados desde WooCommerce → Django
3. **Retry automático** si WooCommerce falla (cola de tareas con Celery)
4. **Enriquecer OrderItem** con imagen del producto desde WooCommerce
5. **Panel admin** para reenviar órdenes fallidas

---

**Fecha de implementación:** Octubre 3, 2025  
**Versión:** 1.0

