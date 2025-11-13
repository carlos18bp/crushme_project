#!/bin/bash

# Script de Deploy Optimizado para Producción
# NO ejecuta sincronización automática para evitar trabar el servidor

set -e  # Exit on error

echo "🚀 Iniciando deploy de CrushMe Backend..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="/home/cerrotico/work/crushme_project/backend"
VENV_DIR="$PROJECT_DIR/venv"

cd $PROJECT_DIR

echo -e "${YELLOW}📦 1. Actualizando código desde Git...${NC}"
git pull origin main || {
    echo -e "${RED}❌ Error al actualizar código${NC}"
    exit 1
}

echo -e "${YELLOW}🔧 2. Activando entorno virtual...${NC}"
source $VENV_DIR/bin/activate || {
    echo -e "${RED}❌ Error al activar entorno virtual${NC}"
    exit 1
}

echo -e "${YELLOW}📚 3. Instalando/actualizando dependencias...${NC}"
pip install -r requirements.txt --quiet || {
    echo -e "${RED}❌ Error al instalar dependencias${NC}"
    exit 1
}

echo -e "${YELLOW}🗄️  4. Ejecutando migraciones...${NC}"
python manage.py migrate --noinput || {
    echo -e "${RED}❌ Error en migraciones${NC}"
    exit 1
}

echo -e "${YELLOW}📁 5. Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --noinput --clear || {
    echo -e "${YELLOW}⚠️  Advertencia: Error al recolectar estáticos (continuando...)${NC}"
}

echo -e "${YELLOW}🔄 6. Reiniciando servidor...${NC}"

# Detectar si está usando systemd o proceso manual
if systemctl is-active --quiet crushme 2>/dev/null; then
    echo "   Usando systemd service..."
    sudo systemctl restart crushme
    sleep 2
    sudo systemctl status crushme --no-pager
elif pgrep -f "gunicorn.*crushme" > /dev/null; then
    echo "   Reiniciando Gunicorn..."
    pkill -HUP -f "gunicorn.*crushme"
elif pgrep -f "python.*manage.py runserver" > /dev/null; then
    echo "   ⚠️  Detectado runserver (NO recomendado para producción)"
    echo "   Por favor, detén manualmente y reinicia el servidor"
else
    echo "   ℹ️  No se detectó servidor corriendo"
    echo "   Inicia el servidor manualmente con:"
    echo "   gunicorn crushme_project.wsgi:application --bind 0.0.0.0:8000 --workers 2"
fi

echo ""
echo -e "${GREEN}✅ Deploy completado exitosamente!${NC}"
echo ""
echo -e "${YELLOW}📝 Notas importantes:${NC}"
echo "   - La sincronización de WooCommerce NO se ejecuta automáticamente"
echo "   - Para sincronizar manualmente: python manage.py sync_woocommerce --stock"
echo "   - Para ver logs: tail -f /var/log/crushme/error.log"
echo ""
echo -e "${GREEN}🎉 Servidor listo para recibir requests!${NC}"
