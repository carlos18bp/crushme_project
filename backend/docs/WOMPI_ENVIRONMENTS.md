# Wompi - Ambientes (Sandbox vs Production)

## 🐛 Error Común

```
ERROR: "La llave proporcionada no corresponde a este ambiente"
```

Este error ocurre cuando usas llaves de **TEST** con la URL de **PRODUCTION** (o viceversa).

---

## 🌍 Ambientes de Wompi

Wompi tiene 2 ambientes completamente separados:

### **1. Sandbox (Testing)**
- **URL:** `https://sandbox.wompi.co/v1`
- **Llaves:** Comienzan con `pub_test_`, `prv_test_`, `test_events_`, `test_integrity_`
- **Uso:** Desarrollo y pruebas
- **Tarjetas:** Tarjetas de prueba (no se cobran)

### **2. Production (Live)**
- **URL:** `https://production.wompi.co/v1`
- **Llaves:** Comienzan con `pub_prod_`, `prv_prod_`, `prod_events_`, `prod_integrity_`
- **Uso:** Producción con dinero real
- **Tarjetas:** Tarjetas reales (se cobran)

---

## ✅ Configuración Correcta

### **Para Testing (Sandbox)**

```python
# settings.py
WOMPI_PUBLIC_KEY = 'pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR'
WOMPI_PRIVATE_KEY = 'prv_test_KfwGaDHAt9QikBRArROhTFbUFobB8dnn'
WOMPI_EVENTS_SECRET = 'test_events_yfttSa6ec6puxj8Ld6YTzbzdqY4w47gk'
WOMPI_INTEGRITY_KEY = 'test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1'
WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'  # ⭐ SANDBOX
WOMPI_ENVIRONMENT = 'test'
```

### **Para Producción (Live)**

```python
# settings.py
WOMPI_PUBLIC_KEY = 'pub_prod_YOUR_PRODUCTION_KEY'
WOMPI_PRIVATE_KEY = 'prv_prod_YOUR_PRODUCTION_KEY'
WOMPI_EVENTS_SECRET = 'prod_events_YOUR_PRODUCTION_SECRET'
WOMPI_INTEGRITY_KEY = 'prod_integrity_YOUR_PRODUCTION_KEY'
WOMPI_BASE_URL = 'https://production.wompi.co/v1'  # ⭐ PRODUCTION
WOMPI_ENVIRONMENT = 'production'
```

---

## 🔑 Identificar Tipo de Llave

| Prefijo | Ambiente | Ejemplo |
|---------|----------|---------|
| `pub_test_` | Sandbox | `pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR` |
| `prv_test_` | Sandbox | `prv_test_KfwGaDHAt9QikBRArROhTFbUFobB8dnn` |
| `test_events_` | Sandbox | `test_events_yfttSa6ec6puxj8Ld6YTzbzdqY4w47gk` |
| `test_integrity_` | Sandbox | `test_integrity_Zjk5ESr4C6fLn2vH3JA8G2MPTqHIsPy1` |
| `pub_prod_` | Production | `pub_prod_ABC123...` |
| `prv_prod_` | Production | `prv_prod_ABC123...` |
| `prod_events_` | Production | `prod_events_ABC123...` |
| `prod_integrity_` | Production | `prod_integrity_ABC123...` |

---

## 🧪 Tarjetas de Prueba (Sandbox)

### **Visa - Aprobada**
```
Número: 4242 4242 4242 4242
CVV: 123
Fecha: Cualquier fecha futura (ej: 12/25)
```

### **Visa - Rechazada**
```
Número: 4111 1111 1111 1111
CVV: 123
Fecha: Cualquier fecha futura
```

### **Mastercard - Aprobada**
```
Número: 5555 5555 5555 4444
CVV: 123
Fecha: Cualquier fecha futura
```

**⚠️ Importante:** Estas tarjetas **SOLO** funcionan en Sandbox. No se cobran.

---

## 🔄 Cambiar de Sandbox a Production

### **Paso 1: Obtener Llaves de Producción**

1. Ir a https://comercios.wompi.co/
2. Completar proceso de verificación
3. Obtener llaves de producción (comienzan con `prod_`)

### **Paso 2: Actualizar Settings**

```python
# settings.py
WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY', 'pub_prod_YOUR_KEY')
WOMPI_PRIVATE_KEY = os.environ.get('WOMPI_PRIVATE_KEY', 'prv_prod_YOUR_KEY')
WOMPI_EVENTS_SECRET = os.environ.get('WOMPI_EVENTS_SECRET', 'prod_events_YOUR_SECRET')
WOMPI_INTEGRITY_KEY = os.environ.get('WOMPI_INTEGRITY_KEY', 'prod_integrity_YOUR_KEY')
WOMPI_BASE_URL = 'https://production.wompi.co/v1'  # Cambiar a production
WOMPI_ENVIRONMENT = 'production'
```

### **Paso 3: Variables de Entorno**

```bash
# .env
WOMPI_PUBLIC_KEY=pub_prod_YOUR_KEY
WOMPI_PRIVATE_KEY=prv_prod_YOUR_KEY
WOMPI_EVENTS_SECRET=prod_events_YOUR_SECRET
WOMPI_INTEGRITY_KEY=prod_integrity_YOUR_KEY
```

---

## 🔍 Debugging

### **Verificar Ambiente Actual**

Agrega este log en `wompi_service.py`:

```python
def __init__(self):
    self.public_key = getattr(settings, 'WOMPI_PUBLIC_KEY', '')
    self.base_url = getattr(settings, 'WOMPI_BASE_URL', '')
    
    # Detectar ambiente por la llave
    environment = 'SANDBOX' if 'test' in self.public_key else 'PRODUCTION'
    logger.info(f"🌍 [WOMPI] Environment: {environment}")
    logger.info(f"🔗 [WOMPI] Base URL: {self.base_url}")
    logger.info(f"🔑 [WOMPI] Public Key: {self.public_key[:20]}...")
```

### **Logs Esperados**

**Sandbox:**
```
🌍 [WOMPI] Environment: SANDBOX
🔗 [WOMPI] Base URL: https://sandbox.wompi.co/v1
🔑 [WOMPI] Public Key: pub_test_lHrCKMGf7JV...
```

**Production:**
```
🌍 [WOMPI] Environment: PRODUCTION
🔗 [WOMPI] Base URL: https://production.wompi.co/v1
🔑 [WOMPI] Public Key: pub_prod_ABC123...
```

---

## ⚠️ Errores Comunes

### **1. Llave Test con URL Production**

```python
# ❌ ERROR
WOMPI_PUBLIC_KEY = 'pub_test_...'  # Test key
WOMPI_BASE_URL = 'https://production.wompi.co/v1'  # Production URL
```

**Error:**
```
"La llave proporcionada no corresponde a este ambiente"
```

**Solución:**
```python
# ✅ CORRECTO
WOMPI_PUBLIC_KEY = 'pub_test_...'
WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'  # Sandbox URL
```

### **2. Llave Production con URL Sandbox**

```python
# ❌ ERROR
WOMPI_PUBLIC_KEY = 'pub_prod_...'  # Production key
WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'  # Sandbox URL
```

**Solución:**
```python
# ✅ CORRECTO
WOMPI_PUBLIC_KEY = 'pub_prod_...'
WOMPI_BASE_URL = 'https://production.wompi.co/v1'  # Production URL
```

### **3. Mezclar Llaves de Diferentes Ambientes**

```python
# ❌ ERROR - Mezclando test y prod
WOMPI_PUBLIC_KEY = 'pub_test_...'  # Test
WOMPI_INTEGRITY_KEY = 'prod_integrity_...'  # Production
```

**Solución:** Todas las llaves deben ser del mismo ambiente.

---

## 📊 Comparación

| Característica | Sandbox | Production |
|---------------|---------|------------|
| **URL** | `sandbox.wompi.co` | `production.wompi.co` |
| **Llaves** | `pub_test_`, `prv_test_` | `pub_prod_`, `prv_prod_` |
| **Tarjetas** | Tarjetas de prueba | Tarjetas reales |
| **Cobros** | ❌ No se cobran | ✅ Se cobran |
| **Verificación** | ❌ No requerida | ✅ Requerida |
| **Uso** | Desarrollo/Testing | Producción |

---

## 🎯 Configuración Recomendada

### **Development (Local)**

```python
# settings.py
if DEBUG:
    # Sandbox para desarrollo
    WOMPI_PUBLIC_KEY = 'pub_test_...'
    WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'
else:
    # Production para producción
    WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY')
    WOMPI_BASE_URL = 'https://production.wompi.co/v1'
```

### **Con Variables de Entorno**

```python
# settings.py
WOMPI_ENVIRONMENT = os.environ.get('WOMPI_ENVIRONMENT', 'test')

if WOMPI_ENVIRONMENT == 'production':
    WOMPI_BASE_URL = 'https://production.wompi.co/v1'
else:
    WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'

WOMPI_PUBLIC_KEY = os.environ.get('WOMPI_PUBLIC_KEY')
WOMPI_PRIVATE_KEY = os.environ.get('WOMPI_PRIVATE_KEY')
WOMPI_EVENTS_SECRET = os.environ.get('WOMPI_EVENTS_SECRET')
WOMPI_INTEGRITY_KEY = os.environ.get('WOMPI_INTEGRITY_KEY')
```

---

## 🚀 Testing

### **Verificar Configuración**

```bash
# En Django shell
python manage.py shell

>>> from django.conf import settings
>>> print(f"URL: {settings.WOMPI_BASE_URL}")
>>> print(f"Key: {settings.WOMPI_PUBLIC_KEY[:20]}...")
>>> 
>>> # Verificar que coincidan
>>> if 'test' in settings.WOMPI_PUBLIC_KEY:
...     assert 'sandbox' in settings.WOMPI_BASE_URL, "URL debe ser sandbox"
... else:
...     assert 'production' in settings.WOMPI_BASE_URL, "URL debe ser production"
```

---

## 📚 Referencias

- **Documentación Wompi:** https://docs.wompi.co/
- **Panel de Comercios:** https://comercios.wompi.co/
- **API Reference:** https://docs.wompi.co/docs/en/api

---

## ✅ Resumen

**Tu configuración actual (CORREGIDA):**
```python
WOMPI_PUBLIC_KEY = 'pub_test_lHrCKMGf7JVnO4DgnYrdDPgj1DSqJ0OR'  # TEST
WOMPI_BASE_URL = 'https://sandbox.wompi.co/v1'  # SANDBOX ✅
```

**Antes (INCORRECTO):**
```python
WOMPI_PUBLIC_KEY = 'pub_test_...'  # TEST
WOMPI_BASE_URL = 'https://production.wompi.co/v1'  # PRODUCTION ❌
```

**Ahora las llaves y el URL coinciden!** 🎉
