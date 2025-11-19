#!/bin/bash

# Script para exponer el backend con ngrok para testing del webhook de Wompi
# Uso: ./setup_ngrok_webhook.sh

echo "🚀 Configurando ngrok para webhook de Wompi..."
echo ""

# Verificar si ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado"
    echo ""
    echo "Para instalar ngrok:"
    echo "1. Visita: https://ngrok.com/download"
    echo "2. O instala con snap: sudo snap install ngrok"
    echo ""
    exit 1
fi

# Verificar si el servidor Django está corriendo
if ! curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    echo "⚠️  El servidor Django no está corriendo en localhost:8000"
    echo ""
    echo "Por favor inicia el servidor primero:"
    echo "  python manage.py runserver"
    echo ""
    exit 1
fi

echo "✅ ngrok está instalado"
echo "✅ Servidor Django está corriendo"
echo ""

# Iniciar ngrok
echo "🌐 Iniciando ngrok en puerto 8000..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 INSTRUCCIONES PARA CONFIGURAR WOMPI:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Copia la URL pública de ngrok que aparecerá abajo"
echo "   Ejemplo: https://xxxx-xx-xx-xx-xx.ngrok-free.app"
echo ""
echo "2. Ve al dashboard de Wompi:"
echo "   https://comercios.wompi.co/dashboard"
echo ""
echo "3. Navega a: Configuración → Webhooks → Eventos"
echo ""
echo "4. Configura el webhook URL como:"
echo "   https://TU-URL-NGROK.ngrok-free.app/api/orders/wompi/webhook/"
echo ""
echo "5. Selecciona el evento: transaction.updated"
echo ""
echo "6. Guarda la configuración"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Logs del webhook aparecerán en la terminal del servidor Django"
echo ""
echo "Presiona Ctrl+C para detener ngrok"
echo ""

# Iniciar ngrok
ngrok http 8000
