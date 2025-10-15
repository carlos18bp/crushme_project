# 📋 **ENDPOINT: Categorías Destacadas Aleatorias**

## 🎯 **Visión General**
Este endpoint obtiene 4 categorías aleatorias de las categorías principales del sitio, junto con la imagen del primer producto disponible en cada una. Está diseñado para mostrar categorías destacadas en el frontend, permitiendo a los usuarios navegar rápidamente a listas de productos mediante el slug de la categoría.

## 🔗 **URL y Método**
```
GET /api/products/woocommerce/categories/featured-random/
```

## 🔐 **Permisos**
- **Público**: No requiere autenticación (`AllowAny`).

## 📥 **Parámetros de Consulta**
No se requieren parámetros específicos. El endpoint selecciona categorías aleatoriamente en cada llamada.

## 📤 **Respuesta Exitosa**
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
      "first_product_image": "https://tienda.com/wp-content/uploads/producto1.jpg"
    },
    {
      "name": "Lencería",
      "slug": "lenceria",
      "icon": "👗",
      "category_id": 246,
      "first_product_image": "https://tienda.com/wp-content/uploads/producto2.jpg"
    },
    {
      "name": "Lubricantes y Cosmética",
      "slug": "lubricantes",
      "icon": "💧",
      "category_id": 136,
      "first_product_image": "https://tienda.com/wp-content/uploads/producto3.jpg"
    },
    {
      "name": "Bondage",
      "slug": "bondage",
      "icon": "⛓️",
      "category_id": 137,
      "first_product_image": "https://tienda.com/wp-content/uploads/producto4.jpg"
    }
  ],
  "total_selected": 4
}
```

### **Campos de la Respuesta**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | string | Nombre de la categoría en español. |
| `slug` | string | Slug único de la categoría (usado para navegar al endpoint de productos). |
| `icon` | string | Emoji representativo de la categoría. |
| `category_id` | integer | ID numérico de la categoría en WooCommerce. |
| `first_product_image` | string | URL de la imagen del primer producto disponible en la categoría. Puede estar vacía si no hay productos o imágenes. |

## 🚨 **Casos de Error**

### **500 Internal Server Error**
```json
{
  "success": false,
  "error": "Error interno del servidor",
  "details": "Descripción del error específico"
}
```
*Causa*: Problemas al conectar con WooCommerce o errores inesperados en el servidor.

### **502 Bad Gateway**
```json
{
  "success": false,
  "error": "Error obteniendo categorías de WooCommerce",
  "details": "Error específico de la API de WooCommerce"
}
```
*Causa*: Fallo en la conexión con WooCommerce (tiempo de espera, credenciales inválidas, etc.).

## 🔒 **Características de Seguridad**
- ✅ **Acceso Público**: No requiere token JWT ni autenticación.
- ✅ **Solo Lectura**: Es un endpoint de consulta, no modifica datos.
- ✅ **Límite de Datos**: Selecciona solo 4 categorías y consulta productos mínimos para optimizar rendimiento.
- ✅ **Traducción Automática**: Traduce nombres de categorías si el idioma solicitado no es español.

## 💡 **Ejemplos de Uso en Frontend**

### **1. Obtener Categorías Destacadas**
```javascript
const fetchFeaturedCategories = async () => {
  try {
    const response = await fetch('/api/products/woocommerce/categories/featured-random/');
    const data = await response.json();

    if (data.success) {
      console.log(`Categorías destacadas:`, data.data);
      // Muestra las categorías con sus imágenes en el UI
      data.data.forEach(category => {
        displayCategory({
          name: category.name,
          icon: category.icon,
          image: category.first_product_image,
          slug: category.slug  // Usa esto para navegar
        });
      });
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Error fetching categories:', error);
  }
};
```

### **2. Navegar a Productos de una Categoría**
```javascript
const navigateToCategory = (slug) => {
  // Usa el slug para llamar al endpoint existente de productos
  window.location.href = `/productos?categoria=${slug}`;
  // O haz una llamada fetch:
  // fetch(`/api/products/category/?category=${slug}`)
  //   .then(response => response.json())
  //   .then(data => displayProducts(data.products));
};
```

### **3. Mostrar en una Sección Destacada**
```javascript
const renderFeaturedSection = (categories) => {
  const section = document.getElementById('featured-categories');
  section.innerHTML = categories.map(cat => `
    <div class="category-card" onclick="navigateToCategory('${cat.slug}')">
      <img src="${cat.first_product_image || '/default-image.jpg'}" alt="${cat.name}" />
      <h3>${cat.name}</h3>
      <p>${cat.icon}</p>
    </div>
  `).join('');
};
```

## 🎯 **URLs Relacionadas**
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/products/woocommerce/categories/featured-random/` | Obtiene 4 categorías destacadas aleatorias con imágenes. |
| `GET` | `/api/products/category/?category=<slug>` | Obtiene productos de una categoría específica usando el slug. |

## ✅ **Estado de Implementación**
- **✅ Completamente Implementado**: Endpoint funcional con manejo de errores y traducción.
- **🔧 Próximas Mejoras**:
  - [ ] **Caché**: Agregar caché para reducir consultas a WooCommerce.
  - [ ] **Personalización**: Permitir filtrar categorías por parámetros (ej: tema específico).
  - [ ] **Imágenes por Defecto**: Usar imágenes placeholder si no hay productos.

## 🎊 **¡Endpoint Listo para Usar!**
Este endpoint está integrado en tu aplicación y listo para ser consumido por el frontend. Si necesitas ajustes o más funcionalidades, ¡házmelo saber! 😊
