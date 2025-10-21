# 📦 Gestión de Stock

## Resumen

El sistema tiene un **enfoque híbrido** para la gestión de stock:
- 🚀 **Lista de productos**: Stock local (rápido)
- ✅ **Detalle del producto**: Stock en tiempo real desde WooCommerce (preciso)
- 🛒 **Agregar al carrito**: Stock en tiempo real (crítico - a implementar)

---

## 1. Lista de Productos (Rápido)

### Endpoint:
```
GET /api/products/woocommerce/products/
GET /api/products/woocommerce/products/?category_id=134
```

### Comportamiento:
- ✅ **Stock desde DB local** (sincronizado cada 6 horas)
- ⚡ **Ultra rápido**: 50-150ms
- 📊 **Incluye**:
  - `stock_status`: "instock" / "outofstock"
  - `in_stock`: true / false

### Ejemplo de respuesta:
```json
{
  "success": true,
  "data": [
    {
      "id": 82257,
      "name": "Massage oil Coco Tropical Erotic",
      "price": 8490.0,
      "image": "https://...",
      "stock_status": "instock",
      "in_stock": true
    }
  ],
  "source": "local_db"
}
```

### ¿Cuándo usar?
- ✅ Listados de productos
- ✅ Búsquedas
- ✅ Categorías
- ✅ Productos en tendencia

---

## 2. Detalle de Producto (Preciso)

### Endpoint:
```
GET /api/products/woocommerce/products/{product_id}/
```

### Comportamiento:
- ✅ **Stock en tiempo real desde WooCommerce** (por defecto)
- ⚡ **Velocidad**: 300-800ms
- 📊 **Incluye**:
  - `stock_status`: Estado actual
  - `stock_quantity`: Cantidad exacta
  - `manage_stock`: Si maneja inventario
  - `in_stock`: Disponibilidad
  - `real_time_stock`: Indicador de origen

### Ejemplo de respuesta:
```json
{
  "success": true,
  "data": {
    "id": 82257,
    "name": "Massage oil Coco Tropical Erotic",
    "price": 8490.0,
    "stock_status": "instock",
    "stock_quantity": 15,
    "manage_stock": true,
    "in_stock": true,
    "real_time_stock": true
  },
  "source": "local_db_with_realtime_stock"
}
```

### Parámetros opcionales:
```
?real_time_stock=false  # Usar stock local (más rápido pero puede estar desactualizado)
?real_time_stock=true   # Usar stock real (por defecto)
```

### ¿Cuándo usar?
- ✅ Vista de detalle del producto
- ✅ Antes de mostrar el botón "Agregar al carrito"
- ✅ Cuando el usuario está considerando la compra

---

## 3. Agregar al Carrito (Crítico) 🚧

### Endpoint (a implementar):
```
POST /api/cart/add/
```

### Comportamiento recomendado:
- ✅ **SIEMPRE verificar stock real antes de agregar**
- ❌ **NO confiar en datos locales**
- ✅ **Validar cantidad disponible**
- ✅ **Retornar error si no hay stock**

### Flujo sugerido:
```python
def add_to_cart(request):
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    # 1. Consultar stock REAL de WooCommerce
    stock_result = woocommerce_service.get_product_by_id(
        product_id,
        fields='id,stock_status,stock_quantity,manage_stock'
    )
    
    # 2. Validar disponibilidad
    if not stock_result['success']:
        return Error('No se pudo verificar disponibilidad')
    
    stock_data = stock_result['data']
    if stock_data['stock_status'] != 'instock':
        return Error('Producto sin stock')
    
    if stock_data['manage_stock']:
        if stock_data['stock_quantity'] < quantity:
            return Error(f'Solo hay {stock_data["stock_quantity"]} unidades disponibles')
    
    # 3. Agregar al carrito
    # ...
```

---

## 4. Sincronización de Stock

### Frecuencia actual:
- ⏰ **Cada 6 horas** (configurable via cron)
- 🔄 **Manual**: `python manage.py sync_woocommerce`

### Comando:
```bash
# Sincronización completa (productos, categorías, variaciones)
./venv/bin/python manage.py sync_woocommerce --full

# Solo actualizar stock (más rápido)
./venv/bin/python manage.py sync_woocommerce --stock-only
```

### Configurar cron (recomendado):
```bash
# Cada 6 horas
0 */6 * * * cd /path/to/backend && ./venv/bin/python manage.py sync_woocommerce
```

---

## 5. Estrategias por Caso de Uso

### Caso A: E-commerce de alto volumen
```
- Lista: Stock local
- Detalle: Stock local
- Carrito: Stock real (validación crítica)
- Checkout: Stock real (doble validación)
```

### Caso B: Inventario dinámico (recomendado para tu caso)
```
- Lista: Stock local
- Detalle: Stock real ✅ (implementado)
- Carrito: Stock real ✅ (pendiente)
- Checkout: Stock real ✅ (pendiente)
```

### Caso C: Máxima precisión (más lento)
```
- Lista: Stock real (añade 500ms-1s por request)
- Detalle: Stock real
- Carrito: Stock real
- Checkout: Stock real
```

---

## 6. Ventajas y Desventajas

### Stock Local (DB)
**Ventajas:**
- ⚡ Ultra rápido (50-150ms)
- 🔋 No sobrecarga WooCommerce API
- 💰 No consume límite de API

**Desventajas:**
- ⏰ Puede estar desactualizado (hasta 6 horas)
- ❌ Riesgo de mostrar productos sin stock

### Stock en Tiempo Real (WooCommerce API)
**Ventajas:**
- ✅ Siempre actualizado
- ✅ 100% preciso
- ✅ Previene sobreventas

**Desventajas:**
- 🐌 Más lento (300-800ms por producto)
- 📉 Consume límite de API
- ⚠️ Depende de disponibilidad de WooCommerce

---

## 7. Configuración Actual

### Endpoints Optimizados:

| Endpoint | Stock | Velocidad | Uso |
|----------|-------|-----------|-----|
| `/products/` | Local | 50-150ms | Lista |
| `/products/{id}/` | **Real** ✅ | 300-800ms | Detalle |
| `/products/trending/` | Local | 50-150ms | Trending |
| `/categories/` | Local | 30-80ms | Categorías |

### Modificar comportamiento:

```bash
# Detalle con stock LOCAL (más rápido)
curl "http://localhost:8000/api/products/woocommerce/products/82257/?real_time_stock=false"

# Detalle con stock REAL (por defecto)
curl "http://localhost:8000/api/products/woocommerce/products/82257/?real_time_stock=true"
```

---

## 8. Próximos Pasos (Recomendaciones)

### Corto plazo:
1. ✅ **Implementado**: Detalle de producto con stock real
2. 🔄 **Pendiente**: Validación de stock al agregar al carrito
3. 🔄 **Pendiente**: Validación de stock en checkout

### Mediano plazo:
4. 📊 **Implementar**: Cache de stock por 5-10 minutos (Redis)
5. 🔔 **Implementar**: Webhooks de WooCommerce para actualización instantánea
6. 📈 **Implementar**: Logs de consultas de stock para análisis

### Largo plazo:
7. 🚀 **Optimizar**: Sistema de reserva temporal de stock durante checkout
8. 🤖 **Automatizar**: Alertas cuando productos están por agotarse
9. 📊 **Analytics**: Dashboard de movimiento de stock

---

## 9. Testing

### Test 1: Verificar stock local en lista
```bash
curl "http://localhost:8000/api/products/woocommerce/products/?per_page=1" | jq '.data[0].stock_status'
```

### Test 2: Verificar stock real en detalle
```bash
curl "http://localhost:8000/api/products/woocommerce/products/82257/" | jq '.data.real_time_stock'
# Debe retornar: true
```

### Test 3: Comparar velocidad
```bash
# Stock local
time curl "http://localhost:8000/api/products/woocommerce/products/82257/?real_time_stock=false"

# Stock real
time curl "http://localhost:8000/api/products/woocommerce/products/82257/?real_time_stock=true"
```

---

## 10. Troubleshooting

### Problema: Stock siempre muestra "outofstock"
**Solución**: Sincronizar datos
```bash
./venv/bin/python manage.py sync_woocommerce --full
```

### Problema: Stock real es muy lento
**Solución**: Usar stock local en listas, real solo en detalle (ya configurado)

### Problema: WooCommerce API rate limit
**Solución**: Reducir consultas de stock real, usar más cache local

---

## Resumen de Configuración Actual

✅ **Lista de productos**: Stock local (rápido)  
✅ **Detalle de producto**: Stock real (preciso) - **POR DEFECTO**  
🔄 **Agregar al carrito**: Pendiente implementar validación real  
🔄 **Checkout**: Pendiente implementar validación real  

**El sistema está optimizado para balance entre velocidad y precisión! 🎯**
