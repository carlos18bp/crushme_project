# Atributos de Productos WooCommerce - Guía para Frontend

## 🎯 Problema
En WooCommerce, los productos tienen atributos que pueden ser **seleccionables** (para variaciones) o **solo informativos** (para mostrar información adicional).

## ✅ Cómo Identificar Atributos Seleccionables

### Campo Clave: `variation`

Cada atributo en el array `attributes` tiene un campo booleano llamado `variation`:

- **`variation: true`** → **SELECCIONABLE** (se usa para crear variaciones del producto)
- **`variation: false`** → **SOLO INFORMATIVO** (solo para mostrar información)

---

## 📊 Ejemplo Real

### Producto de WooCommerce (ID: 19300)

```json
{
  "type": "variable",
  "has_options": true,
  "attributes": [
    {
      "id": 0,
      "name": "Tamaño",
      "slug": "Tamaño",
      "visible": false,
      "variation": true,  ← SELECCIONABLE
      "options": ["Sachet", "39 ML"]
    },
    {
      "id": 0,
      "name": "Sabor",
      "slug": "Sabor",
      "visible": false,
      "variation": true,  ← SELECCIONABLE
      "options": ["Anís", "Baileys", "Mojito", "Ron", "Tequila"]
    },
    {
      "id": 0,
      "name": "Marca",
      "slug": "Marca",
      "visible": true,
      "variation": false,  ← SOLO INFORMATIVO
      "options": ["Erotic"]
    }
  ],
  "variations": [19301, 19303, 19304, 19305, 19306, ...]
}
```

### Interpretación:

✅ **Atributos Seleccionables** (el usuario debe elegir):
- **Tamaño**: Sachet o 39 ML
- **Sabor**: Anís, Baileys, Mojito, Ron, o Tequila

ℹ️ **Atributos Informativos** (solo mostrar, NO seleccionables):
- **Marca**: Erotic

---

## 🎨 Cómo Implementar en el Frontend

### Código de Ejemplo (JavaScript/React)

```javascript
// Obtener producto de WooCommerce
const product = await fetch(`/api/products/woocommerce/products/19300/`).then(r => r.json());

// Separar atributos seleccionables de informativos
const selectableAttributes = product.data.attributes.filter(attr => attr.variation === true);
const informativeAttributes = product.data.attributes.filter(attr => attr.variation === false);

// Renderizar atributos seleccionables (con selector/dropdown)
selectableAttributes.forEach(attr => {
  console.log(`Mostrar selector para: ${attr.name}`);
  console.log(`Opciones: ${attr.options}`);
  // Renderizar <select> o botones para elegir
});

// Renderizar atributos informativos (solo texto)
informativeAttributes.forEach(attr => {
  console.log(`Mostrar info: ${attr.name}: ${attr.options.join(', ')}`);
  // Renderizar como badge o etiqueta informativa
});
```

### Ejemplo Visual

```jsx
function ProductAttributes({ attributes }) {
  return (
    <>
      {/* ATRIBUTOS SELECCIONABLES */}
      <div className="product-options">
        {attributes
          .filter(attr => attr.variation === true)
          .map(attr => (
            <div key={attr.name} className="option-group">
              <label>{attr.name}</label>
              <select>
                {attr.options.map(option => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          ))}
      </div>

      {/* ATRIBUTOS INFORMATIVOS */}
      <div className="product-info">
        {attributes
          .filter(attr => attr.variation === false)
          .map(attr => (
            <div key={attr.name} className="info-badge">
              <strong>{attr.name}:</strong> {attr.options.join(', ')}
            </div>
          ))}
      </div>
    </>
  );
}
```

---

## 📝 Campos Adicionales Relacionados

### `type` - Tipo de Producto

```javascript
if (product.data.type === 'variable') {
  // Producto con variaciones → Mostrar selectores
  // Usar attributes donde variation === true
}

if (product.data.type === 'simple') {
  // Producto simple → No tiene variaciones
  // Todos los attributes son solo informativos
}
```

### `has_options` - Tiene Opciones

```javascript
if (product.data.has_options === true) {
  // El producto tiene opciones seleccionables
  // Filtrar attributes por variation === true
}
```

### `variations` - Array de IDs de Variaciones

```javascript
// IDs de las variaciones del producto
product.data.variations // [19301, 19303, 19304, ...]

// Para obtener detalles completos de una variación:
const variation = await fetch(`/api/products/woocommerce/variations/${variationId}/`);
```

---

## 🔍 Estructura Completa de un Atributo

```javascript
{
  "id": 0,              // ID del atributo (0 si es personalizado)
  "name": "Tamaño",     // Nombre visible del atributo
  "slug": "tamaño",     // Slug para URLs
  "visible": false,     // Si debe mostrarse en la página del producto
  "variation": true,    // ⭐ CAMPO CLAVE: true = seleccionable, false = informativo
  "options": [          // Opciones disponibles
    "Sachet",
    "39 ML"
  ]
}
```

---

## 🎯 Reglas de Negocio

### Regla 1: Tipo de Producto
- **`type: "simple"`** → No tiene variaciones, todos los attributes son informativos
- **`type: "variable"`** → Tiene variaciones, filtrar por `variation: true`
- **`type: "grouped"`** → Producto agrupado
- **`type: "external"`** → Producto externo

### Regla 2: Validación
```javascript
// Antes de agregar al carrito, validar que se seleccionaron todos los atributos requeridos
const requiredAttributes = product.data.attributes.filter(attr => attr.variation === true);

if (requiredAttributes.length > 0) {
  // Usuario DEBE seleccionar opciones antes de agregar al carrito
  const allSelected = requiredAttributes.every(attr => userSelection[attr.name] !== undefined);
  
  if (!allSelected) {
    alert('Por favor selecciona todas las opciones');
    return;
  }
}
```

### Regla 3: Obtener Variación Específica
```javascript
// Después de que el usuario selecciona opciones, encontrar la variación correspondiente
const selectedOptions = {
  "Tamaño": "39 ML",
  "Sabor": "Tequila"
};

// Hacer request para obtener la variación específica con esos atributos
// WooCommerce devuelve el precio, stock y SKU de esa combinación específica
```

---

## 📋 Checklist para el Frontend

- [ ] Filtrar `attributes` por `variation === true` para selectores
- [ ] Filtrar `attributes` por `variation === false` para badges informativos
- [ ] Validar tipo de producto (`type === 'variable'`) antes de mostrar selectores
- [ ] Requerir selección de todos los atributos con `variation: true`
- [ ] Mostrar atributos informativos como texto o badges, NO como selectores
- [ ] Deshabilitar botón "Agregar al carrito" si no se han seleccionado todas las opciones

---

## 🚨 Errores Comunes

### ❌ Error: Mostrar TODOS los atributos como seleccionables
```javascript
// MAL ❌
product.data.attributes.map(attr => <Select options={attr.options} />)
```

### ✅ Correcto: Filtrar por variation
```javascript
// BIEN ✅
product.data.attributes
  .filter(attr => attr.variation === true)
  .map(attr => <Select options={attr.options} />)
```

---

## 🎨 Ejemplo Completo React

```jsx
function ProductDetail({ productId }) {
  const [product, setProduct] = useState(null);
  const [selectedOptions, setSelectedOptions] = useState({});

  useEffect(() => {
    fetch(`/api/products/woocommerce/products/${productId}/`)
      .then(r => r.json())
      .then(data => setProduct(data.data));
  }, [productId]);

  if (!product) return <div>Cargando...</div>;

  const selectableAttrs = product.attributes.filter(a => a.variation === true);
  const infoAttrs = product.attributes.filter(a => a.variation === false);
  const canAddToCart = selectableAttrs.length === 0 || 
                       selectableAttrs.every(a => selectedOptions[a.name]);

  return (
    <div className="product-detail">
      <h1>{product.name}</h1>
      
      {/* Atributos Informativos */}
      {infoAttrs.length > 0 && (
        <div className="product-info-badges">
          {infoAttrs.map(attr => (
            <span key={attr.name} className="badge">
              {attr.name}: {attr.options.join(', ')}
            </span>
          ))}
        </div>
      )}

      {/* Atributos Seleccionables */}
      {selectableAttrs.length > 0 && (
        <div className="product-options">
          <h3>Selecciona tus opciones:</h3>
          {selectableAttrs.map(attr => (
            <div key={attr.name} className="option-group">
              <label>{attr.name} *</label>
              <select
                value={selectedOptions[attr.name] || ''}
                onChange={e => setSelectedOptions({
                  ...selectedOptions,
                  [attr.name]: e.target.value
                })}
              >
                <option value="">Selecciona {attr.name}</option>
                {attr.options.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      <button 
        disabled={!canAddToCart}
        onClick={() => addToCart(product.id, selectedOptions)}
      >
        {canAddToCart ? 'Agregar al Carrito' : 'Selecciona todas las opciones'}
      </button>
    </div>
  );
}
```

---

**Última actualización:** Octubre 2025  
**Producto de ejemplo analizado:** ID 19300 (Lubricante Íntimo Caliente Licor Lush)


