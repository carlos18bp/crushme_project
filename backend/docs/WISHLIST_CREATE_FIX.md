# Fix: Error 400 al Crear Wishlist

## Problema

Al intentar crear una wishlist desde el frontend, se recibía un error 400:

```
POST http://localhost:5173/api/wishlists/create/ 400 (Bad Request)
Error: Invalid data
```

## Causa Raíz

El problema estaba en el serializer `WishListCreateUpdateSerializer`:

1. **Campos no marcados como opcionales explícitamente:**
   - Los campos `description`, `is_active`, `is_public`, y `shipping_data` no estaban marcados como `required=False`
   - Django REST Framework los trataba como requeridos por defecto

2. **Campo `shipping_data` sin `null=True` en el modelo:**
   - El modelo tenía `default=dict` pero no `null=True`
   - Esto causaba problemas de validación cuando el campo no se enviaba

3. **Validación de `shipping_data` retornaba `None`:**
   - Si el valor era vacío, retornaba `None` en lugar de `{}`
   - Esto causaba inconsistencias con el default del modelo

## Solución Implementada

### 1. Actualizar Serializer

**Archivo:** `crushme_app/serializers/wishlist_serializers.py`

```python
class WishListCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating wishlists
    """
    # Make optional fields explicitly optional
    description = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False, default=True)
    is_public = serializers.BooleanField(required=False, default=False)
    shipping_data = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = WishList
        fields = [
            'name', 'description', 'is_active', 'is_public', 'shipping_data'
        ]
    
    def validate_name(self, value):
        """Validate wishlist name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Wishlist name must be at least 2 characters long."
            )
        return value.strip()
    
    def validate_description(self, value):
        """Validate description if provided"""
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Description must be at least 5 characters long if provided."
            )
        return value.strip() if value else ""
    
    def validate_shipping_data(self, value):
        """Validate shipping data structure"""
        if value:
            allowed_keys = {'name', 'address', 'phone', 'email'}
            if not isinstance(value, dict):
                raise serializers.ValidationError(
                    "Shipping data must be a valid JSON object."
                )
            
            invalid_keys = set(value.keys()) - allowed_keys
            if invalid_keys:
                raise serializers.ValidationError(
                    f"Invalid shipping data keys: {', '.join(invalid_keys)}"
                )
            return value
        
        return {}  # Retornar {} en lugar de None
```

**Cambios:**
- ✅ `description`: `required=False, allow_blank=True`
- ✅ `is_active`: `required=False, default=True`
- ✅ `is_public`: `required=False, default=False`
- ✅ `shipping_data`: `required=False, allow_null=True`
- ✅ `validate_description`: Retorna `""` si está vacío
- ✅ `validate_shipping_data`: Retorna `{}` si está vacío o None

### 2. Actualizar Modelo

**Archivo:** `crushme_app/models/wishlist.py`

```python
# Shipping data stored as JSON
shipping_data = models.JSONField(
    default=dict,
    blank=True,
    null=True,  # ⭐ Agregado
    verbose_name="Shipping Data",
    help_text="JSON data containing shipping information (name, address, phone, email)"
)
```

**Cambios:**
- ✅ Agregado `null=True` para permitir valores nulos

### 3. Migración

**Archivo:** `crushme_app/migrations/0017_fix_wishlist_shipping_data_null.py`

```bash
python manage.py makemigrations crushme_app --name fix_wishlist_shipping_data_null
python manage.py migrate crushme_app
```

### 4. Mejorar Logging

**Archivo:** `crushme_app/views/wishlist_views.py`

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_wishlist(request):
    """
    Create a new wishlist
    
    Required fields:
    - name: string (min 2 characters)
    
    Optional fields:
    - description: string (min 5 characters if provided)
    - is_active: boolean (default: true)
    - is_public: boolean (default: false)
    - shipping_data: object with keys: name, address, phone, email
    """
    # Log request data for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Creating wishlist with data: {request.data}")
    
    serializer = WishListCreateUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        wishlist = serializer.save(user=request.user)
        detail_serializer = WishListDetailSerializer(wishlist, context={'request': request})
        
        return Response({
            'message': 'Wishlist created successfully',
            'wishlist': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    # Log validation errors
    logger.error(f"Wishlist creation failed: {serializer.errors}")
    
    return Response({
        'error': 'Invalid data',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
```

**Cambios:**
- ✅ Logging de datos de entrada
- ✅ Logging de errores de validación
- ✅ Documentación de campos en docstring

## Estructura de Request

### Mínimo Requerido

```json
POST /api/wishlists/create/
{
  "name": "Mi Wishlist"
}
```

### Con Todos los Campos Opcionales

```json
POST /api/wishlists/create/
{
  "name": "Mi Wishlist",
  "description": "Lista de productos que me gustan",
  "is_active": true,
  "is_public": false,
  "shipping_data": {
    "name": "Juan Pérez",
    "address": "Calle 123 #45-67",
    "phone": "+57 300 123 4567",
    "email": "juan@example.com"
  }
}
```

### Solo con Nombre y Descripción

```json
POST /api/wishlists/create/
{
  "name": "Mi Wishlist",
  "description": "Lista de productos favoritos"
}
```

## Validaciones

### Campo `name`
- ✅ **Requerido**
- ✅ Mínimo 2 caracteres (sin espacios)
- ✅ Se hace trim automático

### Campo `description`
- ✅ **Opcional**
- ✅ Mínimo 5 caracteres si se proporciona
- ✅ Se hace trim automático
- ✅ Default: `""`

### Campo `is_active`
- ✅ **Opcional**
- ✅ Tipo: boolean
- ✅ Default: `true`

### Campo `is_public`
- ✅ **Opcional**
- ✅ Tipo: boolean
- ✅ Default: `false`

### Campo `shipping_data`
- ✅ **Opcional**
- ✅ Tipo: JSON object
- ✅ Claves permitidas: `name`, `address`, `phone`, `email`
- ✅ Default: `{}`

## Respuestas

### Éxito (201 Created)

```json
{
  "message": "Wishlist created successfully",
  "wishlist": {
    "id": 1,
    "name": "Mi Wishlist",
    "description": "Lista de productos que me gustan",
    "user": {
      "id": 1,
      "username": "carlos18bp",
      "email": "carlos@example.com"
    },
    "user_username": "carlos18bp",
    "is_active": true,
    "is_public": false,
    "unique_link": "550e8400-e29b-41d4-a716-446655440000",
    "public_url": "http://localhost:5173/@carlos18bp/1",
    "shareable_path": "/@carlos18bp/1",
    "items": [],
    "total_items": 0,
    "total_value": 0,
    "is_favorited": false,
    "favorites_count": 0,
    "shipping_data": {
      "name": "Juan Pérez",
      "address": "Calle 123 #45-67",
      "phone": "+57 300 123 4567",
      "email": "juan@example.com"
    },
    "shipping_name": "Juan Pérez",
    "shipping_address": "Calle 123 #45-67",
    "shipping_phone": "+57 300 123 4567",
    "shipping_email": "juan@example.com",
    "created_at": "2025-10-27T08:00:00Z",
    "updated_at": "2025-10-27T08:00:00Z"
  }
}
```

### Error (400 Bad Request)

```json
{
  "error": "Invalid data",
  "details": {
    "name": [
      "Wishlist name must be at least 2 characters long."
    ]
  }
}
```

## Testing

### Test 1: Crear wishlist con solo nombre
```bash
curl -X POST http://localhost:8000/api/wishlists/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "Mi Wishlist"}'
```

**Resultado esperado:** 201 Created ✅

### Test 2: Crear wishlist con todos los campos
```bash
curl -X POST http://localhost:8000/api/wishlists/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Mi Wishlist",
    "description": "Lista de productos favoritos",
    "is_active": true,
    "is_public": false,
    "shipping_data": {
      "name": "Juan Pérez",
      "address": "Calle 123",
      "phone": "+57 300 123 4567",
      "email": "juan@example.com"
    }
  }'
```

**Resultado esperado:** 201 Created ✅

### Test 3: Crear wishlist con nombre corto
```bash
curl -X POST http://localhost:8000/api/wishlists/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "A"}'
```

**Resultado esperado:** 400 Bad Request con error de validación ✅

### Test 4: Crear wishlist sin nombre
```bash
curl -X POST http://localhost:8000/api/wishlists/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{}'
```

**Resultado esperado:** 400 Bad Request con error "name is required" ✅

## Logs del Backend

Con el logging agregado, ahora verás en la consola:

```
INFO: Creating wishlist with data: {'name': 'Mi Wishlist', 'description': 'Test'}
INFO: Wishlist created successfully: Mi Wishlist (ID: 1)
```

O en caso de error:

```
INFO: Creating wishlist with data: {'name': 'A'}
ERROR: Wishlist creation failed: {'name': ['Wishlist name must be at least 2 characters long.']}
```

## Archivos Modificados

1. **crushme_app/serializers/wishlist_serializers.py**
   - Clase `WishListCreateUpdateSerializer`
   - Campos marcados como opcionales explícitamente
   - Validaciones mejoradas

2. **crushme_app/models/wishlist.py**
   - Campo `shipping_data` con `null=True`

3. **crushme_app/views/wishlist_views.py**
   - Función `create_wishlist()`
   - Logging agregado
   - Documentación mejorada

4. **crushme_app/migrations/0017_fix_wishlist_shipping_data_null.py**
   - Nueva migración

## Fecha de Implementación

27 de octubre de 2025
