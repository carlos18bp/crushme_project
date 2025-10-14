#!/usr/bin/env python
"""
Script para instalar los modelos de traducción de argostranslate
Ejecutar después de instalar argostranslate:
    python install_translation_models.py
"""

import argostranslate.package
import argostranslate.translate

def install_translation_models():
    """Instala los modelos de traducción español <-> inglés"""
    print('📥 Descargando e instalando modelos de traducción...')
    print('Esto solo se hace una vez y descargará ~500MB')
    print()
    
    try:
        # Actualizar índice de paquetes
        print('🔄 Actualizando índice de paquetes...')
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        
        # Instalar español -> inglés
        print('📦 Buscando paquete: Español → Inglés')
        es_en = next(
            filter(
                lambda x: x.from_code == 'es' and x.to_code == 'en',
                available_packages
            ),
            None
        )
        
        if es_en:
            print(f'   Instalando: {es_en}')
            argostranslate.package.install_from_path(es_en.download())
            print('   ✅ Español → Inglés instalado')
        else:
            print('   ⚠️  No se encontró el paquete Español → Inglés')
        
        # Instalar inglés -> español  
        print('📦 Buscando paquete: Inglés → Español')
        en_es = next(
            filter(
                lambda x: x.from_code == 'en' and x.to_code == 'es',
                available_packages
            ),
            None
        )
        
        if en_es:
            print(f'   Instalando: {en_es}')
            argostranslate.package.install_from_path(en_es.download())
            print('   ✅ Inglés → Español instalado')
        else:
            print('   ⚠️  No se encontró el paquete Inglés → Español')
        
        print()
        print('✅ ¡Modelos de traducción instalados correctamente!')
        print('   Los modelos están listos para traducción offline')
        
    except Exception as e:
        print(f'❌ Error al instalar modelos: {e}')
        return False
    
    return True

if __name__ == '__main__':
    install_translation_models()


