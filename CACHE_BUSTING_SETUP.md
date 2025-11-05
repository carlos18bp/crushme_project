# Cache Busting - Configuración Completa

## ✅ Cambios Implementados

### 1. **Vite Config** (`frontend/vite.config.js`)
- ✅ Configurado para generar archivos con **hash** en el nombre
- ✅ Genera `manifest.json` para mapear archivos
- ✅ Estructura: `assets/[name].[hash].js` y `assets/[name].[hash].css`

### 2. **Template Tags de Django** (`backend/crushme_app/templatetags/vite_asset.py`)
- ✅ Creado `vite_asset` tag para cargar JS con hash
- ✅ Creado `vite_css` tag para cargar CSS con hash
- ✅ Lee automáticamente el `manifest.json` generado por Vite

### 3. **Template HTML** (`backend/templates/index.html`)
- ✅ Actualizado para usar los template tags
- ✅ Carga dinámicamente archivos con hash

### 4. **Nginx Config** (`backend/crushme` y `backend/crushme_nginx_fixed`)
- ✅ Assets con hash (`/static/frontend/assets/`): **cache 1 año + immutable**
- ✅ HTML (Django): **no-cache** para siempre obtener nuevos hashes
- ✅ Compresión gzip para JS/CSS

---

## 🚀 Pasos para Desplegar

### 1. Compilar el Frontend
```bash
cd /home/ryzepeck/webapps/crushme_project/frontend
npm run build
```

Esto generará:
- `/backend/static/frontend/assets/index.[hash].js`
- `/backend/static/frontend/assets/index.[hash].css`
- `/backend/static/frontend/.vite/manifest.json`

### 2. Verificar el Manifest
```bash
cat /home/ryzepeck/webapps/crushme_project/backend/static/frontend/.vite/manifest.json
```

Deberías ver algo como:
```json
{
  "src/main.js": {
    "file": "assets/index.abc123.js",
    "css": ["assets/index.def456.css"]
  }
}
```

### 3. Actualizar Nginx en el Servidor
```bash
# Copiar la configuración actualizada
sudo cp /home/ryzepeck/webapps/crushme_project/backend/crushme /etc/nginx/sites-available/crushme

# Verificar la configuración
sudo nginx -t

# Si todo está bien, recargar nginx
sudo systemctl reload nginx
```

### 4. Reiniciar Gunicorn
```bash
sudo systemctl restart gunicorn
```

---

## 🔍 Cómo Funciona

### Antes (Problema)
```
index.js  ← Siempre el mismo nombre
index.css ← Siempre el mismo nombre
```
El navegador cachea estos archivos y no detecta cambios.

### Después (Solución)
```
assets/index.abc123.js  ← Hash único por contenido
assets/index.def456.css ← Hash único por contenido
```
Cuando cambias el código:
1. Vite genera **nuevos archivos con hash diferente**
2. El `manifest.json` se actualiza con los nuevos nombres
3. Django lee el manifest y sirve el HTML con las **nuevas rutas**
4. El navegador ve URLs diferentes y **descarga automáticamente**

### Estrategia de Caché
- **HTML**: `no-cache` → Siempre se descarga fresco
- **Assets con hash**: `max-age=31536000, immutable` → Cache 1 año (seguro porque el hash cambia)
- **Otros static**: `max-age=604800` → Cache 7 días

---

## 🧪 Verificación

### 1. Después del build, verifica los archivos generados:
```bash
ls -la /home/ryzepeck/webapps/crushme_project/backend/static/frontend/assets/
```

Deberías ver archivos como:
- `index.a1b2c3d4.js`
- `index.e5f6g7h8.css`

### 2. Verifica que el HTML carga correctamente:
```bash
curl -I https://crushme.com.co/
```

Deberías ver:
```
Cache-Control: no-cache, no-store, must-revalidate
```

### 3. Verifica que los assets tienen cache largo:
```bash
curl -I https://crushme.com.co/static/frontend/assets/index.abc123.js
```

Deberías ver:
```
Cache-Control: public, max-age=31536000, immutable
```

---

## 🎯 Resultado Final

✅ **Los usuarios siempre verán la última versión**
- No necesitan hacer Ctrl+Shift+R
- Funciona en modo incógnito
- Funciona en todos los navegadores
- Los assets se cachean eficientemente (menos tráfico)

✅ **Flujo de actualización automático**:
1. Haces cambios en Vue
2. Ejecutas `npm run build`
3. Copias archivos al servidor
4. Reinicias gunicorn
5. ¡Los usuarios ven los cambios inmediatamente!

---

## 📝 Notas Importantes

1. **Siempre ejecuta `npm run build`** después de hacer cambios en el frontend
2. **El manifest.json es crítico**: Django lo lee para saber qué archivos cargar
3. **No borres la carpeta `.vite`** dentro de `static/frontend/`
4. **Si ves errores 404**: verifica que los archivos existen en `static/frontend/assets/`
5. **Si los cambios no se ven**: verifica que nginx y gunicorn se reiniciaron

---

## 🐛 Troubleshooting

### Error: "Template tag 'vite_asset' not found"
```bash
# Verifica que el directorio templatetags existe
ls -la /home/ryzepeck/webapps/crushme_project/backend/crushme_app/templatetags/

# Debe contener:
# - __init__.py
# - vite_asset.py
```

### Error: "manifest.json not found"
```bash
# Ejecuta el build nuevamente
cd /home/ryzepeck/webapps/crushme_project/frontend
npm run build

# Verifica que se generó
ls -la /home/ryzepeck/webapps/crushme_project/backend/static/frontend/.vite/
```

### Los cambios no se ven
```bash
# 1. Verifica que compilaste
npm run build

# 2. Verifica que nginx se recargó
sudo systemctl status nginx

# 3. Verifica que gunicorn se reinició
sudo systemctl status gunicorn

# 4. Limpia cache del navegador o prueba en incógnito
```
