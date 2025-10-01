# API de Autenticación - CrushMe E-commerce

Esta documentación describe todos los endpoints de autenticación disponibles en la API de CrushMe.

## Configuración Base

**Base URL:** `http://localhost:8000/api/auth/`

**Headers requeridos:**
```
Content-Type: application/json
```

**Headers para endpoints autenticados:**
```
Authorization: Bearer <access_token>
```

---

## 📝 Flujo de Registro de Usuario

### 1. Registro (Signup)

Crea una nueva cuenta de usuario y envía código de verificación por email.

**Endpoint:** `POST /api/auth/signup/`

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "username": "miusuario123",
  "password": "MiPassword123!",
  "password_confirm": "MiPassword123!"
}
```

**Response (201 Created):**
```json
{
  "message": "Registration successful. Please check your email for verification code.",
  "email": "usuario@ejemplo.com",
  "requires_verification": true
}
```

**Response (400 Bad Request):**
```json
{
  "email": ["A user with this email already exists."],
  "username": ["A user with this username already exists."],
  "password": ["Passwords don't match."]
}
```

---

### 2. Verificación de Email

Verifica el código de 4 dígitos enviado por email y activa la cuenta.

**Endpoint:** `POST /api/auth/verify-email/`

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "verification_code": "1234"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "miusuario123",
    "first_name": "",
    "last_name": "",
    "full_name": "",
    "phone": "",
    "about": "",
    "date_joined": "2024-01-15T10:30:00Z",
    "is_active": true,
    "is_guest_converted": false,
    "addresses": [],
    "gallery_photos": [],
    "links": [],
    "profile_picture": null,
    "guest_profile": null
  },
  "message": "Email verified successfully. Account activated."
}
```

**Response (400 Bad Request):**
```json
{
  "verification_code": ["Invalid verification code."],
  "non_field_errors": ["Verification code has expired."]
}
```

---

### 3. Reenviar Código de Verificación

Reenvía un nuevo código de verificación si el anterior expiró.

**Endpoint:** `POST /api/auth/resend-verification/`

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

**Response (400 Bad Request):**
```json
{
  "error": "Email is already verified"
}
```

---

## 🔐 Autenticación

### 4. Iniciar Sesión (Login)

Autentica al usuario con email y contraseña.

**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "MiPassword123!"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "miusuario123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "full_name": "Juan Pérez",
    "phone": "+1234567890",
    "about": "Desarrollador apasionado",
    "date_joined": "2024-01-15T10:30:00Z",
    "is_active": true,
    "is_guest_converted": false,
    "addresses": [
      {
        "id": 1,
        "country": "Colombia",
        "state": "Cundinamarca",
        "city": "Bogotá",
        "zip_code": "110111",
        "address_line_1": "Calle 123 #45-67",
        "address_line_2": "Apt 101",
        "is_default_shipping": true,
        "is_default_billing": true
      }
    ],
    "gallery_photos": [],
    "links": [],
    "profile_picture": null,
    "guest_profile": null
  },
  "message": "Login successful."
}
```

**Response (400 Bad Request):**
```json
{
  "non_field_errors": ["Invalid email or password."]
}
```

**Response (400 Bad Request - Email no verificado):**
```json
{
  "non_field_errors": ["Email not verified. Please check your email for verification code."]
}
```

---

## 🔄 Recuperación de Contraseña

### 5. Solicitar Código de Recuperación

Envía código de 4 dígitos para recuperar contraseña.

**Endpoint:** `POST /api/auth/forgot-password/`

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

**Response (404 Not Found):**
```json
{
  "error": "User with this email does not exist"
}
```

---

### 6. Restablecer Contraseña

Verifica código y establece nueva contraseña.

**Endpoint:** `POST /api/auth/reset-password/`

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "reset_code": "5678",
  "new_password": "NuevaPassword123!",
  "new_password_confirm": "NuevaPassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successful. You can now login with your new password."
}
```

**Response (400 Bad Request):**
```json
{
  "reset_code": ["Invalid or expired reset code."],
  "new_password": ["Passwords don't match."]
}
```

---

## 👤 Gestión de Perfil

### 7. Obtener Perfil de Usuario

Obtiene información completa del perfil del usuario autenticado.

**Endpoint:** `GET /api/auth/profile/`

**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "miusuario123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "phone": "+1234567890",
  "about": "Desarrollador apasionado por la tecnología",
  "date_joined": "2024-01-15T10:30:00Z",
  "is_active": true,
  "is_guest_converted": false,
  "addresses": [
    {
      "id": 1,
      "user": 1,
      "country": "Colombia",
      "state": "Cundinamarca",
      "city": "Bogotá",
      "zip_code": "110111",
      "address_line_1": "Calle 123 #45-67",
      "address_line_2": "Apt 101",
      "is_default_shipping": true,
      "is_default_billing": true,
      "guest_email": null,
      "guest_first_name": null,
      "guest_last_name": null,
      "guest_phone": null,
      "guest_full_name": null,
      "created_at": "2024-01-15T11:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ],
  "gallery_photos": [
    {
      "id": 1,
      "user": 1,
      "image": "http://localhost:8000/media/user_gallery/2024/01/15/photo.jpg",
      "caption": "Mi foto de perfil",
      "is_profile_picture": true,
      "uploaded_at": "2024-01-15T12:00:00Z"
    }
  ],
  "links": [
    {
      "id": 1,
      "user": 1,
      "title": "Mi Portfolio",
      "url": "https://miportfolio.com",
      "order": 1,
      "is_active": true,
      "created_at": "2024-01-15T13:00:00Z"
    }
  ],
  "profile_picture": "http://localhost:8000/media/user_gallery/2024/01/15/photo.jpg",
  "guest_profile": null
}
```

---

### 8. Actualizar Perfil

Actualiza información del perfil del usuario.

**Endpoint:** `PUT /api/auth/update_profile/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "first_name": "Juan Carlos",
  "last_name": "Pérez García",
  "phone": "+57 300 123 4567",
  "about": "Desarrollador Full Stack con 5 años de experiencia"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "miusuario123",
    "first_name": "Juan Carlos",
    "last_name": "Pérez García",
    "full_name": "Juan Carlos Pérez García",
    "phone": "+57 300 123 4567",
    "about": "Desarrollador Full Stack con 5 años de experiencia"
  }
}
```

---

### 9. Cambiar Contraseña

Cambia la contraseña del usuario autenticado.

**Endpoint:** `POST /api/auth/update_password/`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "current_password": "MiPasswordActual123!",
  "new_password": "MiNuevaPassword456!",
  "new_password_confirm": "MiNuevaPassword456!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "current_password": ["Current password is incorrect."],
  "new_password": ["New passwords don't match."]
}
```

---

## 🛒 Checkout de Invitado

### 10. Checkout como Invitado

Permite realizar compras sin registrarse, guardando datos para futura conversión.

**Endpoint:** `POST /api/auth/guest_checkout/`

**Request Body:**
```json
{
  "email": "invitado@ejemplo.com",
  "first_name": "María",
  "last_name": "González",
  "phone": "+57 301 987 6543",
  "country": "Colombia",
  "state": "Antioquia",
  "city": "Medellín",
  "zip_code": "050001",
  "address_line_1": "Carrera 70 #45-30",
  "address_line_2": "Torre 2, Apt 502"
}
```

**Response (201 Created):**
```json
{
  "guest_user": {
    "id": 1,
    "email": "invitado@ejemplo.com",
    "first_name": "María",
    "last_name": "González",
    "full_name": "María González",
    "phone": "+57 301 987 6543",
    "total_orders": 0,
    "total_spent": "0.00"
  },
  "message": "Guest checkout information saved successfully."
}
```

---

## 🔍 Utilidades

### 11. Verificar Disponibilidad de Username

Verifica si un username está disponible para registro.

**Endpoint:** `POST /api/auth/check_username/`

**Request Body:**
```json
{
  "username": "nuevousuario123"
}
```

**Response (200 OK - Disponible):**
```json
{
  "available": true,
  "username": "nuevousuario123",
  "message": "Username is available."
}
```

**Response (200 OK - No disponible):**
```json
{
  "available": false,
  "username": "usuarioexistente",
  "message": "Username is already taken."
}
```

---

### 12. Verificar Usuario Invitado

Verifica si existe un perfil de invitado para un email (para conversión).

**Endpoint:** `POST /api/auth/check_guest/`

**Request Body:**
```json
{
  "email": "invitado@ejemplo.com"
}
```

**Response (200 OK - Con perfil de invitado):**
```json
{
  "has_guest_profile": true,
  "guest_data": {
    "first_name": "María",
    "last_name": "González",
    "phone": "+57 301 987 6543",
    "total_orders": 2,
    "total_spent": "150.00"
  },
  "message": "Found guest profile with 2 orders and $150.00 spent."
}
```

**Response (200 OK - Sin perfil de invitado):**
```json
{
  "has_guest_profile": false,
  "message": "No guest profile found with this email."
}
```

---

## 🔐 OAuth2

### 13. Login con Google

Autentica usuario usando token de Google OAuth2.

**Endpoint:** `POST /api/auth/google_login/`

**Request Body:**
```json
{
  "google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjdkYzAyYjk..."
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "usuario@gmail.com",
    "username": "usuario_google",
    "first_name": "Usuario",
    "last_name": "Google"
  },
  "message": "Google login successful."
}
```

---

## ⚠️ Códigos de Error Comunes

### Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos inválidos o faltantes
- **401 Unauthorized**: Token inválido o expirado
- **403 Forbidden**: Sin permisos para la operación
- **404 Not Found**: Recurso no encontrado
- **409 Conflict**: Conflicto (email/username ya existe)
- **500 Internal Server Error**: Error del servidor

### Errores de Validación Comunes

```json
{
  "email": ["Enter a valid email address."],
  "username": ["This field is required."],
  "password": ["This password is too short. It must contain at least 8 characters."],
  "verification_code": ["Code must be 4 digits"],
  "non_field_errors": ["Passwords don't match."]
}
```

---

## 📋 Características Especiales

### Códigos de Verificación
- **Longitud**: 4 dígitos numéricos
- **Duración**: 5 minutos
- **Tipos**: `email_verification`, `password_reset`
- **Uso único**: Se marcan como usados después de la verificación

### Conversión de Invitado a Usuario
- Los datos de checkout de invitado se preservan
- Al registrarse con el mismo email, se vinculan automáticamente
- El historial de compras se mantiene

### Tokens JWT
- **Access Token**: 60 minutos de duración
- **Refresh Token**: Para renovar access tokens
- **Formato**: Bearer token en header Authorization

### Validaciones de Seguridad
- Contraseñas con validación robusta de Django
- Usernames únicos (case-insensitive)
- Emails únicos
- Verificación obligatoria de email para activar cuenta

---

## 🚀 Ejemplos de Uso

### Flujo Completo de Registro
```bash
# 1. Registrarse
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "username": "testuser",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!"
  }'

# 2. Verificar email (código recibido por email)
curl -X POST http://localhost:8000/api/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "verification_code": "1234"
  }'

# 3. Iniciar sesión
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "password": "TestPassword123!"
  }'
```

### Flujo de Recuperación de Contraseña
```bash
# 1. Solicitar código de reset
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com"
  }'

# 2. Restablecer contraseña
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@ejemplo.com",
    "reset_code": "5678",
    "new_password": "NuevaPassword123!",
    "new_password_confirm": "NuevaPassword123!"
  }'
```

---

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contacta al equipo de desarrollo.

**Última actualización:** Enero 2024



