# Sistema de Re-registro para Usuarios Inactivos

## Problema Resuelto

Usuarios que iniciaron el registro pero no completaron la verificación de email quedaban "atrapados":
- No podían completar el registro (perdieron el código de verificación)
- No podían registrarse de nuevo (el email ya existía en la BD)
- No podían acceder a la vista de verificación

Esto también afectaba a:
- Pre-registros de compras como invitado
- Usuarios que cerraron el navegador antes de verificar
- Códigos de verificación expirados (5 minutos)

## Solución Implementada

### Flujo de Re-registro para Usuarios Inactivos

**Endpoint:** `POST /api/auth/signup/`

**Lógica:**

1. **Usuario nuevo (email no existe):**
   - Crea usuario con `email_verified=False`
   - Genera código de 4 dígitos
   - Envía email de verificación
   - Retorna: `status=201`, `requires_verification=True`

2. **Usuario existe y está VERIFICADO (`email_verified=True`):**
   - Rechaza el registro
   - Retorna: `error: "A user with this email is already registered and verified. Please login."`
   - Status: `400 BAD_REQUEST`

3. **Usuario existe pero NO está VERIFICADO (`email_verified=False`):** ⭐ **NUEVO**
   - **Actualiza** username (si cambió y no está tomado por otro usuario verificado)
   - **Actualiza** password (si se proporcionó)
   - **Invalida** códigos de verificación anteriores (`used=True`)
   - **Genera** nuevo código de 4 dígitos
   - **Envía** nuevo email de verificación
   - Retorna: `status=200`, `requires_verification=True`, `updated=True`

### Validaciones

#### En la Vista (`auth_views.py`)

```python
# 1. Verificar si el email ya existe
existing_user = User.objects.get(email=email)

# 2. Si existe y está verificado → RECHAZAR
if existing_user and existing_user.email_verified:
    return Response({'error': '...'}, status=400)

# 3. Si existe pero NO verificado → ACTUALIZAR
if existing_user and not existing_user.email_verified:
    # Validar que el nuevo username no esté tomado por OTRO usuario
    if username != existing_user.username:
        if User.objects.filter(username__iexact=username).exclude(id=existing_user.id).exists():
            return Response({'error': 'Username taken'}, status=400)
    
    # Actualizar datos
    existing_user.username = username
    existing_user.set_password(password)
    existing_user.save()
    
    # Invalidar códigos anteriores
    PasswordCode.objects.filter(
        user=existing_user,
        code_type='email_verification',
        used=False
    ).update(used=True)
    
    # Generar y enviar nuevo código
    # ...
```

#### En el Serializer (`user_serializers.py`)

```python
def validate_email(self, value):
    """Solo rechaza si el email está VERIFICADO"""
    user = User.objects.filter(email=value).first()
    if user and user.email_verified:
        raise ValidationError("Email already registered and verified.")
    return value

def validate_username(self, value):
    """Solo rechaza si el username está tomado por usuario VERIFICADO"""
    existing = User.objects.filter(username__iexact=value).first()
    if existing and existing.email_verified:
        raise ValidationError("Username already taken.")
    return value
```

## Casos de Uso

### Caso 1: Usuario perdió el código
```
1. Usuario se registra: carlos@email.com, @carlos, pass123
2. Recibe código: 1234
3. Cierra el navegador sin verificar
4. Regresa más tarde
5. Intenta registrarse de nuevo con los mismos datos
6. ✅ Sistema actualiza su registro y envía nuevo código
```

### Caso 2: Usuario quiere cambiar username
```
1. Usuario se registró: carlos@email.com, @carlos, pass123
2. No verificó email
3. Regresa y quiere usar: carlos@email.com, @carlitos, pass123
4. ✅ Sistema actualiza username a @carlitos y envía nuevo código
```

### Caso 3: Usuario quiere cambiar password
```
1. Usuario se registró: carlos@email.com, @carlos, pass123
2. No verificó email
3. Regresa y quiere usar: carlos@email.com, @carlos, newpass456
4. ✅ Sistema actualiza password y envía nuevo código
```

### Caso 4: Pre-registro de compra
```
1. Usuario invitado hace compra
2. Sistema crea pre-registro: guest@email.com, @guest123, temppass
3. Usuario no completa verificación
4. Usuario regresa y se registra: guest@email.com, @mynewname, mypass
5. ✅ Sistema actualiza datos y envía código
```

### Caso 5: Username ya tomado por otro usuario
```
1. Usuario A: carlos@email.com, @carlos (verificado)
2. Usuario B se registra: maria@email.com, @maria (no verificado)
3. Usuario B regresa y quiere: maria@email.com, @carlos, pass
4. ❌ Sistema rechaza: "Username already taken by another user"
```

## Respuestas del Endpoint

### Usuario Nuevo
```json
{
  "message": "Registration successful. Please check your email for verification code.",
  "email": "user@email.com",
  "requires_verification": true
}
```
**Status:** `201 CREATED`

### Usuario Inactivo Actualizado
```json
{
  "message": "Your registration data has been updated. Please check your email for a new verification code.",
  "email": "user@email.com",
  "requires_verification": true,
  "updated": true
}
```
**Status:** `200 OK`

### Usuario Ya Verificado
```json
{
  "error": "A user with this email is already registered and verified. Please login."
}
```
**Status:** `400 BAD_REQUEST`

### Username Tomado
```json
{
  "error": "This username is already taken by another user."
}
```
**Status:** `400 BAD_REQUEST`

## Seguridad

✅ **Códigos anteriores invalidados:** Previene uso de códigos viejos
✅ **Validación de username:** No permite tomar usernames de usuarios verificados
✅ **Password hasheado:** Usa `set_password()` para hash seguro
✅ **Email único:** Solo permite un email por usuario verificado
✅ **Expiración de códigos:** 5 minutos de validez

## Logs

```
📧 Usuario inactivo encontrado: carlos@email.com. Actualizando datos y reenviando código...
```

## Archivos Modificados

- `crushme_app/views/auth_views.py` - Lógica de re-registro
- `crushme_app/serializers/user_serializers.py` - Validaciones ajustadas

## Testing

```bash
# 1. Registrar usuario
POST /api/auth/signup/
{
  "email": "test@email.com",
  "username": "testuser",
  "password": "Test123!",
  "password_confirm": "Test123!"
}
# Respuesta: 201, requires_verification=true

# 2. NO verificar email (simular usuario que cerró navegador)

# 3. Intentar registrarse de nuevo con datos diferentes
POST /api/auth/signup/
{
  "email": "test@email.com",
  "username": "newusername",
  "password": "NewPass123!",
  "password_confirm": "NewPass123!"
}
# Respuesta: 200, updated=true, nuevo código enviado

# 4. Verificar con el nuevo código
POST /api/auth/verify-email/
{
  "email": "test@email.com",
  "verification_code": "5678"
}
# Respuesta: 200, tokens JWT, cuenta activada
```

## Beneficios

✅ Usuarios nunca quedan "atrapados"
✅ Pueden actualizar sus datos antes de verificar
✅ Códigos viejos se invalidan automáticamente
✅ Experiencia de usuario mejorada
✅ Compatible con pre-registros de compras
✅ Seguro y validado
