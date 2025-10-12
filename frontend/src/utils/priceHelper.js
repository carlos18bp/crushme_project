/**
 * Utilidades para manejar precios de productos WooCommerce
 */

/**
 * Extrae el precio del campo short_description de un producto
 * @param {string} shortDescription - HTML con el precio sugerido
 * @returns {number|null} - Precio extraído o null si no se encuentra
 * 
 * Soporta múltiples formatos:
 * - $21,900 (coma colombiana) ✅
 * - $21.900 (punto como separador de miles) ✅
 * - $ 21,900 (con espacio) ✅
 * - $21900 (sin separadores) ✅
 */
export function extractPriceFromShortDescription(shortDescription) {
  if (!shortDescription || typeof shortDescription !== 'string') {
    console.debug('[priceHelper] short_description vacío o inválido');
    return null;
  }

  try {
    // Buscar el patrón: $XX,XXX o $XX.XXX con posibles espacios
    // Soporta AMBOS formatos: coma (16,000) y punto (16.000)
    const priceMatch = shortDescription.match(/\$\s*([\d,.]+)/);
    
    if (priceMatch && priceMatch[1]) {
      const rawPrice = priceMatch[1];
      
      // 🔥 NORMALIZACIÓN: Remover TANTO comas como puntos (separadores de miles)
      // En Colombia los precios son en miles, no hay decimales
      const priceString = rawPrice.replace(/[,.]/g, '');
      const price = parseInt(priceString, 10);
      
      if (!isNaN(price)) {
        console.debug(`[priceHelper] ✅ Precio extraído de "${rawPrice}" → ${price.toLocaleString('es-CO')}`);
        return price;
      }
    }
    
    console.warn('[priceHelper] ⚠️ No se pudo extraer precio de short_description:', shortDescription.substring(0, 100));
    return null;
  } catch (error) {
    console.error('[priceHelper] ❌ Error extrayendo precio:', error);
    return null;
  }
}

/**
 * Obtiene el precio de un producto (simple o variable)
 * @param {object} product - Producto de WooCommerce o Variación
 * @returns {number|null} - Precio del producto
 */
export function getProductPrice(product) {
  if (!product) {
    console.debug('[priceHelper] Producto no definido');
    return null;
  }

  // ⭐ PRIMERO: Intentar extraer de short_description (productos simples)
  const priceFromShort = extractPriceFromShortDescription(product.short_description);
  
  if (priceFromShort !== null) {
    console.debug(`[priceHelper] ✅ Precio extraído de short_description para producto ${product.id || 'unknown'}: $${priceFromShort.toLocaleString('es-CO')}`);
    return priceFromShort;
  }

  // ⭐ SEGUNDO: Intentar extraer de description (productos variables/variaciones)
  const priceFromDesc = extractPriceFromShortDescription(product.description);
  
  if (priceFromDesc !== null) {
    console.debug(`[priceHelper] ✅ Precio extraído de description para producto ${product.id || 'unknown'}: $${priceFromDesc.toLocaleString('es-CO')}`);
    return priceFromDesc;
  }

  // Fallback: usar price o regular_price si existe (PRECIO MAYORISTA - NO RECOMENDADO)
  if (product.price) {
    console.warn(`[priceHelper] ⚠️ Usando precio mayorista (price) como fallback para producto ${product.id || 'unknown'}: $${product.price}`);
    return parseFloat(product.price);
  }

  if (product.regular_price) {
    console.warn(`[priceHelper] ⚠️ Usando precio regular mayorista (regular_price) como fallback para producto ${product.id || 'unknown'}: $${product.regular_price}`);
    return parseFloat(product.regular_price);
  }

  console.error(`[priceHelper] ❌ No se pudo obtener precio para producto ${product.id || 'unknown'} - Nombre: ${product.name || 'unknown'}`);
  return null;
}

/**
 * Formatea un precio en COP (pesos colombianos)
 * @param {number} price - Precio a formatear
 * @param {boolean} includeSymbol - Incluir símbolo $
 * @returns {string} - Precio formateado (ej: "$21,900" o "21,900")
 */
export function formatCOP(price, includeSymbol = true) {
  if (price === null || price === undefined || isNaN(price)) {
    return includeSymbol ? '$0' : '0';
  }

  // Formatear con separadores de miles
  const formattedPrice = new Intl.NumberFormat('es-CO', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price);

  return includeSymbol ? `$${formattedPrice}` : formattedPrice;
}

/**
 * Obtiene el precio formateado de un producto
 * @param {object} product - Producto de WooCommerce
 * @returns {string} - Precio formateado (ej: "$21,900")
 */
export function getFormattedProductPrice(product) {
  const price = getProductPrice(product);
  return formatCOP(price);
}

/**
 * Verifica si un producto tiene variaciones de precio
 * @param {object} product - Producto de WooCommerce
 * @returns {boolean}
 */
export function isVariableProduct(product) {
  return product && product.type === 'variable';
}

/**
 * Verifica si un producto es simple (sin variaciones)
 * @param {object} product - Producto de WooCommerce
 * @returns {boolean}
 */
export function isSimpleProduct(product) {
  return product && product.type === 'simple';
}

