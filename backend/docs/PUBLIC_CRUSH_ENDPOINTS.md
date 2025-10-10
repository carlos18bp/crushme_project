# API Pública de Crushes - CrushMe

**Versión:** 1.0.0  
**Última actualización:** 10 de Octubre, 2025

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Detalles de Endpoints](#detalles-de-endpoints)
   - [1. Perfil Público por Username](#1-perfil-público-por-username)
   - [2. Crush Aleatorio (Completo)](#2-crush-aleatorio-completo)
   - [3. 7 Crushes Aleatorios (Carousel)](#3-7-crushes-aleatorios-carousel)
   - [4. Lista de Crushes (Paginada)](#4-lista-de-crushes-paginada)
   - [5. Búsqueda de Usuarios](#5-búsqueda-de-usuarios)
4. [Tipos de Respuesta](#tipos-de-respuesta)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Casos de Uso Comunes](#casos-de-uso-comunes)

---

## Introducción

Esta API proporciona endpoints públicos (sin autenticación requerida) para acceder a perfiles de usuarios y explorar Crushes (webcammers verificados) en la plataforma CrushMe.

### Características Principales

- ✅ **Sin autenticación requerida** - Todos los endpoints son públicos
- ✅ **Múltiples niveles de detalle** - Desde datos básicos hasta perfiles completos
- ✅ **Optimizado para diferentes casos de uso** - Cards, carousels, búsqueda, etc.
- ✅ **URLs completas para imágenes** - Listas para usar en el frontend
- ✅ **Paginación incluida** - Para listados grandes

---

## Endpoints Disponibles

| Endpoint | Método | URL | Descripción |
|----------|--------|-----|-------------|
| **Perfil por Username** | GET | `/api/auth/public/@{username}/` | Perfil completo de cualquier usuario |
| **Crush Aleatorio** | GET | `/api/auth/crush/random/` | 1 Crush aleatorio con perfil completo |
| **7 Crushes Aleatorios** | GET | `/api/auth/crush/random-7/` | 7 Crushes para carousel/grid |
| **Lista de Crushes** | GET | `/api/auth/crush/list/` | Lista paginada de todos los Crushes |
| **Búsqueda** | GET | `/api/auth/search/` | Buscar usuarios por username |

---

## Detalles de Endpoints

### 1. Perfil Público por Username

Obtiene el perfil completo de cualquier usuario (Crush o no) por su username.

**URL:** `GET /api/auth/public/@{username}/`

**Parámetros de URL:**
- `username` (string, requerido): El username del usuario

**Autenticación:** No requerida

**Respuesta exitosa (200):**

```json
{
  "success": true,
  "data": {
    "id": 2,
    "username": "cerrotico",
    "about": "Webcammer profesional con 3 años de experiencia",
    "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/09/foto.jpg",
    "cover_image_url": "http://localhost:8000/media/cover_images/2025/10/09/portada.jpg",
    "current_status": "Online",
    "note": "¡Estoy en vivo! Ven a visitarme 💕",
    "gallery_photos": [
      {
        "id": 1,
        "image": "http://localhost:8000/media/gallery/2025/10/09/photo1.jpg",
        "caption": "Mi setup",
        "is_profile_picture": false,
        "order": 1,
        "created_at": "2025-10-09T15:30:00Z"
      }
    ],
    "links": [
      {
        "id": 1,
        "platform": "Instagram",
        "url": "https://instagram.com/cerrotico",
        "order": 1
      },
      {
        "id": 2,
        "platform": "Twitter",
        "url": "https://twitter.com/cerrotico",
        "order": 2
      }
    ],
    "public_wishlists": [
      {
        "id": 1,
        "name": "Mi Lista de Deseos",
        "description": "Cosas que me encantan",
        "user": {
          "id": 2,
          "username": "cerrotico",
          "email": "dev.gustavo.perezp@gmail.com",
          "full_name": "Gustavo Adolfo Pérez Pérez"
        },
        "user_username": "cerrotico",
        "is_active": true,
        "is_public": true,
        "unique_link": "52b3946a-6d38-4d09-b696-097352274c7c",
        "public_url": "http://localhost:5173/@cerrotico/1",
        "shareable_path": "/@cerrotico/1",
        "items": [
          {
            "id": 1,
            "woocommerce_product_id": 19397,
            "product_name": "Lubricante Íntimo Saborizado Action Lube",
            "product_price": 6890.0,
            "product_image": "https://ejemplo.com/producto.jpg",
            "product_info": {
              "name": "Lubricante Íntimo Saborizado Action Lube",
              "price": "6890",
              "regular_price": "",
              "sale_price": "",
              "images": [
                {
                  "src": "https://ejemplo.com/producto.jpg"
                }
              ],
              "stock_status": "instock",
              "stock_quantity": 10
            },
            "notes": "Me encanta este producto",
            "priority": "high",
            "created_at": "2025-10-03T20:00:00Z"
          }
        ],
        "total_items": 1,
        "total_value": 6890.0,
        "is_favorited": false,
        "favorites_count": 5,
        "shipping_data": {},
        "shipping_name": "",
        "shipping_address": "",
        "shipping_phone": "",
        "shipping_email": "",
        "created_at": "2025-10-03T19:42:44Z",
        "updated_at": "2025-10-09T10:15:00Z"
      }
    ],
    "is_crush": true,
    "crush_verified_at": "2025-10-10T05:02:18Z"
  }
}
```

**Respuesta de error (404):**

```json
{
  "success": false,
  "error": "User not found."
}
```

**Campos del Perfil Completo:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del usuario |
| `username` | string | Nombre de usuario |
| `about` | string | Biografía del usuario |
| `profile_picture_url` | string/null | URL completa de la foto de perfil |
| `cover_image_url` | string/null | URL completa de la imagen de portada |
| `current_status` | string | Estado actual (Online, Busy, Away, etc.) |
| `note` | string | Nota o mensaje personal |
| `gallery_photos` | array | Fotos de la galería del usuario |
| `links` | array | Enlaces a redes sociales |
| `public_wishlists` | array | **Wishlists públicas del usuario** (solo `is_public=true` y `is_active=true`) |
| `is_crush` | boolean | Si es un Crush verificado |
| `crush_verified_at` | string/null | Fecha de verificación como Crush |

**Campos de cada Wishlist Pública:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único de la wishlist |
| `name` | string | Nombre de la wishlist |
| `description` | string | Descripción de la wishlist |
| `user` | object | Información completa del dueño de la wishlist |
| `user_username` | string | Username del dueño (o email si no tiene username) |
| `is_active` | boolean | Si la wishlist está activa (siempre `true`) |
| `is_public` | boolean | Si la wishlist es pública (siempre `true`) |
| `unique_link` | string (UUID) | Link único para compartir la wishlist |
| `public_url` | string | URL completa para acceder a la wishlist |
| `shareable_path` | string | Path relativo para el frontend (ej: `/@username/1`) |
| **`items`** | **array** | **Array de productos/items completos de la wishlist** |
| `total_items` | integer | Cantidad total de items en la wishlist |
| `total_value` | float | Valor total de todos los items |
| `is_favorited` | boolean | Si está marcada como favorita (requiere autenticación) |
| `favorites_count` | integer | Número de usuarios que marcaron como favorita |
| `shipping_data` | object | Datos de envío (JSON) |
| `shipping_name` | string | Nombre para envío |
| `shipping_address` | string | Dirección de envío |
| `shipping_phone` | string | Teléfono de envío |
| `shipping_email` | string | Email de envío |
| `created_at` | string | Fecha de creación en formato ISO 8601 |
| `updated_at` | string | Última fecha de actualización |

**Campos de cada Item/Producto dentro de `items`:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del item en la wishlist |
| `woocommerce_product_id` | integer | ID del producto en WooCommerce |
| `product_name` | string | Nombre del producto |
| `product_price` | float | Precio del producto |
| `product_image` | string/null | URL de la imagen del producto |
| `product_info` | object | Información completa del producto desde WooCommerce |
| `notes` | string | Notas personales sobre el item |
| `priority` | string | Prioridad: `low`, `medium`, o `high` |
| `created_at` | string | Fecha cuando se agregó el item |

**Campos dentro de `product_info` (datos de WooCommerce):**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | string | Nombre del producto en WooCommerce |
| `price` | string | Precio actual |
| `regular_price` | string | Precio regular |
| `sale_price` | string | Precio en oferta (si aplica) |
| `images` | array | Array de imágenes del producto |
| `stock_status` | string | Estado del stock: `instock`, `outofstock`, etc. |
| `stock_quantity` | integer/null | Cantidad disponible en stock |

---

### 2. Crush Aleatorio (Completo)

Devuelve el perfil completo de un Crush aleatorio, incluyendo sus **wishlists públicas**.

**URL:** `GET /api/auth/crush/random/`

**Autenticación:** No requerida

**Respuesta exitosa (200):**

```json
{
  "success": true,
  "data": {
    "id": 5,
    "username": "sophia_crush",
    "about": "Live streaming every day! 🎥",
    "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/10/sophia.jpg",
    "cover_image_url": "http://localhost:8000/media/cover_images/2025/10/10/sophia_banner.jpg",
    "current_status": "Online",
    "note": "Ready to make your day! 💖",
    "gallery_photos": [],
    "links": [
      {
        "id": 1,
        "platform": "Instagram",
        "url": "https://instagram.com/sophia_crush",
        "order": 1
      }
    ],
    "public_wishlists": [
      {
        "id": 3,
        "name": "Mis Favoritos ❤️",
        "description": "Cosas que me gustaría recibir",
        "user": {
          "id": 5,
          "username": "sophia_crush",
          "full_name": "Sophia Martinez"
        },
        "user_username": "sophia_crush",
        "is_active": true,
        "is_public": true,
        "unique_link": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "public_url": "http://localhost:5173/@sophia_crush/3",
        "shareable_path": "/@sophia_crush/3",
        "items": [
          {
            "id": 5,
            "woocommerce_product_id": 12345,
            "product_name": "Set de Lencería Elegante",
            "product_price": 35000.0,
            "product_image": "https://ejemplo.com/lenceria.jpg",
            "product_info": {
              "name": "Set de Lencería Elegante",
              "price": "35000",
              "regular_price": "45000",
              "sale_price": "35000",
              "images": [
                {
                  "src": "https://ejemplo.com/lenceria.jpg"
                }
              ],
              "stock_status": "instock",
              "stock_quantity": 5
            },
            "notes": "Talla M, color negro preferido",
            "priority": "high",
            "created_at": "2025-10-01T11:00:00Z"
          },
          {
            "id": 6,
            "woocommerce_product_id": 67890,
            "product_name": "Perfume Floral 50ml",
            "product_price": 10000.0,
            "product_image": "https://ejemplo.com/perfume.jpg",
            "product_info": {
              "name": "Perfume Floral 50ml",
              "price": "10000",
              "regular_price": "10000",
              "sale_price": "",
              "images": [
                {
                  "src": "https://ejemplo.com/perfume.jpg"
                }
              ],
              "stock_status": "instock",
              "stock_quantity": 15
            },
            "notes": "",
            "priority": "medium",
            "created_at": "2025-10-01T11:30:00Z"
          }
        ],
        "total_items": 2,
        "total_value": 45000.0,
        "is_favorited": false,
        "favorites_count": 12,
        "shipping_data": {},
        "shipping_name": "",
        "shipping_address": "",
        "shipping_phone": "",
        "shipping_email": "",
        "created_at": "2025-10-01T10:30:00Z",
        "updated_at": "2025-10-01T11:30:00Z"
      }
    ],
    "is_crush": true,
    "crush_verified_at": "2025-10-05T12:00:00Z"
  }
}
```

**Respuesta de error (404):**

```json
{
  "success": false,
  "error": "No verified Crushes found."
}
```

**Uso típico:**
- Botón "Sorpréndeme" con perfil completo
- Página de "Crush del Día"
- Exploración individual de Crushes

---

### 3. 7 Crushes Aleatorios (Carousel)

Devuelve exactamente 7 Crushes aleatorios con información optimizada para cards/carousel.

**URL:** `GET /api/auth/crush/random-7/`

**Autenticación:** No requerida

**Respuesta exitosa (200):**

```json
{
  "success": true,
  "count": 7,
  "results": [
    {
      "id": 14,
      "username": "emma_cam",
      "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/10/emma.jpg",
      "current_status": "Busy",
      "note": "Live now! Join me 🔥",
      "is_crush": true
    },
    {
      "id": 13,
      "username": "sophia_crush",
      "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/10/sophia.jpg",
      "current_status": "Online",
      "note": "Ready to make your day! 💖",
      "is_crush": true
    },
    {
      "id": 15,
      "username": "olivia_star",
      "profile_picture_url": null,
      "current_status": "Online",
      "note": "Your favorite webcammer ⭐",
      "is_crush": true
    }
    // ... 4 más
  ]
}
```

**Respuesta de error (404):**

```json
{
  "success": false,
  "error": "No verified Crushes found."
}
```

**Campos de Crush Card:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del Crush |
| `username` | string | Nombre de usuario |
| `profile_picture_url` | string/null | URL completa de la foto de perfil |
| `current_status` | string | Estado actual (Online, Busy, etc.) |
| `note` | string | Mensaje o nota del Crush |
| `is_crush` | boolean | Siempre `true` |

**Características:**
- ✅ Siempre devuelve 7 Crushes (o menos si no hay suficientes)
- ✅ Orden aleatorio en cada petición
- ✅ Optimizado para carousels y grids
- ✅ Datos ligeros (sin galería ni wishlists)

**Uso típico:**
- 🎠 Carousel de homepage
- 📱 Grid de Crushes destacados
- 🔍 Sección "Descubre Crushes"
- 🎲 Recomendaciones aleatorias

---

### 4. Lista de Crushes (Paginada)

Lista completa de todos los Crushes verificados con paginación.

**URL:** `GET /api/auth/crush/list/`

**Query Parameters:**

| Parámetro | Tipo | Requerido | Default | Max | Descripción |
|-----------|------|-----------|---------|-----|-------------|
| `limit` | integer | No | 50 | 100 | Número de resultados por página |
| `offset` | integer | No | 0 | - | Número de resultados a saltar |

**Autenticación:** No requerida

**Ejemplo de uso:**
```
GET /api/auth/crush/list/
GET /api/auth/crush/list/?limit=20
GET /api/auth/crush/list/?limit=20&offset=20
GET /api/auth/crush/list/?limit=20&offset=40
```

**Respuesta exitosa (200):**

```json
{
  "success": true,
  "count": 20,
  "total": 156,
  "offset": 0,
  "limit": 20,
  "results": [
    {
      "id": 2,
      "username": "alice_cam",
      "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/09/alice.jpg",
      "is_crush": true
    },
    {
      "id": 8,
      "username": "bella_crush",
      "profile_picture_url": null,
      "is_crush": true
    }
    // ... 18 más
  ]
}
```

**Campos de respuesta:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `success` | boolean | Indica si la petición fue exitosa |
| `count` | integer | Número de resultados devueltos en esta página |
| `total` | integer | Número total de Crushes en la plataforma |
| `offset` | integer | Offset usado en la petición |
| `limit` | integer | Límite usado en la petición |
| `results` | array | Array de Crushes |

**Campos de cada Crush:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del Crush |
| `username` | string | Nombre de usuario |
| `profile_picture_url` | string/null | URL completa de la foto de perfil |
| `is_crush` | boolean | Siempre `true` |

**Cálculo de paginación en el frontend:**

```javascript
// Calcular número total de páginas
const totalPages = Math.ceil(response.total / response.limit);

// Calcular página actual
const currentPage = Math.floor(response.offset / response.limit) + 1;

// Verificar si hay página siguiente
const hasNextPage = (response.offset + response.count) < response.total;

// Verificar si hay página anterior
const hasPrevPage = response.offset > 0;

// Offset para siguiente página
const nextOffset = response.offset + response.limit;

// Offset para página anterior
const prevOffset = Math.max(0, response.offset - response.limit);
```

**Uso típico:**
- 📋 Directorio completo de Crushes
- 🔍 Catálogo de webcammers
- 📱 Lista paginada en la app
- 🗂️ Explorar todos los Crushes

---

### 5. Búsqueda de Usuarios

Busca usuarios por username con coincidencia parcial.

**URL:** `GET /api/auth/search/`

**Query Parameters:**

| Parámetro | Tipo | Requerido | Default | Max | Descripción |
|-----------|------|-----------|---------|-----|-------------|
| `q` | string | **Sí** | - | - | Texto de búsqueda (username) |
| `limit` | integer | No | 20 | 50 | Número máximo de resultados |

**Autenticación:** No requerida

**Ejemplo de uso:**
```
GET /api/auth/search/?q=maria
GET /api/auth/search/?q=sophia&limit=10
GET /api/auth/search/?q=cam
```

**Respuesta exitosa (200):**

```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "id": 6,
      "username": "maria_crush",
      "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/09/maria.jpg",
      "is_crush": true
    },
    {
      "id": 5,
      "username": "maria",
      "profile_picture_url": null,
      "is_crush": false
    },
    {
      "id": 7,
      "username": "mariana",
      "profile_picture_url": "http://localhost:8000/media/profile_pictures/2025/10/09/mariana.jpg",
      "is_crush": false
    }
  ]
}
```

**Respuesta sin query (400):**

```json
{
  "success": false,
  "error": "Search query parameter \"q\" is required."
}
```

**Respuesta sin resultados (200):**

```json
{
  "success": true,
  "count": 0,
  "results": []
}
```

**Características:**
- ✅ Búsqueda **case-insensitive** (no distingue mayúsculas)
- ✅ Coincidencia **parcial** (busca "mar" encuentra "maria", "mario", "mariana")
- ✅ Resultados ordenados: **Crushes primero**, luego por username
- ✅ Incluye tanto Crushes como usuarios normales

**Campos de cada resultado:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del usuario |
| `username` | string | Nombre de usuario |
| `profile_picture_url` | string/null | URL completa de la foto de perfil |
| `is_crush` | boolean | Si es un Crush verificado |

**Uso típico:**
- 🔍 Barra de búsqueda
- 👤 Autocompletado de usuarios
- 🔎 Encontrar usuarios específicos
- 📱 Búsqueda en tiempo real

---

## Tipos de Respuesta

### Respuesta Completa (Full Profile)

**Endpoints:** Perfil por Username, Crush Aleatorio

**Incluye:**
- ✅ Información básica (username, about)
- ✅ Imágenes (profile_picture_url, cover_image_url)
- ✅ Estado y nota (current_status, note)
- ✅ Galería de fotos
- ✅ Enlaces a redes sociales
- ✅ **Wishlists públicas** (con detalles completos: items, valor total, etc.)
- ✅ Información de Crush (is_crush, crush_verified_at)

**Wishlists incluidas:**
- Solo wishlists marcadas como `is_public=true`
- Solo wishlists activas (`is_active=true`)
- **Incluye todos los productos/items completos con sus datos de WooCommerce**
- Cada producto incluye: nombre, precio, imagen, stock, información completa
- Cada wishlist incluye: información del dueño, estadísticas, datos de envío, favoritos

**Tamaño:** ~5-50 KB dependiendo del número de wishlists y productos por wishlist

**⚠️ Nota de rendimiento:** Si un Crush tiene muchas wishlists o muchos productos, considera paginar o limitar la cantidad mostrada inicialmente

**Uso:** Páginas de perfil completo, detalles de Crush, ver listas de deseos

---

### Respuesta Card

**Endpoints:** 7 Crushes Aleatorios

**Incluye:**
- ✅ Información básica (id, username)
- ✅ Foto de perfil (profile_picture_url)
- ✅ Estado y nota (current_status, note)
- ✅ Flag de Crush (is_crush)

**Tamaño:** ~500 bytes por Crush

**Uso:** Carousels, grids, tarjetas de preview

---

### Respuesta Básica

**Endpoints:** Lista de Crushes, Búsqueda

**Incluye:**
- ✅ Información mínima (id, username)
- ✅ Foto de perfil (profile_picture_url)
- ✅ Flag de Crush (is_crush)

**Tamaño:** ~200 bytes por usuario

**Uso:** Listados, búsquedas, resultados múltiples

---

## Ejemplos de Uso

### React / Next.js

#### 1. Carousel de 7 Crushes

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function CrushCarousel() {
  const [crushes, setCrushes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCrushes = async () => {
      try {
        const response = await axios.get('/api/auth/crush/random-7/');
        setCrushes(response.data.results);
      } catch (error) {
        console.error('Error fetching crushes:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCrushes();
  }, []);

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="crush-carousel">
      {crushes.map(crush => (
        <div key={crush.id} className="crush-card">
          <img 
            src={crush.profile_picture_url || '/default-avatar.png'} 
            alt={crush.username}
          />
          <h3>{crush.username}</h3>
          <span className="status">{crush.current_status}</span>
          <p>{crush.note}</p>
          {crush.is_crush && <span className="badge">✓ Crush</span>}
        </div>
      ))}
    </div>
  );
}
```

#### 2. Perfil Público

```jsx
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function PublicProfile() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`/api/auth/public/@${username}/`);
        setProfile(response.data.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Usuario no encontrado');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [username]);

  if (loading) return <div>Cargando perfil...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="profile">
      <div 
        className="cover" 
        style={{ backgroundImage: `url(${profile.cover_image_url})` }}
      />
      <img 
        src={profile.profile_picture_url || '/default-avatar.png'} 
        alt={profile.username}
        className="avatar"
      />
      <h1>{profile.username}</h1>
      {profile.is_crush && <span className="crush-badge">✓ Verified Crush</span>}
      
      <div className="status-note">
        <span className="status">{profile.current_status}</span>
        <p>{profile.note}</p>
      </div>

      <div className="about">
        <h2>Acerca de</h2>
        <p>{profile.about}</p>
      </div>

      {profile.links.length > 0 && (
        <div className="social-links">
          <h3>Redes Sociales</h3>
          {profile.links.map(link => (
            <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer">
              {link.platform}
            </a>
          ))}
        </div>
      )}

      {profile.gallery_photos.length > 0 && (
        <div className="gallery">
          <h3>Galería</h3>
          <div className="gallery-grid">
            {profile.gallery_photos.map(photo => (
              <img key={photo.id} src={photo.image} alt={photo.caption} />
            ))}
          </div>
        </div>
      )}

      {profile.public_wishlists.length > 0 && (
        <div className="wishlists">
          <h3>Listas de Deseos Públicas</h3>
          {profile.public_wishlists.map(wishlist => (
            <div key={wishlist.id} className="wishlist-card">
              <h4>{wishlist.name}</h4>
              <p>{wishlist.description}</p>
              <div className="wishlist-stats">
                <span className="items-count">
                  📦 {wishlist.total_items} items
                </span>
                <span className="total-value">
                  💰 ${wishlist.total_value.toLocaleString()}
                </span>
                <span className="favorites">
                  ❤️ {wishlist.favorites_count} favoritos
                </span>
              </div>
              
              {/* Mostrar items/productos de la wishlist */}
              <div className="wishlist-items">
                <h5>Productos:</h5>
                {wishlist.items.map(item => (
                  <div key={item.id} className="product-item">
                    <img 
                      src={item.product_image || '/default-product.png'} 
                      alt={item.product_name}
                      className="product-image"
                    />
                    <div className="product-details">
                      <h6>{item.product_name}</h6>
                      <p className="product-price">
                        ${item.product_price.toLocaleString()}
                      </p>
                      {item.product_info.sale_price && (
                        <span className="sale-badge">
                          ¡En Oferta! Antes: ${item.product_info.regular_price}
                        </span>
                      )}
                      {item.notes && (
                        <p className="item-notes">
                          📝 {item.notes}
                        </p>
                      )}
                      <span className={`priority-badge priority-${item.priority}`}>
                        {item.priority === 'high' ? '⭐ Alta' : 
                         item.priority === 'medium' ? '🔸 Media' : '🔹 Baja'}
                      </span>
                      <span className={`stock-badge ${item.product_info.stock_status}`}>
                        {item.product_info.stock_status === 'instock' ? 
                          `✓ En stock (${item.product_info.stock_quantity})` : 
                          '✗ Agotado'}
                      </span>
                      <a 
                        href={`/producto/${item.woocommerce_product_id}`}
                        className="buy-product-btn"
                      >
                        Comprar →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
              
              <small>Creada el {new Date(wishlist.created_at).toLocaleDateString()}</small>
              <a 
                href={wishlist.shareable_path}
                className="view-wishlist-btn"
              >
                Ver Lista Completa →
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### 3. Búsqueda de Usuarios

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import { debounce } from 'lodash';

function UserSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchUsers = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get('/api/auth/search/', {
        params: { q: searchQuery, limit: 10 }
      });
      setResults(response.data.results);
    } catch (error) {
      console.error('Error searching users:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Debounce para no hacer request en cada tecla
  const debouncedSearch = debounce(searchUsers, 300);

  useEffect(() => {
    debouncedSearch(query);
    return () => debouncedSearch.cancel();
  }, [query]);

  return (
    <div className="user-search">
      <input
        type="text"
        placeholder="Buscar usuarios..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      {loading && <div>Buscando...</div>}

      <div className="search-results">
        {results.map(user => (
          <div key={user.id} className="user-result">
            <img 
              src={user.profile_picture_url || '/default-avatar.png'} 
              alt={user.username}
            />
            <span>{user.username}</span>
            {user.is_crush && <span className="crush-badge">✓</span>}
          </div>
        ))}
      </div>

      {!loading && query && results.length === 0 && (
        <div>No se encontraron usuarios</div>
      )}
    </div>
  );
}
```

#### 4. Lista Paginada de Crushes

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function CrushList() {
  const [crushes, setCrushes] = useState([]);
  const [pagination, setPagination] = useState({
    total: 0,
    offset: 0,
    limit: 20
  });
  const [loading, setLoading] = useState(true);

  const fetchCrushes = async (offset = 0) => {
    setLoading(true);
    try {
      const response = await axios.get('/api/auth/crush/list/', {
        params: { limit: pagination.limit, offset }
      });
      
      setCrushes(response.data.results);
      setPagination({
        total: response.data.total,
        offset: response.data.offset,
        limit: response.data.limit
      });
    } catch (error) {
      console.error('Error fetching crushes:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCrushes();
  }, []);

  const currentPage = Math.floor(pagination.offset / pagination.limit) + 1;
  const totalPages = Math.ceil(pagination.total / pagination.limit);
  const hasNextPage = (pagination.offset + crushes.length) < pagination.total;
  const hasPrevPage = pagination.offset > 0;

  const goToPage = (page) => {
    const newOffset = (page - 1) * pagination.limit;
    fetchCrushes(newOffset);
  };

  const nextPage = () => {
    if (hasNextPage) {
      fetchCrushes(pagination.offset + pagination.limit);
    }
  };

  const prevPage = () => {
    if (hasPrevPage) {
      fetchCrushes(Math.max(0, pagination.offset - pagination.limit));
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="crush-list">
      <h2>Todos los Crushes ({pagination.total})</h2>

      <div className="crush-grid">
        {crushes.map(crush => (
          <div key={crush.id} className="crush-card">
            <img 
              src={crush.profile_picture_url || '/default-avatar.png'} 
              alt={crush.username}
            />
            <h3>{crush.username}</h3>
            <span className="crush-badge">✓ Verified</span>
          </div>
        ))}
      </div>

      <div className="pagination">
        <button onClick={prevPage} disabled={!hasPrevPage}>
          ← Anterior
        </button>
        
        <span>
          Página {currentPage} de {totalPages}
        </span>
        
        <button onClick={nextPage} disabled={!hasNextPage}>
          Siguiente →
        </button>
      </div>
    </div>
  );
}
```

---

### Vue.js

#### Carousel de Crushes

```vue
<template>
  <div class="crush-carousel">
    <div v-if="loading">Cargando...</div>
    <div v-else class="carousel-container">
      <div 
        v-for="crush in crushes" 
        :key="crush.id" 
        class="crush-card"
      >
        <img 
          :src="crush.profile_picture_url || '/default-avatar.png'" 
          :alt="crush.username"
        />
        <h3>{{ crush.username }}</h3>
        <span class="status">{{ crush.current_status }}</span>
        <p>{{ crush.note }}</p>
        <span v-if="crush.is_crush" class="badge">✓ Crush</span>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CrushCarousel',
  data() {
    return {
      crushes: [],
      loading: true
    };
  },
  async mounted() {
    try {
      const response = await axios.get('/api/auth/crush/random-7/');
      this.crushes = response.data.results;
    } catch (error) {
      console.error('Error fetching crushes:', error);
    } finally {
      this.loading = false;
    }
  }
};
</script>
```

---

### JavaScript Vanilla

#### Obtener y Mostrar Crushes

```javascript
// Función para obtener 7 crushes aleatorios
async function fetchRandomCrushes() {
  try {
    const response = await fetch('/api/auth/crush/random-7/');
    const data = await response.json();
    
    if (data.success) {
      displayCrushes(data.results);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Función para mostrar crushes en el DOM
function displayCrushes(crushes) {
  const container = document.getElementById('crush-container');
  container.innerHTML = '';
  
  crushes.forEach(crush => {
    const card = document.createElement('div');
    card.className = 'crush-card';
    card.innerHTML = `
      <img src="${crush.profile_picture_url || '/default-avatar.png'}" alt="${crush.username}">
      <h3>${crush.username}</h3>
      <span class="status">${crush.current_status}</span>
      <p>${crush.note}</p>
      ${crush.is_crush ? '<span class="badge">✓ Crush</span>' : ''}
    `;
    container.appendChild(card);
  });
}

// Llamar la función al cargar la página
document.addEventListener('DOMContentLoaded', fetchRandomCrushes);
```

---

## Casos de Uso Comunes

### 1. Homepage con Crushes Destacados

```
Objetivo: Mostrar 7 Crushes aleatorios en la página principal

Endpoint: GET /api/auth/crush/random-7/

Flujo:
1. Al cargar la página, hacer request al endpoint
2. Mostrar los 7 Crushes en un carousel o grid
3. Cada Crush muestra: foto, username, status, nota
4. Click en un Crush lleva a su perfil completo

Refresh: Cada vez que se carga la página se obtienen Crushes diferentes
```

### 2. Perfil Público de Usuario

```
Objetivo: Mostrar el perfil completo de un usuario específico

Endpoint: GET /api/auth/public/@{username}/

Flujo:
1. Usuario navega a /@username
2. Frontend hace request con el username
3. Mostrar perfil completo: cover, foto, bio, galería, links, wishlists
4. Indicar si es Crush verificado

URL ejemplo: yourapp.com/@cerrotico
```

### 3. Directorio de Crushes

```
Objetivo: Listar todos los Crushes con paginación

Endpoint: GET /api/auth/crush/list/?limit=20&offset=0

Flujo:
1. Mostrar primera página de Crushes (20 por defecto)
2. Usuario puede navegar entre páginas
3. Mostrar contador: "Mostrando 1-20 de 156 Crushes"
4. Botones de Anterior/Siguiente
5. Click en un Crush lleva a su perfil

Paginación: 
- Página 1: offset=0
- Página 2: offset=20
- Página 3: offset=40
```

### 4. Búsqueda de Usuarios

```
Objetivo: Permitir buscar usuarios por username

Endpoint: GET /api/auth/search/?q={query}&limit=10

Flujo:
1. Usuario escribe en barra de búsqueda
2. Después de 300ms sin escribir, hacer request
3. Mostrar resultados con foto y username
4. Indicar cuáles son Crushes verificados
5. Click en resultado lleva a su perfil

Optimización: Usar debounce para evitar requests excesivos
```

### 5. Botón "Sorpréndeme"

```
Objetivo: Mostrar un Crush aleatorio completo

Endpoint: GET /api/auth/crush/random/

Flujo:
1. Usuario hace click en "Sorpréndeme"
2. Hacer request al endpoint
3. Mostrar perfil completo del Crush aleatorio
4. Incluir botón "Otro Crush" para obtener uno nuevo

Diferencia con random-7: Este devuelve 1 Crush con datos completos
```

### 6. Explorar Crushes (Infinite Scroll)

```
Objetivo: Lista infinita de Crushes al hacer scroll

Endpoint: GET /api/auth/crush/list/?limit=20&offset={offset}

Flujo:
1. Cargar primeros 20 Crushes (offset=0)
2. Al llegar al final, cargar siguientes 20 (offset=20)
3. Continuar cargando al hacer scroll
4. Mostrar "Cargando más..." mientras se obtienen datos

Implementación:
- Usar Intersection Observer
- Incrementar offset en múltiplos de limit
- Parar cuando se alcance el total
```

---

## Notas Importantes

### Wishlists Públicas

**Solo en endpoints Full Profile:**
- Los endpoints que devuelven perfiles completos (`public/@{username}` y `crush/random`) incluyen las **wishlists públicas**
- Los endpoints de cards y listados NO incluyen wishlists (para mantener respuestas ligeras)

**Filtros aplicados automáticamente:**
- Solo wishlists con `is_public=true`
- Solo wishlists con `is_active=true`
- Las wishlists privadas NUNCA se muestran en endpoints públicos

**Información incluida de cada wishlist:**
- Datos básicos (id, name, description)
- Información del propietario (user object)
- **Productos/items completos con toda su información**
- Estadísticas (total_items, total_value)
- Información de envío (shipping_data)
- Contadores sociales (favorites_count, is_favorited)
- Fechas (created_at, updated_at)
- URLs compartibles (public_url, shareable_path)

**Información de cada producto/item:**
- Datos del producto (nombre, precio, imagen)
- ID de WooCommerce para enlazar a la tienda
- Información completa del producto desde WooCommerce (stock, imágenes, precios)
- Notas personales del usuario sobre el producto
- Prioridad (alta, media, baja)

**Uso típico:**
- Mostrar las listas de deseos completas del Crush en su perfil
- Permitir que los fans vean exactamente qué productos quiere recibir
- Mostrar imágenes, precios y disponibilidad de cada producto
- Links directos para comprar cada producto en WooCommerce
- Mostrar ofertas y descuentos disponibles
- Indicar prioridades del Crush (qué quiere más)

### Rendimiento

1. **Caching**: Considera cachear los resultados de `/crush/random-7/` por algunos minutos
2. **Lazy Loading**: Carga las imágenes con lazy loading para mejor rendimiento
3. **Debouncing**: En búsqueda, usa debounce de 300-500ms para evitar requests excesivos
4. **Paginación**: Para listas largas, usa paginación en lugar de cargar todo
5. **Wishlists**: Si un Crush tiene muchas wishlists públicas, considera mostrar solo las primeras 3-5 y un botón "Ver más"

### URLs de Imágenes

- Todas las URLs de imágenes son **absolutas** y listas para usar
- Si una imagen es `null`, usa una imagen por defecto
- Las URLs incluyen el dominio del backend (ej: `http://localhost:8000`)

### Manejo de Errores

```javascript
try {
  const response = await axios.get('/api/auth/crush/random-7/');
  // Procesar respuesta...
} catch (error) {
  if (error.response?.status === 404) {
    console.log('No hay Crushes disponibles');
  } else {
    console.error('Error al cargar Crushes:', error);
  }
}
```

### SEO y Meta Tags

Para perfiles públicos, genera meta tags dinámicos:

```html
<meta property="og:title" content="@username | CrushMe" />
<meta property="og:description" content="Bio del usuario..." />
<meta property="og:image" content="URL de profile_picture" />
<meta property="og:type" content="profile" />
```

---

## Resumen: ¿Qué Endpoints Incluyen Wishlists?

| Endpoint | Wishlists | Razón |
|----------|-----------|-------|
| `public/@{username}` | ✅ **SÍ** | Perfil completo con todas las wishlists públicas |
| `crush/random` | ✅ **SÍ** | Perfil completo de Crush aleatorio |
| `crush/random-7` | ❌ No | Respuesta ligera tipo "card" para carousels |
| `crush/list` | ❌ No | Listado básico para performance |
| `search` | ❌ No | Resultados de búsqueda minimalistas |

**Nota:** Solo los endpoints que devuelven **perfiles completos** incluyen wishlists públicas.

---

## Changelog

### v1.1.0 (2025-10-10)
- ✅ **Wishlists ahora incluyen productos/items completos** 
- ✅ Cada wishlist devuelve array `items` con todos los productos
- ✅ Información completa de WooCommerce para cada producto
- ✅ Datos de stock, precios, imágenes, y disponibilidad
- ✅ Notas personales y prioridades de cada item
- ✅ URLs compartibles y datos de envío incluidos

### v1.0.0 (2025-10-10)
- ✅ Endpoint de perfil público por username
- ✅ Endpoint de Crush aleatorio completo
- ✅ Endpoint de 7 Crushes aleatorios para carousel
- ✅ Endpoint de lista paginada de Crushes
- ✅ Endpoint de búsqueda de usuarios
- ✅ Todos los endpoints públicos (sin autenticación)
- ✅ URLs completas de imágenes en todas las respuestas
- ✅ Wishlists públicas incluidas en perfiles completos

---

## Soporte

Para reportar problemas o sugerencias sobre estos endpoints:
- 📧 Email: dev.gustavo.perezp@gmail.com
- 📝 Documentación actualizada: 10 de Octubre, 2025

---

**¡Disfruta construyendo con la API de CrushMe! 🚀**

