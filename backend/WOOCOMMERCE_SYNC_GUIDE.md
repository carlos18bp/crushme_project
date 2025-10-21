# 🚀 Guía de Sincronización WooCommerce

## 📋 Resumen del Sistema

Este sistema sincroniza productos y categorías de WooCommerce a la base de datos local, pre-traduce todo el contenido y aplica márgenes de precio por categoría.

### ✅ Flujo Implementado

1. **Sincronización**: WooCommerce → Base de datos local (cada 6 horas)
2. **Traducciones**: Pre-traducir todo el contenido (español → inglés)
3. **Precios**: Calculados localmente con márgen por categoría
4. **Stock**: Consultado en tiempo real a WooCommerce en cada request

---

## 🗄️ Modelos Creados

### WooCommerce Models

- **WooCommerceCategory**: Categorías sincronizadas
- **WooCommerceProduct**: Productos completos (sin stock/precio real-time)
- **WooCommerceProductImage**: URLs de imágenes (no descarga archivos)
- **WooCommerceProductVariation**: Variaciones de productos
- **ProductSyncLog**: Registro de sincronizaciones

### Translation Models

- **TranslatedContent**: Cache de traducciones pre-calculadas
- **CategoryPriceMargin**: Márgen de ganancia por categoría
- **DefaultPriceMargin**: Márgen por defecto

---

## 🔧 Comandos Disponibles

### 1. Sincronización WooCommerce

```bash
# Sincronización completa (primera vez o cambios grandes)
./venv/bin/python manage.py sync_woocommerce --full

# Solo categorías
./venv/bin/python manage.py sync_woocommerce --categories

# Solo productos
./venv/bin/python manage.py sync_woocommerce --products

# Solo variaciones
./venv/bin/python manage.py sync_woocommerce --variations

# Solo actualizar stock/precios (rápido)
./venv/bin/python manage.py sync_woocommerce --stock
```

### 2. Traducción de Contenido

```bash
# Traducir todo el contenido nuevo
./venv/bin/python manage.py translate_content

# Forzar re-traducción de todo
./venv/bin/python manage.py translate_content --force

# Traducir producto específico
./venv/bin/python manage.py translate_content --product-id 123
```

---

## ⏰ Configuración de Sincronización Automática

### Opción 1: Cron Jobs (Recomendado para producción)

```bash
# Editar crontab
crontab -e

# Agregar estas líneas:

# Sincronización completa cada 6 horas
0 */6 * * * cd /path/to/backend && ./venv/bin/python manage.py sync_woocommerce --full >> /var/log/crushme/sync.log 2>&1

# Traducir nuevo contenido cada 6 horas (15 min después del sync)
15 */6 * * * cd /path/to/backend && ./venv/bin/python manage.py translate_content >> /var/log/crushme/translations.log 2>&1

# Opcional: Actualizar solo stock cada 10 minutos
*/10 * * * * cd /path/to/backend && ./venv/bin/python manage.py sync_woocommerce --stock >> /var/log/crushme/stock.log 2>&1
```

### Opción 2: Celery (Para aplicaciones más complejas)

```python
# tasks.py
from celery import shared_task
from crushme_app.services.woocommerce_sync_service import woocommerce_sync_service
from crushme_app.services.translation_batch_service import translation_batch_service

@shared_task
def sync_woocommerce_full():
    """Sincronización completa cada 6 horas"""
    return woocommerce_sync_service.sync_all()

@shared_task
def sync_woocommerce_stock():
    """Actualizar stock cada 10 minutos"""
    return woocommerce_sync_service.sync_stock_and_prices()

@shared_task
def translate_all_content():
    """Traducir contenido nuevo"""
    return translation_batch_service.translate_all()
```

```python
# celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'sync-woocommerce-full': {
        'task': 'tasks.sync_woocommerce_full',
        'schedule': crontab(minute=0, hour='*/6'),  # Cada 6 horas
    },
    'sync-woocommerce-stock': {
        'task': 'tasks.sync_woocommerce_stock',
        'schedule': crontab(minute='*/10'),  # Cada 10 minutos
    },
    'translate-content': {
        'task': 'tasks.translate_all_content',
        'schedule': crontab(minute=15, hour='*/6'),  # Cada 6 horas
    },
}
```

---

## 💰 Configuración de Márgenes de Precio

### En el Admin de Django

1. **Ir a**: Admin → Category Price Margins
2. **Crear márgen por categoría**:
   - Seleccionar categoría
   - Opción A: Porcentaje (ej: 30% → `margin_percentage = 30.00`)
   - Opción B: Multiplicador fijo (ej: x1.3 → `fixed_multiplier = 1.30`)

3. **Configurar márgen por defecto**:
   - Admin → Default Price Margins
   - Crear un registro con el márgen por defecto
   - Solo puede haber uno activo

### Uso Programático

```python
from crushme_app.models import CategoryPriceMargin, WooCommerceCategory

# Crear márgen para una categoría
category = WooCommerceCategory.objects.get(wc_id=15)
margin = CategoryPriceMargin.objects.create(
    category=category,
    margin_percentage=25.00,  # 25% de margen
    is_active=True
)

# Calcular precio con márgen
base_price = 100.00
final_price = margin.calculate_price(base_price)  # 125.00
```

---

## 🌐 Uso de Traducciones en las Vistas

### Obtener Producto con Traducción

```python
from crushme_app.models import WooCommerceProduct, TranslatedContent
from crushme_app.services.translation_batch_service import translation_batch_service

def get_product_translated(product_id, language='en'):
    product = WooCommerceProduct.objects.get(wc_id=product_id)
    
    if language == 'es':
        # Devolver contenido original
        return {
            'id': product.wc_id,
            'name': product.name,
            'short_description': product.short_description,
            'description': product.description,
        }
    else:
        # Obtener traducciones desde caché
        return {
            'id': product.wc_id,
            'name': translation_batch_service.get_translated_text(
                TranslatedContent.CONTENT_TYPE_PRODUCT_NAME,
                product.wc_id,
                language,
                fallback_text=product.name
            ),
            'short_description': translation_batch_service.get_translated_text(
                TranslatedContent.CONTENT_TYPE_PRODUCT_SHORT_DESC,
                product.wc_id,
                language,
                fallback_text=product.short_description
            ),
            'description': translation_batch_service.get_translated_text(
                TranslatedContent.CONTENT_TYPE_PRODUCT_DESC,
                product.wc_id,
                language,
                fallback_text=product.description
            ),
        }
```

### Consultar Stock en Tiempo Real

```python
from crushme_app.services.woocommerce_service import woocommerce_service

def get_product_with_real_stock(product_id):
    # Obtener info local (rápido)
    product = WooCommerceProduct.objects.get(wc_id=product_id)
    
    # Consultar solo stock a WooCommerce (rápido con _fields)
    wc_result = woocommerce_service.get_product_by_id(
        product_id,
        fields='id,stock_quantity,stock_status,manage_stock'
    )
    
    if wc_result['success']:
        wc_data = wc_result['data']
        return {
            **product_data_from_local,
            'stock_quantity': wc_data.get('stock_quantity'),
            'stock_status': wc_data.get('stock_status'),
            'in_stock': wc_data.get('stock_status') == 'instock'
        }
```

---

## 📊 Monitoreo

### Ver Logs de Sincronización

```python
from crushme_app.models import ProductSyncLog

# Últimas sincronizaciones
recent_syncs = ProductSyncLog.objects.all()[:10]

for sync in recent_syncs:
    print(f"{sync.sync_type}: {sync.status}")
    print(f"  Products: {sync.products_synced}")
    print(f"  Duration: {sync.duration_seconds}s")
    if sync.errors_count > 0:
        print(f"  Errors: {sync.error_details}")
```

### Ver Estadísticas de Traducciones

```python
from crushme_app.models import TranslatedContent

# Total de traducciones
total = TranslatedContent.objects.count()

# Por tipo de contenido
from django.db.models import Count
stats = TranslatedContent.objects.values('content_type').annotate(count=Count('id'))

for stat in stats:
    print(f"{stat['content_type']}: {stat['count']}")
```

---

## ⚠️ Notas Importantes

1. **Primera Sincronización**: Puede demorar dependiendo de la cantidad de productos
   - ~100 productos: 2-5 minutos
   - ~1000 productos: 20-40 minutos
   - ~5000+ productos: 1-2 horas

2. **Traducción**: También puede ser lenta la primera vez
   - Depende de la longitud de las descripciones
   - Descripciones >5000 caracteres se omiten por defecto
   - Se puede ejecutar en background

3. **Stock en Tiempo Real**: 
   - NO usar datos locales de stock para decisiones de compra
   - SIEMPRE consultar WooCommerce antes de crear orden
   - Usar parámetro `_fields` para consultas rápidas

4. **Precios**:
   - Los precios de WooCommerce son solo referencia
   - El precio final se calcula con el márgen de categoría
   - Actualizar márgenes desde el Admin

---

## 🐛 Troubleshooting

### Error: "Module not found: argostranslate"
```bash
./venv/bin/pip install argostranslate
```

### Error: "Timezone warnings"
Ya corregido en el código, pero si persiste:
```python
# settings.py
USE_TZ = True
TIME_ZONE = 'America/Bogota'  # o tu zona horaria
```

### Sincronización muy lenta
- Reducir `per_page` en el servicio (de 100 a 50)
- Ejecutar en horarios de bajo tráfico
- Considerar sincronización incremental

### Traducciones incorrectas
```bash
# Re-traducir todo
./venv/bin/python manage.py translate_content --force

# O verificar manualmente en el admin
# Admin → Translated Contents → Editar y marcar "Manually Verified"
```

---

## 📈 Próximas Mejoras (Opcionales)

- [ ] Webhooks de WooCommerce para sincronización en tiempo real
- [ ] Cache de Redis para consultas de stock
- [ ] API de traducción profesional (Google/DeepL) para mejor calidad
- [ ] Dashboard de monitoreo en el admin
- [ ] Notificaciones de errores de sincronización
- [ ] Versionado de traducciones

---

## 📞 Soporte

Para problemas o dudas:
1. Revisar logs: `/var/log/crushme/`
2. Revisar admin: ProductSyncLog
3. Verificar configuración de WooCommerce API
