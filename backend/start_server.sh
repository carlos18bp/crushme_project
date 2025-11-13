#!/bin/bash

# Script para iniciar el servidor Django con Gunicorn
# Optimizado para producción

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Directorio del proyecto
PROJECT_DIR="/home/cerrotico/work/crushme_project/backend"
VENV_DIR="$PROJECT_DIR/venv"

cd $PROJECT_DIR

echo -e "${YELLOW}🔧 Preparando servidor...${NC}"

# Activar entorno virtual
source $VENV_DIR/bin/activate

# Verificar que gunicorn esté instalado
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}📦 Instalando Gunicorn...${NC}"
    pip install gunicorn
fi

# Crear directorio de logs si no existe
mkdir -p /tmp/crushme_logs

# Matar procesos anteriores si existen
echo -e "${YELLOW}🧹 Limpiando procesos anteriores...${NC}"
pkill -f "gunicorn.*crushme" || true
pkill -f "python.*manage.py runserver" || true
sleep 2

# Verificar configuración de Django
echo -e "${YELLOW}✅ Verificando configuración...${NC}"
python manage.py check --deploy || {
    echo -e "${RED}❌ Error en configuración de Django${NC}"
    exit 1
}

# Iniciar Gunicorn
echo -e "${GREEN}🚀 Iniciando servidor con Gunicorn...${NC}"
echo ""

gunicorn crushme_project.wsgi:application \
    --config gunicorn_config.py \
    --daemon

# Esperar a que inicie
sleep 3

# Verificar que está corriendo
if pgrep -f "gunicorn.*crushme" > /dev/null; then
    PID=$(pgrep -f "gunicorn.*crushme" | head -1)
    echo -e "${GREEN}✅ Servidor iniciado exitosamente!${NC}"
    echo ""
    echo "📍 URL: http://0.0.0.0:8000"
    echo "🆔 PID: $PID"
    echo "📝 Logs: /tmp/gunicorn-error.log"
    echo ""
    echo "Para ver logs en tiempo real:"
    echo "  tail -f /tmp/gunicorn-error.log"
    echo ""
    echo "Para detener el servidor:"
    echo "  ./stop_server.sh"
    echo ""
else
    echo -e "${RED}❌ Error al iniciar servidor${NC}"
    echo "Ver logs: tail -f /tmp/gunicorn-error.log"
    exit 1
fi
