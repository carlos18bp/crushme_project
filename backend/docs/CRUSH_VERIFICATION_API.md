# API de Verificación de Crush - Documentación para Frontend

Esta documentación describe el sistema de verificación de Crush (Webcammer) en CrushMe. Los usuarios pueden solicitar ser verificados como Crush, y los administradores pueden aprobar o rechazar estas solicitudes.

## Tabla de Contenidos

- [Información General](#información-general)
- [¿Qué es un Crush?](#qué-es-un-crush)
- [Campos del Sistema](#campos-del-sistema)
- [Estados de Verificación](#estados-de-verificación)
- [Endpoints](#endpoints)
  - [Solicitar Verificación](#1-solicitar-verificación-de-crush)
  - [Cancelar Solicitud](#2-cancelar-solicitud-de-verificación)
  - [Verificar Estado](#3-verificar-estado-actual)
- [Gestión desde Admin](#gestión-desde-admin)
- [Ejemplos de Código](#ejemplos-de-código)
- [Flujo Completo](#flujo-completo)

---

## Información General

### Base URL

```
http://your-domain.com/api/auth/crush/
```

### Autenticación

Todos los endpoints de gestión de verificación de Crush requieren autenticación JWT.

```
Authorization: Bearer <access_token>
```

---

## ¿Qué es un Crush?

Un **Crush** es un usuario verificado que tiene un perfil especial en la plataforma, típicamente webcammers o creadores de contenido. El sistema de verificación asegura que solo usuarios legítimos tengan este estatus especial.

### Características de un Crush Verificado

- 🌟 **Badge especial** en el perfil
- ✨ **Visibilidad mejorada** en la plataforma
- 🎯 **Funcionalidades exclusivas** (si aplican)
- ✅ **Estatus verificado** visible para otros usuarios

---

## Campos del Sistema

El modelo User incluye los siguientes campos relacionados con Crush:

| Campo | Tipo | Descripción | Editable por Usuario |
|-------|------|-------------|---------------------|
| `is_crush` | boolean | Indica si el usuario es un Crush verificado | ❌ No (solo admin) |
| `crush_verification_status` | string | Estado de la solicitud de verificación | ❌ No (solo admin) |
| `crush_requested_at` | datetime | Fecha y hora de la solicitud | ❌ No (automático) |
| `crush_verified_at` | datetime | Fecha y hora de aprobación | ❌ No (automático) |
| `crush_rejection_reason` | string | Motivo de rechazo (si aplica) | ❌ No (solo admin) |

### Visibilidad de Campos

| Campo | Visible en Perfil Público | Visible en Perfil Propio |
|-------|---------------------------|-------------------------|
| `is_crush` | ✅ Sí | ✅ Sí |
| `crush_verification_status` | ❌ No | ✅ Sí |
| `crush_requested_at` | ❌ No | ✅ Sí |
| `crush_verified_at` | ❌ No | ✅ Sí |
| `crush_rejection_reason` | ❌ No | ✅ Sí |

---

## Estados de Verificación

El campo `crush_verification_status` puede tener los siguientes valores:

| Estado | Descripción | `is_crush` | Acciones Disponibles |
|--------|-------------|-----------|---------------------|
| `none` | Sin solicitud | `false` | Puede solicitar verificación |
| `pending` | Solicitud pendiente | `false` | Puede cancelar solicitud |
| `approved` | Verificación aprobada | `true` | Ninguna (ya verificado) |
| `rejected` | Solicitud rechazada | `false` | Puede volver a solicitar |

### Diagrama de Estados

```
┌─────────┐
│  none   │ ────── Solicitar ──────> ┌─────────┐
└─────────┘                           │ pending │
                                      └─────────┘
     ↑                                    │   │
     │                                    │   │
     │                              Aprobar Rechazar
     │                                    │   │
     │                                    ↓   ↓
     │                              ┌─────────┐  ┌──────────┐
     └──────── Cancelar ────────────│approved │  │ rejected │
                                    └─────────┘  └──────────┘
                                                       │
                                                       │
                                    Solicitar ─────────┘
                                    de nuevo
```

---

## Endpoints

### 1. Solicitar Verificación de Crush

Permite al usuario autenticado solicitar verificación como Crush.

**Endpoint:** `POST /auth/crush/request-verification/`

**Autenticación:** Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** Ninguno (vacío)

**Response Success (200 OK):**
```json
{
  "success": true,
  "message": "Crush verification request submitted successfully. An admin will review your request.",
  "crush_verification_status": "pending",
  "crush_requested_at": "2025-10-09T10:30:00Z"
}
```

**Errores Comunes:**

**Error 400 - Ya verificado:**
```json
{
  "success": false,
  "error": "You are already a verified Crush."
}
```

**Error 400 - Solicitud pendiente:**
```json
{
  "success": false,
  "error": "You already have a pending Crush verification request.",
  "requested_at": "2025-10-08T15:20:00Z"
}
```

**Error 401 - No autenticado:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 2. Cancelar Solicitud de Verificación

Permite al usuario cancelar una solicitud de verificación pendiente.

**Endpoint:** `POST /auth/crush/cancel-request/`

**Autenticación:** Requerida (JWT Token)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** Ninguno (vacío)

**Response Success (200 OK):**
```json
{
  "success": true,
  "message": "Crush verification request cancelled successfully.",
  "crush_verification_status": "none"
}
```

**Errores Comunes:**

**Error 400 - No hay solicitud pendiente:**
```json
{
  "success": false,
  "error": "You do not have a pending Crush verification request to cancel."
}
```

---

### 3. Verificar Estado Actual

Para verificar el estado actual de verificación de Crush, utiliza el endpoint de perfil estándar.

**Endpoint:** `GET /auth/profile/`

**Autenticación:** Requerida (JWT Token)

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "usuario123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "is_crush": false,
  "crush_verification_status": "pending",
  "crush_requested_at": "2025-10-09T10:30:00Z",
  "crush_verified_at": null,
  ...
}
```

---

## Gestión desde Admin

### Panel de Administración

Los administradores pueden gestionar las solicitudes de verificación de Crush desde el panel de Django Admin.

#### Vista de Lista

La lista de usuarios muestra:
- **Email** y **Username**
- **Crush Status**: Badge visual indicando si es Crush verificado
- **Request Status**: Estado de la solicitud con colores:
  - 🟡 **Amarillo** = Pendiente
  - 🟢 **Verde** = Aprobado
  - 🔴 **Rojo** = Rechazado
  - ⚪ **Gris** = Sin solicitud

#### Filtros Disponibles

Los administradores pueden filtrar usuarios por:
- `is_crush`: Mostrar solo Crushes verificados
- `crush_verification_status`: Filtrar por estado de solicitud
- `is_active`, `is_staff`, `date_joined`: Filtros estándar

#### Búsqueda

Buscar usuarios por:
- Email
- Username
- Nombre
- Apellido

#### Acciones en Masa

Los administradores pueden seleccionar múltiples usuarios y aplicar:

1. **✓ Approve selected Crush verification requests**
   - Aprueba todas las solicitudes pendientes seleccionadas
   - Establece `is_crush = true`
   - Establece `crush_verification_status = 'approved'`
   - Registra `crush_verified_at` con fecha actual
   - Limpia `crush_rejection_reason`

2. **✗ Reject selected Crush verification requests**
   - Rechaza todas las solicitudes pendientes seleccionadas
   - Mantiene `is_crush = false`
   - Establece `crush_verification_status = 'rejected'`
   - Añade un motivo de rechazo genérico
   - Limpia `crush_verified_at`

#### Vista de Detalle

En la página de detalle de un usuario, los administradores ven una sección colapsable "Crush Verification" con:
- `is_crush`: Checkbox para verificación manual
- `crush_verification_status`: Dropdown con estados
- `crush_requested_at`: Fecha de solicitud (read-only)
- `crush_verified_at`: Fecha de verificación (read-only)
- `crush_rejection_reason`: Campo de texto para motivo de rechazo

---

## Ejemplos de Código

### Ejemplo 1: Solicitar Verificación de Crush

```javascript
async function requestCrushVerification(accessToken) {
  try {
    const response = await fetch('http://api.crushme.com/api/auth/crush/request-verification/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok && data.success) {
      console.log('✅ Solicitud enviada:', data.message);
      console.log('Estado:', data.crush_verification_status);
      console.log('Fecha:', data.crush_requested_at);
      return data;
    } else {
      console.error('❌ Error:', data.error);
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Error de conexión:', error);
    throw error;
  }
}

// Uso:
requestCrushVerification(accessToken)
  .then(result => {
    alert('Solicitud enviada. Un administrador la revisará pronto.');
  })
  .catch(error => {
    alert(`Error: ${error.message}`);
  });
```

### Ejemplo 2: React - Componente de Verificación de Crush

```jsx
import React, { useState, useEffect } from 'react';

function CrushVerificationPanel({ user, accessToken, onUpdate }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Determinar el estado actual
  const isCrush = user.is_crush;
  const status = user.crush_verification_status;
  const isPending = status === 'pending';
  const isRejected = status === 'rejected';
  const canRequest = status === 'none' || status === 'rejected';

  // Solicitar verificación
  const handleRequestVerification = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://api.crushme.com/api/auth/crush/request-verification/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok && data.success) {
        alert('✅ Solicitud enviada exitosamente');
        onUpdate(); // Recargar perfil del usuario
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Error de conexión. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  // Cancelar solicitud
  const handleCancelRequest = async () => {
    if (!confirm('¿Estás seguro de cancelar tu solicitud?')) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://api.crushme.com/api/auth/crush/cancel-request/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok && data.success) {
        alert('Solicitud cancelada');
        onUpdate();
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Error de conexión. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  // Render
  return (
    <div className="crush-verification-panel">
      <h2>Verificación de Crush</h2>

      {/* Badge si ya es Crush */}
      {isCrush && (
        <div className="crush-badge">
          <span className="badge badge-crush">✓ CRUSH VERIFICADO</span>
          <p>¡Felicitaciones! Eres un Crush verificado.</p>
          {user.crush_verified_at && (
            <small>Verificado el: {new Date(user.crush_verified_at).toLocaleDateString()}</small>
          )}
        </div>
      )}

      {/* Estado pendiente */}
      {isPending && !isCrush && (
        <div className="status-pending">
          <div className="status-icon">⏳</div>
          <h3>Solicitud Pendiente</h3>
          <p>Tu solicitud está siendo revisada por un administrador.</p>
          <small>Solicitado el: {new Date(user.crush_requested_at).toLocaleDateString()}</small>
          <button 
            onClick={handleCancelRequest} 
            disabled={loading}
            className="btn btn-secondary"
          >
            {loading ? 'Cancelando...' : 'Cancelar Solicitud'}
          </button>
        </div>
      )}

      {/* Estado rechazado */}
      {isRejected && (
        <div className="status-rejected">
          <div className="status-icon">✗</div>
          <h3>Solicitud Rechazada</h3>
          <p>Tu solicitud fue revisada pero no fue aprobada.</p>
          {user.crush_rejection_reason && (
            <div className="rejection-reason">
              <strong>Motivo:</strong> {user.crush_rejection_reason}
            </div>
          )}
          <p>Puedes volver a solicitar verificación.</p>
        </div>
      )}

      {/* Botón para solicitar */}
      {canRequest && !isCrush && (
        <div className="request-section">
          <h3>Conviértete en Crush Verificado</h3>
          <p>
            Los Crushes verificados obtienen un badge especial y mayor visibilidad en la plataforma.
          </p>
          <button 
            onClick={handleRequestVerification} 
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Enviando...' : '🌟 Solicitar Verificación'}
          </button>
        </div>
      )}

      {/* Errores */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}

export default CrushVerificationPanel;
```

### Ejemplo 3: TypeScript - Hook Personalizado

```typescript
import { useState, useCallback } from 'react';

interface CrushVerificationResponse {
  success: boolean;
  message?: string;
  error?: string;
  crush_verification_status?: string;
  crush_requested_at?: string;
}

interface UseCrushVerification {
  requestVerification: () => Promise<void>;
  cancelRequest: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

export function useCrushVerification(accessToken: string): UseCrushVerification {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestVerification = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://api.crushme.com/api/auth/crush/request-verification/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data: CrushVerificationResponse = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Error al solicitar verificación');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  const cancelRequest = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://api.crushme.com/api/auth/crush/cancel-request/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      const data: CrushVerificationResponse = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Error al cancelar solicitud');
      }

      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  return {
    requestVerification,
    cancelRequest,
    loading,
    error
  };
}

// Uso del hook:
function MyComponent() {
  const { requestVerification, cancelRequest, loading, error } = useCrushVerification(accessToken);

  const handleRequest = async () => {
    try {
      await requestVerification();
      alert('Solicitud enviada');
    } catch (err) {
      console.error(err);
    }
  };

  // ... resto del componente
}
```

---

## Flujo Completo

### Desde la Perspectiva del Usuario

```
1. Usuario → Solicita verificación
   └─> POST /auth/crush/request-verification/
       
2. Sistema → Cambia estado a 'pending'
   └─> crush_verification_status = 'pending'
   └─> crush_requested_at = fecha actual

3. Usuario → Ve estado pendiente en su perfil
   └─> GET /auth/profile/
   └─> Muestra: "Solicitud pendiente"

4a. Admin → Aprueba solicitud (en Django Admin)
    └─> is_crush = true
    └─> crush_verification_status = 'approved'
    └─> crush_verified_at = fecha actual
    └─> Usuario ve badge de Crush verificado

4b. Admin → Rechaza solicitud (en Django Admin)
    └─> is_crush = false
    └─> crush_verification_status = 'rejected'
    └─> crush_rejection_reason = "motivo"
    └─> Usuario puede volver a solicitar

5. Usuario → (Opcional) Cancela solicitud antes de aprobación
   └─> POST /auth/crush/cancel-request/
   └─> crush_verification_status = 'none'
```

### Desde la Perspectiva del Admin

```
1. Admin → Accede a Django Admin
   └─> /admin/crushme_app/user/

2. Admin → Filtra usuarios con solicitudes pendientes
   └─> Filtro: crush_verification_status = 'pending'

3. Admin → Revisa perfil del usuario
   └─> Verifica información
   └─> Valida que sea legítimo

4a. Admin → Aprueba (selecciona usuarios y ejecuta acción)
    └─> Acción: "✓ Approve selected Crush verification requests"
    └─> Resultado: Usuarios verificados

4b. Admin → Rechaza (selecciona usuarios y ejecuta acción)
    └─> Acción: "✗ Reject selected Crush verification requests"
    └─> Opcionalmente: Edita motivo de rechazo
    └─> Resultado: Solicitudes rechazadas
```

---

## Mejores Prácticas

### Para el Frontend

1. **Mostrar estado claramente**
   - Usa badges visuales para Crushes verificados
   - Muestra el estado de la solicitud en el perfil del usuario
   - Indica claramente qué acciones están disponibles

2. **Validar antes de enviar**
   - Verifica el estado actual antes de permitir solicitar
   - Deshabilita botones durante operaciones pendientes
   - Muestra mensajes de confirmación claros

3. **Manejo de errores**
   - Captura y muestra errores de forma amigable
   - Proporciona opciones de retry
   - Explica por qué falló una acción

4. **Feedback visual**
   - Loading states durante requests
   - Mensajes de éxito/error
   - Actualizar UI inmediatamente después de acciones

### Para el Backend/Admin

1. **Revisar cuidadosamente**
   - Verificar información del perfil
   - Validar legitimidad del usuario
   - Documentar motivos de rechazo

2. **Comunicación**
   - Proporcionar motivos claros de rechazo
   - Considerar notificaciones por email
   - Mantener historial de cambios

3. **Seguridad**
   - Solo admins pueden aprobar/rechazar
   - Validar permisos en cada operación
   - Auditar cambios de estado

---

## Códigos de Estado HTTP

| Código | Descripción | Cuándo Ocurre |
|--------|-------------|---------------|
| 200 | OK | Solicitud/cancelación exitosa |
| 400 | Bad Request | Ya verificado, solicitud duplicada, sin solicitud para cancelar |
| 401 | Unauthorized | Token inválido o no proporcionado |
| 403 | Forbidden | Sin permisos (no debería ocurrir en estos endpoints) |
| 500 | Internal Server Error | Error del servidor |

---

## Preguntas Frecuentes

### ¿Cuánto tiempo tarda la aprobación?
Depende de la disponibilidad de los administradores. Generalmente entre 24-48 horas.

### ¿Puedo solicitar de nuevo después de un rechazo?
Sí, puedes volver a solicitar verificación después de un rechazo.

### ¿Puedo cancelar una solicitud aprobada?
No, una vez aprobado como Crush, solo un administrador puede remover el estatus.

### ¿Los Crushes pueden perder su verificación?
Sí, los administradores pueden remover el estatus de Crush si es necesario.

### ¿Qué información ven otros usuarios?
Otros usuarios solo ven si eres un Crush verificado (`is_crush: true`). No ven el estado de tu solicitud ni otros detalles.

---

## Changelog

### v1.0.0 (2025-10-09)
- 🎉 Lanzamiento inicial del sistema de verificación de Crush
- ✨ Endpoint para solicitar verificación
- ✨ Endpoint para cancelar solicitud
- ✨ Panel de administración con acciones en masa
- 📝 Documentación completa con ejemplos

---

## Contacto y Soporte

Para preguntas o problemas con el sistema de verificación de Crush, contacta al equipo de desarrollo.

**Última actualización:** 9 de octubre, 2025
**Versión:** 1.0.0

