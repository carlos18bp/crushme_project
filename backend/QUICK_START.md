# 🚀 Quick Start - CrushMe Backend

## Comandos Esenciales

### 🔧 Deploy (Sin Sincronización)
```bash
./deploy_production.sh
```

### 🚀 Iniciar Servidor
```bash
./start_server.sh
```

### 🛑 Detener Servidor
```bash
./stop_server.sh
```

### 🔄 Sincronizar Datos (Manual)
```bash
./sync_manual.sh
# Selecciona opción 1 para actualización rápida
```

### 📝 Ver Logs
```bash
tail -f /tmp/gunicorn-error.log
```

### 🔍 Verificar Estado
```bash
# Ver procesos
ps aux | grep python

# Ver uso de recursos
htop

# Verificar API
curl http://localhost:8000/api/
```

## ⚠️ IMPORTANTE

**La sincronización de WooCommerce NO se ejecuta automáticamente.**

Solo sincroniza cuando sea necesario usando `./sync_manual.sh`

## 📞 Ayuda

- Documentación completa: `SOLUCION_SERVIDOR_TRABADO.md`
- Guía de optimización: `SYNC_OPTIMIZATION_GUIDE.md`
