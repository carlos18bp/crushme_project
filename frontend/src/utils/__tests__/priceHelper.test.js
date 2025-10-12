/**
 * Tests de ejemplo para priceHelper.js
 * Puedes ejecutar estos manualmente en la consola del navegador
 */

import {
  extractPriceFromShortDescription,
  getProductPrice,
  formatCOP,
  getFormattedProductPrice,
  isVariableProduct,
  isSimpleProduct
} from '../priceHelper.js';

// Ejemplo 1: HTML real de WooCommerce (formato con coma)
const exampleHTML1 = '<h5><span style="color: #333333;"><strong>Precio sugerido </strong></span><strong><span style="color: #18badb;">$21,900</span></strong></h5>';
console.log('Test 1 - Extraer precio con COMA (21,900):', extractPriceFromShortDescription(exampleHTML1));
// Esperado: 21900

// Ejemplo 2: HTML con PUNTO (formato inconsistente de "esos mkones")
const exampleHTML2 = '<h5><span style="color: #333333;"><strong>Precio sugerido </strong></span><strong><span style="color: #18badb;">$21.900</span></strong></h5>';
console.log('Test 2 - Extraer precio con PUNTO (21.900):', extractPriceFromShortDescription(exampleHTML2));
// Esperado: 21900 (mismo resultado que con coma)

// Ejemplo 3: HTML con espacios y coma
const exampleHTML3 = '<h5>Precio: $ 45,000</h5>';
console.log('Test 3 - HTML con espacios y coma:', extractPriceFromShortDescription(exampleHTML3));
// Esperado: 45000

// Ejemplo 4: HTML con espacios y PUNTO
const exampleHTML4 = '<h5>Precio: $ 45.000</h5>';
console.log('Test 4 - HTML con espacios y PUNTO:', extractPriceFromShortDescription(exampleHTML4));
// Esperado: 45000

// Ejemplo 5: HTML sin separadores
const exampleHTML5 = '<div>Precio: $12000</div>';
console.log('Test 5 - HTML sin separadores:', extractPriceFromShortDescription(exampleHTML5));
// Esperado: 12000

// Ejemplo 6: Precio con PUNTO y múltiples miles (16.000)
const exampleHTML6 = '<p>Precio: $16.000</p>';
console.log('Test 6 - Precio 16.000 (con punto):', extractPriceFromShortDescription(exampleHTML6));
// Esperado: 16000

// Ejemplo 7: Precio con COMA y múltiples miles (16,000)
const exampleHTML7 = '<p>Precio: $16,000</p>';
console.log('Test 7 - Precio 16,000 (con coma):', extractPriceFromShortDescription(exampleHTML7));
// Esperado: 16000

console.log('\n=== TESTS DE PRODUCTOS COMPLETOS ===\n')

// Ejemplo 8: Producto simple completo
const simpleProduct = {
  id: 123,
  name: 'Producto Test',
  type: 'simple',
  short_description: exampleHTML1,
  price: '15000', // Precio mayorista (no usar)
  regular_price: '15000'
};

console.log('Test 8 - Producto simple:', {
  price: getProductPrice(simpleProduct),
  formatted: getFormattedProductPrice(simpleProduct),
  isSimple: isSimpleProduct(simpleProduct),
  isVariable: isVariableProduct(simpleProduct)
});
// Esperado: price: 21900, formatted: "$21,900", isSimple: true, isVariable: false

// Ejemplo 9: Producto variable
const variableProduct = {
  id: 456,
  name: 'Producto Variable',
  type: 'variable',
  short_description: '<p>Precio desde <strong>$30,500</strong></p>',
  price: '20000' // Precio mayorista (no usar)
};

console.log('Test 9 - Producto variable:', {
  price: getProductPrice(variableProduct),
  formatted: getFormattedProductPrice(variableProduct),
  isSimple: isSimpleProduct(variableProduct),
  isVariable: isVariableProduct(variableProduct)
});
// Esperado: price: 30500, formatted: "$30,500", isSimple: false, isVariable: true

// Ejemplo 10: Formateo de precios
console.log('Test 10 - Formateo COP:', {
  con_simbolo: formatCOP(21900, true),
  sin_simbolo: formatCOP(21900, false),
  precio_alto: formatCOP(1500000, true),
  cero: formatCOP(0, true)
});
// Esperado: "$21,900", "21,900", "$1,500,000", "$0"

// Ejemplo 11: Caso sin short_description (fallback)
const productSinShortDesc = {
  id: 789,
  name: 'Sin Short Description',
  type: 'simple',
  price: '18500'
};

console.log('Test 11 - Fallback a precio mayorista:', {
  price: getProductPrice(productSinShortDesc),
  formatted: getFormattedProductPrice(productSinShortDesc)
});
// Esperado: price: 18500, formatted: "$18,500" (con warning en consola)

// Ejemplo 12: Producto inválido
const productInvalido = null;
console.log('Test 12 - Producto inválido:', getProductPrice(productInvalido));
// Esperado: null

console.log('\n✅ Tests de priceHelper completados. Revisa los resultados arriba.');

