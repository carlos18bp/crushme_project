#!/bin/bash

# Script para verificar el estado del servidor

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Estado del Servidor CrushMe${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# 1. Verificar procesos
echo -e "${YELLOW}📊 Procesos activos:${NC}"
if pgrep -f "gunicorn.*crushme" > /dev/null; then
    PID=$(pgrep -f "gunicorn.*crushme" | head -1)
    WORKERS=$(pgrep -f "gunicorn.*crushme" | wc -l)
    echo -e "   ${GREEN}✅ Gunicorn corriendo${NC}"
    echo "      PID: $PID"
    echo "      Workers: $WORKERS"
elif pgrep -f "python.*manage.py runserver" > /dev/null; then
    PID=$(pgrep -f "python.*manage.py runserver" | head -1)
    echo -e "   ${YELLOW}⚠️  Runserver corriendo (no recomendado para producción)${NC}"
    echo "      PID: $PID"
else
    echo -e "   ${RED}❌ Servidor NO está corriendo${NC}"
fi
echo ""

# 2. Verificar sincronización
echo -e "${YELLOW}🔄 Sincronización:${NC}"
if pgrep -f "sync_woocommerce" > /dev/null; then
    echo -e "   ${RED}⚠️  Sincronización en proceso${NC}"
    echo "      Esto puede estar consumiendo recursos"
else
    echo -e "   ${GREEN}✅ No hay sincronización corriendo${NC}"
fi
echo ""

# 3. Verificar recursos
echo -e "${YELLOW}💻 Uso de recursos:${NC}"
CPU=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
MEM=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
echo "   CPU: ${CPU}%"
echo "   Memoria: ${MEM}%"
echo ""

# 4. Verificar puerto
echo -e "${YELLOW}🌐 Puerto 8000:${NC}"
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Puerto 8000 en uso${NC}"
    lsof -i :8000 | grep LISTEN
else
    echo -e "   ${RED}❌ Puerto 8000 libre (servidor no está escuchando)${NC}"
fi
echo ""

# 5. Verificar API
echo -e "${YELLOW}🔌 API:${NC}"
if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ API respondiendo${NC}"
else
    echo -e "   ${RED}❌ API no responde${NC}"
fi
echo ""

# 6. Logs recientes
echo -e "${YELLOW}📝 Últimas líneas del log:${NC}"
if [ -f /tmp/gunicorn-error.log ]; then
    tail -n 5 /tmp/gunicorn-error.log | sed 's/^/   /'
else
    echo "   (No hay logs disponibles)"
fi
echo ""

# 7. Resumen
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
if pgrep -f "gunicorn.*crushme" > /dev/null && ! pgrep -f "sync_woocommerce" > /dev/null; then
    echo -e "${GREEN}✅ Estado: SALUDABLE${NC}"
    echo "   El servidor está corriendo correctamente"
elif pgrep -f "sync_woocommerce" > /dev/null; then
    echo -e "${YELLOW}⚠️  Estado: SINCRONIZANDO${NC}"
    echo "   Sincronización en proceso (puede estar lento)"
else
    echo -e "${RED}❌ Estado: DETENIDO${NC}"
    echo "   Inicia el servidor con: ./start_server.sh"
fi
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
