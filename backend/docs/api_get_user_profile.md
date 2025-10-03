# API Endpoint: Get User Profile

## Información General

Obtiene toda la información completa del perfil del usuario autenticado, incluyendo sus datos personales, direcciones, galería de fotos, enlaces y foto de perfil.

---

## Endpoint

```
GET /api/auth/profile/
```

---

## Autenticación

✅ **Requerida** - Token JWT Bearer

```
Authorization: Bearer <token>
```

---

## Parámetros

Este endpoint no requiere parámetros en la URL ni en el body de la petición.

---

## Respuesta Exitosa

**Código:** `200 OK`

**Estructura de la respuesta:**

```json
{
  "id": 1,
  "email": "usuario@example.com",
  "username": "usuario123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "phone": "+56912345678",
  "about": "Descripción del usuario",
  "current_status": "Disponible",
  "note": "Notas personales del usuario",
  "date_joined": "2025-01-15T10:30:00Z",
  "is_active": true,
  "is_guest_converted": false,
  "profile_picture": "https://example.com/media/gallery/profile.jpg",
  "addresses": [
    {
      "id": 1,
      "user": 1,
      "address_line1": "Calle Principal 123",
      "address_line2": "Departamento 4B",
      "additional_details": "Portón azul, timbre 4B",
      "city": "Santiago",
      "state": "Región Metropolitana",
      "postal_code": "8320000",
      "country": "Chile",
      "is_default": true,
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": "2025-01-15T11:00:00Z"
    }
  ],
  "gallery_photos": [
    {
      "id": 1,
      "user": 1,
      "image": "/media/gallery/photo1.jpg",
      "caption": "Mi foto de perfil",
      "is_profile_picture": true,
      "uploaded_at": "2025-01-15T11:30:00Z"
    },
    {
      "id": 2,
      "user": 1,
      "image": "/media/gallery/photo2.jpg",
      "caption": "Otra foto",
      "is_profile_picture": false,
      "uploaded_at": "2025-01-16T09:00:00Z"
    }
  ],
  "links": [
    {
      "id": 1,
      "user": 1,
      "title": "Instagram",
      "url": "https://instagram.com/usuario",
      "platform": "instagram",
      "order": 1,
      "created_at": "2025-01-15T12:00:00Z"
    },
    {
      "id": 2,
      "user": 1,
      "title": "Twitter",
      "url": "https://twitter.com/usuario",
      "platform": "twitter",
      "order": 2,
      "created_at": "2025-01-15T12:05:00Z"
    }
  ],
  "guest_profile": null
}
```

---

## Campos de la Respuesta

### Datos Personales del Usuario

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del usuario |
| `email` | string | Correo electrónico del usuario |
| `username` | string | Nombre de usuario único |
| `first_name` | string | Primer nombre |
| `last_name` | string | Apellido |
| `full_name` | string | Nombre completo (generado automáticamente) |
| `phone` | string | Número de teléfono |
| `about` | string | Descripción o biografía del usuario |
| `current_status` | string | Estado actual del usuario (ej: "Disponible", "Ocupado") |
| `note` | string | Notas personales o información adicional del usuario |
| `date_joined` | datetime | Fecha de registro |
| `is_active` | boolean | Si la cuenta está activa |
| `is_guest_converted` | boolean | Si el usuario fue convertido desde invitado |
| `profile_picture` | string/null | URL completa de la foto de perfil principal |

### Direcciones (`addresses`)

Array de objetos con las direcciones del usuario:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID de la dirección |
| `user` | integer | ID del usuario propietario |
| `address_line1` | string | Línea 1 de la dirección |
| `address_line2` | string/null | Línea 2 de la dirección (opcional) |
| `additional_details` | string/null | Detalles adicionales o instrucciones de entrega |
| `city` | string | Ciudad |
| `state` | string | Estado/Región |
| `postal_code` | string | Código postal |
| `country` | string | País |
| `is_default` | boolean | Si es la dirección predeterminada |
| `created_at` | datetime | Fecha de creación |
| `updated_at` | datetime | Fecha de última actualización |

### Galería de Fotos (`gallery_photos`)

Array de objetos con las fotos del usuario:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID de la foto |
| `user` | integer | ID del usuario propietario |
| `image` | string | Ruta de la imagen |
| `caption` | string/null | Descripción de la foto |
| `is_profile_picture` | boolean | Si es la foto de perfil |
| `uploaded_at` | datetime | Fecha de subida |

### Enlaces (`links`)

Array de objetos con los enlaces del usuario:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID del enlace |
| `user` | integer | ID del usuario propietario |
| `title` | string | Título del enlace |
| `url` | string | URL del enlace |
| `platform` | string | Plataforma (instagram, twitter, etc.) |
| `order` | integer | Orden de visualización |
| `created_at` | datetime | Fecha de creación |

### Perfil de Invitado (`guest_profile`)

Objeto con información adicional si el usuario fue invitado (null si no aplica):

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID del perfil de invitado |
| `email` | string | Email del invitado |
| `full_name` | string | Nombre completo |
| `phone` | string/null | Teléfono |
| `created_at` | datetime | Fecha de creación |

---

## Respuestas de Error

### 401 Unauthorized

**Causa:** Token no proporcionado o inválido

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Causa:** Token expirado

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

---

## Ejemplos de Uso

### cURL

```bash
curl -X GET "http://localhost:8000/api/auth/profile/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### JavaScript (Fetch API)

```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/api/auth/profile/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log('User Profile:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Python (requests)

```python
import requests

token = "tu_token_aqui"
url = "http://localhost:8000/api/auth/profile/"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    user_profile = response.json()
    print(f"Usuario: {user_profile['full_name']}")
    print(f"Email: {user_profile['email']}")
    print(f"Direcciones: {len(user_profile['addresses'])}")
else:
    print(f"Error: {response.status_code}")
```

### Axios (JavaScript/TypeScript)

```typescript
import axios from 'axios';

const getUserProfile = async () => {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await axios.get('http://localhost:8000/api/auth/profile/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

// Uso
getUserProfile()
  .then(profile => {
    console.log('Profile:', profile);
  })
  .catch(error => {
    console.error('Failed to get profile:', error);
  });
```

---

## Notas

- Este endpoint solo devuelve información del usuario autenticado (basado en el token JWT)
- No es posible obtener el perfil de otros usuarios con este endpoint
- El campo `profile_picture` contiene la URL completa de la imagen marcada como `is_profile_picture: true` en la galería
- Si el usuario no tiene foto de perfil, el campo `profile_picture` será `null`
- Los arrays (`addresses`, `gallery_photos`, `links`) pueden estar vacíos `[]` si el usuario no tiene datos relacionados
- El campo `guest_profile` será `null` si el usuario no fue convertido desde un checkout de invitado

---

## Implementación

**Archivo:** `crushme_app/views/auth_views.py`

**Función:** `get_user_profile()`

**Serializer:** `UserProfileSerializer` (definido en `crushme_app/serializers/user_serializers.py`)

---

## Changelog

- **2025-10-02**: Documentación creada

---
---

# API Endpoint: Update User Profile

## Información General

Actualiza la información del perfil del usuario autenticado. Permite modificar datos personales como nombre, email, username, teléfono y descripción.

---

## Endpoint

```
POST/PUT/PATCH /api/auth/update_profile/
```

**Métodos aceptados:** POST, PUT, PATCH

---

## Autenticación

✅ **Requerida** - Token JWT Bearer

```
Authorization: Bearer <token>
```

---

## Parámetros del Body (JSON)

Todos los campos son **opcionales** (actualización parcial). Envía solo los campos que deseas actualizar.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | string | No | Nuevo correo electrónico del usuario |
| `username` | string | No | Nuevo nombre de usuario (único, case-insensitive) |
| `first_name` | string | No | Primer nombre |
| `last_name` | string | No | Apellido |
| `phone` | string | No | Número de teléfono |
| `about` | string | No | Descripción o biografía del usuario |
| `current_status` | string | No | Estado actual del usuario |
| `note` | string | No | Notas personales o información adicional |
| `addresses` | array | No | Array de direcciones del usuario (nested) |
| `links` | array | No | Array de links tipo linktree (nested) |
| `gallery_photos` | array | No | Array de fotos de galería (nested) |

**Nota:** Los campos `id`, `full_name`, `date_joined`, `is_guest_converted` y `profile_picture` son de solo lectura y no pueden ser modificados a través de este endpoint.

### Estructura de `addresses` (nested):

Cada elemento del array `addresses` puede incluir:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | No | ID de la dirección (para actualizar existente) |
| `country` | string | Sí* | País |
| `state` | string | Sí* | Estado/Región |
| `city` | string | Sí* | Ciudad |
| `zip_code` | string | Sí* | Código postal |
| `address_line_1` | string | Sí* | Línea 1 de dirección |
| `address_line_2` | string | No | Línea 2 de dirección |
| `additional_details` | string | No | Detalles adicionales |
| `is_default_shipping` | boolean | No | Si es dirección de envío por defecto |
| `is_default_billing` | boolean | No | Si es dirección de facturación por defecto |

*Requerido solo al crear una nueva dirección (sin `id`)

### Estructura de `links` (nested):

Cada elemento del array `links` puede incluir:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | No | ID del link (para actualizar existente) |
| `title` | string | Sí* | Título o nombre del link |
| `url` | string | Sí* | URL del link |
| `order` | integer | No | Orden de visualización (default: 0) |
| `is_active` | boolean | No | Si el link está activo (default: true) |

*Requerido solo al crear un nuevo link (sin `id`)

### Estructura de `gallery_photos` (nested):

Cada elemento del array `gallery_photos` puede incluir:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | No | ID de la foto (para actualizar/eliminar existente) |
| `image` | string | Sí* | URL o path de la imagen |
| `caption` | string | No | Descripción de la imagen |
| `is_profile_picture` | boolean | No | Si es la foto de perfil principal (default: false) |

*Requerido solo al crear una nueva foto (sin `id`)

**Notas importantes sobre gallery_photos:**
- **Para actualizar metadatos** (caption, is_profile_picture): Incluye el `id` de la foto
- **Para eliminar fotos**: No las incluyas en el array
- **Para subir archivos nuevos**: 
  - **Opción 1 (Recomendada)**: Usa `multipart/form-data` y sube el archivo directamente en este endpoint
  - **Opción 2**: Primero sube la imagen a través de otro endpoint, luego referencia la URL
- Solo puede haber una foto marcada como `is_profile_picture: true` (las demás se marcarán automáticamente como false)

---

## Ejemplos de Petición

### Actualizar solo campos básicos del usuario:

```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+56912345678",
  "about": "Desarrollador Full Stack apasionado por la tecnología",
  "current_status": "Disponible",
  "note": "Prefiero ser contactado por email"
}
```

### Actualizar solo un campo:

```json
{
  "current_status": "Ocupado"
}
```

### Actualizar con direcciones (nested):

```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "addresses": [
    {
      "country": "Chile",
      "state": "Región Metropolitana",
      "city": "Santiago",
      "zip_code": "8320000",
      "address_line_1": "Calle Principal 123",
      "address_line_2": "Departamento 4B",
      "additional_details": "Portón azul, timbre 4B",
      "is_default_shipping": true,
      "is_default_billing": true
    }
  ]
}
```

### Actualizar dirección existente (incluye ID):

```json
{
  "addresses": [
    {
      "id": 1,
      "address_line_1": "Nueva Calle 456",
      "city": "Valparaíso"
    }
  ]
}
```

### Actualizar con links (nested):

```json
{
  "current_status": "Disponible",
  "links": [
    {
      "title": "Instagram",
      "url": "https://instagram.com/usuario",
      "order": 1,
      "is_active": true
    },
    {
      "title": "Twitter",
      "url": "https://twitter.com/usuario",
      "order": 2,
      "is_active": true
    }
  ]
}
```

### Actualizar metadatos de fotos existentes:

```json
{
  "gallery_photos": [
    {
      "id": 1,
      "caption": "Nueva descripción de mi foto",
      "is_profile_picture": true
    },
    {
      "id": 2,
      "caption": "Foto de vacaciones"
    }
  ]
}
```

### Agregar nueva foto con imagen previamente subida:

```json
{
  "gallery_photos": [
    {
      "image": "/media/gallery/2025/10/nueva_foto.jpg",
      "caption": "Mi nueva foto",
      "is_profile_picture": false
    }
  ]
}
```

### Actualización completa (todos los campos):

```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan@example.com",
  "username": "juanperez",
  "phone": "+56912345678",
  "about": "Desarrollador Full Stack",
  "current_status": "Disponible",
  "note": "Prefiero contacto por email",
  "addresses": [
    {
      "country": "Chile",
      "state": "Región Metropolitana",
      "city": "Santiago",
      "zip_code": "8320000",
      "address_line_1": "Calle Principal 123",
      "address_line_2": "Depto 4B",
      "additional_details": "Portón azul",
      "is_default_shipping": true,
      "is_default_billing": true
    }
  ],
  "links": [
    {
      "title": "Instagram",
      "url": "https://instagram.com/usuario",
      "order": 1,
      "is_active": true
    },
    {
      "title": "Portfolio",
      "url": "https://miportfolio.com",
      "order": 2,
      "is_active": true
    }
  ],
  "gallery_photos": [
    {
      "id": 1,
      "caption": "Mi foto de perfil",
      "is_profile_picture": true
    },
    {
      "id": 2,
      "caption": "Foto de vacaciones",
      "is_profile_picture": false
    }
  ]
}
```

**Notas importantes:**
- Los campos `addresses`, `links` y `gallery_photos` son **opcionales**
- Si incluyes estos arrays, se actualizarán/crearán según tengan o no `id`:
  - **Con `id`**: Actualiza el elemento existente
  - **Sin `id`**: Crea un nuevo elemento
- Los elementos **no incluidos** en arrays con IDs serán **eliminados**

---

## Subir Imágenes con Multipart/Form-Data

El endpoint también acepta `multipart/form-data` para subir archivos de imagen. Hay dos formas de hacerlo:

### **Forma 1: Datos planos (Simple)**

Ideal para actualizar campos básicos y subir una o dos imágenes:

```
POST /api/auth/update_profile/
Content-Type: multipart/form-data

first_name: "Juan"
last_name: "Pérez"
current_status: "Disponible"
gallery_image_1: [archivo de imagen]
gallery_caption_1: "Mi nueva foto"
gallery_is_profile_1: "true"
gallery_image_2: [archivo de imagen]
gallery_caption_2: "Otra foto"
```

### **Forma 2: JSON + Archivos (Avanzada)**

Ideal para actualizaciones complejas con datos anidados:

```
POST /api/auth/update_profile/
Content-Type: multipart/form-data

data: {
  "first_name": "Juan",
  "addresses": [...],
  "links": [...]
}
gallery_image_1: [archivo de imagen]
gallery_caption_1: "Mi foto"
gallery_is_profile_1: "true"
```

**Formato de campos de imagen:**
- `gallery_image_N`: Archivo de imagen (N = 1, 2, 3...)
- `gallery_caption_N`: Caption de la imagen N (opcional)
- `gallery_is_profile_N`: "true" o "false" para marcar como foto de perfil (opcional)

### **Ejemplos de código para subir imágenes:**

#### JavaScript (Fetch API con FormData):

```javascript
const token = localStorage.getItem('access_token');
const formData = new FormData();

// Campos básicos
formData.append('first_name', 'Juan');
formData.append('last_name', 'Pérez');
formData.append('current_status', 'Disponible');

// Subir imagen 1
const file1 = document.getElementById('fileInput1').files[0];
formData.append('gallery_image_1', file1);
formData.append('gallery_caption_1', 'Mi foto de perfil');
formData.append('gallery_is_profile_1', 'true');

// Subir imagen 2
const file2 = document.getElementById('fileInput2').files[0];
if (file2) {
  formData.append('gallery_image_2', file2);
  formData.append('gallery_caption_2', 'Otra foto');
}

fetch('http://localhost:8000/api/auth/update_profile/', {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`
    // NO incluir Content-Type, el navegador lo configura automáticamente
  },
  body: formData
})
  .then(response => response.json())
  .then(data => {
    console.log('Profile updated:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

#### Python (requests con archivos):

```python
import requests

token = "tu_token_aqui"
url = "http://localhost:8000/api/auth/update_profile/"

headers = {
    "Authorization": f"Bearer {token}"
}

# Datos básicos
data = {
    "first_name": "Juan",
    "last_name": "Pérez",
    "current_status": "Disponible"
}

# Archivos de imagen
files = {
    'gallery_image_1': open('foto_perfil.jpg', 'rb'),
    'gallery_image_2': open('foto_vacaciones.jpg', 'rb')
}

# Datos adicionales de las imágenes
data.update({
    'gallery_caption_1': 'Mi foto de perfil',
    'gallery_is_profile_1': 'true',
    'gallery_caption_2': 'Foto de vacaciones'
})

response = requests.put(url, headers=headers, data=data, files=files)

if response.status_code == 200:
    print("Perfil actualizado:", response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())

# Cerrar archivos
for file in files.values():
    file.close()
```

#### Axios (JavaScript/TypeScript con FormData):

```typescript
import axios from 'axios';

const updateProfileWithImages = async (
  userData: any,
  imageFiles: File[]
) => {
  try {
    const token = localStorage.getItem('access_token');
    const formData = new FormData();
    
    // Agregar datos básicos
    Object.keys(userData).forEach(key => {
      formData.append(key, userData[key]);
    });
    
    // Agregar imágenes
    imageFiles.forEach((file, index) => {
      const n = index + 1;
      formData.append(`gallery_image_${n}`, file);
      formData.append(`gallery_caption_${n}`, file.name);
      if (index === 0) {
        formData.append(`gallery_is_profile_${n}`, 'true');
      }
    });
    
    const response = await axios.put(
      'http://localhost:8000/api/auth/update_profile/',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error);
    throw error;
  }
};

// Uso
const userData = {
  first_name: 'Juan',
  last_name: 'Pérez',
  current_status: 'Disponible'
};

const fileInput = document.getElementById('fileInput') as HTMLInputElement;
const files = Array.from(fileInput.files || []);

updateProfileWithImages(userData, files)
  .then(profile => {
    console.log('Profile updated:', profile);
  })
  .catch(error => {
    console.error('Failed:', error);
  });
```

#### cURL con multipart/form-data:

```bash
curl -X PUT "http://localhost:8000/api/auth/update_profile/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -F "first_name=Juan" \
  -F "last_name=Pérez" \
  -F "current_status=Disponible" \
  -F "gallery_image_1=@/path/to/foto_perfil.jpg" \
  -F "gallery_caption_1=Mi foto de perfil" \
  -F "gallery_is_profile_1=true" \
  -F "gallery_image_2=@/path/to/otra_foto.jpg" \
  -F "gallery_caption_2=Foto de vacaciones"
```

---

## Respuesta Exitosa

**Código:** `200 OK`

La respuesta devuelve el **perfil completo actualizado** con todos los campos (igual que GET `/api/auth/profile/`):

```json
{
  "id": 1,
  "email": "juan@example.com",
  "username": "juanperez",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "phone": "+56912345678",
  "about": "Desarrollador Full Stack",
  "current_status": "Disponible",
  "note": "Prefiero contacto por email",
  "date_joined": "2025-01-15T10:30:00Z",
  "is_active": true,
  "is_guest_converted": false,
  "profile_picture": "https://example.com/media/gallery/profile.jpg",
  "addresses": [
    {
      "id": 1,
      "user": 1,
      "country": "Chile",
      "state": "Región Metropolitana",
      "city": "Santiago",
      "zip_code": "8320000",
      "address_line_1": "Calle Principal 123",
      "address_line_2": "Depto 4B",
      "additional_details": "Portón azul",
      "is_default_shipping": true,
      "is_default_billing": true,
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": "2025-10-02T15:30:00Z"
    }
  ],
  "gallery_photos": [
    {
      "id": 1,
      "user": 1,
      "image": "/media/gallery/photo1.jpg",
      "caption": "Mi foto de perfil",
      "is_profile_picture": true,
      "uploaded_at": "2025-01-15T11:30:00Z"
    }
  ],
  "links": [
    {
      "id": 1,
      "user": 1,
      "title": "Instagram",
      "url": "https://instagram.com/usuario",
      "order": 1,
      "is_active": true,
      "created_at": "2025-01-15T12:00:00Z"
    },
    {
      "id": 2,
      "user": 1,
      "title": "Portfolio",
      "url": "https://miportfolio.com",
      "order": 2,
      "is_active": true,
      "created_at": "2025-10-02T15:30:00Z"
    }
  ],
  "guest_profile": null
}
```

---

## Respuestas de Error

### 400 Bad Request

**Causa:** Validación fallida - Username ya existe

```json
{
  "username": [
    "A user with this username already exists."
  ]
}
```

**Causa:** Validación fallida - Email inválido

```json
{
  "email": [
    "Enter a valid email address."
  ]
}
```

**Causa:** Validación fallida - Campos inválidos

```json
{
  "field_name": [
    "This field is required.",
    "Ensure this field has no more than X characters."
  ]
}
```

### 401 Unauthorized

**Causa:** Token no proporcionado o inválido

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Causa:** Token expirado

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

---

## Ejemplos de Uso

### cURL

**Usando POST:**
```bash
curl -X POST "http://localhost:8000/api/auth/update_profile/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+56912345678",
    "about": "Desarrollador Full Stack",
    "current_status": "Disponible",
    "note": "Prefiero ser contactado por email"
  }'
```

**Usando PUT:**
```bash
curl -X PUT "http://localhost:8000/api/auth/update_profile/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "current_status": "Disponible"
  }'
```

### JavaScript (Fetch API)

```javascript
const token = localStorage.getItem('access_token');

const updateData = {
  first_name: "Juan",
  last_name: "Pérez",
  phone: "+56912345678",
  about: "Desarrollador Full Stack",
  current_status: "Disponible",
  note: "Prefiero ser contactado por email"
};

fetch('http://localhost:8000/api/auth/update_profile/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(updateData)
})
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data.message);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Python (requests)

```python
import requests

token = "tu_token_aqui"
url = "http://localhost:8000/api/auth/update_profile/"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+56912345678",
    "about": "Desarrollador Full Stack",
    "current_status": "Disponible",
    "note": "Prefiero ser contactado por email"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print(response.json()['message'])
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Axios (JavaScript/TypeScript)

```typescript
import axios from 'axios';

interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  email?: string;
  username?: string;
  phone?: string;
  about?: string;
  current_status?: string;
  note?: string;
}

const updateUserProfile = async (data: UpdateProfileData) => {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await axios.post(
      'http://localhost:8000/api/auth/update_profile/',
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Manejar errores de validación
      console.error('Validation errors:', error.response.data);
      throw error.response.data;
    }
    console.error('Error updating profile:', error);
    throw error;
  }
};

// Uso
updateUserProfile({
  first_name: "Juan",
  last_name: "Pérez",
  about: "Nueva descripción",
  current_status: "Disponible",
  note: "Prefiero ser contactado por email"
})
  .then(result => {
    console.log(result.message);
  })
  .catch(errors => {
    console.error('Failed to update profile:', errors);
  });
```

---

## Validaciones

### Username
- Debe ser único en el sistema (case-insensitive)
- Si intentas usar un username que ya existe, recibirás un error 400
- La validación excluye tu propio usuario al actualizar

### Email
- Debe ser una dirección de email válida
- El formato es validado por Django

### Campos de Solo Lectura
Los siguientes campos **no pueden ser modificados** a través de este endpoint:
- `id` - ID del usuario
- `full_name` - Generado automáticamente desde first_name + last_name
- `date_joined` - Fecha de registro
- `is_guest_converted` - Estado de conversión de invitado
- `is_active` - Estado de la cuenta

---

## Notas

- Este endpoint utiliza **actualización parcial** (`partial=True`), por lo que puedes enviar solo los campos que deseas modificar
- No es necesario enviar todos los campos del usuario
- El endpoint actualiza automáticamente el timestamp `last_login` después de una actualización exitosa
- Solo puedes actualizar tu propio perfil (basado en el token JWT)
- Los cambios se guardan inmediatamente en la base de datos

### Comportamiento de Datos Anidados (Addresses, Links y Gallery):

**Crear nuevo elemento:**
```json
{
  "addresses": [
    {
      "country": "Chile",
      "city": "Santiago"
      // ... sin campo "id" = CREAR
    }
  ],
  "gallery_photos": [
    {
      "image": "/media/gallery/photo.jpg",
      "caption": "Nueva foto"
      // Sin "id" = CREAR (requiere que image ya exista)
    }
  ]
}
```

**Actualizar elemento existente:**
```json
{
  "addresses": [
    {
      "id": 1,
      "city": "Valparaíso"  // Con "id" = ACTUALIZAR solo campos enviados
    }
  ],
  "gallery_photos": [
    {
      "id": 2,
      "caption": "Nueva descripción",  // Con "id" = ACTUALIZAR metadatos
      "is_profile_picture": true
    }
  ]
}
```

**Eliminar elementos:**
- Si envías un array de `addresses`, `links` o `gallery_photos`, solo los elementos incluidos se mantendrán
- Los elementos con ID que no estén en el array serán **eliminados**
- Si no envías el campo, no se modifica nada

**Ejemplo de eliminación:**
```json
{
  "addresses": [
    {"id": 1, "city": "Santiago"}  // Solo mantiene la dirección con ID 1
    // Otras direcciones se eliminan
  ],
  "gallery_photos": [
    {"id": 1}  // Solo mantiene la foto con ID 1
    // Otras fotos se eliminan
  ]
}
```

**Para mantener sin cambios:**
- Simplemente no incluyas el campo `addresses`, `links` o `gallery_photos` en tu petición

**Especial para gallery_photos:**
- **Actualizar metadatos**: Envía el `id` con los campos a cambiar (caption, is_profile_picture)
- **Marcar como foto de perfil**: Solo una foto puede tener `is_profile_picture: true` (las demás se marcarán como false automáticamente)
- **Eliminar foto**: No la incluyas en el array
- **Subir archivo nuevo**: Requiere endpoint separado de upload multipart/form-data

---

## Flujo Recomendado

1. **Obtener perfil actual:**
   ```
   GET /api/auth/profile/
   ```

2. **Mostrar datos en el formulario** para que el usuario edite

3. **Enviar solo campos modificados:**
   ```
   POST /api/auth/update_profile/
   ```

4. **Obtener perfil actualizado (opcional):**
   ```
   GET /api/auth/profile/
   ```

---

## Implementación

**Archivo:** `crushme_app/views/auth_views.py`

**Función:** `update_profile()`

**Serializer:** `UserSerializer` (definido en `crushme_app/serializers/user_serializers.py`)

**Método del Serializer:** `update()` - Maneja la lógica de actualización

---

## Diferencias con GET /api/auth/profile/

| Aspecto | GET /api/auth/profile/ | POST/PUT/PATCH /api/auth/update_profile/ |
|---------|------------------------|--------------------------------|
| Propósito | Obtener información | Actualizar información |
| Método | GET | POST, PUT o PATCH |
| Body | No requiere | Requiere JSON con campos a actualizar |
| Respuesta | Objeto completo del usuario | Objeto completo actualizado del usuario |
| Datos básicos | ✅ Incluye | ✅ Acepta y actualiza |
| Addresses | ✅ Incluye | ✅ Acepta crear/actualizar/eliminar |
| Links | ✅ Incluye | ✅ Acepta crear/actualizar/eliminar |
| Gallery Photos | ✅ Incluye | ✅ Acepta actualizar metadatos/eliminar |

**Nota:** 
- `addresses`, `links` y `gallery_photos` son totalmente actualizables a través de este endpoint
- Para `gallery_photos`:
  - ✅ Actualizar metadatos (caption, is_profile_picture)
  - ✅ Eliminar fotos
  - ✅ Referenciar imágenes ya subidas
  - ✅ Subir archivos nuevos usando `multipart/form-data`
- **Content-Type soportados:**
  - `application/json` - Para datos sin archivos
  - `multipart/form-data` - Para subir archivos de imagen

---

## Changelog

- **2025-10-02**: Documentación inicial creada
- **2025-10-02**: Agregados campos `current_status` y `note` al modelo User
- **2025-10-02**: Agregado campo `additional_details` al modelo UserAddress
- **2025-10-02**: Endpoint `update_profile` ahora acepta POST, PUT y PATCH
- **2025-10-02**: **ACTUALIZACIÓN MAYOR**: Endpoint `update_profile` ahora acepta datos anidados (addresses, links y gallery_photos)
- **2025-10-02**: Endpoint `update_profile` ahora devuelve el perfil completo actualizado en lugar de solo un mensaje
- **2025-10-02**: **ACTUALIZACIÓN CRÍTICA**: Soporte completo para subir archivos de imagen usando `multipart/form-data`
- **2025-10-02**: Vista actualizada para procesar archivos de imagen (`gallery_image_N` format)
- **2025-10-02**: Serializer `UserGallerySerializer` ahora acepta archivos de imagen directamente
- **2025-10-02**: Documentación ampliada con ejemplos de código para subir imágenes (JavaScript, Python, cURL)
- **2025-10-02**: Soporte dual: `application/json` y `multipart/form-data`

