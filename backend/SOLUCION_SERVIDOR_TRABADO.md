# 🚨 SOLUCIÓN: Servidor se Traba al Desplegar

## Problema Identificado

El servidor VPS se traba porque la sincronización de WooCommerce consume demasiados recursos (CPU, memoria, I/O).

## ✅ Solución Implementada

### 1. NO Ejecutar Sincronización Automática

**La sincronización ya NO se ejecuta automáticamente en ningún momento.**

- ❌ NO hay scheduler configurado
- ❌ NO hay cron jobs activos
- ❌ NO se ejecuta en deploy
- ❌ NO se ejecuta al iniciar el servidor

### 2. Scripts Creados

#### `start_server.sh` - Iniciar servidor optimizado
```bash
./start_server.sh
```
- Usa Gunicorn (optimizado para producción)
- Máximo 2 workers (no sobrecarga el VPS)
- NO ejecuta sincronización

#### `stop_server.sh` - Detener servidor
```bash
./stop_server.sh
```

#### `deploy_production.sh` - Deploy sin sincronización
```bash
./deploy_production.sh
```
- Actualiza código
- Instala dependencias
- Ejecuta migraciones
- Reinicia servidor
- **NO ejecuta sincronización**

#### `sync_manual.sh` - Sincronización manual (cuando la necesites)
```bash
./sync_manual.sh
```
Opciones:
1. **Stock y Precios** (Rápido: 2-5 min) ← **RECOMENDADO**
2. Productos Completos (Lento: 30-60 min)
3. Categorías (Raro: 1-2 min)
4. Sincronización Completa (Muy lento: 60+ min)

### 3. Configuración de Gunicorn

Archivo: `gunicorn_config.py`

- **Workers:** 2 (limitado para VPS pequeño)
- **Threads:** 2 por worker
- **Timeout:** 120 segundos
- **Max requests:** 1000 (reinicia workers automáticamente)

## 🚀 Cómo Usar

### Deploy Normal (SIN sincronización)

```bash
cd /home/cerrotico/work/crushme_project/backend
./deploy_production.sh
```

Esto:
1. ✅ Actualiza código
2. ✅ Instala dependencias
3. ✅ Ejecuta migraciones
4. ✅ Reinicia servidor
5. ❌ NO ejecuta sincronización

### Sincronizar Datos (Solo cuando sea necesario)

```bash
./sync_manual.sh
```

Selecciona opción 1 (Stock y Precios) para actualización rápida.

### Iniciar/Detener Servidor

```bash
# Iniciar
./start_server.sh

# Detener
./stop_server.sh

# Ver logs
tail -f /tmp/gunicorn-error.log
```

## 📅 Sincronización Programada (Opcional)

Si necesitas sincronización automática, usa cron en horarios de BAJA demanda:

```bash
# Editar crontab
crontab -e

# Agregar (ejecuta a las 3 AM)
0 3 * * * cd /home/cerrotico/work/crushme_project/backend && ./sync_manual.sh <<< "1" >> /tmp/sync.log 2>&1
```

## 🔍 Monitoreo

### Ver uso de recursos:
```bash
htop
```

### Ver procesos de Python:
```bash
ps aux | grep python
```

### Ver logs en tiempo real:
```bash
tail -f /tmp/gunicorn-error.log
```

### Verificar que el servidor está corriendo:
```bash
curl http://localhost:8000/api/
```

## 🆘 Troubleshooting

### Servidor aún se traba:

1. **Verificar que NO hay sincronización corriendo:**
   ```bash
   ps aux | grep sync_woocommerce
   ```

2. **Matar proceso de sincronización:**
   ```bash
   pkill -f sync_woocommerce
   ```

3. **Reiniciar servidor:**
   ```bash
   ./stop_server.sh
   ./start_server.sh
   ```

### Servidor no inicia:

1. **Ver logs:**
   ```bash
   tail -f /tmp/gunicorn-error.log
   ```

2. **Verificar puerto 8000:**
   ```bash
   lsof -i :8000
   ```

3. **Matar procesos en puerto 8000:**
   ```bash
   fuser -k 8000/tcp
   ```

### Memoria llena:

1. **Ver uso de memoria:**
   ```bash
   free -h
   ```

2. **Limpiar caché:**
   ```bash
   sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches
   ```

3. **Reiniciar servidor:**
   ```bash
   ./stop_server.sh
   sleep 5
   ./start_server.sh
   ```

## 📊 Comparación

### ❌ ANTES (Problemático):
- Sincronización automática en cada deploy
- Servidor se traba
- Alto consumo de recursos
- Timeouts frecuentes

### ✅ AHORA (Optimizado):
- Sincronización MANUAL solamente
- Servidor estable
- Recursos controlados
- Sin timeouts

## 🎯 Resumen

**IMPORTANTE:** 

1. **Deploy normal:** `./deploy_production.sh` (NO sincroniza)
2. **Sincronizar datos:** `./sync_manual.sh` (solo cuando lo necesites)
3. **Iniciar servidor:** `./start_server.sh`
4. **Detener servidor:** `./stop_server.sh`

**El servidor ya NO se trabará porque la sincronización NO se ejecuta automáticamente.**

## 📞 Soporte

Si el servidor sigue trabándose después de estos cambios:

1. Verifica que NO haya cron jobs: `crontab -l`
2. Verifica procesos: `ps aux | grep python`
3. Revisa logs: `tail -f /tmp/gunicorn-error.log`
4. Contacta al equipo de desarrollo

---

**Última actualización:** 2025-11-13
**Estado:** ✅ Implementado y probado
