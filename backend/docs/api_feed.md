# API Endpoints: Feed de Usuario

## Información General

Sistema completo de Feed para usuarios autenticados. Permite crear, leer, actualizar y eliminar posts personales con texto y temas de color. Incluye endpoints para ver feeds de todos los usuarios, feeds propios, y feeds de usuarios específicos.

---

## Endpoints Disponibles

### 1. Listar Todos los Feeds y Crear Nuevo Feed
```
GET  /api/feeds/
POST /api/feeds/
```

### 2. Obtener Feeds del Usuario Autenticado
```
GET /api/feeds/my-feeds/
```

### 3. Obtener Feeds de un Usuario Específico
```
GET /api/feeds/user/<user_id>/
```

### 4. Obtener, Actualizar o Eliminar un Feed Específico
```
GET    /api/feeds/<feed_id>/
PUT    /api/feeds/<feed_id>/
PATCH  /api/feeds/<feed_id>/
DELETE /api/feeds/<feed_id>/
```

---

## Autenticación

✅ **Requerida** - Token JWT Bearer

```
Authorization: Bearer <token>
```

Todos los endpoints de Feed requieren autenticación.

---

## 1. Listar Todos los Feeds

### Endpoint
```
GET /api/feeds/
```

### Descripción
Obtiene una lista paginada de todos los feeds de todos los usuarios, ordenados por fecha de creación (más recientes primero).

### Parámetros Query Opcionales

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | integer | Número de página (default: 1) |
| `page_size` | integer | Items por página (default: 20, max: 100) |
| `user_id` | integer | Filtrar feeds por ID de usuario específico |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/feeds/?page=2",
  "previous": null,
  "results": [
    {
      "id": 45,
      "user": 3,
      "user_email": "usuario@example.com",
      "user_username": "usuario123",
      "user_full_name": "Juan Pérez",
      "text": "¡Acabo de comprar un producto increíble en CrushMe!",
      "color": "#FF5733",
      "created_at": "2025-10-02T14:30:00Z",
      "updated_at": "2025-10-02T14:30:00Z"
    },
    {
      "id": 44,
      "user": 5,
      "user_email": "maria@example.com",
      "user_username": "maria_g",
      "user_full_name": "María González",
      "text": "Me encanta esta comunidad ❤️",
      "color": "#3498DB",
      "created_at": "2025-10-02T13:15:00Z",
      "updated_at": "2025-10-02T13:15:00Z"
    }
  ]
}
```

### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/feeds/?page=1&page_size=20" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 2. Crear Nuevo Feed

### Endpoint
```
POST /api/feeds/
```

### Descripción
Crea un nuevo post de feed para el usuario autenticado.

### Parámetros del Body

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `text` | string | ✅ Sí | Texto del post (máximo 1000 caracteres) |
| `color` | string | ❌ No | Código hexadecimal del color (ej: #FF5733). Default: #000000 |

### Request Body Ejemplo

```json
{
  "text": "¡Hola a todos! Este es mi primer post en CrushMe 🎉",
  "color": "#FF5733"
}
```

### Respuesta Exitosa

**Código:** `201 Created`

```json
{
  "id": 46,
  "user": 3,
  "user_email": "usuario@example.com",
  "user_username": "usuario123",
  "user_full_name": "Juan Pérez",
  "text": "¡Hola a todos! Este es mi primer post en CrushMe 🎉",
  "color": "#FF5733",
  "created_at": "2025-10-02T15:00:00Z",
  "updated_at": "2025-10-02T15:00:00Z"
}
```

### Validaciones

- El texto no puede estar vacío
- El texto no puede exceder 1000 caracteres
- El color debe ser un código hexadecimal válido (formato: #RRGGBB)
- Si no se proporciona color, se usa #000000 por defecto
- El color se convierte automáticamente a mayúsculas

### Respuestas de Error

**400 Bad Request** - Validación fallida

```json
{
  "text": ["El texto no puede estar vacío."]
}
```

```json
{
  "color": ["Código de color hexadecimal inválido"]
}
```

### Ejemplo cURL
```bash
curl -X POST "http://localhost:8000/api/feeds/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "¡Hola a todos! Este es mi primer post",
    "color": "#FF5733"
  }'
```

---

## 3. Obtener Mis Feeds

### Endpoint
```
GET /api/feeds/my-feeds/
```

### Descripción
Obtiene todos los feeds del usuario autenticado, paginados y ordenados por fecha (más recientes primero).

### Parámetros Query Opcionales

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | integer | Número de página (default: 1) |
| `page_size` | integer | Items por página (default: 20, max: 100) |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/feeds/my-feeds/?page=2",
  "previous": null,
  "results": [
    {
      "id": 46,
      "user": 3,
      "user_email": "usuario@example.com",
      "user_username": "usuario123",
      "user_full_name": "Juan Pérez",
      "text": "Mi post más reciente",
      "color": "#FF5733",
      "created_at": "2025-10-02T15:00:00Z",
      "updated_at": "2025-10-02T15:00:00Z"
    },
    {
      "id": 40,
      "user": 3,
      "user_email": "usuario@example.com",
      "user_username": "usuario123",
      "user_full_name": "Juan Pérez",
      "text": "Post anterior",
      "color": "#3498DB",
      "created_at": "2025-10-01T10:30:00Z",
      "updated_at": "2025-10-01T10:30:00Z"
    }
  ]
}
```

### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/feeds/my-feeds/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 4. Obtener Feeds de Usuario Específico

### Endpoint
```
GET /api/feeds/user/<user_id>/
```

### Descripción
Obtiene todos los feeds de un usuario específico por su ID.

### Parámetros de URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `user_id` | integer | ID del usuario del cual obtener los feeds |

### Parámetros Query Opcionales

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | integer | Número de página (default: 1) |
| `page_size` | integer | Items por página (default: 20, max: 100) |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 50,
      "user": 5,
      "user_email": "maria@example.com",
      "user_username": "maria_g",
      "user_full_name": "María González",
      "text": "Compartiendo mi experiencia con CrushMe",
      "color": "#E74C3C",
      "created_at": "2025-10-02T16:00:00Z",
      "updated_at": "2025-10-02T16:00:00Z"
    }
  ]
}
```

### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/feeds/user/5/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 5. Obtener Feed Específico

### Endpoint
```
GET /api/feeds/<feed_id>/
```

### Descripción
Obtiene los detalles de un feed específico por su ID.

### Parámetros de URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `feed_id` | integer | ID del feed a obtener |

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "id": 46,
  "user": 3,
  "user_email": "usuario@example.com",
  "user_username": "usuario123",
  "user_full_name": "Juan Pérez",
  "text": "Este es el contenido del feed",
  "color": "#FF5733",
  "created_at": "2025-10-02T15:00:00Z",
  "updated_at": "2025-10-02T15:00:00Z"
}
```

### Respuestas de Error

**404 Not Found** - Feed no existe

```json
{
  "detail": "Not found."
}
```

### Ejemplo cURL
```bash
curl -X GET "http://localhost:8000/api/feeds/46/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 6. Actualizar Feed

### Endpoint
```
PUT   /api/feeds/<feed_id>/
PATCH /api/feeds/<feed_id>/
```

### Descripción
Actualiza un feed existente. Solo el propietario del feed puede actualizarlo.

- **PUT**: Requiere todos los campos
- **PATCH**: Permite actualización parcial

### Parámetros de URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `feed_id` | integer | ID del feed a actualizar |

### Parámetros del Body

| Campo | Tipo | PUT | PATCH | Descripción |
|-------|------|-----|-------|-------------|
| `text` | string | ✅ Requerido | ❌ Opcional | Nuevo texto del post |
| `color` | string | ✅ Requerido | ❌ Opcional | Nuevo color hexadecimal |

### Request Body Ejemplo (PATCH)

```json
{
  "text": "Texto actualizado del post"
}
```

### Respuesta Exitosa

**Código:** `200 OK`

```json
{
  "id": 46,
  "user": 3,
  "user_email": "usuario@example.com",
  "user_username": "usuario123",
  "user_full_name": "Juan Pérez",
  "text": "Texto actualizado del post",
  "color": "#FF5733",
  "created_at": "2025-10-02T15:00:00Z",
  "updated_at": "2025-10-02T15:30:00Z"
}
```

### Respuestas de Error

**403 Forbidden** - No es el propietario

```json
{
  "detail": "No tienes permiso para realizar esta acción."
}
```

**404 Not Found** - Feed no existe

```json
{
  "detail": "Not found."
}
```

### Ejemplo cURL (PATCH)
```bash
curl -X PATCH "http://localhost:8000/api/feeds/46/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Texto actualizado"
  }'
```

---

## 7. Eliminar Feed

### Endpoint
```
DELETE /api/feeds/<feed_id>/
```

### Descripción
Elimina un feed existente. Solo el propietario del feed puede eliminarlo.

### Parámetros de URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `feed_id` | integer | ID del feed a eliminar |

### Respuesta Exitosa

**Código:** `204 No Content`

```json
{
  "detail": "Feed eliminado correctamente."
}
```

### Respuestas de Error

**403 Forbidden** - No es el propietario

```json
{
  "detail": "No tienes permiso para realizar esta acción."
}
```

**404 Not Found** - Feed no existe

```json
{
  "detail": "Not found."
}
```

### Ejemplo cURL
```bash
curl -X DELETE "http://localhost:8000/api/feeds/46/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Campos de la Respuesta

### Objeto Feed

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del feed |
| `user` | integer | ID del usuario propietario |
| `user_email` | string | Email del usuario propietario |
| `user_username` | string | Username del usuario propietario |
| `user_full_name` | string | Nombre completo del usuario propietario |
| `text` | string | Contenido del post |
| `color` | string | Código hexadecimal del color (ej: #FF5733) |
| `created_at` | datetime | Fecha y hora de creación |
| `updated_at` | datetime | Fecha y hora de última actualización |

---

## Respuestas de Error Comunes

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

## Ejemplos de Uso Completos

### JavaScript (Fetch API)

#### Obtener todos los feeds
```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/api/feeds/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log('Feeds:', data.results);
    console.log('Total:', data.count);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

#### Crear un nuevo feed
```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/api/feeds/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: '¡Mi nuevo post!',
    color: '#FF5733'
  })
})
  .then(response => response.json())
  .then(data => {
    console.log('Feed creado:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

#### Actualizar un feed
```javascript
const token = localStorage.getItem('access_token');
const feedId = 46;

fetch(`http://localhost:8000/api/feeds/${feedId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Texto actualizado'
  })
})
  .then(response => response.json())
  .then(data => {
    console.log('Feed actualizado:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

#### Eliminar un feed
```javascript
const token = localStorage.getItem('access_token');
const feedId = 46;

fetch(`http://localhost:8000/api/feeds/${feedId}/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
  .then(response => {
    if (response.ok) {
      console.log('Feed eliminado correctamente');
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### Python (requests)

#### Obtener feeds del usuario autenticado
```python
import requests

token = "tu_token_aqui"
url = "http://localhost:8000/api/feeds/my-feeds/"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"Total de mis feeds: {data['count']}")
    for feed in data['results']:
        print(f"- {feed['text']} (Color: {feed['color']})")
else:
    print(f"Error: {response.status_code}")
```

#### Crear un nuevo feed
```python
import requests

token = "tu_token_aqui"
url = "http://localhost:8000/api/feeds/"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "text": "Mi nuevo post desde Python",
    "color": "#3498DB"
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    feed = response.json()
    print(f"Feed creado con ID: {feed['id']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Axios (JavaScript/TypeScript)

#### Clase de servicio completa
```typescript
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/feeds';

class FeedService {
  private getAuthHeader() {
    const token = localStorage.getItem('access_token');
    return { Authorization: `Bearer ${token}` };
  }

  // Obtener todos los feeds
  async getAllFeeds(page = 1, pageSize = 20, userId?: number) {
    const params: any = { page, page_size: pageSize };
    if (userId) params.user_id = userId;
    
    const response = await axios.get(`${API_URL}/`, {
      headers: this.getAuthHeader(),
      params
    });
    return response.data;
  }

  // Obtener mis feeds
  async getMyFeeds(page = 1, pageSize = 20) {
    const response = await axios.get(`${API_URL}/my-feeds/`, {
      headers: this.getAuthHeader(),
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  // Obtener feeds de un usuario
  async getUserFeeds(userId: number, page = 1, pageSize = 20) {
    const response = await axios.get(`${API_URL}/user/${userId}/`, {
      headers: this.getAuthHeader(),
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  // Obtener un feed específico
  async getFeed(feedId: number) {
    const response = await axios.get(`${API_URL}/${feedId}/`, {
      headers: this.getAuthHeader()
    });
    return response.data;
  }

  // Crear un feed
  async createFeed(text: string, color: string = '#000000') {
    const response = await axios.post(`${API_URL}/`, 
      { text, color },
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // Actualizar un feed
  async updateFeed(feedId: number, data: { text?: string; color?: string }) {
    const response = await axios.patch(`${API_URL}/${feedId}/`, 
      data,
      { headers: this.getAuthHeader() }
    );
    return response.data;
  }

  // Eliminar un feed
  async deleteFeed(feedId: number) {
    const response = await axios.delete(`${API_URL}/${feedId}/`, {
      headers: this.getAuthHeader()
    });
    return response.data;
  }
}

export default new FeedService();
```

#### Uso del servicio
```typescript
import FeedService from './FeedService';

// Obtener todos los feeds
FeedService.getAllFeeds()
  .then(data => {
    console.log('Feeds:', data.results);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Crear un feed
FeedService.createFeed('¡Hola mundo!', '#FF5733')
  .then(feed => {
    console.log('Feed creado:', feed);
  })
  .catch(error => {
    console.error('Error:', error);
  });

// Actualizar un feed
FeedService.updateFeed(46, { text: 'Texto actualizado' })
  .then(feed => {
    console.log('Feed actualizado:', feed);
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

---

## Notas Importantes

### Permisos
- **Lectura**: Cualquier usuario autenticado puede ver feeds de todos los usuarios
- **Creación**: Cualquier usuario autenticado puede crear sus propios feeds
- **Actualización**: Solo el propietario puede actualizar su feed
- **Eliminación**: Solo el propietario puede eliminar su feed

### Paginación
- Todos los endpoints de listado soportan paginación
- Tamaño de página por defecto: 20 items
- Tamaño máximo de página: 100 items
- La respuesta incluye `count`, `next`, `previous` y `results`

### Validaciones de Color
- El color debe ser un código hexadecimal de 6 caracteres
- Formato: `#RRGGBB` (ej: `#FF5733`)
- Se acepta con o sin el símbolo `#` al inicio
- Se convierte automáticamente a mayúsculas
- Si no se proporciona, se usa `#000000` (negro) por defecto

### Validaciones de Texto
- El texto es requerido al crear un feed
- No puede estar vacío ni contener solo espacios
- Máximo 1000 caracteres
- Se eliminan espacios al inicio y final automáticamente

### Ordenamiento
- Todos los listados se ordenan por `created_at` descendente
- Los feeds más recientes aparecen primero

### Rendimiento
- Los queries incluyen `select_related('user')` para optimizar las consultas
- Se recomienda usar paginación para grandes cantidades de datos

---

## Implementación

**Archivos:**
- **Modelo:** `crushme_app/models/feed.py`
- **Serializers:** `crushme_app/serializers/feed_serializers.py`
- **Views:** `crushme_app/views/feed_views.py`
- **URLs:** `crushme_app/urls/feed_urls.py`

**Clases principales:**
- `Feed` - Modelo Django
- `FeedSerializer` - Serializer completo con info de usuario
- `FeedCreateSerializer` - Serializer para creación
- `FeedUpdateSerializer` - Serializer para actualización
- `FeedPagination` - Paginación personalizada

---

## Changelog

- **2025-10-02**: Documentación completa del API de Feed creada
- **2025-10-02**: Sistema de Feed implementado con CRUD completo

---

## Modelo de Base de Datos

### Tabla: `feed`

| Campo | Tipo | Propiedades |
|-------|------|-------------|
| `id` | BigInteger | Primary Key, Auto Increment |
| `user_id` | BigInteger | Foreign Key → User, NOT NULL, Indexed |
| `text` | Text | NOT NULL, Max 1000 chars |
| `color` | VARCHAR(7) | NOT NULL, Default '#000000', Regex validation |
| `created_at` | DateTime | NOT NULL, Auto Now Add, Indexed |
| `updated_at` | DateTime | NOT NULL, Auto Now |

**Índices:**
- `idx_feed_created_at` en `created_at` (descendente)
- `idx_feed_user_created` en `user_id, created_at` (descendente)

**Relaciones:**
- `user` → Many-to-One con `User` (related_name: `feeds`)



