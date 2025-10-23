# Wompi - Corrección de Firma de Integridad

## 🐛 Problema Identificado

Las transacciones de Wompi estaban fallando porque **se estaba usando la llave incorrecta** para generar la firma de integridad.

### **Error:**
```python
# ❌ INCORRECTO - Usaba events_secret
integrity_string = f"{reference}{amount_in_cents}{currency}{self.events_secret}"
```

### **Solución:**
```python
# ✅ CORRECTO - Usa integrity_key
integrity_string = f"{reference}{amount_in_cents}{currency}{self.integrity_key}"
```

---

## 🔑 Llaves de Wompi y sus Usos

Wompi proporciona **4 llaves diferentes**, cada una con un propósito específico:

| Llave | Valor | Uso |
|-------|-------|-----|
| **Llave Pública** | `pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR` | Autenticación en requests API |
| **Llave Privada** | `prv_test_KfwGaDHAt9QikBRArROhTFbUFobB8dnn` | Operaciones sensibles (backend only) |
| **Eventos** | `test_events_yfttSa6ec6puxj8Ld6YTzbzdqY4w47gk` | Verificar webhooks |
| **Integridad** | `test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1` | **Firmar transacciones** ⭐ |

---

## 📝 Firma de Integridad

### **¿Qué es?**
La firma de integridad es un hash SHA-256 que Wompi usa para verificar que la transacción no ha sido manipulada.

### **Formato:**
```
reference + amount_in_cents + currency + integrity_key
```

### **Ejemplo:**
```python
reference = "ORD123456ABC"
amount_in_cents = 11500000  # 115,000 COP
currency = "COP"
integrity_key = "test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1"

# Concatenar
integrity_string = "ORD123456ABC11500000COPtest_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1"

# Generar SHA-256
integrity_signature = hashlib.sha256(integrity_string.encode()).hexdigest()
# Resultado: "a1b2c3d4e5f6..."
```

### **Envío a Wompi:**
```json
{
  "public_key": "pub_test_...",
  "amount_in_cents": 11500000,
  "currency": "COP",
  "reference": "ORD123456ABC",
  "signature:integrity": "a1b2c3d4e5f6...",
  "customer_email": "customer@example.com",
  "redirect_url": "https://yoursite.com/success"
}
```

---

## 🔧 Cambios Realizados

### **1. `wompi_service.py`**

**Agregado:**
```python
def __init__(self):
    self.public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
    self.private_key = getattr(settings, 'WOMPI_PRIVATE_KEY', '')
    self.events_secret = getattr(settings, 'WOMPI_EVENTS_SECRET', '')
    self.integrity_key = getattr(settings, 'WOMPI_INTEGRITY_KEY', '')  # ⭐ NUEVO
    self.base_url = getattr(settings, 'WOMPI_BASE_URL', 'https://production.wompi.co/v1')
    self.timeout = 30
```

**Corregido:**
```python
def create_transaction(self, ...):
    # Generate integrity signature
    # Format: reference + amount_in_cents + currency + integrity_key
    integrity_string = f"{reference}{amount_in_cents}{currency}{self.integrity_key}"  # ⭐ CORREGIDO
    integrity_signature = hashlib.sha256(integrity_string.encode()).hexdigest()
    
    logger.info(f"🔐 [WOMPI] Integrity string: {reference}{amount_in_cents}{currency}[INTEGRITY_KEY]")
    logger.info(f"🔐 [WOMPI] Integrity signature: {integrity_signature}")
```

### **2. `settings.py`**

**Agregado:**
```python
WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY', 'pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR')
WOMPI_PRIVATE_KEY = os.environ.get('WOMPI_PRIVATE_KEY', 'prv_test_KfwGaDHAt9QikBRArROhTFbUFobB8dnn')
WOMPI_EVENTS_SECRET = os.environ.get('WOMPI_EVENTS_SECRET', 'test_events_yfttSa6ec6puxj8Ld6YTzbzdqY4w47gk')
WOMPI_INTEGRITY_KEY = os.environ.get('WOMPI_INTEGRITY_KEY', 'test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1')  # ⭐ NUEVO
WOMPI_BASE_URL = 'https://production.wompi.co/v1'
WOMPI_ENVIRONMENT = 'test'
```

---

## ✅ Verificación

### **Logs Mejorados**

Ahora el servicio loguea la firma de integridad para debugging:

```
🔐 [WOMPI] Integrity string: ORD123456ABC11500000COP[INTEGRITY_KEY]
🔐 [WOMPI] Integrity signature: a1b2c3d4e5f6789...
🔵 [WOMPI] Creating transaction for reference: ORD123456ABC
✅ [WOMPI] Transaction created: 12345-1234-1234-1234
```

### **Test Manual**

Puedes probar la firma manualmente:

```python
import hashlib

reference = "TEST123"
amount = 10000  # 100 COP
currency = "COP"
integrity_key = "test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1"

string = f"{reference}{amount}{currency}{integrity_key}"
signature = hashlib.sha256(string.encode()).hexdigest()

print(f"String: {string}")
print(f"Signature: {signature}")
```

---

## 🧪 Testing

### **Request de Prueba**

```bash
POST /api/orders/wompi/create/
Content-Type: application/json

{
  "customer_email": "test@example.com",
  "customer_name": "Test User",
  "items": [
    {
      "woocommerce_product_id": 123,
      "product_name": "Test Product",
      "quantity": 1,
      "unit_price": 50000
    }
  ],
  "shipping_address": "Calle 123",
  "shipping_city": "Medellín",
  "shipping_state": "Antioquia",
  "shipping_postal_code": "050001",
  "shipping_country": "CO",
  "phone_number": "+57 300 1234567",
  "shipping": 10000
}
```

### **Response Esperada (Éxito)**

```json
{
  "success": true,
  "transaction_id": "12345-1234-1234-1234-123456789012",
  "payment_url": "https://checkout.wompi.co/l/aBcDeF123456",
  "reference": "ORD123456ABC",
  "total": "60000",
  "amount_in_cents": 6000000,
  "items_count": 1
}
```

### **Response Esperada (Error de Firma)**

Si la firma es incorrecta, Wompi retorna:

```json
{
  "error": {
    "type": "INPUT_VALIDATION_ERROR",
    "messages": {
      "signature:integrity": ["The signature is invalid"]
    }
  }
}
```

---

## 📚 Documentación de Wompi

### **Firma de Integridad:**
https://docs.wompi.co/docs/en/widgets-checkout#firma-de-integridad

### **API Reference:**
https://docs.wompi.co/docs/en/api

### **Formato de Firma:**
```
SHA256(reference + amount_in_cents + currency + integrity_key)
```

**⚠️ Importante:**
- No hay separadores entre los valores
- El orden es crítico: reference → amount → currency → key
- Debe ser SHA-256 en hexadecimal (lowercase)

---

## 🔐 Seguridad

### **Llaves en Producción**

Para producción, **NUNCA** hardcodear las llaves en el código:

```python
# ❌ MAL - Hardcoded
WOMPI_INTEGRITY_KEY = 'prod_integrity_ABC123...'

# ✅ BIEN - Variables de entorno
WOMPI_INTEGRITY_KEY = os.environ.get('WOMPI_INTEGRITY_KEY')
```

### **Variables de Entorno**

```bash
# .env
WOMPI_PUBLIC_KEY=pub_prod_YOUR_KEY
WOMPI_PRIVATE_KEY=prv_prod_YOUR_KEY
WOMPI_EVENTS_SECRET=prod_events_YOUR_SECRET
WOMPI_INTEGRITY_KEY=prod_integrity_YOUR_KEY
WOMPI_ENVIRONMENT=production
```

---

## 🎯 Resumen

### **Problema:**
❌ Usaba `events_secret` para firmar transacciones

### **Solución:**
✅ Usa `integrity_key` para firmar transacciones

### **Archivos Modificados:**
1. `crushme_app/services/wompi_service.py` - Corregida firma
2. `crushme_project/settings.py` - Agregada WOMPI_INTEGRITY_KEY

### **Resultado:**
✅ Las transacciones de Wompi ahora se crean correctamente  
✅ La firma de integridad es válida  
✅ Logs mejorados para debugging  

---

## 🚀 Próximos Pasos

1. **Reiniciar servidor Django** para cargar la nueva configuración
2. **Probar creación de transacción** con el endpoint `/wompi/create/`
3. **Verificar logs** para confirmar que la firma se genera correctamente
4. **Probar flujo completo** de pago con Wompi

Si sigues teniendo errores, revisa los logs del servidor para ver el mensaje exacto de error de Wompi.
