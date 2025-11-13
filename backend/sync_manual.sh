#!/bin/bash

# Script para sincronización MANUAL de WooCommerce
# Úsalo solo cuando necesites actualizar datos

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Directorio del proyecto
PROJECT_DIR="/home/cerrotico/work/crushme_project/backend"
VENV_DIR="$PROJECT_DIR/venv"

cd $PROJECT_DIR
source $VENV_DIR/bin/activate

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Sincronización Manual de WooCommerce${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Menú de opciones
echo "Selecciona el tipo de sincronización:"
echo ""
echo "  1) 🚀 Stock y Precios (RÁPIDO - Recomendado)"
echo "     Actualiza solo stock y precios de productos existentes"
echo "     Tiempo estimado: 2-5 minutos"
echo ""
echo "  2) 📦 Productos Completos (LENTO)"
echo "     Sincroniza todos los productos con todos sus datos"
echo "     Tiempo estimado: 30-60 minutos"
echo ""
echo "  3) 📁 Categorías (RARO)"
echo "     Sincroniza categorías (solo si agregaste nuevas)"
echo "     Tiempo estimado: 1-2 minutos"
echo ""
echo "  4) 🔄 Sincronización Completa (MUY LENTO)"
echo "     Categorías + Productos + Variaciones"
echo "     Tiempo estimado: 60+ minutos"
echo ""
echo "  5) ❌ Cancelar"
echo ""
read -p "Opción (1-5): " option

case $option in
    1)
        echo ""
        echo -e "${YELLOW}🚀 Iniciando sincronización de stock y precios...${NC}"
        echo ""
        python manage.py sync_woocommerce --stock
        ;;
    2)
        echo ""
        echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto puede tardar 30-60 minutos${NC}"
        read -p "¿Continuar? (s/n): " confirm
        if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
            echo ""
            echo -e "${YELLOW}📦 Iniciando sincronización de productos...${NC}"
            echo ""
            python manage.py sync_woocommerce --products
        else
            echo "Cancelado"
            exit 0
        fi
        ;;
    3)
        echo ""
        echo -e "${YELLOW}📁 Iniciando sincronización de categorías...${NC}"
        echo ""
        python manage.py sync_woocommerce --categories
        ;;
    4)
        echo ""
        echo -e "${RED}⚠️  ADVERTENCIA: Esto puede tardar más de 1 hora${NC}"
        echo -e "${RED}⚠️  El servidor puede ponerse lento durante este proceso${NC}"
        read -p "¿Estás SEGURO? (s/n): " confirm
        if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
            echo ""
            echo -e "${YELLOW}🔄 Iniciando sincronización completa...${NC}"
            echo ""
            python manage.py sync_woocommerce --full
        else
            echo "Cancelado"
            exit 0
        fi
        ;;
    5)
        echo "Cancelado"
        exit 0
        ;;
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Sincronización completada!${NC}"
echo ""
echo "Para verificar los datos sincronizados:"
echo "  python manage.py shell -c \"from crushme_app.models import WooCommerceProduct; print(f'Productos: {WooCommerceProduct.objects.count()}')\""
