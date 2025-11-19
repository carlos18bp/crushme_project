# 🎯 Testing del Webhook de Wompi

## TL;DR - Pasos Rápidos

```bash
# 1. Iniciar servidor Django
python manage.py runserver

# 2. En otra terminal, exponer con ngrok
./setup_ngrok_webhook.sh

# 3. Copiar la URL de ngrok (ej: https://a1b2-3c4d.ngrok-free.app)

# 4. Configurar en Wompi Dashboard
# URL: https://TU-URL-NGROK.ngrok-free.app/api/orders/wompi/webhook/
# Evento: transaction.updated

# 5. Crear una transacción de prueba desde el frontend
# O usar Postman/curl

# 6. Completar el pago en Wompi

# 7. Ver logs en la terminal del servidor Django
```

## 📍 Endpoint del Webhook

**URL Local:** `http://localhost:8000/api/orders/wompi/webhook/`

**URL con ngrok:** `https://TU-URL-NGROK.ngrok-free.app/api/orders/wompi/webhook/`

**Características:**
- ✅ Público (AllowAny)
- ✅ Acepta POST de Wompi
- ✅ Procesa pagos APPROVED automáticamente
- ✅ Crea órdenes en DB
- ✅ Envía emails
- ✅ Sincroniza con WooCommerce

## 🔧 Configuración con ngrok

### Opción 1: Script Automático (Recomendado)

```bash
./setup_ngrok_webhook.sh
```

Este script:
- ✅ Verifica que ngrok esté instalado
- ✅ Verifica que Django esté corriendo
- ✅ Inicia ngrok en puerto 8000
- ✅ Muestra instrucciones de configuración

### Opción 2: Manual

```bash
# Instalar ngrok
sudo snap install ngrok

# Iniciar ngrok
ngrok http 8000

# Copiar la URL que aparece
# Ejemplo: https://a1b2-3c4d-5e6f.ngrok-free.app
```

## 🎮 Configurar en Wompi Dashboard

1. **Ir a:** https://comercios.wompi.co/dashboard

2. **Navegar a:** Configuración → Webhooks → Eventos

3. **Agregar webhook:**
   - URL: `https://TU-URL-NGROK.ngrok-free.app/api/orders/wompi/webhook/`
   - Evento: `transaction.updated` ✅
   - Guardar

## 🧪 Testing Manual

### 1. Crear transacción de prueba

```bash
curl -X POST http://localhost:8000/api/orders/wompi/create/ \
  -H "Content-Type: application/json" \
  -H "X-Currency: COP" \
  -d '{
    "customer_email": "test@example.com",
    "customer_name": "Test User",
    "phone_number": "3001234567",
    "items": [
      {
        "woocommerce_product_id": 1234,
        "product_name": "Test Product",
        "quantity": 1,
        "unit_price": 50000
      }
    ],
    "shipping": 15000,
    "total": 65000,
    "shipping_address": "Calle 123",
    "shipping_city": "Bogotá",
    "shipping_state": "Cundinamarca",
    "shipping_postal_code": "110111",
    "shipping_country": "CO"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "widget_data": {...},
  "reference": "ORD-20231119-123456"  // ← Guardar este reference
}
```

### 2. Completar pago en Wompi

- Abrir la URL del widget
- Usar tarjeta de prueba de Wompi
- Completar el pago

### 3. Wompi envía webhook automáticamente

El webhook llegará a:
```
https://TU-URL-NGROK.ngrok-free.app/api/orders/wompi/webhook/
```

### 4. Verificar logs

En la terminal del servidor Django:

```
📬 [WOMPI WEBHOOK] Received webhook
📬 [WOMPI WEBHOOK] Event: transaction.updated, Status: APPROVED
✅ [WOMPI WEBHOOK] Found order data in cache
🔄 [WOMPI WEBHOOK] Processing order
✅ [WOMPI WEBHOOK] Order processed successfully: ORD-123456
```

## 🧪 Testing con Script

Para simular un webhook sin hacer un pago real:

```bash
# Primero crea una transacción y copia el reference
# Luego ejecuta:
python test_wompi_webhook.py ORD-20231119-123456
```

**Nota:** El reference debe existir en el cache (creado con `/api/orders/wompi/create/`)

## 🔍 Debugging

### Ver requests de ngrok

Abre en el navegador:
```
http://localhost:4040
```

Verás todos los requests que llegan a ngrok, incluyendo headers y body.

### Ver logs del servidor

```bash
# En la terminal donde corre Django
# Los logs aparecen automáticamente

# O ver archivo de logs
tail -f logs/django.log
```

### Verificar cache

```python
python manage.py shell

from django.core.cache import cache

# Ver datos de una orden
reference = "ORD-20231119-123456"
data = cache.get(f'wompi_order_data_{reference}')
print(data)

# Ver status de pago
status = cache.get(f'wompi_payment_status_{reference}')
print(status)
```

## ⚠️ Problemas Comunes

### 1. Webhook no llega

**Causa:** URL mal configurada en Wompi

**Solución:**
- Verificar que la URL sea exacta: `https://xxx.ngrok-free.app/api/orders/wompi/webhook/`
- Incluir la barra final `/`
- Verificar que ngrok esté corriendo

### 2. Error 404 - Order data not found

**Causa:** El reference no existe en cache

**Solución:**
- Crear la transacción primero con `/api/orders/wompi/create/`
- El cache expira en 1 hora
- Usar el reference correcto

### 3. Webhook llega pero no procesa

**Causa:** Status no es APPROVED

**Solución:**
- El webhook solo procesa transacciones APPROVED
- Verificar el status en los logs

### 4. Orden duplicada

**Causa:** El webhook se envió dos veces

**Solución:**
- El sistema detecta duplicados automáticamente
- Verifica los logs: "Order already exists"

## 📊 Estructura del Webhook

Wompi envía:

```json
{
  "event": "transaction.updated",
  "data": {
    "transaction": {
      "id": "12345-1234-1234-1234-123456789012",
      "status": "APPROVED",
      "reference": "ORD-20231119-123456",
      "customer_email": "test@example.com",
      "amount_in_cents": 6500000,
      "currency": "COP"
    }
  }
}
```

## 🚀 Producción

En producción, configura la URL real:

```
https://api.crushme.com/api/orders/wompi/webhook/
```

**Requisitos:**
- ✅ HTTPS (obligatorio)
- ✅ Certificado SSL válido
- ✅ Servidor accesible públicamente

## 📚 Documentación Completa

Ver: `docs/WOMPI_WEBHOOK_SETUP.md`

## ✅ Checklist

- [ ] Servidor Django corriendo
- [ ] ngrok instalado y corriendo
- [ ] URL de ngrok copiada
- [ ] Webhook configurado en Wompi
- [ ] Evento `transaction.updated` seleccionado
- [ ] Transacción de prueba creada
- [ ] Pago completado
- [ ] Webhook recibido
- [ ] Orden creada en DB
- [ ] Email enviado
