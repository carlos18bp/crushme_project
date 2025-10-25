/**
 * Debug helper para verificar geolocalización y configuración
 * Usar en consola: window.debugGeoLocation()
 */

export async function debugGeoLocation() {
  console.log('🔍 ===== DEBUG GEOLOCATION =====')
  
  // 1. Verificar localStorage
  console.log('📦 LocalStorage:')
  console.log('  - currency:', localStorage.getItem('currency'))
  console.log('  - i18n:', localStorage.getItem('i18n'))
  
  // 2. Verificar Pinia stores
  try {
    const { useCurrencyStore } = await import('@/stores/modules/currencyStore')
    const { useI18nStore } = await import('@/stores/modules/i18nStore')
    
    const currencyStore = useCurrencyStore()
    const i18nStore = useI18nStore()
    
    console.log('🏪 Pinia Stores:')
    console.log('  Currency Store:', {
      currentCurrency: currencyStore.currentCurrency,
      isInitialized: currencyStore.isInitialized,
      detectedCountry: currencyStore.detectedCountry
    })
    console.log('  i18n Store:', {
      locale: i18nStore.locale,
      isInitialized: i18nStore.isInitialized,
      detectedLocale: i18nStore.detectedLocale,
      countryCode: i18nStore.countryCode
    })
  } catch (error) {
    console.error('❌ Error accediendo a stores:', error)
  }
  
  // 3. Consultar backend geolocation API directamente
  console.log('🌍 Consultando backend geolocation API...')
  try {
    const response = await fetch('/api/geolocation/me/')
    const data = await response.json()
    console.log('✅ Respuesta del backend:', {
      ip: data.ip,
      country_code: data.country_code,
      is_colombia: data.is_colombia,
      recommended_currency: data.recommended_currency
    })
    
    console.log('🎯 Configuración esperada:')
    console.log('  - Currency:', data.recommended_currency)
    console.log('  - Idioma: Basado en navegador (navigator.language)')
    console.log('  - Es Colombia:', data.is_colombia)
    
  } catch (error) {
    console.error('❌ Error consultando backend geolocation API:', error)
  }
  
  console.log('🔍 ===== FIN DEBUG =====')
}

/**
 * Limpiar localStorage y forzar re-detección
 */
export function resetGeoLocation() {
  console.log('🧹 Limpiando configuración de geolocalización...')
  
  // Limpiar localStorage completamente
  const keysToRemove = ['currency', 'i18n']
  keysToRemove.forEach(key => {
    localStorage.removeItem(key)
    console.log(`  ✅ Eliminado: ${key}`)
  })
  
  // También limpiar cualquier key de Pinia persist
  Object.keys(localStorage).forEach(key => {
    if (key.includes('currency') || key.includes('i18n')) {
      localStorage.removeItem(key)
      console.log(`  ✅ Eliminado (Pinia): ${key}`)
    }
  })
  
  console.log('✅ LocalStorage limpiado completamente')
  console.log('🔄 Recargando página en 1 segundo...')
  
  // Recargar automáticamente
  setTimeout(() => {
    window.location.reload()
  }, 1000)
}

// Exponer funciones globalmente para debug en consola
if (typeof window !== 'undefined') {
  window.debugGeoLocation = debugGeoLocation
  window.resetGeoLocation = resetGeoLocation
  console.log('🔧 Debug helpers disponibles:')
  console.log('  - window.debugGeoLocation() - Ver estado actual')
  console.log('  - window.resetGeoLocation() - Limpiar y re-detectar')
}
