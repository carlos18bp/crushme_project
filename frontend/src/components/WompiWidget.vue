<template>
  <div class="wompi-widget-container">
    <!-- Formulario del widget de Wompi -->
    <form ref="wompiForm"></form>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';

const props = defineProps({
  widgetData: {
    type: Object,
    required: true
  },
  renderMode: {
    type: String,
    default: 'button' // 'button' o 'inline'
  }
});

const wompiForm = ref(null);
let scriptElement = null;

// Cargar el script del widget cuando el componente se monta
onMounted(() => {
  loadWompiWidget();
});

// Limpiar el script cuando el componente se desmonta
onBeforeUnmount(() => {
  if (scriptElement && scriptElement.parentNode) {
    scriptElement.parentNode.removeChild(scriptElement);
  }
});

// Recargar el widget si los datos cambian
watch(() => props.widgetData, () => {
  loadWompiWidget();
}, { deep: true });

function loadWompiWidget() {
  console.log('🔵 [WOMPI WIDGET] Loading widget with data:', props.widgetData);
  console.log('🔵 [WOMPI WIDGET] Form ref:', wompiForm.value);
  console.log('🔵 [WOMPI WIDGET] Render mode:', props.renderMode);
  
  if (!wompiForm.value || !props.widgetData) {
    console.warn('⚠️ [WOMPI WIDGET] Form ref or widget data not ready', {
      hasForm: !!wompiForm.value,
      hasData: !!props.widgetData
    });
    return;
  }

  // Limpiar script anterior si existe
  if (scriptElement && scriptElement.parentNode) {
    console.log('🧹 [WOMPI WIDGET] Removing previous script');
    scriptElement.parentNode.removeChild(scriptElement);
  }

  // Crear el script element dinámicamente
  scriptElement = document.createElement('script');
  scriptElement.src = 'https://checkout.wompi.co/widget.js';
  
  console.log('📝 [WOMPI WIDGET] Configurando atributos del widget:', {
    public_key: props.widgetData.public_key,
    currency: props.widgetData.currency,
    amount_in_cents: props.widgetData.amount_in_cents,
    reference: props.widgetData.reference,
    redirect_url: props.widgetData.redirect_url
  });
  
  // Configurar atributos data-* para el widget
  scriptElement.setAttribute('data-render', props.renderMode);
  scriptElement.setAttribute('data-public-key', props.widgetData.public_key);
  scriptElement.setAttribute('data-currency', props.widgetData.currency);
  scriptElement.setAttribute('data-amount-in-cents', props.widgetData.amount_in_cents);
  scriptElement.setAttribute('data-reference', props.widgetData.reference);
  scriptElement.setAttribute('data-signature:integrity', props.widgetData.signature);
  scriptElement.setAttribute('data-redirect-url', props.widgetData.redirect_url);
  
  // Customer data
  if (props.widgetData.customer_data) {
    console.log('👤 [WOMPI WIDGET] Customer data:', props.widgetData.customer_data);
    scriptElement.setAttribute('data-customer-data:email', props.widgetData.customer_data.email);
    scriptElement.setAttribute('data-customer-data:full-name', props.widgetData.customer_data.full_name);
    
    // Phone number (requerido por Wompi)
    if (props.widgetData.customer_data.phone_number) {
      scriptElement.setAttribute('data-customer-data:phone-number', props.widgetData.customer_data.phone_number);
    }
    if (props.widgetData.customer_data.phone_number_prefix) {
      scriptElement.setAttribute('data-customer-data:phone-number-prefix', props.widgetData.customer_data.phone_number_prefix);
    }
  }

  // Agregar el script al form
  wompiForm.value.appendChild(scriptElement);
  console.log('✅ [WOMPI WIDGET] Script agregado al DOM');
  
  // Escuchar eventos del widget
  setupWompiEventListeners();
  
  console.log('✅ [WOMPI WIDGET] Widget script loaded and listeners setup');
}

function setupWompiEventListeners() {
  // Wompi emite eventos cuando el pago se completa
  // Documentación: https://docs.wompi.co/en/docs/colombia/widget-checkout-web/#step-7-listen-to-a-transactions-event
  
  // Método 1: Escuchar postMessage de Wompi
  const handleWompiMessage = (event) => {
    // Verificar que el mensaje viene de Wompi
    if (!event.origin.includes('wompi.co') && !event.origin.includes('localhost')) {
      return;
    }
    
    // Loguear solo eventos importantes
    const data = event.data;
    if (data && data.event && !['heightchanged', 'scrolltop'].includes(data.event)) {
      console.log('📨 [WOMPI WIDGET] Evento:', data.event, data);
    }
    
    // Wompi puede enviar diferentes formatos de datos
    let transactionId = null;
    let status = null;
    let reference = null;
    
    // Intentar extraer transaction ID de diferentes formatos
    
    // Formato 1: event.data.transaction
    if (data && data.transaction) {
      transactionId = data.transaction.id;
      status = data.transaction.status;
      reference = data.transaction.reference;
      console.log('📋 [WOMPI] Formato 1 - transaction object:', data.transaction);
    }
    // Formato 2: event.data directamente tiene el id
    else if (data && data.id) {
      transactionId = data.id;
      status = data.status;
      reference = data.reference;
      console.log('📋 [WOMPI] Formato 2 - direct id:', data);
    }
    // Formato 3: event.data.data.transaction_id
    else if (data && data.data && data.data.transaction_id) {
      transactionId = data.data.transaction_id;
      status = data.data.status;
      reference = data.data.reference;
      console.log('📋 [WOMPI] Formato 3 - nested transaction_id:', data.data);
    }
    // Formato 4: event.data.transaction_id directo
    else if (data && data.transaction_id) {
      transactionId = data.transaction_id;
      status = data.status;
      reference = data.reference;
      console.log('📋 [WOMPI] Formato 4 - direct transaction_id:', data);
    }
    // Formato 5: event.data es un string JSON
    else if (typeof data === 'string') {
      try {
        const parsed = JSON.parse(data);
        transactionId = parsed.transaction?.id || parsed.transaction_id || parsed.id;
        status = parsed.transaction?.status || parsed.status;
        reference = parsed.transaction?.reference || parsed.reference;
        console.log('📋 [WOMPI] Formato 5 - parsed string:', parsed);
      } catch (e) {
        // Ignorar
      }
    }
    
    // Si encontramos un transaction ID, redirigir
    if (transactionId) {
      console.log('✅ [WOMPI WIDGET] Transacción detectada:', {
        id: transactionId,
        status: status,
        reference: reference
      });
      
      // Guardar en localStorage
      localStorage.setItem('wompi_last_transaction', JSON.stringify({
        id: transactionId,
        status: status,
        reference: reference,
        timestamp: Date.now()
      }));
      
      // Redirigir a la página de éxito
      const redirectUrl = `${props.widgetData.redirect_url}?id=${transactionId}`;
      console.log('🔗 [WOMPI WIDGET] Redirigiendo a:', redirectUrl);
      
      window.removeEventListener('message', handleWompiMessage);
      
      setTimeout(() => {
        window.location.href = redirectUrl;
      }, 500);
    }
  };
  
  window.addEventListener('message', handleWompiMessage);
  
  // Método 2: Polling para detectar cuando el modal de Wompi se cierra
  // Esto es un fallback en caso de que el postMessage no funcione
  const checkInterval = setInterval(() => {
    // Verificar si hay un transaction ID en localStorage que Wompi pueda haber guardado
    const wompiData = localStorage.getItem('wompi_last_transaction');
    if (wompiData) {
      try {
        const data = JSON.parse(wompiData);
        if (data.id && data.reference === props.widgetData.reference) {
          console.log('✅ [WOMPI WIDGET] Transacción detectada via localStorage:', data);
          clearInterval(checkInterval);
          window.removeEventListener('message', handleWompiMessage);
          window.location.href = `${props.widgetData.redirect_url}?id=${data.id}`;
        }
      } catch (e) {
        // Ignorar errores de parsing
      }
    }
  }, 1000);
  
  // Limpiar el interval después de 5 minutos
  setTimeout(() => {
    clearInterval(checkInterval);
  }, 300000);
}
</script>

<style scoped>
.wompi-widget-container {
  width: 100%;
  margin: 0;
  padding: 0;
  overflow: visible;
}

/* Estilos para el formulario del widget */
.wompi-widget-container :deep(form) {
  width: 100%;
  overflow: visible;
}

/* Estilos para el botón del widget */
.wompi-widget-container :deep(button) {
  width: 100%;
  min-height: 56px;
  padding: 1rem 2rem;
  background: var(--color-brand-purple-light);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.0625rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
  box-shadow: 0 4px 12px rgba(218, 157, 255, 0.3);
  overflow: visible;
  white-space: normal;
  line-height: 1.4;
}

.wompi-widget-container :deep(button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(218, 157, 255, 0.4);
  opacity: 0.95;
}
</style>
