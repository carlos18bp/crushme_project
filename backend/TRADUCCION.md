# 🌐 Sistema de Traducción Offline

Sistema de traducción automática **español ↔ inglés** usando **argostranslate** (100% offline, sin API keys).

## ✅ Características

- **100% Offline**: No requiere conexión a internet después de instalar los modelos
- **Rápido**: ~0.24s por texto (10x más rápido que APIs online)
- **Sin costos**: Sin API keys ni límites de uso
- **Detección automática**: Detecta el idioma fuente automáticamente

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Instalar modelos de traducción

```bash
python install_translation_models.py
```

Esto descargará e instalará los modelos de traducción (~500MB). Solo se hace **una vez**.

## 🚀 Uso

### En el Frontend

El frontend envía el idioma deseado en cada petición:

```javascript
// Query parameter (GET requests)
GET /api/products/woocommerce/products/trending/?lang=en

// O con header (cualquier método)
headers: {
  'Accept-Language': 'en'
}
```

**Idiomas soportados:**
- `lang=es` o `Accept-Language: es` → Español (por defecto, sin traducción)
- `lang=en` o `Accept-Language: en` → Inglés (traduce desde español)

### Desactivar traducción temporalmente

```javascript
// Útil para debug o testing
GET /api/products/woocommerce/products/trending/?lang=en&translate=false
```

## 📍 Endpoints con Traducción

### Perfiles de Usuarios (PÚBLICOS)

Endpoints que traducen contenido de usuario:

- `GET /api/auth/public/@{username}/`
- `GET /api/auth/crush/random/`
- `GET /api/auth/crush/random-7/`

**Campos traducidos:**
- `about` - Biografía
- `note` - Mensaje personal
- `gallery_photos[].caption` - Descripciones de fotos
- `public_wishlists[].name` - Nombre de wishlist
- `public_wishlists[].description` - Descripción
- `public_wishlists[].items[].notes` - Notas sobre productos

### Productos WooCommerce

Endpoints que traducen productos:

- `GET /api/products/woocommerce/products/trending/`
- `GET /api/products/woocommerce/products/`
- `GET /api/products/woocommerce/products/{id}/`
- `POST /api/products/woocommerce/products/batch/`
- `GET /api/products/woocommerce/categories/`

**Campos traducidos:**

**Productos (listados - optimizado):**
- `name` - Nombre del producto
- `short_description` - Descripción corta
- `categories[0].name` - Primera categoría

**Productos (detalle - completo):**
- `name` - Nombre del producto
- `short_description` - Descripción corta
- `description` - Descripción completa (HTML)
- `categories[0].name` - Primera categoría

**Categorías:**
- `name` - Nombre de la categoría
- `description` - Descripción

## ⚡ Rendimiento

**Tiempo de traducción:**
- Primer texto: ~2s (carga modelo en memoria)
- Textos siguientes: ~0.24s cada uno

**Ejemplo (8 productos):**
- 8 productos × 3 campos = ~5 segundos total
- Bien dentro del timeout de 10s ✅

## 🔧 Configuración Avanzada

### Modificar idiomas de detección

Editar `crushme_app/services/translation_service.py`:

```python
# Agregar más palabras clave para detección
spanish_words = [' el ', ' la ', ...]
english_words = [' the ', ' and ', ...]
```

### Agregar más idiomas

```python
# Instalar paquetes adicionales
argostranslate.package.install_from_path(package.download())
```

## 📊 Comparación

| Característica | argostranslate | deep-translator |
|----------------|----------------|-----------------|
| Velocidad | ⚡ ~0.24s/texto | 🐌 ~1-2s/texto |
| Conexión | ✅ Offline | ❌ Online (HTTP) |
| API Keys | ✅ No necesita | ❌ Limitado gratis |
| Costo | ✅ Gratis | ⚠️ Límites |
| Instalación | ~500MB modelos | ~50MB |

## 🐛 Troubleshooting

### Error: "No translation package found"

```bash
# Reinstalar modelos
python install_translation_models.py
```

### Traducción muy lenta

La primera traducción carga el modelo en memoria (~2s). Las siguientes son rápidas.

### Error: "Out of memory"

Los modelos usan ~500MB de RAM. Asegúrate de tener suficiente memoria disponible.

## 📝 Notas

- **Contenido de WooCommerce**: Sabemos que está en español, solo se traduce si se pide inglés
- **Contenido de usuarios**: Se auto-detecta el idioma y se traduce según sea necesario
- **Endpoints privados**: NO se traducen (info que el usuario mismo puso)

## 🔗 Referencias

- [argostranslate](https://github.com/argosopentech/argos-translate)
- [Modelos disponibles](https://www.argosopentech.com/argospm/index/)

