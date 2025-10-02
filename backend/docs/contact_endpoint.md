# API de Contacto - CrushMe

## Endpoint POST para Contacto

### URL
```
POST /api/contact/
```

### Descripción
Endpoint público para enviar mensajes de contacto. Cualquier usuario puede enviar un mensaje sin necesidad de autenticación.

### Campos Requeridos

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `email` | string | Email del contacto | Requerido, formato email válido |
| `nombre` | string | Nombre completo | Requerido, no vacío |
| `asunto` | string | Asunto del mensaje | Requerido, no vacío |
| `texto` | string | Contenido del mensaje | Requerido, mínimo 10 caracteres |

### Campos Opcionales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `numero` | string | Número de teléfono | Opcional |

---

## Ejemplo de Uso

### Request (Solicitud)

```bash
curl -X POST http://localhost:8000/api/contact/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "nombre": "Juan Pérez",
    "numero": "+506 8888-8888",
    "asunto": "Consulta sobre productos",
    "texto": "Hola, me gustaría obtener más información sobre los productos disponibles en su tienda."
  }'
```

### Response Exitosa (201 Created)

```json
{
  "success": true,
  "message": "Mensaje de contacto enviado exitosamente. Te responderemos pronto.",
  "contact": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "nombre": "Juan Pérez",
    "numero": "+506 8888-8888",
    "asunto": "Consulta sobre productos",
    "texto": "Hola, me gustaría obtener más información sobre los productos disponibles en su tienda.",
    "is_read": false,
    "is_responded": false,
    "admin_notes": null,
    "created_at": "2025-10-01T10:30:00Z",
    "updated_at": "2025-10-01T10:30:00Z"
  }
}
```

### Response de Error (400 Bad Request)

```json
{
  "success": false,
  "errors": {
    "email": ["El email es requerido"],
    "nombre": ["El nombre es requerido"],
    "asunto": ["El asunto es requerido"],
    "texto": ["El mensaje debe tener al menos 10 caracteres"]
  }
}
```

---

## Endpoints Adicionales (Solo Admin)

### Listar todos los contactos
```
GET /api/contact/all/
```

**Query Params:**
- `is_read` (opcional): Filtrar por leído (`true`/`false`)
- `is_responded` (opcional): Filtrar por respondido (`true`/`false`)

**Requiere:** Autenticación como Admin

---

### Ver detalle de un contacto
```
GET /api/contact/{contact_id}/
```

**Requiere:** Autenticación como Admin  
**Nota:** Al ver un mensaje, automáticamente se marca como leído

---

### Actualizar estado de un contacto
```
PATCH /api/contact/{contact_id}/status/
```

**Body (todos opcionales):**
```json
{
  "is_read": true,
  "is_responded": true,
  "admin_notes": "Cliente respondido por email"
}
```

**Requiere:** Autenticación como Admin

---

### Eliminar un contacto
```
DELETE /api/contact/{contact_id}/delete/
```

**Requiere:** Autenticación como Admin

---

## Ejemplo en JavaScript (Frontend)

```javascript
// Enviar formulario de contacto
async function enviarContacto(datos) {
  try {
    const response = await fetch('http://localhost:8000/api/contact/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: datos.email,
        nombre: datos.nombre,
        numero: datos.numero,
        asunto: datos.asunto,
        texto: datos.texto
      })
    });

    const result = await response.json();

    if (result.success) {
      console.log('Mensaje enviado:', result.message);
      // Mostrar mensaje de éxito al usuario
      alert(result.message);
    } else {
      console.error('Errores:', result.errors);
      // Mostrar errores al usuario
    }
  } catch (error) {
    console.error('Error al enviar:', error);
  }
}

// Ejemplo de uso
enviarContacto({
  email: 'cliente@example.com',
  nombre: 'María González',
  numero: '+506 1234-5678',
  asunto: 'Pregunta sobre envío',
  texto: '¿Realizan envíos a todo el país? ¿Cuánto tiempo tarda normalmente?'
});
```

## Ejemplo con Axios

```javascript
import axios from 'axios';

const contactoData = {
  email: 'cliente@example.com',
  nombre: 'Carlos Rodríguez',
  numero: '+506 9999-8888',
  asunto: 'Devolución de producto',
  texto: 'Necesito ayuda con la devolución de un producto que compré la semana pasada.'
};

axios.post('http://localhost:8000/api/contact/', contactoData)
  .then(response => {
    console.log('Éxito:', response.data.message);
    console.log('ID del contacto:', response.data.contact.id);
  })
  .catch(error => {
    if (error.response) {
      console.error('Errores de validación:', error.response.data.errors);
    } else {
      console.error('Error:', error.message);
    }
  });
```

---

## Modelo de Datos

### Campo `Contact` en la Base de Datos

```python
{
  "id": Integer,                    # ID único
  "email": String(EmailField),      # Email del contacto
  "nombre": String(max 100),        # Nombre completo
  "numero": String(max 20),         # Teléfono (opcional)
  "asunto": String(max 200),        # Asunto del mensaje
  "texto": Text,                    # Mensaje completo
  "is_read": Boolean,               # ¿Ha sido leído?
  "is_responded": Boolean,          # ¿Ha sido respondido?
  "admin_notes": Text,              # Notas internas del admin
  "created_at": DateTime,           # Fecha de creación
  "updated_at": DateTime            # Última actualización
}
```

---

## Notas Importantes

1. **Sin autenticación requerida:** El endpoint POST `/api/contact/` es público y puede ser usado por cualquier usuario sin necesidad de login.

2. **Validaciones automáticas:**
   - El email se convierte a minúsculas automáticamente
   - Los espacios en blanco se eliminan de nombre, asunto y texto
   - El mensaje debe tener al menos 10 caracteres

3. **Gestión de spam:** Considera implementar:
   - Rate limiting (límite de solicitudes)
   - reCAPTCHA en el frontend
   - Filtros de palabras prohibidas

4. **Notificaciones:** Puedes agregar lógica para enviar emails al admin cuando se reciba un nuevo contacto.

5. **Protección CSRF:** Si usas sesiones, asegúrate de incluir el token CSRF en las peticiones.


