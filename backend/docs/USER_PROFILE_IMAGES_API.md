# API de Imágenes de Perfil - Documentación para Frontend

Esta documentación describe cómo gestionar las imágenes de perfil de los usuarios en CrushMe, incluyendo foto de perfil (`profile_picture`) e imagen de portada (`cover_image`).

## Tabla de Contenidos

- [Información General](#información-general)
- [Campos de Imagen](#campos-de-imagen)
- [Subir/Actualizar Imágenes](#subiractualizar-imágenes)
- [Obtener URLs de Imágenes](#obtener-urls-de-imágenes)
- [Eliminar Imágenes](#eliminar-imágenes)
- [Validaciones y Límites](#validaciones-y-límites)
- [Ejemplos de Código](#ejemplos-de-código)
- [Mejores Prácticas](#mejores-prácticas)

---

## Información General

### Base URL

```
http://your-domain.com/api/auth/
```

### Autenticación

Todos los endpoints de gestión de imágenes de perfil requieren autenticación JWT.

```
Authorization: Bearer <access_token>
```

---

## Campos de Imagen

El modelo User incluye dos campos principales para imágenes:

### 1. Profile Picture (Foto de Perfil)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `profile_picture` | ImageField | Foto de perfil circular del usuario |
| `profile_picture_url` | string (read-only) | URL completa de la foto de perfil |

**Características:**
- ✅ Imagen cuadrada o circular recomendada
- 📐 Dimensiones recomendadas: 400x400px o 512x512px
- 📁 Se guarda en: `media/profile_pictures/YYYY/MM/DD/`
- 🔒 Campo **PÚBLICO** (visible para otros usuarios)

### 2. Cover Image (Imagen de Portada)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `cover_image` | ImageField | Imagen de banner/portada del perfil |
| `cover_image_url` | string (read-only) | URL completa de la imagen de portada |

**Características:**
- ✅ Imagen horizontal/banner recomendada
- 📐 Dimensiones recomendadas: 1500x500px (ratio 3:1)
- 📁 Se guarda en: `media/cover_images/YYYY/MM/DD/`
- 🔒 Campo **PÚBLICO** (visible para otros usuarios)

---

## Subir/Actualizar Imágenes

### Endpoint

**URL:** `PATCH /auth/profile/update/` o `PUT /auth/profile/update/`

**Autenticación:** Requerida (JWT Token)

**Content-Type:** `multipart/form-data`

### Método 1: Subir Profile Picture

**Request:**
```javascript
const formData = new FormData();
formData.append('profile_picture', profilePictureFile);

const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});
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
  "about": "Desarrollador web apasionado",
  "profile_picture": "/media/profile_pictures/2025/10/09/usuario123_profile.jpg",
  "profile_picture_url": "http://api.crushme.com/media/profile_pictures/2025/10/09/usuario123_profile.jpg",
  "cover_image": null,
  "cover_image_url": null,
  "current_status": "Disponible",
  "note": "Siempre aprendiendo algo nuevo",
  "date_joined": "2025-09-15T10:30:00Z",
  "is_active": true,
  "is_guest_converted": false,
  "addresses": [],
  "gallery_photos": [],
  "links": [],
  "guest_profile": null
}
```

### Método 2: Subir Cover Image

**Request:**
```javascript
const formData = new FormData();
formData.append('cover_image', coverImageFile);

const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});
```

**Response:** Similar al anterior, pero con `cover_image` y `cover_image_url` actualizados.

### Método 3: Subir Ambas Imágenes Simultáneamente

**Request:**
```javascript
const formData = new FormData();
formData.append('profile_picture', profilePictureFile);
formData.append('cover_image', coverImageFile);

const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});
```

### Método 4: Actualizar Imágenes con Otros Datos

**Request:**
```javascript
const formData = new FormData();
formData.append('profile_picture', profilePictureFile);
formData.append('cover_image', coverImageFile);
formData.append('first_name', 'Juan');
formData.append('last_name', 'Pérez');
formData.append('about', 'Nueva descripción');
formData.append('current_status', 'Ocupado');

const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});
```

---

## Obtener URLs de Imágenes

### Obtener Perfil Completo

**Endpoint:** `GET /auth/profile/`

**Autenticación:** Requerida (JWT Token)

**Request:**
```javascript
const response = await fetch('http://api.crushme.com/api/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const data = await response.json();
console.log('Profile Picture:', data.profile_picture_url);
console.log('Cover Image:', data.cover_image_url);
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "usuario123",
  "profile_picture_url": "http://api.crushme.com/media/profile_pictures/2025/10/09/usuario123_profile.jpg",
  "cover_image_url": "http://api.crushme.com/media/cover_images/2025/10/09/usuario123_cover.jpg",
  ...
}
```

---

## Eliminar Imágenes

Para eliminar una imagen, simplemente envía `null` o una cadena vacía en el campo correspondiente.

### Eliminar Profile Picture

**Request:**
```javascript
const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    profile_picture: null
  })
});
```

### Eliminar Cover Image

**Request:**
```javascript
const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    cover_image: null
  })
});
```

---

## Validaciones y Límites

### Formatos Soportados

✅ **Formatos permitidos:**
- JPEG / JPG
- PNG
- GIF
- WEBP

❌ **Formatos NO permitidos:**
- BMP, TIFF, SVG, otros

### Tamaños Recomendados

#### Profile Picture
- **Tamaño recomendado:** 400x400px o 512x512px
- **Ratio recomendado:** 1:1 (cuadrado)
- **Tamaño máximo de archivo:** 5MB
- **Uso:** Se muestra como círculo en la mayoría de interfaces

#### Cover Image
- **Tamaño recomendado:** 1500x500px
- **Ratio recomendado:** 3:1 (horizontal)
- **Tamaño máximo de archivo:** 5MB
- **Uso:** Banner horizontal en la parte superior del perfil

### Validaciones del Backend

El backend realiza las siguientes validaciones automáticamente:

1. ✅ Verifica que el archivo sea una imagen válida
2. ✅ Valida el formato de imagen
3. ✅ Comprueba el tamaño del archivo
4. ✅ Genera automáticamente una ruta única con fecha

### Errores Comunes

**Error 400 - Formato inválido:**
```json
{
  "profile_picture": ["Upload a valid image. The file you uploaded was either not an image or a corrupted image."]
}
```

**Error 400 - Archivo muy grande:**
```json
{
  "profile_picture": ["File size exceeds maximum allowed size."]
}
```

**Error 401 - No autenticado:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Ejemplos de Código

### Ejemplo 1: React - Subir Profile Picture con Preview

```jsx
import React, { useState } from 'react';

function ProfilePictureUpload({ accessToken }) {
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Mostrar preview
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    setUploading(true);

    const fileInput = document.querySelector('input[type="file"]');
    const file = fileInput.files[0];

    if (!file) {
      alert('Por favor selecciona una imagen');
      setUploading(false);
      return;
    }

    const formData = new FormData();
    formData.append('profile_picture', file);

    try {
      const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        alert('Foto de perfil actualizada exitosamente');
        console.log('Nueva URL:', data.profile_picture_url);
      } else {
        const error = await response.json();
        alert('Error: ' + JSON.stringify(error));
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="profile-picture-upload">
      <h2>Actualizar Foto de Perfil</h2>
      
      {preview && (
        <div className="preview">
          <img 
            src={preview} 
            alt="Preview" 
            style={{
              width: '150px',
              height: '150px',
              borderRadius: '50%',
              objectFit: 'cover'
            }}
          />
        </div>
      )}

      <form onSubmit={handleUpload}>
        <input 
          type="file" 
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button type="submit" disabled={uploading}>
          {uploading ? 'Subiendo...' : 'Subir Foto'}
        </button>
      </form>
    </div>
  );
}

export default ProfilePictureUpload;
```

### Ejemplo 2: React - Subir Cover Image

```jsx
import React, { useState } from 'react';

function CoverImageUpload({ accessToken }) {
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    setUploading(true);

    const fileInput = document.querySelector('input[type="file"]');
    const file = fileInput.files[0];

    if (!file) {
      alert('Por favor selecciona una imagen');
      setUploading(false);
      return;
    }

    const formData = new FormData();
    formData.append('cover_image', file);

    try {
      const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        alert('Imagen de portada actualizada exitosamente');
        console.log('Nueva URL:', data.cover_image_url);
      } else {
        const error = await response.json();
        alert('Error: ' + JSON.stringify(error));
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="cover-image-upload">
      <h2>Actualizar Imagen de Portada</h2>
      
      {preview && (
        <div className="preview">
          <img 
            src={preview} 
            alt="Preview" 
            style={{
              width: '100%',
              maxWidth: '600px',
              height: '200px',
              objectFit: 'cover',
              borderRadius: '8px'
            }}
          />
        </div>
      )}

      <form onSubmit={handleUpload}>
        <input 
          type="file" 
          accept="image/*"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button type="submit" disabled={uploading}>
          {uploading ? 'Subiendo...' : 'Subir Portada'}
        </button>
      </form>
      
      <p className="hint">
        Recomendado: 1500x500px (ratio 3:1) - Máx 5MB
      </p>
    </div>
  );
}

export default CoverImageUpload;
```

### Ejemplo 3: JavaScript Vanilla - Upload con Progress

```javascript
async function uploadProfileImage(file, accessToken, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append('profile_picture', file);

    // Track upload progress
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        onProgress(percentComplete);
      }
    });

    // Handle completion
    xhr.addEventListener('load', () => {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        resolve(data);
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    // Handle errors
    xhr.addEventListener('error', () => {
      reject(new Error('Network error'));
    });

    // Send request
    xhr.open('PATCH', 'http://api.crushme.com/api/auth/profile/update/');
    xhr.setRequestHeader('Authorization', `Bearer ${accessToken}`);
    xhr.send(formData);
  });
}

// Usage:
const fileInput = document.getElementById('profilePictureInput');
const file = fileInput.files[0];

uploadProfileImage(file, accessToken, (progress) => {
  console.log(`Upload progress: ${progress.toFixed(2)}%`);
  document.getElementById('progressBar').value = progress;
})
.then(data => {
  console.log('Upload successful:', data.profile_picture_url);
})
.catch(error => {
  console.error('Upload failed:', error);
});
```

### Ejemplo 4: Subir Ambas Imágenes con Validación

```javascript
async function uploadProfileImages(profilePicture, coverImage, accessToken) {
  // Validar formatos
  const validFormats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  
  if (profilePicture && !validFormats.includes(profilePicture.type)) {
    throw new Error('Formato de profile picture no válido');
  }
  
  if (coverImage && !validFormats.includes(coverImage.type)) {
    throw new Error('Formato de cover image no válido');
  }
  
  // Validar tamaños (5MB máximo)
  const maxSize = 5 * 1024 * 1024; // 5MB en bytes
  
  if (profilePicture && profilePicture.size > maxSize) {
    throw new Error('Profile picture excede 5MB');
  }
  
  if (coverImage && coverImage.size > maxSize) {
    throw new Error('Cover image excede 5MB');
  }
  
  // Crear FormData
  const formData = new FormData();
  if (profilePicture) formData.append('profile_picture', profilePicture);
  if (coverImage) formData.append('cover_image', coverImage);
  
  // Enviar request
  const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(JSON.stringify(error));
  }
  
  return await response.json();
}

// Usage:
const profilePicFile = document.getElementById('profilePic').files[0];
const coverImageFile = document.getElementById('coverImage').files[0];

try {
  const result = await uploadProfileImages(profilePicFile, coverImageFile, accessToken);
  console.log('Success:', result);
  console.log('Profile Picture URL:', result.profile_picture_url);
  console.log('Cover Image URL:', result.cover_image_url);
} catch (error) {
  console.error('Error:', error.message);
}
```

---

## Mejores Prácticas

### 1. Optimización de Imágenes

✅ **Antes de subir:**
- Redimensiona las imágenes a los tamaños recomendados
- Comprime las imágenes para reducir el tamaño del archivo
- Usa herramientas como TinyPNG, ImageOptim, o Sharp.js

```javascript
// Ejemplo: Redimensionar imagen antes de subir con Canvas
function resizeImage(file, maxWidth, maxHeight) {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height *= maxWidth / width;
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width *= maxHeight / height;
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(resolve, 'image/jpeg', 0.85);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

// Usage:
const originalFile = fileInput.files[0];
const resizedBlob = await resizeImage(originalFile, 1500, 500);
const resizedFile = new File([resizedBlob], originalFile.name, { type: 'image/jpeg' });
```

### 2. Validación en el Frontend

Valida las imágenes antes de enviarlas al backend:

```javascript
function validateImage(file, maxSize = 5 * 1024 * 1024) {
  const errors = [];
  
  // Validar que sea un archivo
  if (!file) {
    errors.push('No se ha seleccionado ningún archivo');
    return errors;
  }
  
  // Validar tipo
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  if (!validTypes.includes(file.type)) {
    errors.push('Formato de imagen no válido. Usa JPG, PNG, GIF o WEBP');
  }
  
  // Validar tamaño
  if (file.size > maxSize) {
    errors.push(`El archivo excede el tamaño máximo de ${maxSize / 1024 / 1024}MB`);
  }
  
  return errors;
}
```

### 3. Manejo de Errores

Implementa un manejo robusto de errores:

```javascript
async function uploadWithErrorHandling(file, accessToken) {
  try {
    // Validar antes de subir
    const errors = validateImage(file);
    if (errors.length > 0) {
      throw new Error(errors.join(', '));
    }
    
    // Subir imagen
    const formData = new FormData();
    formData.append('profile_picture', file);
    
    const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      
      if (response.status === 401) {
        throw new Error('Sesión expirada. Por favor inicia sesión nuevamente');
      } else if (response.status === 400) {
        throw new Error(JSON.stringify(errorData));
      } else {
        throw new Error('Error del servidor. Intenta nuevamente más tarde');
      }
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('Error al subir imagen:', error);
    // Mostrar mensaje al usuario
    alert(error.message);
    throw error;
  }
}
```

### 4. Loading States y UX

Proporciona feedback visual durante la carga:

```jsx
function ImageUploader({ accessToken }) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    setSuccess(false);
    setProgress(0);

    try {
      // Simular progreso durante la carga
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await uploadProfileImage(file, accessToken);
      
      clearInterval(progressInterval);
      setProgress(100);
      setSuccess(true);
      
      // Limpiar estado después de 3 segundos
      setTimeout(() => {
        setSuccess(false);
        setProgress(0);
      }, 3000);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      {uploading && (
        <div className="progress-bar">
          <div style={{ width: `${progress}%` }}></div>
          <span>{progress}%</span>
        </div>
      )}
      
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {success && (
        <div className="success-message">¡Imagen subida exitosamente!</div>
      )}
      
      <button onClick={() => handleUpload(file)} disabled={uploading}>
        {uploading ? 'Subiendo...' : 'Subir Imagen'}
      </button>
    </div>
  );
}
```

### 5. Cache y Actualización de URLs

Invalida el caché de imágenes después de actualizarlas:

```javascript
// Añadir timestamp para forzar recarga
function getImageUrlWithCacheBusting(url) {
  if (!url) return null;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}t=${Date.now()}`;
}

// Usage:
const updatedProfile = await uploadProfileImage(file, accessToken);
const freshImageUrl = getImageUrlWithCacheBusting(updatedProfile.profile_picture_url);

// Actualizar imagen en el DOM
document.getElementById('profilePic').src = freshImageUrl;
```

---

## Privacidad y Seguridad

### Campos Públicos vs Privados

| Campo | Visibilidad | Notas |
|-------|-------------|-------|
| `profile_picture` | 🌍 **PÚBLICO** | Visible para todos los usuarios |
| `profile_picture_url` | 🌍 **PÚBLICO** | URL pública accesible |
| `cover_image` | 🌍 **PÚBLICO** | Visible para todos los usuarios |
| `cover_image_url` | 🌍 **PÚBLICO** | URL pública accesible |

⚠️ **Importante:** Las imágenes de perfil y portada son públicas por diseño. No subas imágenes que contengan información sensible o privada.

### Recomendaciones de Seguridad

1. ✅ Valida siempre el tamaño y tipo de archivo en el frontend
2. ✅ El backend valida automáticamente las imágenes
3. ✅ Usa HTTPS en producción para proteger las transferencias
4. ✅ No almacenes tokens de acceso en localStorage (usa httpOnly cookies o memoria)
5. ✅ Implementa rate limiting para prevenir abuso

---

## Troubleshooting

### Problema: La imagen no se actualiza en el frontend

**Solución:** El navegador puede estar cacheando la imagen antigua. Usa cache-busting:

```javascript
const imageUrl = `${profile.profile_picture_url}?t=${Date.now()}`;
```

### Problema: Error CORS al subir imagen

**Solución:** Asegúrate de que el backend tiene configurados los headers CORS correctamente.

### Problema: "File too large" error

**Solución:** Comprime o redimensiona la imagen antes de subirla. El límite es 5MB.

### Problema: Preview no se muestra

**Solución:** Usa `URL.createObjectURL()` y recuerda revocar el objeto URL:

```javascript
const preview = URL.createObjectURL(file);
// Usar preview...
// Limpiar cuando ya no se necesite
URL.revokeObjectURL(preview);
```

---

## TypeScript Types

```typescript
// Types para imágenes de perfil
interface ProfileImages {
  profile_picture: File | null;
  profile_picture_url: string | null;
  cover_image: File | null;
  cover_image_url: string | null;
}

interface ImageUploadResponse {
  id: number;
  profile_picture_url: string | null;
  cover_image_url: string | null;
}

// Función con tipos
async function uploadImage(
  file: File,
  type: 'profile_picture' | 'cover_image',
  accessToken: string
): Promise<ImageUploadResponse> {
  const formData = new FormData();
  formData.append(type, file);
  
  const response = await fetch('http://api.crushme.com/api/auth/profile/update/', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Upload failed');
  }
  
  return await response.json();
}
```

---

## Changelog

### v1.2.0 (2025-10-09)
- ✨ Añadido campo `cover_image` para imagen de portada/banner
- ✨ Añadido campo `cover_image_url` (read-only) en respuestas
- 📝 Documentación completa de gestión de imágenes de perfil
- 📝 Ejemplos de código para React y JavaScript

### v1.1.0 (2025-10-06)
- ✨ Añadido campo `profile_picture` al modelo User
- ✨ Añadido campo `profile_picture_url` (read-only) en serializers
- 📝 Guías de uso de multipart/form-data

---

## Contacto y Soporte

Para preguntas o problemas con las imágenes de perfil, contacta al equipo de desarrollo.

**Última actualización:** 9 de octubre, 2025
**Versión:** 1.2.0

