# API de Usuario - Documentación para Frontend

Esta documentación describe todos los endpoints relacionados con usuarios en CrushMe, incluyendo autenticación, gestión de perfil y funcionalidad de invitados.

## Tabla de Contenidos

- [Autenticación](#autenticación)
  - [Registro de Usuario](#1-registro-de-usuario)
  - [Verificación de Email](#2-verificación-de-email)
  - [Reenviar Código de Verificación](#3-reenviar-código-de-verificación)
  - [Inicio de Sesión](#4-inicio-de-sesión)
  - [Inicio de Sesión con Google](#5-inicio-de-sesión-con-google)
- [Gestión de Contraseña](#gestión-de-contraseña)
  - [Olvidé mi Contraseña](#6-olvidé-mi-contraseña)
  - [Restablecer Contraseña](#7-restablecer-contraseña)
  - [Cambiar Contraseña](#8-cambiar-contraseña-autenticado)
- [Gestión de Perfil](#gestión-de-perfil)
  - [Obtener Perfil Completo](#9-obtener-perfil-completo)
  - [Actualizar Perfil](#10-actualizar-perfil)
  - [Subir Foto de Perfil](#actualizar-foto-de-perfil)
- [Funcionalidades Adicionales](#funcionalidades-adicionales)
  - [Checkout de Invitado](#11-checkout-de-invitado)
  - [Verificar Disponibilidad de Username](#12-verificar-disponibilidad-de-username)
  - [Verificar Usuario Invitado](#13-verificar-usuario-invitado)

---

## Base URL

```
http://your-domain.com/api/auth/
```

---

## Autenticación

### 1. Registro de Usuario

Registra un nuevo usuario. El usuario se crea inactivo hasta que verifique su email.

**Endpoint:** `POST /auth/signup/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "username": "usuario123",
  "password": "ContraseñaSegura123!",
  "password_confirm": "ContraseñaSegura123!"
}
```

**Validaciones:**
- `email`: Requerido, único, formato email válido
- `username`: Requerido, único (case-insensitive), máx 30 caracteres
- `password`: Requerido, debe cumplir con validaciones de Django (mínimo 8 caracteres, no muy común, no similar al email)
- `password_confirm`: Debe coincidir con `password`

**Response (201 Created):**
```json
{
  "message": "Registration successful. Please check your email for verification code.",
  "email": "usuario@ejemplo.com",
  "requires_verification": true
}
```

**Errores Comunes:**
- `400`: Email ya registrado, username ya existe, contraseñas no coinciden
- `500`: Error al enviar email de verificación

---

### 2. Verificación de Email

Verifica el email del usuario con el código de 4 dígitos enviado por correo. Activa la cuenta y retorna tokens JWT.

**Endpoint:** `POST /auth/verify-email/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "verification_code": "1234"
}
```

**Validaciones:**
- Código debe ser válido y no expirado (5 minutos)
- Usuario debe existir

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "first_name": "",
    "last_name": "",
    "full_name": "",
    "phone": null,
    "about": null,
    "profile_picture": null,
    "profile_picture_url": null,
    "current_status": null,
    "note": null,
    "date_joined": "2025-10-06T10:30:00Z",
    "is_active": true,
    "is_guest_converted": false,
    "addresses": [],
    "gallery_photos": [],
    "links": [],
    "guest_profile": null
  },
  "message": "Email verified successfully. Account activated."
}
```

**Errores Comunes:**
- `400`: Código inválido, código expirado, usuario no existe

---

### 3. Reenviar Código de Verificación

Reenvía un nuevo código de verificación de 4 dígitos al email del usuario.

**Endpoint:** `POST /auth/resend-verification/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

**Response (200 OK):**
```json
{
  "message": "New verification code sent to your email."
}
```

**Errores Comunes:**
- `400`: Email requerido, email ya verificado
- `404`: Usuario no existe
- `500`: Error al enviar email

---

### 4. Inicio de Sesión

Autentica un usuario con email y contraseña. El usuario debe haber verificado su email.

**Endpoint:** `POST /auth/login/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "ContraseñaSegura123!"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "full_name": "Juan Pérez",
    "phone": "+1234567890",
    "about": "Desarrollador apasionado",
    "profile_picture": "/media/profile_pictures/2025/10/06/profile.jpg",
    "profile_picture_url": "http://your-domain.com/media/profile_pictures/2025/10/06/profile.jpg",
    "current_status": "Disponible",
    "note": "Notas personales",
    "date_joined": "2025-10-06T10:30:00Z",
    "is_active": true,
    "is_guest_converted": false,
    "addresses": [
      {
        "id": 1,
        "country": "USA",
        "state": "California",
        "city": "Los Angeles",
        "zip_code": "90001",
        "address_line_1": "123 Main St",
        "address_line_2": "Apt 4B",
        "additional_details": "Puerta azul",
        "is_default_shipping": true,
        "is_default_billing": true,
        "created_at": "2025-10-06T10:35:00Z",
        "updated_at": "2025-10-06T10:35:00Z"
      }
    ],
    "gallery_photos": [
      {
        "id": 1,
        "image": "http://your-domain.com/media/user_gallery/2025/10/06/photo1.jpg",
        "caption": "Mi foto favorita",
        "is_profile_picture": false,
        "uploaded_at": "2025-10-06T10:40:00Z"
      }
    ],
    "links": [
      {
        "id": 1,
        "title": "Mi Portfolio",
        "url": "https://mi-portfolio.com",
        "order": 0,
        "is_active": true,
        "created_at": "2025-10-06T10:45:00Z"
      }
    ],
    "guest_profile": null
  },
  "message": "Login successful."
}
```

**Errores Comunes:**
- `400`: Email o contraseña incorrectos, cuenta no activada, email no verificado

---

### 5. Inicio de Sesión con Google

Autentica o crea un usuario usando datos de Google OAuth2.

**Endpoint:** `POST /auth/google_login/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@gmail.com",
  "given_name": "Juan",
  "family_name": "Pérez"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errores Comunes:**
- `400`: Campos requeridos faltantes
- `405`: Método no permitido
- `500`: Error interno del servidor

---

## Gestión de Contraseña

### 6. Olvidé mi Contraseña

Envía un código de 4 dígitos al email del usuario para restablecer la contraseña.

**Endpoint:** `POST /auth/forgot-password/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset code sent to your email."
}
```

**Errores Comunes:**
- `400`: Email requerido
- `404`: Usuario no existe
- `500`: Error al enviar email

---

### 7. Restablecer Contraseña

Verifica el código de restablecimiento y establece una nueva contraseña.

**Endpoint:** `POST /auth/reset-password/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "reset_code": "1234",
  "new_password": "NuevaContraseñaSegura123!",
  "new_password_confirm": "NuevaContraseñaSegura123!"
}
```

**Validaciones:**
- `reset_code`: Debe ser válido y no expirado (5 minutos)
- `new_password`: Debe cumplir validaciones de Django
- `new_password_confirm`: Debe coincidir con `new_password`

**Response (200 OK):**
```json
{
  "message": "Password reset successful. You can now login with your new password."
}
```

**Errores Comunes:**
- `400`: Contraseñas no coinciden, código inválido o expirado
- `404`: Usuario no existe

---

### 8. Cambiar Contraseña (Autenticado)

Cambia la contraseña del usuario autenticado.

**Endpoint:** `POST /auth/update_password/`

**Autenticación:** Requerida (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Request Body:**
```json
{
  "current_password": "ContraseñaActual123!",
  "new_password": "NuevaContraseña123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

**Errores Comunes:**
- `400`: Contraseña actual incorrecta, ambos campos requeridos
- `401`: Token no válido o expirado

---

## Gestión de Perfil

### 9. Obtener Perfil Completo

Obtiene el perfil completo del usuario autenticado incluyendo direcciones, fotos de galería y enlaces.

**Endpoint:** `GET /auth/profile/`

**Autenticación:** Requerida (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "usuario123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "phone": "+1234567890",
  "about": "Desarrollador apasionado por la tecnología",
  "profile_picture": "/media/profile_pictures/2025/10/06/mi_foto.jpg",
  "profile_picture_url": "http://your-domain.com/media/profile_pictures/2025/10/06/mi_foto.jpg",
  "cover_image": "/media/cover_images/2025/10/09/mi_portada.jpg",
  "cover_image_url": "http://your-domain.com/media/cover_images/2025/10/09/mi_portada.jpg",
  "current_status": "Disponible",
  "note": "Notas personales",
  "date_joined": "2025-10-06T10:30:00Z",
  "is_active": true,
  "is_guest_converted": false,
  "is_crush": true,
  "crush_verification_status": "approved",
  "crush_requested_at": "2025-10-08T10:30:00Z",
  "crush_verified_at": "2025-10-09T15:45:00Z",
  "addresses": [
    {
      "id": 1,
      "user": 1,
      "country": "USA",
      "state": "California",
      "city": "Los Angeles",
      "zip_code": "90001",
      "address_line_1": "123 Main St",
      "address_line_2": "Apt 4B",
      "additional_details": "Puerta azul",
      "is_default_shipping": true,
      "is_default_billing": true,
      "guest_email": null,
      "guest_first_name": null,
      "guest_last_name": null,
      "guest_phone": null,
      "guest_full_name": null,
      "created_at": "2025-10-06T10:35:00Z",
      "updated_at": "2025-10-06T10:35:00Z"
    }
  ],
  "gallery_photos": [
    {
      "id": 1,
      "user": 1,
      "image": "http://your-domain.com/media/user_gallery/2025/10/06/photo1.jpg",
      "caption": "Mi foto favorita",
      "is_profile_picture": false,
      "uploaded_at": "2025-10-06T10:40:00Z"
    }
  ],
  "links": [
    {
      "id": 1,
      "user": 1,
      "title": "Mi Portfolio",
      "url": "https://mi-portfolio.com",
      "order": 0,
      "is_active": true,
      "created_at": "2025-10-06T10:45:00Z"
    }
  ],
  "guest_profile": null
}
```

**Errores Comunes:**
- `401`: Token no válido o expirado

---

### 10. Actualizar Perfil

Actualiza el perfil del usuario autenticado. Soporta actualización parcial (PATCH).

**Endpoint:** `POST /auth/update_profile/` o `PUT /auth/update_profile/` o `PATCH /auth/update_profile/`

**Autenticación:** Requerida (Bearer Token)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Opción A: JSON Request (application/json)

**Request Body:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "username": "juanperez",
  "phone": "+1234567890",
  "about": "Desarrollador apasionado",
  "current_status": "Disponible",
  "note": "Mis notas personales",
  "addresses": [
    {
      "id": 1,
      "country": "USA",
      "state": "California",
      "city": "Los Angeles",
      "zip_code": "90001",
      "address_line_1": "123 Main St",
      "address_line_2": "Apt 4B",
      "is_default_shipping": true,
      "is_default_billing": true
    }
  ],
  "links": [
    {
      "id": 1,
      "title": "Mi Portfolio",
      "url": "https://mi-portfolio.com",
      "order": 0,
      "is_active": true
    },
    {
      "title": "GitHub",
      "url": "https://github.com/usuario",
      "order": 1,
      "is_active": true
    }
  ]
}
```

**Nota sobre direcciones y links:**
- Si incluyes un `id`, se actualizará ese registro existente
- Si no incluyes `id`, se creará un nuevo registro
- Los registros que no estén en el array serán eliminados

**Response (200 OK):** Mismo formato que "Obtener Perfil Completo"

---

### Actualizar Foto de Perfil

Para actualizar la foto de perfil, usa el endpoint de actualizar perfil con `multipart/form-data`.

#### Opción B: Multipart Request (multipart/form-data)

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: multipart/form-data
```

**Form Data:**
```
first_name: Juan
last_name: Pérez
username: juanperez
phone: +1234567890
about: Desarrollador apasionado
profile_picture: [archivo de imagen]
```

**Tipos de archivo soportados para `profile_picture`:**
- JPG/JPEG
- PNG
- GIF
- WEBP

**Tamaño máximo recomendado:** 5MB

**Ejemplo con JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('first_name', 'Juan');
formData.append('last_name', 'Pérez');
formData.append('profile_picture', fileInput.files[0]);

fetch('http://your-domain.com/api/auth/update_profile/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Ejemplo con Axios:**
```javascript
const formData = new FormData();
formData.append('first_name', 'Juan');
formData.append('last_name', 'Pérez');
formData.append('profile_picture', fileInput.files[0]);

axios.post('http://your-domain.com/api/auth/update_profile/', formData, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'multipart/form-data'
  }
})
.then(response => console.log(response.data));
```

**Ejemplo con React:**
```jsx
const handleProfileUpdate = async (e) => {
  e.preventDefault();
  
  const formData = new FormData();
  formData.append('first_name', firstName);
  formData.append('last_name', lastName);
  if (profilePicture) {
    formData.append('profile_picture', profilePicture);
  }
  
  try {
    const response = await fetch('http://your-domain.com/api/auth/update_profile/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    });
    
    const data = await response.json();
    console.log('Profile updated:', data);
  } catch (error) {
    console.error('Error updating profile:', error);
  }
};
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "juanperez",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "phone": "+1234567890",
  "about": "Desarrollador apasionado",
  "profile_picture": "/media/profile_pictures/2025/10/06/nueva_foto.jpg",
  "profile_picture_url": "http://your-domain.com/media/profile_pictures/2025/10/06/nueva_foto.jpg",
  "current_status": "Disponible",
  "note": "Mis notas",
  "date_joined": "2025-10-06T10:30:00Z",
  "is_active": true,
  "is_guest_converted": false,
  "addresses": [...],
  "gallery_photos": [...],
  "links": [...],
  "guest_profile": null
}
```

---

### Subir Fotos a la Galería

Para subir fotos a la galería del usuario, usa `multipart/form-data` con campos numerados:

**Form Data:**
```
gallery_image_1: [archivo de imagen]
gallery_caption_1: Mi foto favorita
gallery_is_profile_1: false

gallery_image_2: [archivo de imagen]
gallery_caption_2: Vacaciones 2025
gallery_is_profile_2: false
```

**Nota:** Si estableces `gallery_is_profile_X: true`, esa foto también se mostrará como foto de perfil (además del campo `profile_picture` directo).

**Errores Comunes:**
- `400`: Datos de validación incorrectos, username ya existe
- `401`: Token no válido o expirado

---

## Funcionalidades Adicionales

### 11. Checkout de Invitado

Permite a usuarios no registrados realizar compras guardando su información como invitado.

**Endpoint:** `POST /auth/guest_checkout/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "invitado@ejemplo.com",
  "first_name": "María",
  "last_name": "García",
  "phone": "+1234567890",
  "country": "USA",
  "state": "California",
  "city": "Los Angeles",
  "zip_code": "90001",
  "address_line_1": "456 Oak St",
  "address_line_2": ""
}
```

**Response (201 Created):**
```json
{
  "guest_user": {
    "id": 1,
    "email": "invitado@ejemplo.com",
    "first_name": "María",
    "last_name": "García",
    "full_name": "María García",
    "phone": "+1234567890",
    "total_orders": 0,
    "total_spent": "0.00"
  },
  "message": "Guest checkout information saved successfully."
}
```

**Errores Comunes:**
- `400`: Datos de validación incorrectos

---

### 12. Verificar Disponibilidad de Username

Verifica si un username está disponible para registro.

**Endpoint:** `POST /auth/check_username/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "username": "nuevousuario"
}
```

**Response (200 OK):**
```json
{
  "available": true,
  "username": "nuevousuario",
  "message": "Username is available."
}
```

**O si no está disponible:**
```json
{
  "available": false,
  "username": "usuarioexistente",
  "message": "Username is already taken."
}
```

**Errores Comunes:**
- `400`: Username requerido

---

### 13. Verificar Usuario Invitado

Verifica si existe un perfil de invitado para un email (útil para conversión a usuario completo).

**Endpoint:** `POST /auth/check_guest/`

**Autenticación:** No requerida

**Request Body:**
```json
{
  "email": "invitado@ejemplo.com"
}
```

**Response (200 OK) - Con perfil de invitado:**
```json
{
  "has_guest_profile": true,
  "guest_data": {
    "first_name": "María",
    "last_name": "García",
    "phone": "+1234567890",
    "total_orders": 3,
    "total_spent": "150.00"
  },
  "message": "Found guest profile with 3 orders and $150.00 spent."
}
```

**Response (200 OK) - Sin perfil de invitado:**
```json
{
  "has_guest_profile": false,
  "message": "No guest profile found with this email."
}
```

**Errores Comunes:**
- `400`: Email requerido

---

## Estructura de Datos del Usuario

### Objeto User Completo

```typescript
interface User {
  id: number;
  email: string;
  username: string | null;
  first_name: string;
  last_name: string;
  full_name: string; // read-only, calculado
  phone: string | null;
  about: string | null;
  profile_picture: string | null; // Ruta relativa al archivo
  profile_picture_url: string | null; // URL completa (read-only)
  cover_image: string | null; // Ruta relativa al archivo
  cover_image_url: string | null; // URL completa (read-only)
  current_status: string | null;
  note: string | null;
  date_joined: string; // ISO 8601 datetime
  is_active: boolean;
  is_guest_converted: boolean;
  // Campos de Crush (Webcammer)
  is_crush: boolean; // Público - visible para todos
  crush_verification_status: 'none' | 'pending' | 'approved' | 'rejected'; // Privado - solo usuario propio
  crush_requested_at: string | null; // ISO 8601 datetime - Privado
  crush_verified_at: string | null; // ISO 8601 datetime - Privado
  // Relaciones
  addresses: Address[];
  gallery_photos: GalleryPhoto[];
  links: Link[];
  guest_profile: GuestUser | null;
}

interface Address {
  id?: number;
  user?: number;
  country: string;
  state: string;
  city: string;
  zip_code: string;
  address_line_1: string;
  address_line_2?: string;
  additional_details?: string;
  is_default_shipping: boolean;
  is_default_billing: boolean;
  guest_email?: string | null;
  guest_first_name?: string | null;
  guest_last_name?: string | null;
  guest_phone?: string | null;
  guest_full_name?: string | null;
  created_at: string;
  updated_at: string;
}

interface GalleryPhoto {
  id: number;
  user: number;
  image: string; // URL completa
  caption: string | null;
  is_profile_picture: boolean;
  uploaded_at: string;
}

interface Link {
  id?: number;
  user?: number;
  title: string;
  url: string;
  order: number;
  is_active: boolean;
  created_at?: string;
}

interface GuestUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string | null;
  total_orders: number;
  total_spent: string; // Decimal como string
  has_been_converted: boolean;
  converted_user: number | null;
  created_at: string;
  updated_at: string;
}
```

---

## Autenticación con JWT

### Uso de Tokens

Después del login o verificación de email, recibirás dos tokens:

- **Access Token**: Token de corta duración para autenticar requests (expira en 15 minutos por defecto)
- **Refresh Token**: Token de larga duración para obtener nuevos access tokens (expira en 7 días por defecto)

### Incluir Access Token en Requests

```javascript
fetch('http://your-domain.com/api/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

### Refrescar Access Token

Cuando el access token expira, usa el refresh token para obtener uno nuevo:

**Endpoint:** `POST /api/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "nuevo_access_token..."
}
```

### Ejemplo de Manejo de Token Expirado

```javascript
async function fetchWithAuth(url, options = {}) {
  let accessToken = localStorage.getItem('accessToken');
  
  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${accessToken}`
  };
  
  let response = await fetch(url, options);
  
  // Si el token expiró, refrescar y reintentar
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refreshToken');
    
    const refreshResponse = await fetch('http://your-domain.com/api/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      localStorage.setItem('accessToken', data.access);
      
      // Reintentar request original con nuevo token
      options.headers['Authorization'] = `Bearer ${data.access}`;
      response = await fetch(url, options);
    } else {
      // Refresh token también expiró, redirigir a login
      window.location.href = '/login';
      return null;
    }
  }
  
  return response;
}
```

---

## Códigos de Estado HTTP

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| 200 | OK | Request exitoso (GET, PUT, PATCH) |
| 201 | Created | Recurso creado exitosamente (POST) |
| 400 | Bad Request | Datos de validación incorrectos |
| 401 | Unauthorized | Token inválido, expirado o no proporcionado |
| 404 | Not Found | Recurso no encontrado |
| 405 | Method Not Allowed | Método HTTP no permitido |
| 500 | Internal Server Error | Error del servidor |

---

## Campos del Modelo User

### Campos Principales

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | string | Sí | Email único del usuario (usado para login) |
| `username` | string | No* | Username único para mostrar (máx 30 caracteres) |
| `first_name` | string | No | Nombre del usuario (máx 60 caracteres) |
| `last_name` | string | No | Apellido del usuario (máx 60 caracteres) |
| `phone` | string | No | Número de teléfono (formato: +999999999) |
| `about` | string | No | Descripción del usuario (máx 500 caracteres) |
| `profile_picture` | file | No | Foto de perfil del usuario (ImageField) |
| `cover_image` | file | No | Imagen de portada/banner del usuario (ImageField) |
| `current_status` | string | No | Estado actual del usuario (máx 100 caracteres) |
| `note` | string | No | Notas personales del usuario |
| `email_verified` | boolean | Auto | Si el email ha sido verificado |
| `is_guest_converted` | boolean | Auto | Si el usuario fue convertido desde invitado |

\* `username` es requerido durante el registro pero puede ser null/blank después

### Campos de Crush (Webcammer) - Solo Lectura

| Campo | Tipo | Visibilidad | Descripción |
|-------|------|-------------|-------------|
| `is_crush` | boolean | 🌍 Pública | Si el usuario es un Crush/Webcammer verificado |
| `crush_verification_status` | string | 🔒 Privada | Estado de verificación (none/pending/approved/rejected) |
| `crush_requested_at` | datetime | 🔒 Privada | Fecha y hora de solicitud de verificación |
| `crush_verified_at` | datetime | 🔒 Privada | Fecha y hora de aprobación |

**Nota:** Los campos marcados como 🔒 Privada solo son visibles para el propio usuario. El campo `is_crush` es público y se muestra en todos los perfiles.

### Campos de Solo Lectura

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único del usuario |
| `full_name` | string | Nombre completo (first_name + last_name) |
| `profile_picture_url` | string | URL completa de la foto de perfil |
| `cover_image_url` | string | URL completa de la imagen de portada |
| `date_joined` | datetime | Fecha de registro |
| `is_active` | boolean | Si la cuenta está activa |

---

## Validaciones de Campos

### Email
- Formato válido de email
- Único en la base de datos
- Requerido

### Username
- Máximo 30 caracteres
- Único (case-insensitive)
- Puede contener letras, números, guiones y guiones bajos
- Requerido durante registro

### Password
- Mínimo 8 caracteres
- No puede ser completamente numérico
- No puede ser muy común (e.g., "password123")
- No puede ser muy similar al email o username

### Phone
- Formato: `+999999999`
- Entre 9 y 15 dígitos
- El `+` al inicio es opcional

### Profile Picture
- Formatos soportados: JPG, JPEG, PNG, GIF, WEBP
- Se guarda en: `media/profile_pictures/YYYY/MM/DD/`

### Cover Image
- Formatos soportados: JPG, JPEG, PNG, GIF, WEBP
- Se guarda en: `media/cover_images/YYYY/MM/DD/`
- Recomendado: Imagen en formato horizontal/banner (ej: 1500x500px)
- Tamaño máximo recomendado: 5MB

---

## Notas Importantes

1. **Foto de Perfil vs Galería:**
   - El campo `profile_picture` es la forma directa y recomendada de establecer una foto de perfil
   - También existe `UserGallery` con `is_profile_picture=True` como método alternativo
   - El serializer `UserProfileSerializer` prioriza `profile_picture` directo sobre la galería

2. **Actualización Parcial:**
   - Todos los endpoints de actualización soportan `PATCH` para actualización parcial
   - Solo envía los campos que quieres actualizar

3. **Multipart vs JSON:**
   - Usa `multipart/form-data` cuando subas archivos (fotos)
   - Usa `application/json` para otros datos

4. **Tokens JWT:**
   - Guarda el access token y refresh token de forma segura (preferiblemente en httpOnly cookies)
   - Implementa lógica para refrescar automáticamente el access token cuando expire

5. **Direcciones y Links:**
   - Al actualizar direcciones/links, envía el array completo
   - Los items con `id` se actualizan, sin `id` se crean nuevos
   - Los items no incluidos en el array se eliminan

6. **Guest Checkout:**
   - Permite a usuarios no registrados comprar
   - Si luego se registran con el mismo email, su historial de compras se vincula automáticamente

---

## Ejemplos de Uso Completos

### Ejemplo 1: Flujo de Registro Completo

```javascript
// 1. Registrar usuario
const signupResponse = await fetch('http://your-domain.com/api/auth/signup/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'nuevo@ejemplo.com',
    username: 'nuevousuario',
    password: 'MiContraseña123!',
    password_confirm: 'MiContraseña123!'
  })
});

const signupData = await signupResponse.json();
console.log(signupData.message); // "Registration successful..."

// 2. Usuario recibe email con código, ingresa el código
const verifyResponse = await fetch('http://your-domain.com/api/auth/verify-email/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'nuevo@ejemplo.com',
    verification_code: '1234'
  })
});

const verifyData = await verifyResponse.json();
localStorage.setItem('accessToken', verifyData.access);
localStorage.setItem('refreshToken', verifyData.refresh);
console.log('Usuario verificado:', verifyData.user);
```

### Ejemplo 2: Actualizar Perfil con Foto

```javascript
const updateProfileWithPhoto = async (userData, photoFile) => {
  const formData = new FormData();
  
  // Agregar datos del usuario
  formData.append('first_name', userData.firstName);
  formData.append('last_name', userData.lastName);
  formData.append('phone', userData.phone);
  formData.append('about', userData.about);
  
  // Agregar foto de perfil si existe
  if (photoFile) {
    formData.append('profile_picture', photoFile);
  }
  
  const response = await fetch('http://your-domain.com/api/auth/update_profile/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
    },
    body: formData
  });
  
  const data = await response.json();
  console.log('Perfil actualizado:', data);
  console.log('URL de foto de perfil:', data.profile_picture_url);
  
  return data;
};

// Uso
const fileInput = document.querySelector('#profilePictureInput');
updateProfileWithPhoto({
  firstName: 'Juan',
  lastName: 'Pérez',
  phone: '+1234567890',
  about: 'Desarrollador web'
}, fileInput.files[0]);
```

### Ejemplo 3: Componente React Completo

```jsx
import React, { useState, useEffect } from 'react';

function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [profilePicture, setProfilePicture] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  // Cargar perfil al montar componente
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://your-domain.com/api/auth/profile/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });
      
      const data = await response.json();
      setUser(data);
      setFirstName(data.first_name);
      setLastName(data.last_name);
      setPreviewUrl(data.profile_picture_url);
      setLoading(false);
    } catch (error) {
      console.error('Error al cargar perfil:', error);
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfilePicture(file);
      // Crear preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('first_name', firstName);
    formData.append('last_name', lastName);
    if (profilePicture) {
      formData.append('profile_picture', profilePicture);
    }

    try {
      const response = await fetch('http://your-domain.com/api/auth/update_profile/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: formData
      });

      const data = await response.json();
      setUser(data);
      alert('¡Perfil actualizado exitosamente!');
    } catch (error) {
      console.error('Error al actualizar perfil:', error);
      alert('Error al actualizar perfil');
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="profile-container">
      <h1>Mi Perfil</h1>
      
      <form onSubmit={handleSubmit}>
        {/* Preview de foto de perfil */}
        <div className="profile-picture-section">
          {previewUrl && (
            <img 
              src={previewUrl} 
              alt="Profile" 
              style={{ width: '150px', height: '150px', borderRadius: '50%' }}
            />
          )}
          <input 
            type="file" 
            accept="image/*"
            onChange={handleFileChange}
          />
        </div>

        {/* Campos de formulario */}
        <div>
          <label>Nombre:</label>
          <input 
            type="text" 
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
        </div>

        <div>
          <label>Apellido:</label>
          <input 
            type="text" 
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>

        <button type="submit">Guardar Cambios</button>
      </form>

      {/* Mostrar información actual */}
      <div className="current-info">
        <h2>Información Actual</h2>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Nombre completo:</strong> {user.full_name}</p>
        <p><strong>Teléfono:</strong> {user.phone || 'No especificado'}</p>
        <p><strong>Acerca de:</strong> {user.about || 'No especificado'}</p>
        <p><strong>Estado:</strong> {user.current_status || 'No especificado'}</p>
      </div>
    </div>
  );
}

export default UserProfile;
```

---

## Ejemplo: Mostrar Badge de Crush

El campo `is_crush` indica si un usuario es un Crush verificado. Puedes usarlo para mostrar un badge especial.

### React Component - Crush Badge

```jsx
function CrushBadge({ user }) {
  if (!user.is_crush) {
    return null; // No mostrar nada si no es Crush
  }

  return (
    <span className="crush-badge" title="Crush Verificado">
      <span className="badge-icon">✓</span>
      <span className="badge-text">CRUSH</span>
    </span>
  );
}

// CSS sugerido:
/*
.crush-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 8px;
}

.badge-icon {
  font-size: 14px;
}
*/

// Uso en perfil de usuario:
function UserProfile({ user }) {
  return (
    <div className="user-profile">
      <h1>
        {user.username}
        <CrushBadge user={user} />
      </h1>
      <p>{user.about}</p>
    </div>
  );
}
```

### TypeScript - Type Guard y Badge

```typescript
interface User {
  id: number;
  username: string;
  is_crush: boolean;
  crush_verification_status: 'none' | 'pending' | 'approved' | 'rejected';
  // ... otros campos
}

// Type guard para verificar si es Crush
function isCrushVerified(user: User): boolean {
  return user.is_crush && user.crush_verification_status === 'approved';
}

// Componente con TypeScript
interface CrushBadgeProps {
  user: User;
  size?: 'small' | 'medium' | 'large';
}

function CrushBadge({ user, size = 'medium' }: CrushBadgeProps) {
  if (!isCrushVerified(user)) {
    return null;
  }

  const sizeClasses = {
    small: 'text-xs px-2 py-1',
    medium: 'text-sm px-3 py-1',
    large: 'text-base px-4 py-2'
  };

  return (
    <span 
      className={`crush-badge ${sizeClasses[size]}`}
      title="Crush Verificado"
    >
      ✓ CRUSH
    </span>
  );
}

// Uso con verificación de estado
function UserCard({ user }: { user: User }) {
  const renderVerificationStatus = () => {
    if (user.is_crush) {
      return <CrushBadge user={user} />;
    }
    
    if (user.crush_verification_status === 'pending') {
      return <span className="badge-pending">⏳ Verificación Pendiente</span>;
    }
    
    return null;
  };

  return (
    <div className="user-card">
      <img src={user.profile_picture_url} alt={user.username} />
      <h3>
        {user.username}
        {renderVerificationStatus()}
      </h3>
    </div>
  );
}
```

### Vanilla JavaScript - Badge Helper

```javascript
// Helper function para crear badge de Crush
function createCrushBadge(user) {
  if (!user.is_crush) {
    return '';
  }

  return `
    <span class="crush-badge" title="Crush Verificado">
      <span class="badge-icon">✓</span>
      <span class="badge-text">CRUSH</span>
    </span>
  `;
}

// Uso en HTML
function renderUserProfile(user) {
  const profileHTML = `
    <div class="user-profile">
      <div class="user-header">
        <img src="${user.profile_picture_url || '/default-avatar.png'}" 
             alt="${user.username}">
        <h1>
          ${user.username}
          ${createCrushBadge(user)}
        </h1>
      </div>
      <p>${user.about || 'Sin descripción'}</p>
    </div>
  `;
  
  document.getElementById('user-container').innerHTML = profileHTML;
}

// Fetch y renderizar
async function loadAndDisplayUser(accessToken) {
  const response = await fetch('http://api.crushme.com/api/auth/profile/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  const user = await response.json();
  renderUserProfile(user);
}
```

### Vue.js Component

```vue
<template>
  <div class="user-profile">
    <div class="user-header">
      <img :src="user.profile_picture_url || '/default-avatar.png'" 
           :alt="user.username">
      <h1>
        {{ user.username }}
        <span v-if="user.is_crush" class="crush-badge" title="Crush Verificado">
          <span class="badge-icon">✓</span>
          <span class="badge-text">CRUSH</span>
        </span>
      </h1>
    </div>
    
    <!-- Mostrar estado de verificación si es visible -->
    <div v-if="isOwnProfile && user.crush_verification_status === 'pending'" 
         class="verification-status">
      <span class="status-pending">⏳ Tu solicitud de Crush está siendo revisada</span>
    </div>
    
    <p>{{ user.about || 'Sin descripción' }}</p>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  props: {
    user: {
      type: Object,
      required: true
    },
    isOwnProfile: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    isCrushVerified() {
      return this.user.is_crush && this.user.crush_verification_status === 'approved';
    }
  }
}
</script>

<style scoped>
.crush-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, #ff69b4 0%, #ff1493 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 8px;
}

.status-pending {
  display: inline-block;
  padding: 8px 16px;
  background-color: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  color: #856404;
  margin-top: 8px;
}
</style>
```

---

## Soporte y Contacto

Para preguntas o problemas con la API, por favor contacta al equipo de desarrollo.

**Última actualización:** 9 de octubre, 2025

---

## Changelog

### v1.3.0 (2025-10-09)
- ✨ Sistema completo de verificación de Crush (Webcammer)
- ✨ Campos `is_crush`, `crush_verification_status`, `crush_requested_at`, `crush_verified_at`
- ✨ Endpoints para solicitar y cancelar verificación de Crush
- 📝 Documentación completa del sistema de Crush
- 📝 Ejemplos de código para mostrar badge de Crush

### v1.2.0 (2025-10-09)
- ✨ Añadido campo `cover_image` al modelo User para imagen de portada/banner
- ✨ Añadido campo `cover_image_url` (read-only) en serializers
- 📝 Actualizada documentación con validaciones del campo cover_image
- 📝 Actualizada interfaz TypeScript con nuevos campos

### v1.1.0 (2025-10-06)
- ✨ Añadido campo `profile_picture` al modelo User
- ✨ Añadido campo `profile_picture_url` (read-only) en serializers
- 📝 Documentación completa de endpoints de usuario
- 📝 Ejemplos de código en JavaScript/React
- 📝 Guías de uso de multipart/form-data para subir imágenes

### v1.0.0 (2025-10-06)
- 🎉 Lanzamiento inicial de la API de usuarios
- Autenticación con JWT
- Registro con verificación de email
- Gestión de perfil completo
- Guest checkout


