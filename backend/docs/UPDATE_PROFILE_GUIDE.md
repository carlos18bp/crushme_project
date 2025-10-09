# Guía para Actualizar Perfil de Usuario - Frontend

Esta guía explica cómo enviar correctamente la información para actualizar el perfil de usuario, incluyendo imágenes (foto de perfil y cover image).

## Tabla de Contenidos

- [Endpoint](#endpoint)
- [Métodos Soportados](#métodos-soportados)
- [Content-Type](#content-type)
- [Actualizar Solo Texto](#actualizar-solo-texto)
- [Actualizar Solo Imágenes](#actualizar-solo-imágenes)
- [Actualizar Texto + Imágenes](#actualizar-texto--imágenes)
- [Ejemplos Completos](#ejemplos-completos)
- [Errores Comunes](#errores-comunes)
- [Validaciones](#validaciones)

---

## Endpoint

```
POST   /api/auth/update_profile/
PUT    /api/auth/update_profile/
PATCH  /api/auth/update_profile/
```

**Autenticación:** Requerida (JWT Bearer Token)

---

## Métodos Soportados

| Método | Cuándo usar |
|--------|-------------|
| `PATCH` | Actualización parcial (solo campos que cambien) - **RECOMENDADO** |
| `PUT` | Actualización completa (todos los campos) |
| `POST` | Alternativa (funciona igual que PUT) |

---

## Content-Type

Dependiendo de qué estás enviando:

| Tipo de Datos | Content-Type | Cuándo usar |
|---------------|--------------|-------------|
| Solo texto/JSON | `application/json` | Actualizar nombre, email, about, etc. |
| Imágenes o archivos | `multipart/form-data` | Subir profile_picture o cover_image |
| Texto + Imágenes | `multipart/form-data` | Actualizar todo junto |

---

## Actualizar Solo Texto

### Request

```javascript
// ✅ CORRECTO - Solo datos de texto
const response = await axios.patch('/api/auth/update_profile/', {
  first_name: 'Juan',
  last_name: 'Pérez',
  username: 'juanperez',
  about: 'Desarrollador web apasionado',
  phone: '+1234567890',
  current_status: 'Disponible',
  note: 'Mis notas personales'
}, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});
```

### Response (200 OK)

```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "juanperez",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "phone": "+1234567890",
  "about": "Desarrollador web apasionado",
  "current_status": "Disponible",
  "note": "Mis notas personales",
  "profile_picture_url": "http://api.com/media/profile_pictures/foto.jpg",
  "cover_image_url": "http://api.com/media/cover_images/portada.jpg",
  ...
}
```

---

## Actualizar Solo Imágenes

### ✅ FORMA CORRECTA

```javascript
// Obtener archivos del input
const profilePictureFile = document.getElementById('profile-pic').files[0];
const coverImageFile = document.getElementById('cover-image').files[0];

// Crear FormData
const formData = new FormData();

// ✅ Añadir archivos SOLO si existen
if (profilePictureFile) {
  formData.append('profile_picture', profilePictureFile);
}

if (coverImageFile) {
  formData.append('cover_image', coverImageFile);
}

// Enviar request
const response = await axios.patch('/api/auth/update_profile/', formData, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'multipart/form-data'
  }
});
```

### ❌ FORMAS INCORRECTAS

```javascript
// ❌ NO hagas esto - enviando arrays
formData.append('profile_picture', [profilePictureFile]); // Array
formData.append('profile_picture[]', profilePictureFile); // Notación de array

// ❌ NO hagas esto - múltiples archivos en mismo campo
formData.append('profile_picture', file1);
formData.append('profile_picture', file2); // Duplicado

// ❌ NO hagas esto - sin verificar que exista
formData.append('profile_picture', null); // null
formData.append('profile_picture', undefined); // undefined
```

---

## Actualizar Texto + Imágenes

### Request

```javascript
const formData = new FormData();

// Añadir datos de texto
formData.append('first_name', 'Juan');
formData.append('last_name', 'Pérez');
formData.append('about', 'Nueva descripción');
formData.append('phone', '+1234567890');

// Añadir imágenes (solo si existen)
if (profilePictureFile) {
  formData.append('profile_picture', profilePictureFile);
}

if (coverImageFile) {
  formData.append('cover_image', coverImageFile);
}

// Enviar
const response = await axios.put('/api/auth/update_profile/', formData, {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'multipart/form-data'
  }
});
```

---

## Ejemplos Completos

### Ejemplo 1: React Component Básico

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function UpdateProfileForm({ accessToken }) {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [profilePicture, setProfilePicture] = useState(null);
  const [coverImage, setCoverImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleProfilePictureChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('Profile picture seleccionada:', file.name);
      setProfilePicture(file);
    }
  };

  const handleCoverImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      console.log('Cover image seleccionada:', file.name);
      setCoverImage(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();

      // Añadir datos de texto
      if (firstName) formData.append('first_name', firstName);
      if (lastName) formData.append('last_name', lastName);

      // Añadir imágenes solo si existen
      if (profilePicture) {
        formData.append('profile_picture', profilePicture);
      }

      if (coverImage) {
        formData.append('cover_image', coverImage);
      }

      // Enviar request
      const response = await axios.patch('/api/auth/update_profile/', formData, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      console.log('Perfil actualizado:', response.data);
      alert('Perfil actualizado exitosamente');

      // Limpiar formulario
      setProfilePicture(null);
      setCoverImage(null);
    } catch (error) {
      console.error('Error:', error.response?.data || error.message);
      alert('Error al actualizar perfil');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
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

      <div>
        <label>Foto de Perfil:</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleProfilePictureChange}
        />
        {profilePicture && <p>Seleccionado: {profilePicture.name}</p>}
      </div>

      <div>
        <label>Imagen de Portada:</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleCoverImageChange}
        />
        {coverImage && <p>Seleccionado: {coverImage.name}</p>}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Actualizando...' : 'Guardar Cambios'}
      </button>
    </form>
  );
}

export default UpdateProfileForm;
```

### Ejemplo 2: Vue.js con Pinia Store

```javascript
// stores/profileStore.js
import { defineStore } from 'pinia';
import axios from 'axios';

export const useProfileStore = defineStore('profile', {
  state: () => ({
    user: null,
    loading: false,
    error: null
  }),

  actions: {
    // Actualizar solo imágenes
    async uploadProfileImages(profilePicture, coverImage) {
      this.loading = true;
      this.error = null;

      try {
        // Validar que al menos una imagen existe
        if (!profilePicture && !coverImage) {
          throw new Error('Selecciona al menos una imagen');
        }

        const formData = new FormData();

        // Añadir solo si existe y es un File
        if (profilePicture && profilePicture instanceof File) {
          formData.append('profile_picture', profilePicture);
          console.log('✅ profile_picture añadida:', profilePicture.name);
        }

        if (coverImage && coverImage instanceof File) {
          formData.append('cover_image', coverImage);
          console.log('✅ cover_image añadida:', coverImage.name);
        }

        const response = await axios.patch('/api/auth/update_profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        this.user = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Actualizar perfil completo
    async updateProfile(data, profilePicture = null, coverImage = null) {
      this.loading = true;
      this.error = null;

      try {
        const formData = new FormData();

        // Añadir datos de texto
        Object.keys(data).forEach(key => {
          if (data[key] !== null && data[key] !== undefined && data[key] !== '') {
            formData.append(key, data[key]);
          }
        });

        // Añadir imágenes si existen
        if (profilePicture instanceof File) {
          formData.append('profile_picture', profilePicture);
        }

        if (coverImage instanceof File) {
          formData.append('cover_image', coverImage);
        }

        const response = await axios.put('/api/auth/update_profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        this.user = response.data;
        return response.data;
      } catch (error) {
        this.error = error.response?.data || error.message;
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});
```

```vue
<!-- MyProfile.vue -->
<script setup>
import { ref } from 'vue';
import { useProfileStore } from '@/stores/profileStore';

const profileStore = useProfileStore();
const profilePictureFile = ref(null);
const coverImageFile = ref(null);

const handleProfilePictureChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    profilePictureFile.value = file;
    console.log('Profile picture seleccionada:', file.name, file.size, 'bytes');
  }
};

const handleCoverImageChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    coverImageFile.value = file;
    console.log('Cover image seleccionada:', file.name, file.size, 'bytes');
  }
};

const handleSubmit = async () => {
  try {
    await profileStore.uploadProfileImages(
      profilePictureFile.value,
      coverImageFile.value
    );

    alert('Imágenes actualizadas exitosamente');
    
    // Limpiar
    profilePictureFile.value = null;
    coverImageFile.value = null;
  } catch (error) {
    alert('Error al actualizar imágenes');
  }
};
</script>

<template>
  <div class="profile-form">
    <div>
      <label>Foto de Perfil:</label>
      <input type="file" accept="image/*" @change="handleProfilePictureChange" />
      <span v-if="profilePictureFile">{{ profilePictureFile.name }}</span>
    </div>

    <div>
      <label>Imagen de Portada:</label>
      <input type="file" accept="image/*" @change="handleCoverImageChange" />
      <span v-if="coverImageFile">{{ coverImageFile.name }}</span>
    </div>

    <button @click="handleSubmit" :disabled="profileStore.loading">
      {{ profileStore.loading ? 'Subiendo...' : 'Guardar Imágenes' }}
    </button>
  </div>
</template>
```

### Ejemplo 3: JavaScript Vanilla

```javascript
// Obtener elementos del DOM
const form = document.getElementById('profile-form');
const profilePictureInput = document.getElementById('profile-picture');
const coverImageInput = document.getElementById('cover-image');
const firstNameInput = document.getElementById('first-name');
const lastNameInput = document.getElementById('last-name');

// Manejar submit
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData();

  // Añadir datos de texto
  const firstName = firstNameInput.value.trim();
  const lastName = lastNameInput.value.trim();

  if (firstName) formData.append('first_name', firstName);
  if (lastName) formData.append('last_name', lastName);

  // Añadir imágenes
  const profilePicture = profilePictureInput.files[0];
  const coverImage = coverImageInput.files[0];

  if (profilePicture) {
    formData.append('profile_picture', profilePicture);
    console.log('Profile picture:', profilePicture.name);
  }

  if (coverImage) {
    formData.append('cover_image', coverImage);
    console.log('Cover image:', coverImage.name);
  }

  // Validar que haya algo que actualizar
  if (formData.entries().next().done) {
    alert('No hay cambios para guardar');
    return;
  }

  try {
    const token = localStorage.getItem('access_token');

    const response = await fetch('/api/auth/update_profile/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`
        // NO incluir Content-Type - el navegador lo añade automáticamente con boundary
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(JSON.stringify(error));
    }

    const data = await response.json();
    console.log('Perfil actualizado:', data);
    alert('Perfil actualizado exitosamente');

    // Limpiar formulario
    form.reset();
  } catch (error) {
    console.error('Error:', error);
    alert('Error al actualizar perfil: ' + error.message);
  }
});
```

---

## Errores Comunes

### Error 400 - Bad Request

#### Causa 1: Enviando arrays en lugar de archivos

```javascript
// ❌ INCORRECTO
formData.append('profile_picture', [file]); // Array

// ✅ CORRECTO
formData.append('profile_picture', file); // File directo
```

#### Causa 2: Usando notación de array

```javascript
// ❌ INCORRECTO
formData.append('profile_picture[]', file);

// ✅ CORRECTO
formData.append('profile_picture', file);
```

#### Causa 3: Enviando null o undefined

```javascript
// ❌ INCORRECTO
formData.append('profile_picture', null);

// ✅ CORRECTO - Solo añadir si existe
if (file) {
  formData.append('profile_picture', file);
}
```

#### Causa 4: Content-Type incorrecto para imágenes

```javascript
// ❌ INCORRECTO - usando JSON para archivos
headers: {
  'Content-Type': 'application/json'
}

// ✅ CORRECTO - usando multipart/form-data
headers: {
  'Content-Type': 'multipart/form-data'
}
```

### Error 401 - Unauthorized

```javascript
// Problema: Token inválido o expirado
// Solución: Verificar que el token esté correcto

const token = localStorage.getItem('access_token');
console.log('Token:', token); // Verificar que existe

headers: {
  'Authorization': `Bearer ${token}` // Verificar formato
}
```

### Error 413 - Payload Too Large

```javascript
// Problema: Archivo muy grande (>5MB)
// Solución: Validar tamaño antes de enviar

const MAX_SIZE = 5 * 1024 * 1024; // 5MB

if (file.size > MAX_SIZE) {
  alert('El archivo es muy grande. Máximo 5MB');
  return;
}
```

---

## Validaciones

### Validar Tipo de Archivo

```javascript
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];

function validateImageType(file) {
  if (!ALLOWED_TYPES.includes(file.type)) {
    throw new Error('Tipo de archivo no permitido. Usa JPG, PNG, GIF o WEBP');
  }
  return true;
}

// Uso
const file = input.files[0];
try {
  validateImageType(file);
  formData.append('profile_picture', file);
} catch (error) {
  alert(error.message);
}
```

### Validar Tamaño de Archivo

```javascript
const MAX_SIZE = 5 * 1024 * 1024; // 5MB

function validateImageSize(file) {
  if (file.size > MAX_SIZE) {
    throw new Error(`Archivo muy grande. Máximo ${MAX_SIZE / 1024 / 1024}MB`);
  }
  return true;
}

// Uso
try {
  validateImageSize(file);
  formData.append('profile_picture', file);
} catch (error) {
  alert(error.message);
}
```

### Validación Completa

```javascript
function validateImage(file) {
  const errors = [];

  // Validar que sea un File
  if (!(file instanceof File)) {
    errors.push('No es un archivo válido');
    return errors;
  }

  // Validar tipo
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  if (!allowedTypes.includes(file.type)) {
    errors.push('Tipo de archivo no permitido. Usa JPG, PNG, GIF o WEBP');
  }

  // Validar tamaño
  const maxSize = 5 * 1024 * 1024; // 5MB
  if (file.size > maxSize) {
    errors.push('Archivo muy grande. Máximo 5MB');
  }

  // Validar que no esté vacío
  if (file.size === 0) {
    errors.push('El archivo está vacío');
  }

  return errors;
}

// Uso
const file = input.files[0];
const errors = validateImage(file);

if (errors.length > 0) {
  alert('Errores:\n' + errors.join('\n'));
} else {
  formData.append('profile_picture', file);
}
```

---

## Debug y Troubleshooting

### Ver contenido del FormData

```javascript
// Debug: Ver qué estás enviando
const formData = new FormData();
formData.append('profile_picture', file);

for (let pair of formData.entries()) {
  console.log(pair[0], pair[1]);
  if (pair[1] instanceof File) {
    console.log('  - Es un archivo:', pair[1].name, pair[1].size, 'bytes');
  }
}
```

### Verificar el Request en Network

1. Abre DevTools (F12)
2. Ve a la pestaña **Network**
3. Envía el formulario
4. Busca el request a `/api/auth/update_profile/`
5. Ve a la pestaña **Payload** o **Request**
6. Verifica que:
   - Content-Type sea `multipart/form-data`
   - Los archivos aparezcan correctamente
   - No haya arrays

### Consola del Backend

Si ves errores 400, revisa la consola del backend Django:

```bash
# En tu terminal del backend verás algo como:
Bad Request: /api/auth/update_profile/
[09/Oct/2025 05:20:37] "PUT /api/auth/update_profile/ HTTP/1.1" 400 185

# Esto indica que el request llegó pero los datos no son válidos
```

---

## Resumen

### ✅ Checklist para Subir Imágenes

- [ ] Usar URL correcta: `/api/auth/update_profile/`
- [ ] Usar método PATCH o PUT
- [ ] Usar `multipart/form-data` como Content-Type
- [ ] Obtener archivo con `input.files[0]`
- [ ] Verificar que sea un `File` con `instanceof File`
- [ ] Añadir a FormData sin arrays: `formData.append('profile_picture', file)`
- [ ] NO usar notación de array: `profile_picture[]`
- [ ] Validar tipo y tamaño de archivo
- [ ] Incluir token de autenticación
- [ ] Manejar errores apropiadamente

### ✅ Formato Correcto del FormData

```javascript
const formData = new FormData();
formData.append('profile_picture', profilePictureFile); // File directo
formData.append('cover_image', coverImageFile);         // File directo
```

### ❌ Formatos Incorrectos

```javascript
// ❌ NO hagas esto
formData.append('profile_picture', [file]);           // Array
formData.append('profile_picture[]', file);           // Notación de array
formData.append('profile_picture', null);             // null
formData.append('profile_picture', file, file);       // Duplicado
```

---

## Soporte

Si tienes problemas:

1. Verifica los errores en la consola del navegador
2. Revisa el Network tab en DevTools
3. Verifica los logs del backend Django
4. Asegúrate de que el token sea válido
5. Valida que los archivos sean del tipo correcto

**Última actualización:** 9 de octubre, 2025

