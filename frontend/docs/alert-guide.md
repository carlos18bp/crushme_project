# Guía de Uso de Alertas - CrushMe

Esta guía explica cómo usar el composable `useAlert` para mostrar alertas y notificaciones en la aplicación.

## Instalación

El composable ya está configurado y usa SweetAlert2 como librería base.

```bash
npm install sweetalert2
```

## Soporte de Internacionalización (i18n)

El composable `useAlert` está completamente integrado con el sistema de i18n de la aplicación. Los textos de las alertas (títulos, botones) se traducen automáticamente según el idioma seleccionado.

### Idiomas Soportados
- **Español (es)**: Todos los textos en español
- **Inglés (en)**: Todos los textos en inglés

### Traducciones Incluidas

El sistema traduce automáticamente:
- Títulos de alertas (Éxito, Error, Advertencia, Información)
- Botones (Aceptar, Cancelar, Sí continuar, etc.)
- Mensajes de carga

**Archivos de traducción:**
- `src/locales/alerts/es.json` - Traducciones en español
- `src/locales/alerts/en.json` - Traducciones en inglés

### Cambio Automático de Idioma

Las alertas cambian de idioma automáticamente cuando el usuario cambia el idioma de la aplicación:

```javascript
import { useI18nStore } from '@/stores/modules/i18nStore';
import { useAlert } from '@/composables/useAlert';

const i18nStore = useI18nStore();
const { showSuccess } = useAlert();

// Cambiar a español
i18nStore.setLocale('es');
showSuccess('Operación completada'); // Muestra "¡Éxito!" como título

// Cambiar a inglés
i18nStore.setLocale('en');
showSuccess('Operation completed'); // Muestra "Success!" como título
```

### Personalizar Títulos con i18n

Puedes sobrescribir los títulos predeterminados si lo necesitas:

```javascript
// Usar título predeterminado en el idioma actual
showSuccess('Mensaje de éxito'); // Título: "¡Éxito!" o "Success!"

// Proporcionar título personalizado
showSuccess('Mensaje de éxito', 'Completado'); // Título: "Completado"
```

## Importación

```javascript
import { useAlert } from '@/composables/useAlert';
```

## Funciones Disponibles

### 1. `showSuccess()` - Alerta de Éxito

Muestra una alerta de éxito con icono verde y mensaje positivo.

```javascript
import { useAlert } from '@/composables/useAlert';

const { showSuccess } = useAlert();

// Uso básico
showSuccess('Operación completada exitosamente');

// Con título personalizado
showSuccess('Tu pedido ha sido confirmado', '¡Pedido Realizado!');

// Con opciones adicionales
showSuccess('Producto agregado al carrito', '¡Éxito!', {
  timer: 3000, // 3 segundos
  timerProgressBar: true
});
```

**Parámetros:**
- `message` (string): Mensaje a mostrar
- `title` (string, opcional): Título de la alerta (por defecto: "¡Éxito!")
- `options` (object, opcional): Opciones adicionales de SweetAlert2

---

### 2. `showError()` - Alerta de Error

Muestra una alerta de error con icono rojo.

```javascript
const { showError } = useAlert();

// Error simple
showError('No se pudo completar la operación');

// Con título personalizado
showError('Verifica que todos los campos estén completos', 'Error en el formulario');

// Con opciones
showError('El servidor no está disponible', 'Error de conexión', {
  confirmButtonText: 'Reintentar'
});
```

**Parámetros:**
- `message` (string): Mensaje de error
- `title` (string, opcional): Título de la alerta (por defecto: "Error")
- `options` (object, opcional): Opciones adicionales de SweetAlert2

---

### 3. `showWarning()` - Alerta de Advertencia

Muestra una alerta de advertencia con icono amarillo.

```javascript
const { showWarning } = useAlert();

showWarning('Este producto está por agotarse');

showWarning('Solo quedan 3 unidades disponibles', 'Stock Limitado');
```

**Parámetros:**
- `message` (string): Mensaje de advertencia
- `title` (string, opcional): Título de la alerta (por defecto: "Advertencia")
- `options` (object, opcional): Opciones adicionales de SweetAlert2

---

### 4. `showInfo()` - Alerta Informativa

Muestra una alerta informativa con icono azul.

```javascript
const { showInfo } = useAlert();

showInfo('Los envíos se procesan en 24-48 horas');

showInfo('Recuerda verificar tu correo electrónico', 'Importante');
```

**Parámetros:**
- `message` (string): Mensaje informativo
- `title` (string, opcional): Título de la alerta (por defecto: "Información")
- `options` (object, opcional): Opciones adicionales de SweetAlert2

---

### 5. `showConfirm()` - Diálogo de Confirmación

Muestra un diálogo con botones de confirmación y cancelación. Retorna una promesa.

```javascript
const { showConfirm } = useAlert();

// Uso básico
const result = await showConfirm('¿Deseas eliminar este producto?');

if (result.isConfirmed) {
  // Usuario confirmó
  await deleteProduct();
  showSuccess('Producto eliminado');
} else {
  // Usuario canceló
  showInfo('Operación cancelada');
}

// Con título personalizado
const result = await showConfirm(
  'Esta acción no se puede deshacer',
  '¿Estás seguro?'
);

// Con textos de botones personalizados
const result = await showConfirm(
  '¿Deseas cerrar sesión?',
  'Confirmar cierre de sesión',
  {
    confirmButtonText: 'Sí, cerrar sesión',
    cancelButtonText: 'No, quedarme'
  }
);
```

**Parámetros:**
- `message` (string): Mensaje de confirmación
- `title` (string, opcional): Título del diálogo (por defecto: "¿Estás seguro?")
- `options` (object, opcional): Opciones adicionales de SweetAlert2

**Retorna:**
- Promise con objeto que contiene `isConfirmed` (boolean)

---

### 6. `showLoading()` - Indicador de Carga

Muestra un indicador de carga sin botones. Útil para operaciones asíncronas.

```javascript
const { showLoading, closeAlert } = useAlert();

// Mostrar loading
showLoading('Procesando pago...');

// Realizar operación
await processPayment();

// Cerrar loading
closeAlert();

// Mostrar resultado
showSuccess('Pago procesado exitosamente');
```

**Ejemplo completo:**

```javascript
const handleCheckout = async () => {
  showLoading('Procesando tu pedido...', 'Por favor espera');
  
  try {
    await createOrder();
    closeAlert();
    await showSuccess('¡Pedido creado exitosamente!', '¡Gracias por tu compra!');
    router.push('/orders');
  } catch (error) {
    closeAlert();
    showError('No se pudo procesar el pedido', 'Error');
  }
};
```

**Parámetros:**
- `message` (string, opcional): Mensaje de carga (por defecto: "Cargando...")
- `title` (string, opcional): Título del indicador

---

### 7. `showToast()` - Notificación Toast

Muestra una notificación pequeña en la esquina superior derecha. Ideal para feedback no intrusivo.

```javascript
const { showToast } = useAlert();

// Toast de éxito
showToast('Guardado correctamente');

// Toast de error
showToast('Error al guardar', 'error');

// Toast de advertencia
showToast('Verifica los datos', 'warning');

// Toast de información
showToast('Actualización disponible', 'info');

// Con opciones personalizadas
showToast('Producto agregado', 'success', {
  timer: 2000,
  position: 'bottom-end'
});
```

**Parámetros:**
- `message` (string): Mensaje del toast
- `icon` (string, opcional): Tipo de icono ('success', 'error', 'warning', 'info') (por defecto: 'success')
- `options` (object, opcional): Opciones adicionales de SweetAlert2

**Posiciones disponibles:**
- `top-start`, `top`, `top-end`
- `center-start`, `center`, `center-end`
- `bottom-start`, `bottom`, `bottom-end`

---

### 8. `closeAlert()` - Cerrar Alerta

Cierra la alerta actualmente visible.

```javascript
const { closeAlert } = useAlert();

closeAlert();
```

---

## Ejemplos Completos de Uso

### Ejemplo 1: Formulario de Contacto

```javascript
<script setup>
import { ref } from 'vue';
import { useAlert } from '@/composables/useAlert';
import { useContactStore } from '@/stores/modules/contactStore';

const { showSuccess, showError } = useAlert();
const contactStore = useContactStore();

const form = ref({
  email: '',
  message: ''
});

const handleSubmit = async () => {
  try {
    const result = await contactStore.sendMessage(form.value);
    
    if (result.success) {
      await showSuccess(
        'Te responderemos pronto a tu correo electrónico',
        '¡Mensaje Enviado!'
      );
      
      // Limpiar formulario
      form.value = { email: '', message: '' };
    } else {
      const errors = result.errors.join('\n');
      await showError(errors, 'Error en el formulario');
    }
  } catch (error) {
    await showError(
      'Por favor intenta de nuevo más tarde',
      'Error al enviar'
    );
  }
};
</script>
```

---

### Ejemplo 2: Eliminar Producto del Carrito

```javascript
<script setup>
import { useAlert } from '@/composables/useAlert';
import { useCartStore } from '@/stores/modules/cartStore';

const { showConfirm, showSuccess, showToast } = useAlert();
const cartStore = useCartStore();

const handleRemoveItem = async (productId) => {
  const result = await showConfirm(
    '¿Deseas eliminar este producto del carrito?',
    'Confirmar eliminación'
  );
  
  if (result.isConfirmed) {
    cartStore.removeItem(productId);
    showToast('Producto eliminado del carrito');
  }
};
</script>
```

---

### Ejemplo 3: Proceso de Checkout

```javascript
<script setup>
import { useAlert } from '@/composables/useAlert';
import { useOrderStore } from '@/stores/modules/orderStore';
import { useRouter } from 'vue-router';

const { showLoading, closeAlert, showSuccess, showError } = useAlert();
const orderStore = useOrderStore();
const router = useRouter();

const handleCheckout = async () => {
  // Mostrar loading
  showLoading('Procesando tu pedido...', 'Por favor espera');
  
  try {
    // Procesar orden
    const order = await orderStore.createOrder();
    
    // Cerrar loading
    closeAlert();
    
    // Mostrar éxito
    await showSuccess(
      `Tu número de orden es: ${order.id}`,
      '¡Pedido Realizado!'
    );
    
    // Redirigir
    router.push(`/orders/${order.id}`);
    
  } catch (error) {
    closeAlert();
    await showError(
      'Verifica tu información de pago e intenta de nuevo',
      'Error al procesar pedido'
    );
  }
};
</script>
```

---

### Ejemplo 4: Agregar a Favoritos

```javascript
<script setup>
import { useAlert } from '@/composables/useAlert';
import { useWishlistStore } from '@/stores/modules/wishlistStore';

const { showToast } = useAlert();
const wishlistStore = useWishlistStore();

const handleAddToWishlist = async (product) => {
  try {
    await wishlistStore.addItem(product.id);
    showToast('Agregado a tu lista de deseos', 'success');
  } catch (error) {
    showToast('Error al agregar a favoritos', 'error');
  }
};
</script>
```

---

## Personalización de Colores

El composable usa los colores de la marca de CrushMe:

- **Confirmación (Éxito)**: `#406582` (brand-blue-medium)
- **Cancelación (Error)**: `#BF5E81` (brand-pink-dark)
- **Advertencia**: `#DA9DFF` (brand-purple-light)
- **Información**: `#A4C1D0` (brand-blue-light)

---

## Personalización de Fuentes

Las alertas usan:
- **Títulos**: Font Comfortaa
- **Textos y Botones**: Font Poppins

Esto se aplica automáticamente mediante las clases CSS personalizadas.

---

## Opciones Adicionales de SweetAlert2

Puedes pasar cualquier opción válida de SweetAlert2 en el parámetro `options`:

```javascript
showSuccess('Mensaje', 'Título', {
  timer: 3000,              // Tiempo en ms antes de cerrar
  timerProgressBar: true,   // Mostrar barra de progreso
  position: 'top-end',      // Posición de la alerta
  showConfirmButton: false, // Ocultar botón de confirmar
  backdrop: true,           // Mostrar overlay de fondo
  allowEscapeKey: false,    // Deshabilitar cerrar con ESC
  allowOutsideClick: false, // Deshabilitar cerrar al hacer click fuera
  confirmButtonText: 'OK',  // Texto del botón
  width: '600px',           // Ancho personalizado
  padding: '2rem'           // Padding personalizado
});
```

Para ver todas las opciones disponibles, consulta la [documentación oficial de SweetAlert2](https://sweetalert2.github.io/).

---

## Mejores Prácticas

1. **Usa `showToast()` para feedback no intrusivo** - Como "Guardado", "Copiado", etc.

2. **Usa `showConfirm()` para acciones destructivas** - Como eliminar, cancelar pedidos, etc.

3. **Usa `showLoading()` para operaciones asíncronas** - Y siempre cierra con `closeAlert()`

4. **Evita múltiples alertas simultáneas** - SweetAlert2 solo muestra una alerta a la vez

5. **Mensajes claros y concisos** - El usuario debe entender rápidamente qué pasó

6. **Siempre maneja errores** - Muestra mensajes de error útiles al usuario

---

## Troubleshooting

### La alerta no se muestra

- Verifica que hayas importado correctamente el composable
- Asegúrate de que SweetAlert2 esté instalado: `npm install sweetalert2`

### Los estilos no se aplican

- Las fuentes Comfortaa y Poppins deben estar cargadas en `style.css`
- Verifica que Tailwind esté configurado correctamente

### La alerta se cierra muy rápido

- Ajusta el `timer` en las opciones
- Para que no se cierre automáticamente: `{ timer: undefined }`

---

## Recursos Adicionales

- [Documentación de SweetAlert2](https://sweetalert2.github.io/)
- [Ejemplos de SweetAlert2](https://sweetalert2.github.io/#examples)
- [Configuración de SweetAlert2](https://sweetalert2.github.io/#configuration)

