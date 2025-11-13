# Product Attribute Translation

## Overview

The system automatically translates product attribute names and values for variable products (products with variations like Color, Size, etc.).

## Features

- ✅ Automatic translation of attribute names (e.g., "Color" → "Color", "Talla" → "Size")
- ✅ Automatic translation of attribute values (e.g., "Rojo" → "Red", "Grande" → "Large")
- ✅ Pre-translation via batch service for fast delivery
- ✅ Real-time translation fallback if not pre-translated
- ✅ Maintains original values for matching variations

## How It Works

### 1. Automatic Translation (Batch Service)

When products are synced from WooCommerce, the batch translation service automatically:

1. Extracts all unique attribute names from product and variations
2. Extracts all unique attribute values
3. Translates them to English (if target language is English)
4. Stores translations in `TranslatedContent` table

**Trigger:**
```bash
# Translate all product attributes
python manage.py translate_attributes

# Force re-translation
python manage.py translate_attributes --force

# Translate specific product
python manage.py translate_attributes --product-id 12345
```

### 2. Real-Time Translation

When fetching product details via API, if target language is English:

1. Attribute names are translated
2. Attribute values are translated
3. Both translated and original values are returned

## API Response Format

### Product Detail Endpoint

```
GET /api/products/woocommerce/products/{id}/?lang=en
```

**Response (English):**
```json
{
  "id": 12345,
  "name": "Variable Product",
  "type": "variable",
  "is_variable": true,
  "attributes": [
    {
      "name": "Color",              // Translated name
      "name_original": "Color",     // Original name (for reference)
      "slug": "attribute_pa_color",
      "options": [                  // Translated values
        "Red",
        "Blue",
        "Green"
      ]
    },
    {
      "name": "Size",
      "name_original": "Talla",
      "slug": "attribute_pa_talla",
      "options": [
        "Small",
        "Medium",
        "Large"
      ]
    }
  ],
  "available_variations": [
    {
      "id": 67890,
      "attributes": {               // Translated attributes
        "Color": "Red",
        "Size": "Large"
      },
      "attributes_original": {      // Original attributes (for matching)
        "attribute_pa_color": "Rojo",
        "attribute_pa_talla": "Grande"
      },
      "price": 50000,
      "in_stock": true,
      "stock_quantity": 10
    }
  ]
}
```

**Response (Spanish - Original):**
```json
{
  "id": 12345,
  "name": "Producto Variable",
  "type": "variable",
  "is_variable": true,
  "attributes": [
    {
      "name": "Color",
      "name_original": "Color",
      "slug": "attribute_pa_color",
      "options": [
        "Rojo",
        "Azul",
        "Verde"
      ]
    },
    {
      "name": "Talla",
      "name_original": "Talla",
      "slug": "attribute_pa_talla",
      "options": [
        "Pequeño",
        "Mediano",
        "Grande"
      ]
    }
  ],
  "available_variations": [
    {
      "id": 67890,
      "attributes": {
        "Color": "Rojo",
        "Talla": "Grande"
      },
      "attributes_original": {
        "attribute_pa_color": "Rojo",
        "attribute_pa_talla": "Grande"
      },
      "price": 50000,
      "in_stock": true,
      "stock_quantity": 10
    }
  ]
}
```

## Frontend Usage

### Display Attributes

```javascript
// Get product with translations
const response = await axios.get(`/api/products/woocommerce/products/${productId}/`, {
  params: { lang: 'en' }
});

const product = response.data;

// Display attributes
product.attributes.forEach(attr => {
  console.log(`${attr.name}:`);  // "Color:" or "Size:"
  attr.options.forEach(option => {
    console.log(`  - ${option}`);  // "Red", "Blue", etc.
  });
});
```

### Match Variation by Attributes

```javascript
// User selects: Color = "Red", Size = "Large"
const selectedAttributes = {
  "Color": "Red",
  "Size": "Large"
};

// Find matching variation
const variation = product.available_variations.find(v => {
  return Object.keys(selectedAttributes).every(key => {
    return v.attributes[key] === selectedAttributes[key];
  });
});

console.log('Selected variation:', variation.id);
console.log('Price:', variation.price);
console.log('In stock:', variation.in_stock);
```

### Use Original Attributes for API Calls

When adding to cart or selecting variation, use `attributes_original`:

```javascript
// Add variation to cart
await axios.post('/api/cart/add/', {
  product_id: product.id,
  variation_id: variation.id,
  attributes: variation.attributes_original,  // Use original for backend
  quantity: 1
});
```

## Database Schema

### TranslatedContent Table

Stores pre-translated attributes:

```sql
CREATE TABLE translated_content (
  id SERIAL PRIMARY KEY,
  content_type VARCHAR(30),  -- 'variation_attribute'
  object_id INTEGER,         -- Hash of product_id + attribute name/value
  source_language VARCHAR(5), -- 'es'
  target_language VARCHAR(5), -- 'en'
  source_text TEXT,          -- 'Rojo'
  translated_text TEXT,      -- 'Red'
  translation_engine VARCHAR(50), -- 'argostranslate'
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Example Records

| content_type | object_id | source_text | translated_text | target_language |
|--------------|-----------|-------------|-----------------|-----------------|
| variation_attribute | 123456789 | Color | Color | en |
| variation_attribute | 987654321 | Rojo | Red | en |
| variation_attribute | 456789123 | Talla | Size | en |
| variation_attribute | 321654987 | Grande | Large | en |

## Translation Service

### Code Location

**Translation Logic:**
- `crushme_app/utils/translation_helpers.py` - Real-time translation in `get_product_full_data()`
- `crushme_app/services/translation_batch_service.py` - Batch pre-translation

**Translation Service:**
- `crushme_app/services/translation_service.py` - Core translation using argostranslate

### How Attributes Are Translated

1. **Extract Attributes:**
   - From `WooCommerceProduct.attributes` (JSON field)
   - From `WooCommerceProductVariation.attributes` (JSON field)

2. **Clean Attribute Keys:**
   - Remove `attribute_pa_` prefix
   - Remove `attribute_` prefix
   - Example: `attribute_pa_color` → `color`

3. **Translate:**
   - Attribute names: `Color`, `Talla`, etc.
   - Attribute values: `Rojo`, `Grande`, etc.
   - Uses argostranslate (offline translation)

4. **Store:**
   - In `TranslatedContent` table
   - Unique hash ID per attribute/value
   - Indexed for fast lookup

## Performance

### Pre-Translation (Batch)
- **Speed:** ~100-200 attributes per second
- **When:** During product sync or manual command
- **Storage:** ~50 bytes per translation

### Real-Time Translation
- **Speed:** ~10-50ms per attribute (if not cached)
- **Fallback:** Uses pre-translated cache when available
- **Offline:** No external API calls

## Common Attribute Names

### Spanish → English

| Spanish | English |
|---------|---------|
| Color | Color |
| Talla | Size |
| Material | Material |
| Estilo | Style |
| Tamaño | Size |
| Longitud | Length |
| Ancho | Width |
| Altura | Height |
| Peso | Weight |
| Marca | Brand |

### Common Values

| Spanish | English |
|---------|---------|
| Rojo | Red |
| Azul | Blue |
| Verde | Green |
| Negro | Black |
| Blanco | White |
| Pequeño | Small |
| Mediano | Medium |
| Grande | Large |
| Extra Grande | Extra Large |

## Troubleshooting

### Attributes Not Translated

**Check:**
1. Is product type `variable`?
2. Does product have `attributes` field populated?
3. Run batch translation: `python manage.py translate_attributes --product-id {id}`

### Wrong Translation

**Fix:**
1. Update translation in database:
```sql
UPDATE translated_content 
SET translated_text = 'Correct Translation'
WHERE source_text = 'Original Text' 
  AND target_language = 'en';
```

2. Or force re-translation:
```bash
python manage.py translate_attributes --force
```

### Missing Attributes in Response

**Check:**
1. API endpoint: `/api/products/woocommerce/products/{id}/`
2. Query parameter: `?lang=en`
3. Product type: Must be `variable`
4. Variations: Must exist and have attributes

## Testing

### Test Translation

```bash
# Test batch translation
python manage.py translate_attributes --product-id 12345

# Check translations in database
python manage.py shell
>>> from crushme_app.models import TranslatedContent
>>> TranslatedContent.objects.filter(content_type='variation_attribute')
```

### Test API Response

```bash
# Spanish (original)
curl "http://localhost:8000/api/products/woocommerce/products/12345/?lang=es"

# English (translated)
curl "http://localhost:8000/api/products/woocommerce/products/12345/?lang=en"
```

## Future Enhancements

Potential improvements:

1. **More Languages:**
   - Add Portuguese, French, etc.
   - Update `TranslationService.SUPPORTED_LANGUAGES`

2. **Custom Translations:**
   - Admin interface to override automatic translations
   - Manual verification system

3. **Translation Quality:**
   - Use better translation models
   - Context-aware translations

4. **Performance:**
   - Cache translations in Redis
   - Lazy loading for large attribute sets

## Related Documentation

- `docs/TRANSLATION_SYSTEM.md` - Overall translation system
- `docs/WOOCOMMERCE_SYNC.md` - Product synchronization
- `docs/PRODUCT_VARIATIONS.md` - Variation handling
