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
  
  if (!wompiForm.value || !props.widgetData) {
    console.warn('⚠️ [WOMPI WIDGET] Form ref or widget data not ready');
    return;
  }

  // Limpiar script anterior si existe
  if (scriptElement && scriptElement.parentNode) {
    scriptElement.parentNode.removeChild(scriptElement);
  }

  // Crear el script element dinámicamente
  scriptElement = document.createElement('script');
  scriptElement.src = 'https://checkout.wompi.co/widget.js';
  
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
  
  // Escuchar eventos del widget
  setupWompiEventListeners();
  
  console.log('✅ [WOMPI WIDGET] Widget script loaded');
}

function setupWompiEventListeners() {
  // Wompi emite eventos cuando el pago se completa
  // Documentación: https://docs.wompi.co/en/docs/colombia/widget-checkout-web/#step-7-listen-to-a-transactions-event
  
  // Método 1: Escuchar postMessage de Wompi
  const handleWompiMessage = (event) => {
    // Verificar que el mensaje viene de Wompi
    if (!event.origin.includes('wompi.co')) {
      return;
    }
    
    // Solo loguear eventos importantes, no UI events
    if (event.data && event.data.event && 
        !['heightchanged', 'scrolltop'].includes(event.data.event)) {
      console.log('📨 [WOMPI WIDGET] Evento:', event.data.event, event.data);
    }
    
    // Wompi puede enviar diferentes formatos de datos
    let transactionId = null;
    let status = null;
    
    // Verificar si es un evento de transacción completada
    if (event.data && event.data.event) {
      // Eventos que indican que el pago se completó
      if (event.data.event === 'transaction:success' || 
          event.data.event === 'transaction:approved' ||
          event.data.event === 'close' ||
          event.data.event === 'finish') {
        
        console.log('🎉 [WOMPI WIDGET] Evento de finalización detectado:', event.data.event);
        
        // Intentar obtener el transaction ID del evento
        if (event.data.data && event.data.data.transaction_id) {
          transactionId = event.data.data.transaction_id;
        } else if (event.data.transaction_id) {
          transactionId = event.data.transaction_id;
        }
      }
    }
    
    // Formato 1: event.data.transaction
    if (!transactionId && event.data && event.data.transaction) {
      transactionId = event.data.transaction.id;
      status = event.data.transaction.status;
    }
    // Formato 2: event.data directamente tiene el id
    else if (!transactionId && event.data && event.data.id) {
      transactionId = event.data.id;
      status = event.data.status;
    }
    // Formato 3: event.data es un string con el transaction ID
    else if (!transactionId && typeof event.data === 'string' && event.data.includes('transaction')) {
      try {
        const parsed = JSON.parse(event.data);
        transactionId = parsed.transaction?.id || parsed.id;
        status = parsed.transaction?.status || parsed.status;
      } catch (e) {
        console.warn('⚠️ [WOMPI WIDGET] No se pudo parsear el mensaje');
      }
    }
    
    if (transactionId) {
      console.log('✅ [WOMPI WIDGET] Transacción detectada:', {
        id: transactionId,
        status: status
      });
      
      // Redirigir a la página de éxito con el transaction ID
      const redirectUrl = `${props.widgetData.redirect_url}?id=${transactionId}`;
      console.log('🔗 [WOMPI WIDGET] Redirigiendo a:', redirectUrl);
      
      // Remover el listener antes de redirigir
      window.removeEventListener('message', messageHandler);
      
      window.location.href = redirectUrl;
    }
  };
  
  window.addEventListener('message', messageHandler);
  
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
          window.removeEventListener('message', messageHandler);
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
  margin: 2rem 0;
}

/* Estilos para el botón del widget */
.wompi-widget-container :deep(button) {
  width: 100%;
  padding: 1rem 2rem;
  background: var(--color-brand-purple-light);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1.0625rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
  box-shadow: 0 6px 20px rgba(218, 157, 255, 0.4);
}

.wompi-widget-container :deep(button:hover) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(218, 157, 255, 0.5);
  opacity: 0.9;
}
</style>
