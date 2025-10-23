# Discount Code API

Sistema simple de códigos de descuento para CrushMe.

## Modelo: DiscountCode

### Campos:
- **code** (string, unique): Código de descuento (ej: "SUMMER2024", "WELCOME10")
- **discount_percentage** (decimal): Porcentaje de descuento (0-100)
- **is_active** (boolean): Si el código está activo
- **times_used** (integer): Número de veces que se ha usado
- **max_uses** (integer, opcional): Máximo de usos permitidos (null = ilimitado)
- **created_at** (datetime): Fecha de creación
- **updated_at** (datetime): Fecha de última actualización

## Endpoint de Validación

### POST /api/discounts/validate/

Valida un código de descuento introducido por el cliente.

#### Request:
```json
{
  "code": "SUMMER2024"
}
```

#### Response (código válido):
```json
{
  "exists": true,
  "code": "SUMMER2024",
  "discount_percentage": 20.00,
  "is_valid": true,
  "message": "Discount code is valid"
}
```

#### Response (código no existe):
```json
{
  "exists": false,
  "message": "Discount code not found"
}
```

#### Response (código existe pero no es válido):
```json
{
  "exists": true,
  "code": "EXPIRED10",
  "discount_percentage": 10.00,
  "is_valid": false,
  "message": "Discount code is not valid or has been used up"
}
```

## Validaciones

Un código es válido si:
1. `is_active = True`
2. No ha excedido `max_uses` (si está definido)

## Uso desde Frontend

```javascript
// Ejemplo de uso
const validateDiscountCode = async (code) => {
  try {
    const response = await axios.post('/api/discounts/validate/', {
      code: code.trim().toUpperCase()
    });
    
    if (response.data.exists && response.data.is_valid) {
      // Aplicar descuento
      const discountPercentage = response.data.discount_percentage;
      console.log(`Descuento aplicado: ${discountPercentage}%`);
    } else {
      console.log(response.data.message);
    }
  } catch (error) {
    console.error('Error validating discount code:', error);
  }
};
```

## Administración

Los códigos de descuento se pueden gestionar desde el Django Admin:

1. Ir a `/admin/`
2. Buscar "Discount Codes"
3. Crear/editar códigos con:
   - Código único
   - Porcentaje de descuento
   - Estado activo/inactivo
   - Límite de usos (opcional)

### Características del Admin:
- Vista con colores para estado activo/inactivo
- Estadísticas de uso con indicadores visuales
- Búsqueda por código
- Filtros por estado y fecha

## Ejemplos de Códigos

```python
# Código con 20% de descuento, ilimitado
DiscountCode.objects.create(
    code="WELCOME20",
    discount_percentage=20.00,
    is_active=True
)

# Código con 50% de descuento, máximo 100 usos
DiscountCode.objects.create(
    code="FLASH50",
    discount_percentage=50.00,
    is_active=True,
    max_uses=100
)
```

## Notas

- Los códigos son case-insensitive (se buscan en mayúsculas)
- El endpoint es público (AllowAny permission)
- No incrementa el contador de uso automáticamente (debe hacerse al confirmar la compra)
- Para incrementar uso: `discount_code.increment_usage()`
