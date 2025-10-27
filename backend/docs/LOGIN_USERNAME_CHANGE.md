# Cambio de Sistema de Autenticación: Email → Username

## Resumen

El sistema de autenticación ha sido actualizado para usar **username** en lugar de **email** como campo de login.

## Cambios Realizados

### 1. Modelo User (`crushme_app/models/user.py`)

**Antes:**
```python
USERNAME_FIELD = 'email'
REQUIRED_FIELDS = []

username = models.CharField(
    max_length=30, 
    unique=True, 
    null=True,
    blank=True
)
```

**Después:**
```python
USERNAME_FIELD = 'username'
REQUIRED_FIELDS = ['email']

username = models.CharField(
    max_length=30, 
    unique=True, 
    null=False,
    blank=False
)
```

### 2. UserManager (`crushme_app/models/user.py`)

**Antes:**
```python
def create_user(self, email, password=None, **extra_fields):
    if not email:
        raise ValueError('The email must be defined')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    # ...
```

**Después:**
```python
def create_user(self, username, email=None, password=None, **extra_fields):
    if not username:
        raise ValueError('The username must be defined')
    if email:
        email = self.normalize_email(email)
    user = self.model(username=username, email=email, **extra_fields)
    # ...
```

### 3. Serializer de Login (`crushme_app/serializers/user_serializers.py`)

**Antes:**
```python
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = User.objects.get(email=email)
        authenticated_user = authenticate(username=email, password=password)
        # ...
```

**Después:**
```python
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = User.objects.get(username__iexact=username)
        authenticated_user = authenticate(username=user.username, password=password)
        # ...
```

### 4. Vista de Login (`crushme_app/views/auth_views.py`)

Actualizada la documentación para reflejar que ahora usa username en lugar de email.

### 5. Migración

**Archivo:** `crushme_app/migrations/0016_change_username_field_authentication.py`

La migración incluye:
- Función `generate_username_for_null_users()` que genera usernames únicos para usuarios existentes con username null
- Altera el campo `username` para hacerlo non-nullable

## Flujo de Autenticación

### Registro (sin cambios)
```json
POST /api/auth/signup/
{
  "username": "carlos18bp",
  "email": "carlos@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

### Login (ACTUALIZADO)

**Antes:**
```json
POST /api/auth/login/
{
  "email": "carlos@example.com",
  "password": "SecurePass123!"
}
```

**Después:**
```json
POST /api/auth/login/
{
  "username": "carlos18bp",
  "password": "SecurePass123!"
}
```

## Características

### Username
- ✅ Campo obligatorio (no null, no blank)
- ✅ Único en la base de datos
- ✅ Máximo 30 caracteres
- ✅ Case-insensitive para login (`username__iexact`)
- ✅ Usado para autenticación

### Email
- ✅ Sigue siendo único
- ✅ Usado para verificación y comunicación
- ✅ NO usado para autenticación
- ✅ Requerido en creación de superusuario

## Validaciones

### Login
1. Busca usuario por username (case-insensitive)
2. Verifica que el usuario esté activo (`is_active=True`)
3. Verifica que el email esté verificado (`email_verified=True`)
4. Autentica con password
5. Retorna tokens JWT si todo es válido

### Mensajes de Error
- `"Invalid username or password."` - Username no existe o password incorrecto
- `"Account is not activated. Please verify your email."` - Usuario no activo
- `"Email not verified. Please check your email for verification code."` - Email no verificado

## Compatibilidad

### Usuarios Existentes
La migración automáticamente genera usernames para usuarios que tenían username null:
- Usa la parte antes del `@` del email como base
- Agrega sufijo aleatorio si hay conflicto
- Formato: `{email_prefix}_{random6chars}`

### Superusuarios
Para crear superusuarios desde la terminal:
```bash
python manage.py createsuperuser
# Pedirá: username, email (opcional), password
```

## Testing

### Crear usuario de prueba
```bash
python manage.py shell
>>> from crushme_app.models import User
>>> user = User.objects.create_user(
...     username='testuser',
...     email='test@example.com',
...     password='TestPass123!'
... )
>>> user.email_verified = True
>>> user.save()
```

### Probar login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

## Archivos Modificados

1. `crushme_app/models/user.py`
   - Clase `UserManager`
   - Clase `User`
   
2. `crushme_app/serializers/user_serializers.py`
   - Clase `UserLoginSerializer`
   
3. `crushme_app/views/auth_views.py`
   - Función `login()`
   
4. `crushme_app/migrations/0016_change_username_field_authentication.py`
   - Nueva migración

## Próximos Pasos (Frontend)

El frontend necesitará actualizar:

1. **LoginView.vue** - Cambiar campo de email a username
2. **Formulario de login** - Actualizar labels y placeholders
3. **Validaciones** - Ajustar validaciones de username
4. **Mensajes de error** - Actualizar mensajes para reflejar username

### Ejemplo de cambio en frontend:
```vue
<!-- ANTES -->
<input 
  v-model="email" 
  type="email" 
  placeholder="Email"
/>

<!-- DESPUÉS -->
<input 
  v-model="username" 
  type="text" 
  placeholder="Username"
/>
```

## Notas Importantes

- ⚠️ El email sigue siendo único y requerido para registro
- ⚠️ El email sigue siendo usado para verificación y recuperación de contraseña
- ⚠️ Solo el campo de LOGIN cambió de email a username
- ✅ El registro sigue pidiendo username, email y password
- ✅ Cada usuario tiene un username único
- ✅ El login es case-insensitive para username

## Fecha de Implementación

27 de octubre de 2025
