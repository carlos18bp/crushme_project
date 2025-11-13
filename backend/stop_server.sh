#!/bin/bash

# Script para detener el servidor Django/Gunicorn

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Deteniendo servidor...${NC}"

# Detener Gunicorn
if pgrep -f "gunicorn.*crushme" > /dev/null; then
    echo "   Deteniendo Gunicorn..."
    pkill -TERM -f "gunicorn.*crushme"
    sleep 2
    
    # Forzar si aún está corriendo
    if pgrep -f "gunicorn.*crushme" > /dev/null; then
        echo "   Forzando detención..."
        pkill -KILL -f "gunicorn.*crushme"
    fi
    
    echo -e "${GREEN}✅ Gunicorn detenido${NC}"
fi

# Detener runserver si está corriendo
if pgrep -f "python.*manage.py runserver" > /dev/null; then
    echo "   Deteniendo runserver..."
    pkill -TERM -f "python.*manage.py runserver"
    sleep 2
    
    if pgrep -f "python.*manage.py runserver" > /dev/null; then
        pkill -KILL -f "python.*manage.py runserver"
    fi
    
    echo -e "${GREEN}✅ Runserver detenido${NC}"
fi

# Verificar que no hay procesos corriendo
if ! pgrep -f "gunicorn.*crushme" > /dev/null && ! pgrep -f "python.*manage.py runserver" > /dev/null; then
    echo -e "${GREEN}✅ Servidor detenido completamente${NC}"
else
    echo -e "${RED}⚠️  Algunos procesos aún están corriendo${NC}"
    echo "Procesos activos:"
    ps aux | grep -E "gunicorn|manage.py" | grep -v grep
fi
