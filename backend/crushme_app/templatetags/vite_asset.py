import json
import os
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

# Cache del manifest para no leerlo en cada request
_manifest_cache = None


def load_manifest():
    """Carga el manifest.json generado por Vite"""
    global _manifest_cache
    
    # En desarrollo o si DEBUG está activo, siempre recarga el manifest
    if settings.DEBUG or _manifest_cache is None:
        manifest_path = os.path.join(
            settings.BASE_DIR, 
            'static', 
            'frontend', 
            '.vite',
            'manifest.json'
        )
        
        try:
            with open(manifest_path, 'r') as f:
                _manifest_cache = json.load(f)
        except FileNotFoundError:
            # Si no existe el manifest, retornar diccionario vacío
            _manifest_cache = {}
    
    return _manifest_cache


@register.simple_tag
def vite_asset(entry_name):
    """
    Template tag para obtener la ruta del asset con hash desde el manifest.
    
    Uso en template:
        {% load vite_asset %}
        <script type="module" src="{% vite_asset 'src/main.js' %}"></script>
    """
    manifest = load_manifest()
    
    # Buscar el entry en el manifest
    if entry_name in manifest:
        file_path = manifest[entry_name].get('file', '')
        return static(f'frontend/{file_path}')
    
    # Fallback: retornar el nombre original si no se encuentra en el manifest
    return static(f'frontend/{entry_name}')


@register.simple_tag
def vite_css(entry_name):
    """
    Template tag para obtener los archivos CSS asociados a un entry point.
    
    Uso en template:
        {% load vite_asset %}
        {% vite_css 'src/main.js' %}
    """
    manifest = load_manifest()
    
    css_files = []
    
    if entry_name in manifest:
        entry = manifest[entry_name]
        
        # Obtener CSS del entry principal
        if 'css' in entry:
            for css_file in entry['css']:
                css_files.append(static(f'frontend/{css_file}'))
    
    return css_files


@register.inclusion_tag('vite_tags.html')
def vite_hmr_client():
    """
    Incluye el cliente HMR de Vite en desarrollo.
    Solo se activa si DEBUG=True
    """
    return {
        'debug': settings.DEBUG,
        'vite_dev_server': getattr(settings, 'VITE_DEV_SERVER_URL', 'http://localhost:5173')
    }
