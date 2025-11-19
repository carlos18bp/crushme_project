#!/usr/bin/env python
"""
Script para testear el webhook de Wompi localmente
Simula un webhook de Wompi enviando un POST al endpoint
"""
import requests
import json
from datetime import datetime

# Configuración
WEBHOOK_URL = "http://localhost:8000/api/orders/wompi/webhook/"

# Datos de prueba del webhook de Wompi
webhook_payload = {
    "event": "transaction.updated",
    "data": {
        "transaction": {
            "id": "12345-1234-1234-1234-123456789012",
            "status": "APPROVED",
            "reference": "ORD-20231119-123456",  # Cambiar por un reference real de tu cache
            "customer_email": "test@example.com",
            "amount_in_cents": 6500000,
            "currency": "COP",
            "payment_method_type": "CARD",
            "payment_method": {
                "type": "CARD",
                "extra": {
                    "bin": "424242",
                    "name": "VISA-4242",
                    "brand": "VISA",
                    "exp_year": "25",
                    "card_type": "CREDIT",
                    "exp_month": "12",
                    "last_four": "4242",
                    "card_holder": "Test User"
                }
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    },
    "sent_at": datetime.utcnow().isoformat() + "Z"
}

def test_webhook():
    """
    Envía un webhook de prueba al endpoint local
    """
    print("🧪 Testing Wompi Webhook")
    print("=" * 60)
    print(f"URL: {WEBHOOK_URL}")
    print(f"Reference: {webhook_payload['data']['transaction']['reference']}")
    print("=" * 60)
    print()
    
    print("📤 Enviando webhook...")
    print(json.dumps(webhook_payload, indent=2))
    print()
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Wompi-Webhook/1.0'
            },
            timeout=10
        )
        
        print(f"📥 Respuesta recibida:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        print()
        
        if response.status_code == 200:
            print("✅ Webhook procesado exitosamente!")
        elif response.status_code == 404:
            print("❌ Error: Order data not found in cache")
            print()
            print("💡 Solución:")
            print("1. Crea una transacción primero con POST /api/orders/wompi/create/")
            print("2. Copia el 'reference' que retorna")
            print("3. Actualiza el 'reference' en este script")
            print("4. Ejecuta este script de nuevo")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print()
        print("💡 Asegúrate de que el servidor Django esté corriendo:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_with_custom_reference(reference):
    """
    Prueba el webhook con un reference específico
    """
    webhook_payload['data']['transaction']['reference'] = reference
    test_webhook()

if __name__ == "__main__":
    import sys
    
    print()
    print("🚀 Wompi Webhook Tester")
    print()
    
    if len(sys.argv) > 1:
        # Si se pasa un reference como argumento
        reference = sys.argv[1]
        print(f"📋 Usando reference: {reference}")
        print()
        test_with_custom_reference(reference)
    else:
        # Usar reference por defecto
        print("⚠️  Usando reference por defecto (probablemente no existe en cache)")
        print()
        print("💡 Para usar un reference real:")
        print(f"   python {sys.argv[0]} ORD-20231119-123456")
        print()
        test_webhook()
    
    print()
    print("=" * 60)
    print("📚 Para más información, ver: docs/WOMPI_WEBHOOK_SETUP.md")
    print("=" * 60)
