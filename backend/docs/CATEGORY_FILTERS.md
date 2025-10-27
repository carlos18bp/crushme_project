# Filtros de Categorías - Sin Productos/Imágenes

## Resumen

Los endpoints de categorías han sido actualizados para **filtrar automáticamente** categorías que no tienen productos o imágenes, mejorando la experiencia del usuario.

## Cambios Realizados

### 1. Endpoint de Categorías Random con Imagen

**Endpoints actualizados:**
- `GET /api/products/woocommerce/categories/featured-random/` (optimizado - local DB)
- `GET /api/products/woocommerce/legacy/categories/featured-random/` (legacy - WooCommerce API)

**Comportamiento anterior:**
- Seleccionaba 4 categorías aleatorias
- Retornaba categorías incluso si no tenían imagen del primer producto
- Podía mostrar categorías vacías

**Comportamiento nuevo:**
```python
# Mezclar aleatoriamente todas las categorías
shuffled_themes = main_themes.copy()
random.shuffle(shuffled_themes)

featured_categories = []

# Intentar obtener 4 categorías con imagen
for theme in shuffled_themes:
    # Si ya tenemos 4, detener
    if len(featured_categories) >= 4:
        break
    
    # Obtener primer producto de la categoría con imagen
    first_product = WooCommerceProduct.objects.filter(
        categories__wc_id=theme['category_id'],
        status='publish'
    ).prefetch_related('images').first()
    
    # Verificar que el producto tenga imagen
    first_product_image = None
    if first_product and first_product.images.exists():
        first_product_image = first_product.images.first().src
    
    # Solo agregar si tiene imagen
    if first_product_image:
        featured_categories.append({...})
```

**Características:**
- ✅ Mezcla todas las categorías aleatoriamente
- ✅ Solo retorna categorías que tienen productos con imágenes
- ✅ Si una categoría no tiene imagen, la salta y continúa con la siguiente
- ✅ Puede retornar menos de 4 categorías si no hay suficientes con imagen
- ✅ Mensaje dinámico: `"{N} categorías destacadas obtenidas exitosamente"`

### 2. Endpoint de Categorías Organizadas

**Endpoints actualizados:**
- `GET /api/products/woocommerce/categories/organized/` (optimizado - local DB)
- `GET /api/products/woocommerce/legacy/categories/organized/` (legacy - WooCommerce API)

**Comportamiento anterior:**
- Retornaba todas las categorías configuradas
- Incluía categorías sin productos (`count: 0`)
- Incluía subcategorías vacías

**Comportamiento nuevo:**

**Versión optimizada (local DB):**
```python
for cat_id in all_category_ids:
    if cat_id in category_map:
        cat = category_map[cat_id]
        
        # Filtrar categorías sin productos
        if cat.product_count == 0:
            continue
        
        # Buscar subcategorías (solo las que tienen productos)
        subcategories = []
        for sub in all_categories:
            if sub.wc_parent_id == cat_id and sub.product_count > 0:
                subcategories.append({...})
        
        theme_data['categories'].append({...})
```

**Versión legacy (WooCommerce API):**
```python
for cat_id in all_category_ids:
    if cat_id in category_map:
        cat = category_map[cat_id]
        
        # Filtrar categorías sin productos
        if cat.get('count', 0) == 0:
            continue
        
        # Buscar subcategorías (solo las que tienen productos)
        subcategories = [
            {...}
            for sub in categories 
            if sub['parent'] == cat_id and sub.get('count', 0) > 0
        ]
        
        theme_data['categories'].append({...})
```

**Características:**
- ✅ Solo retorna categorías con `product_count > 0`
- ✅ Solo retorna subcategorías con `product_count > 0`
- ✅ Mantiene la estructura de temas
- ✅ Los totales se calculan solo con categorías válidas

## Ejemplos de Respuesta

### Categorías Random (antes)

```json
{
  "success": true,
  "message": "4 categorías destacadas obtenidas exitosamente",
  "data": [
    {
      "name": "Juguetes",
      "slug": "juguetes",
      "icon": "🎮",
      "category_id": 134,
      "first_product_image": "https://..."
    },
    {
      "name": "Bondage",
      "slug": "bondage",
      "icon": "⛓️",
      "category_id": 137,
      "first_product_image": null  // ❌ Sin imagen
    },
    {
      "name": "Lencería",
      "slug": "lenceria",
      "icon": "👗",
      "category_id": 246,
      "first_product_image": "https://..."
    },
    {
      "name": "Ofertas",
      "slug": "ofertas",
      "icon": "💰",
      "category_id": 695,
      "first_product_image": null  // ❌ Sin imagen
    }
  ],
  "total_selected": 4
}
```

### Categorías Random (después)

```json
{
  "success": true,
  "message": "3 categorías destacadas obtenidas exitosamente",
  "data": [
    {
      "name": "Juguetes",
      "slug": "juguetes",
      "icon": "🎮",
      "category_id": 134,
      "first_product_image": "https://..."  // ✅ Con imagen
    },
    {
      "name": "Lencería",
      "slug": "lenceria",
      "icon": "👗",
      "category_id": 246,
      "first_product_image": "https://..."  // ✅ Con imagen
    },
    {
      "name": "Lubricantes",
      "slug": "lubricantes",
      "icon": "💧",
      "category_id": 136,
      "first_product_image": "https://..."  // ✅ Con imagen
    }
  ],
  "total_selected": 3  // ✅ Solo 3 porque las demás no tenían imagen
}
```

### Categorías Organizadas (antes)

```json
{
  "success": true,
  "data": [
    {
      "theme": "juguetes",
      "name": "Juguetes",
      "total_products": 150,
      "categories": [
        {
          "id": 134,
          "name": "Juguetes",
          "count": 120
        },
        {
          "id": 223,
          "name": "Categoría Vacía",
          "count": 0  // ❌ Sin productos
        },
        {
          "id": 329,
          "name": "Vibradores",
          "count": 30
        }
      ]
    }
  ]
}
```

### Categorías Organizadas (después)

```json
{
  "success": true,
  "data": [
    {
      "theme": "juguetes",
      "name": "Juguetes",
      "total_products": 150,
      "categories": [
        {
          "id": 134,
          "name": "Juguetes",
          "count": 120  // ✅ Con productos
        },
        {
          "id": 329,
          "name": "Vibradores",
          "count": 30  // ✅ Con productos
        }
        // ✅ Categoría vacía (223) fue filtrada
      ]
    }
  ]
}
```

## Beneficios

### Para el Usuario
- ✅ No ve categorías vacías
- ✅ Todas las categorías mostradas tienen contenido
- ✅ Mejor experiencia visual (todas con imagen)
- ✅ Menos confusión al navegar

### Para el Sistema
- ✅ Menos datos innecesarios en la respuesta
- ✅ Mejor performance (menos categorías a procesar)
- ✅ Respuestas más limpias
- ✅ Frontend no necesita filtrar

## Casos de Uso

### Caso 1: Categoría sin productos
**Antes:** Se mostraba en la lista con `count: 0`  
**Después:** Se filtra automáticamente, no aparece en la respuesta

### Caso 2: Categoría sin imagen del primer producto
**Antes:** Se mostraba con `first_product_image: null`  
**Después:** Se salta y se busca la siguiente categoría con imagen

### Caso 3: Subcategoría vacía
**Antes:** Aparecía en `subcategories` con `count: 0`  
**Después:** Se filtra, solo aparecen subcategorías con productos

### Caso 4: Menos de 4 categorías con imagen
**Antes:** Retornaba 4 categorías, algunas sin imagen  
**Después:** Retorna solo las que tienen imagen (puede ser 1, 2, 3 o 4)

## Testing

### Test 1: Categorías Random
```bash
curl http://localhost:8000/api/products/woocommerce/categories/featured-random/
```

**Verificar:**
- Todas las categorías tienen `first_product_image` con URL válida
- `total_selected` puede ser <= 4
- Ninguna categoría tiene `first_product_image: null`

### Test 2: Categorías Organizadas
```bash
curl http://localhost:8000/api/products/woocommerce/categories/organized/
```

**Verificar:**
- Todas las categorías tienen `count > 0`
- Todas las subcategorías tienen `count > 0`
- No hay categorías con `count: 0`

### Test 3: Con diferentes idiomas
```bash
curl -H "Accept-Language: en" \
  http://localhost:8000/api/products/woocommerce/categories/featured-random/
```

**Verificar:**
- Los filtros funcionan igual en todos los idiomas
- Las traducciones se aplican correctamente

## Archivos Modificados

1. **crushme_app/views/woocommerce_local_views.py**
   - `get_random_featured_categories_local()` - Líneas 1190-1273
   - `get_organized_categories_local()` - Líneas 987-1136

2. **crushme_app/views/category_views.py**
   - `get_random_featured_categories()` - Líneas 447-528
   - `organize_categories_by_theme()` - Líneas 90-204

## Notas Importantes

- ⚠️ El endpoint de categorías random puede retornar menos de 4 categorías si no hay suficientes con imagen
- ⚠️ Los totales (`total_products`, `total_categories`) se calculan solo con categorías válidas
- ⚠️ El filtrado se aplica tanto a categorías principales como a subcategorías
- ✅ Los filtros funcionan en ambas versiones: optimizada (local DB) y legacy (WooCommerce API)
- ✅ Compatible con el sistema de traducción multi-idioma
- ✅ Compatible con el sistema de conversión de currency

## Fecha de Implementación

27 de octubre de 2025
