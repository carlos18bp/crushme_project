# 🎯 Próximos Pasos - Sistema WooCommerce Optimizado

## ✅ Lo que YA está funcionando

1. ✅ **Sincronización de WooCommerce** → Base de datos local (corriendo ahora)
2. ✅ **Modelos creados**: Productos, Categorías, Variaciones, Imágenes
3. ✅ **Modelos de traducciones**: Cache pre-calculado listo
4. ✅ **Modelos de precios**: Márgenes por categoría configurables
5. ✅ **Comandos Django**: sync_woocommerce, translate_content
6. ✅ **Admin registrado**: Todos los modelos visibles en el admin
7. ✅ **Helpers**: Funciones utilitarias para usar en las vistas

---

## 🚀 PASO 1: Esperar que termine la sincronización actual

**Estado**: Corriendo en background

```bash
# Ver progreso (si hay logs)
tail -f /path/to/logs/sync.log

# O revisar en el admin:
# Admin → Product Sync Logs → Ver último registro
```

**Tiempo estimado**: Depende del número de productos (puede ser 20-60 min)

---

## 🌐 PASO 2: Ejecutar traducción de contenido

Una vez que termine la sincronización:

```bash
# Traducir todo el contenido sincronizado
cd /home/cerrotico/work/crushme_project/backend
./venv/bin/python manage.py translate_content
```

**⚠️ IMPORTANTE sobre la traducción**:
- **Primera vez será lenta** (puede tomar 30-90 min dependiendo de cantidad de productos)
- La traducción se hace producto por producto para mantener calidad
- Descripciones >5000 caracteres se omiten (puedes ajustar esto)
- Se traduce: nombres, descripciones cortas, descripciones completas, categorías

**Optimizaciones si es muy lento**:
- Ejecutar en horario de bajo tráfico
- Usar `screen` o `tmux` para que siga ejecutándose en background
- Reducir cantidad de campos a traducir (editar `translation_batch_service.py`)

---

## 💰 PASO 3: Configurar márgenes de precio

### Vía Admin (Recomendado)

1. **Ir al admin**: http://tu-dominio/admin
2. **Navegar a**: `Category Price Margins` → `Add`
3. **Para cada categoría importante**:
   - Seleccionar categoría
   - Elegir:
     - **Opción A**: Margen porcentual (ej: 25% → `margin_percentage = 25.00`)
     - **Opción B**: Multiplicador fijo (ej: x1.25 → `use_fixed_multiplier = True`, `fixed_multiplier = 1.25`)
   - Activar (`is_active = True`)
   - Guardar

4. **Configurar margen por defecto**:
   - `Default Price Margins` → `Add`
   - Configurar margen para productos sin categoría específica
   - **Solo debe haber uno activo**

### Vía código (para setup rápido)

```python
# Script para configurar márgenes
from crushme_app.models import WooCommerceCategory, CategoryPriceMargin, DefaultPriceMargin

# Margen por defecto: 20%
DefaultPriceMargin.objects.create(
    margin_percentage=20.00,
    is_active=True,
    notes="Margen por defecto para todos los productos"
)

# Ejemplos de márgenes por categoría
categories_margins = {
    'Electrónica': 15.00,
    'Ropa': 30.00,
    'Accesorios': 35.00,
    'Hogar': 25.00,
}

for cat_name, margin in categories_margins.items():
    try:
        category = WooCommerceCategory.objects.get(name__icontains=cat_name)
        CategoryPriceMargin.objects.create(
            category=category,
            margin_percentage=margin,
            is_active=True
        )
        print(f"✅ Margen {margin}% configurado para {category.name}")
    except WooCommerceCategory.DoesNotExist:
        print(f"⚠️  Categoría '{cat_name}' no encontrada")
```

---

## 🔄 PASO 4: Actualizar las vistas para usar datos locales

### Ejemplo: Vista de productos

**ANTES** (lento - consulta directa a WooCommerce):
```python
from crushme_app.services.woocommerce_service import woocommerce_service

@api_view(['GET'])
def get_products(request):
    result = woocommerce_service.get_products()  # LENTO
    products = result['data']
    
    # Traducir en tiempo real (LENTO)
    translator = TranslationService()
    for product in products:
        if target_lang != 'es':
            product['name'] = translator.translate_if_needed(product['name'])
    
    return Response(products)
```

**AHORA** (rápido - datos locales con traducciones pre-calculadas):
```python
from crushme_app.models import WooCommerceProduct
from crushme_app.utils.translation_helpers import get_products_list

@api_view(['GET'])
def get_products(request):
    # Obtener idioma del header
    target_lang = request.headers.get('Accept-Language', 'es')[:2]
    
    # Consultar productos locales (RÁPIDO)
    products_qs = WooCommerceProduct.objects.filter(
        status='publish'
    ).prefetch_related('categories', 'images')
    
    # Obtener con traducciones y precios con margen (RÁPIDO)
    products = get_products_list(
        queryset=products_qs,
        target_language=target_lang,
        include_stock=False  # Stock se consulta por separado
    )
    
    return Response(products)
```

### Ejemplo: Consultar stock en tiempo real

```python
from crushme_app.services.woocommerce_service import woocommerce_service

@api_view(['GET'])
def get_product_detail(request, product_id):
    target_lang = request.headers.get('Accept-Language', 'es')[:2]
    
    # 1. Obtener datos locales con traducción (RÁPIDO)
    from crushme_app.utils.translation_helpers import get_product_full_data
    product = get_product_full_data(
        product_id,
        target_language=target_lang,
        include_stock=False
    )
    
    # 2. Consultar solo stock a WooCommerce (RÁPIDO con _fields)
    stock_result = woocommerce_service.get_product_by_id(
        product_id,
        fields='id,stock_quantity,stock_status,manage_stock'
    )
    
    if stock_result['success']:
        product['stock_quantity'] = stock_result['data']['stock_quantity']
        product['stock_status'] = stock_result['data']['stock_status']
        product['in_stock'] = stock_result['data']['stock_status'] == 'instock'
    
    return Response(product)
```

---

## 📅 PASO 5: Configurar sincronización automática

### Opción A: Cron (Recomendado)

```bash
# Editar crontab
crontab -e

# Agregar:
# Sincronización completa cada 6 horas (0:00, 6:00, 12:00, 18:00)
0 */6 * * * cd /home/cerrotico/work/crushme_project/backend && ./venv/bin/python manage.py sync_woocommerce --full >> /var/log/crushme/sync.log 2>&1

# Traducir contenido nuevo cada 6 horas (15 min después)
15 */6 * * * cd /home/cerrotico/work/crushme_project/backend && ./venv/bin/python manage.py translate_content >> /var/log/crushme/translate.log 2>&1
```

### Opción B: Celery Beat (más robusto)

Ver archivo `WOOCOMMERCE_SYNC_GUIDE.md` para detalles

---

## 🎯 PASO 6: Testing

### Probar el flujo completo

```python
# 1. Verificar productos sincronizados
from crushme_app.models import WooCommerceProduct
print(f"Productos sincronizados: {WooCommerceProduct.objects.count()}")

# 2. Verificar traducciones
from crushme_app.models import TranslatedContent
print(f"Traducciones: {TranslatedContent.objects.count()}")

# 3. Probar obtener producto con traducción
from crushme_app.utils.translation_helpers import get_product_full_data
product = get_product_full_data(product_id=123, target_language='en')
print(product['name'])  # Debe estar en inglés

# 4. Probar cálculo de precio con margen
from crushme_app.utils.translation_helpers import calculate_product_price
from crushme_app.models import WooCommerceProduct
product = WooCommerceProduct.objects.first()
prices = calculate_product_price(product)
print(f"Precio base: ${product.price}")
print(f"Precio con margen: ${prices['price']}")
```

---

## 📊 Monitoreo y Mantenimiento

### Revisar logs de sincronización

```python
from crushme_app.models import ProductSyncLog

# Último sync
last_sync = ProductSyncLog.objects.first()
print(f"Status: {last_sync.status}")
print(f"Productos: {last_sync.products_synced}")
print(f"Errores: {last_sync.errors_count}")
if last_sync.errors_count > 0:
    print(last_sync.error_details)
```

### Revisar estadísticas

```python
from crushme_app.models import WooCommerceProduct, TranslatedContent
from django.db.models import Count

# Productos por tipo
WooCommerceProduct.objects.values('product_type').annotate(count=Count('id'))

# Traducciones por idioma
TranslatedContent.objects.values('target_language').annotate(count=Count('id'))

# Categorías con margen configurado
from crushme_app.models import CategoryPriceMargin
CategoryPriceMargin.objects.filter(is_active=True).count()
```

---

## ⚠️ Problemas Comunes

### 1. Sincronización muy lenta
- ✅ **Ya optimizado**: Usa paginación (100 productos por página)
- ❌ Reducir a 50 si aún es lento
- Ejecutar en horario de bajo tráfico

### 2. Traducción muy lenta
- ✅ **Ya optimizado**: Solo campos esenciales, skip descripciones largas
- Opciones:
  - Traducir solo nombres y descripciones cortas
  - Ejecutar en background con `screen`
  - Traducir por lotes (por categoría)

### 3. Precios no se actualizan
- Los precios en la DB son de referencia
- El precio final se calcula con el margen configurado
- Stock siempre se debe consultar a WooCommerce en tiempo real

### 4. Traducciones no aparecen
- Verificar que el comando `translate_content` se ejecutó sin errores
- Revisar en admin: `Translated Contents`
- Re-ejecutar con `--force` para forzar re-traducción

---

## 🎉 Resultado Final

Cuando todo esté configurado:

✅ **Productos sincronizados localmente** → Respuestas ultra rápidas  
✅ **Traducciones pre-calculadas** → No se traduce en cada request  
✅ **Precios con margen dinámico** → Configurables por categoría  
✅ **Stock actualizado** → Consulta directa a WooCommerce solo cuando se necesita  
✅ **Sincronización automática** → Todo actualizado cada 6 horas  

**Tiempo de respuesta esperado**:
- **Antes**: 2-5 segundos (WooCommerce + traducción en tiempo real)
- **Ahora**: 50-200ms (base de datos local + cache de traducciones)

**Mejora de rendimiento**: ~10-20x más rápido 🚀

---

## 📖 Documentación Adicional

- `WOOCOMMERCE_SYNC_GUIDE.md`: Guía completa de sincronización
- `crushme_app/utils/translation_helpers.py`: Funciones utilitarias
- `crushme_app/services/`: Servicios disponibles
- Admin Django: Gestión visual de todo el sistema
