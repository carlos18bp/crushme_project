# Sistema de Traducción en Endpoints de Variaciones

## ✅ Implementación Completa

Los endpoints de variaciones ahora tienen **traducción automática** siguiendo el mismo patrón que los otros endpoints de WooCommerce.

---

## 🌐 Cómo Funciona la Traducción

### 1. Detección Automática del Idioma
La traducción detecta el idioma desde el header `Accept-Language`:
- **`Accept-Language: en`** → Traduce al inglés
- **`Accept-Language: es`** → No traduce (contenido ya está en español)
- Sin header → Por defecto español (no traduce)

### 2. Desactivar Traducción
Puedes desactivar la traducción con el query parameter:
- **`?translate=false`** → No traduce, sin importar el Accept-Language

---

## 📋 Ejemplos de Uso

### Endpoint 1: Todas las variaciones

#### Traducir a inglés:
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/" \
  -H "Accept-Language: en"
```
**Resultado:** `"Precio sugerido"` → `"Suggested price"`

#### Mantener en español:
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/" \
  -H "Accept-Language: es"
```
**Resultado:** `"Precio sugerido"` (sin cambios)

#### Desactivar traducción:
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/?translate=false" \
  -H "Accept-Language: en"
```
**Resultado:** `"Precio sugerido"` (no traduce aunque el idioma sea inglés)

---

### Endpoint 2: Variación específica

#### Traducir a inglés:
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/19427/" \
  -H "Accept-Language: en"
```
**Resultado:** Descripción y otros campos traducidos al inglés

#### Mantener en español:
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/19427/" \
  -H "Accept-Language: es"
```
**Resultado:** Todo en español original

#### Desactivar traducción:
```bash
curl -X GET "http://localhost:8000/api/products/woocommerce/products/19425/variations/19427/?translate=false" \
  -H "Accept-Language: en"
```
**Resultado:** Sin traducción (español original)

---

## 🔍 Campos que se Traducen

### En variaciones (translate_full=True):
- ✅ `name` - Nombre del producto
- ✅ `description` - Descripción HTML completa
- ✅ `short_description` - Descripción corta
- ✅ `categories[0].name` - Nombre de la categoría principal
- ❌ `attributes` - NO se traducen (son demasiados y ralentizan)

---

## ✅ Matriz de Pruebas

| Endpoint | Accept-Language | translate | Resultado | Estado |
|----------|----------------|-----------|-----------|--------|
| /variations/ | en | true | Traduce a inglés | ✅ FUNCIONA |
| /variations/ | es | true | No traduce (ya español) | ✅ FUNCIONA |
| /variations/ | en | false | No traduce | ✅ FUNCIONA |
| /variations/{id}/ | en | true | Traduce a inglés | ✅ FUNCIONA |
| /variations/{id}/ | es | true | No traduce (ya español) | ✅ FUNCIONA |
| /variations/{id}/ | en | false | No traduce | ✅ FUNCIONA |

---

## 🎯 Uso desde el Frontend

### JavaScript/Fetch

#### Traducir automáticamente:
```javascript
// El navegador envía automáticamente Accept-Language según la configuración del usuario
const response = await fetch('/api/products/woocommerce/products/19425/variations/');
const data = await response.json();
// Se traduce según el idioma del navegador
```

#### Especificar idioma:
```javascript
const response = await fetch('/api/products/woocommerce/products/19425/variations/', {
  headers: {
    'Accept-Language': 'en'
  }
});
```

#### Desactivar traducción:
```javascript
const response = await fetch(
  '/api/products/woocommerce/products/19425/variations/?translate=false',
  {
    headers: {
      'Accept-Language': 'en'
    }
  }
);
// No traduce, devuelve español original
```

---

## 🔧 Implementación Técnica

### Funciones utilizadas:

1. **`translate_woocommerce_products(products, request, translate_full=True)`**
   - Traduce lista de productos/variaciones
   - Verifica idioma y parámetro translate
   - Para variaciones usa `translate_full=True` (traduce description completa)

2. **`translate_woocommerce_product(product, translator, translate_full=True)`**
   - Traduce un solo producto/variación
   - Recibe translator ya inicializado
   - Usado en endpoint de variación específica

3. **`create_translator_from_request(request)`**
   - Detecta idioma del header Accept-Language
   - Crea instancia del servicio de traducción
   - Retorna translator configurado

---

## 📚 Compatibilidad

✅ **Idiomas soportados:**
- Español (es) - Idioma origen
- Inglés (en)
- Todos los idiomas soportados por la biblioteca de traducción

✅ **Endpoints compatibles:**
- `/api/products/woocommerce/products/{id}/variations/` (todas)
- `/api/products/woocommerce/products/{id}/variations/{variation_id}/` (específica)
- Todos los demás endpoints de WooCommerce del proyecto

---

## 💡 Notas Importantes

1. **Performance**: La traducción se hace bajo demanda (no se cachea)
2. **Fallback**: Si falla la traducción, devuelve el texto original en español
3. **HTML**: Los campos con HTML se traducen preservando las etiquetas
4. **Atributos**: Los atributos NO se traducen para optimizar velocidad

---

## 🎉 Estado Final

✅ Traducción implementada y probada
✅ Compatible con patrón de otros endpoints
✅ Todas las pruebas pasando
✅ Documentación completa

**¡Sistema de traducción funcionando al 100%!** 🌍

