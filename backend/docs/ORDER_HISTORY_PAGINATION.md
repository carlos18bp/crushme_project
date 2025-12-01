# 📄 Order History Pagination - Documentación

## 📍 Endpoint

```
GET /api/orders/history/
```

## 🔐 Autenticación

Requiere autenticación (token JWT en header `Authorization: Bearer <token>`)

## 📊 Query Parameters

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Número de página a consultar |
| `page_size` | integer | 10 | Cantidad de órdenes por página |
| `include_gifts` | boolean | true | Incluir órdenes de regalo |
| `lang` | string | es | Idioma de respuesta (es/en) |

**Headers:**
- `X-Currency`: COP o USD (para conversión de precios)
- `Accept-Language`: es o en (para traducciones)

## 📦 Respuesta

```json
{
  "purchases": [
    {
      "id": 1,
      "order_number": "ORD498501HIGGYFEP",
      "status": "processing",
      "status_display": "Processing",
      "total": 100.00,
      "total_items": 2,
      "items": [
        {
          "id": 1,
          "woocommerce_product_id": 123,
          "woocommerce_variation_id": null,
          "quantity": 1,
          "unit_price": 50.00,
          "subtotal": 50.00,
          "product_name": "Producto X",
          "product_description": "Descripción",
          "product_image": "https://...",
          "created_at": "2024-11-30T..."
        }
      ],
      "email": "user@example.com",
      "name": "John Doe",
      "shipping_address": "Calle 123",
      "shipping_city": "Bogotá",
      "shipping_state": "Cundinamarca",
      "shipping_postal_code": "110111",
      "shipping_country": "CO",
      "phone_number": "+57 300 1234567",
      "full_shipping_address": "Calle 123, Bogotá, Cundinamarca, 110111, CO",
      "notes": "",
      "gift_message": "",
      "woocommerce_order_id": null,
      "is_gift": false,
      "sender_username": null,
      "receiver_username": null,
      "gift_summary": null,
      "created_at": "2024-11-30T23:45:51Z",
      "updated_at": "2024-11-30T23:45:51Z",
      "shipped_at": null,
      "delivered_at": null
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_purchases": 25,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  },
  "user_stats": {
    "total_purchases": 25,
    "regular_purchases": 20,
    "gift_purchases": 5,
    "sent_gifts_count": 3,
    "received_gifts_count": 2,
    "total_spent": 2500000.0
  },
  "currency": "COP"
}
```

## 🎯 Ejemplos de Uso

### 1. Primera página (default)
```bash
GET /api/orders/history/?lang=es
# Retorna: órdenes 1-10
```

### 2. Segunda página
```bash
GET /api/orders/history/?page=2&lang=es
# Retorna: órdenes 11-20
```

### 3. Página específica con tamaño personalizado
```bash
GET /api/orders/history/?page=1&page_size=20&lang=es
# Retorna: órdenes 1-20
```

### 4. Solo compras regulares (sin regalos)
```bash
GET /api/orders/history/?include_gifts=false&lang=es
# Retorna: solo órdenes que NO son regalos
```

### 5. Con conversión a USD
```bash
GET /api/orders/history/?page=1&lang=en
Headers: X-Currency: USD
# Retorna: precios convertidos a USD
```

## 🔍 Campos de Paginación

### `pagination.current_page`
Número de la página actual solicitada.

### `pagination.page_size`
Cantidad de órdenes por página (default: 10).

### `pagination.total_purchases`
Total de órdenes del usuario (según filtros aplicados).

### `pagination.total_pages`
Cantidad total de páginas disponibles.

### `pagination.has_next`
`true` si existe una página siguiente, `false` si es la última.

### `pagination.has_previous`
`true` si existe una página anterior, `false` si es la primera.

## 🚫 Filtros Aplicados

### Producto Dropshipping (ID 48500)
El producto de dropshipping (ID 48500) **NO se muestra** en el historial de órdenes.
Es un producto interno usado para cargos adicionales y no debe ser visible para los clientes.

### Precios Históricos
Los precios mostrados son los **precios al momento de compra**, no los precios actuales del producto.
Esto garantiza que el historial refleje exactamente lo que el usuario pagó.

## ⚡ Performance

- **Tiempo de respuesta:** < 100ms
- **Queries a DB:** 2-3 queries optimizadas
- **Llamadas a WooCommerce API:** 0 (usa DB local)
- **Imágenes:** Cargadas desde DB local sincronizada

## 📱 Implementación Frontend

### JavaScript/Fetch
```javascript
async function fetchOrderHistory(page = 1) {
  const response = await fetch(
    `/api/orders/history/?page=${page}&lang=es`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'X-Currency': 'COP'
      }
    }
  );
  
  const data = await response.json();
  
  console.log('Órdenes:', data.purchases);
  console.log('Página actual:', data.pagination.current_page);
  console.log('Total de páginas:', data.pagination.total_pages);
  console.log('¿Hay siguiente?', data.pagination.has_next);
  
  return data;
}

// Uso
const page1 = await fetchOrderHistory(1); // Primera página
const page2 = await fetchOrderHistory(2); // Segunda página
```

### Vue.js/Axios
```javascript
import { ref } from 'vue';
import { get_request } from '@/services/request_http';

const orders = ref([]);
const pagination = ref({});
const currentPage = ref(1);

async function loadOrders(page = 1) {
  try {
    const response = await get_request(
      `orders/history/?page=${page}&lang=es`
    );
    
    orders.value = response.data.purchases;
    pagination.value = response.data.pagination;
    currentPage.value = page;
  } catch (error) {
    console.error('Error loading orders:', error);
  }
}

// Navegación
function nextPage() {
  if (pagination.value.has_next) {
    loadOrders(currentPage.value + 1);
  }
}

function previousPage() {
  if (pagination.value.has_previous) {
    loadOrders(currentPage.value - 1);
  }
}
```

## 🎨 UI Components Sugeridos

### Paginador Simple
```vue
<template>
  <div class="pagination">
    <button 
      @click="previousPage" 
      :disabled="!pagination.has_previous"
    >
      ← Anterior
    </button>
    
    <span>
      Página {{ pagination.current_page }} de {{ pagination.total_pages }}
    </span>
    
    <button 
      @click="nextPage" 
      :disabled="!pagination.has_next"
    >
      Siguiente →
    </button>
  </div>
</template>
```

### Paginador con Números
```vue
<template>
  <div class="pagination">
    <button 
      v-for="page in totalPages" 
      :key="page"
      @click="loadOrders(page)"
      :class="{ active: page === currentPage }"
    >
      {{ page }}
    </button>
  </div>
</template>
```

### Infinite Scroll
```javascript
function setupInfiniteScroll() {
  window.addEventListener('scroll', async () => {
    const bottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
    
    if (bottom && pagination.value.has_next && !loading.value) {
      loading.value = true;
      const nextPage = pagination.value.current_page + 1;
      const response = await loadOrders(nextPage);
      
      // Agregar nuevas órdenes al array existente
      orders.value.push(...response.purchases);
      loading.value = false;
    }
  });
}
```

## 🔧 Configuración

### Cambiar tamaño de página default
Si quieres cambiar el default de 10 órdenes por página:

```python
# En order_views.py línea 459
page_size = int(request.GET.get('page_size', 20))  # Cambiar a 20
```

### Límite máximo de page_size
Para evitar requests muy grandes, puedes agregar un límite:

```python
page_size = min(int(request.GET.get('page_size', 10)), 50)  # Máximo 50
```

## 📊 Estadísticas del Usuario

El endpoint también retorna estadísticas generales del usuario:

- `total_purchases`: Total de compras realizadas
- `regular_purchases`: Compras regulares (no regalos)
- `gift_purchases`: Compras que son regalos
- `sent_gifts_count`: Regalos enviados
- `received_gifts_count`: Regalos recibidos
- `total_spent`: Total gastado (convertido según currency)

## ✅ Ventajas de esta Implementación

1. **Performance:** Solo carga 10 órdenes a la vez
2. **Escalabilidad:** Funciona igual con 10 o 10,000 órdenes
3. **Flexible:** Frontend controla page y page_size
4. **Completo:** Incluye toda la info de paginación necesaria
5. **Rápido:** < 100ms por request
6. **Sin API calls:** Todo desde DB local

## 🐛 Troubleshooting

### Página vacía
Si una página retorna vacía pero `total_pages > current_page`:
- Verificar que `page` sea >= 1
- Verificar que `page` <= `total_pages`

### Órdenes duplicadas
Si ves órdenes duplicadas al navegar:
- Asegúrate de reemplazar el array, no agregarlo
- Usa `orders.value = response.purchases` no `orders.value.push(...)`

### Precios incorrectos
Si los precios no se convierten:
- Verificar header `X-Currency` en el request
- Verificar que el middleware `CurrencyMiddleware` esté activo
