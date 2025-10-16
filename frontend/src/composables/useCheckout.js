/**
 * Composable para lógica compartida de checkout
 */
import { ref, computed } from 'vue';
import { useCartStore } from '@/stores/modules/cartStore.js';
import { useProductStore } from '@/stores/modules/productStore.js';

export function useCheckout() {
  const cartStore = useCartStore();
  const productStore = useProductStore();

  // ⭐ Producto de dropshipping (recargo oculto)
  const DROPSHIPPING_PRODUCT_ID = 48500;
  const dropshippingProduct = ref(null);
  const isLoadingDropshipping = ref(false);

  /**
   * Cargar producto de dropshipping (recargo)
   */
  const loadDropshippingProduct = async () => {
    isLoadingDropshipping.value = true;
    
    try {
      console.log(`📦 [DROPSHIPPING] Consultando producto ${DROPSHIPPING_PRODUCT_ID}...`);
      
      const result = await productStore.fetchWooProduct(DROPSHIPPING_PRODUCT_ID);
      
      if (result.success && result.data) {
        dropshippingProduct.value = result.data;
        console.log('✅ [DROPSHIPPING] Producto cargado:', {
          id: result.data.id,
          name: result.data.name,
          price: result.data.price
        });
      } else {
        console.error('❌ [DROPSHIPPING] Error al cargar producto:', result.error);
      }
    } catch (error) {
      console.error('❌ [DROPSHIPPING] Error inesperado:', error);
    } finally {
      isLoadingDropshipping.value = false;
    }
  };

  /**
   * Calcular shipping base según ciudad
   */
  const calculateBaseShipping = (city) => {
    const ciudad = (city || '').toLowerCase().trim();
    
    if (!ciudad) {
      return 15000;
    }
    
    switch (ciudad) {
      case 'medellín':
      case 'medellin':
        return 10500;
        
      case 'san andrés isla':
      case 'san andres isla':
      case 'san andrés':
      case 'san andres':
      case 'santa catalina':
      case 'providencia':
        return 45000;
        
      default:
        return 15000;
    }
  };

  /**
   * Calcular shipping mostrado (base + dropshipping)
   */
  const calculateShipping = (city) => {
    let total = calculateBaseShipping(city);
    
    if (dropshippingProduct.value && dropshippingProduct.value.price) {
      const dropshippingPrice = parseFloat(dropshippingProduct.value.price);
      total += dropshippingPrice;
      console.log(`📦 [DROPSHIPPING] Shipping mostrado: ${calculateBaseShipping(city)} + ${dropshippingPrice} = ${total}`);
    }
    
    return total;
  };

  /**
   * Calcular IVA incluido en el subtotal
   */
  const calculateTax = (subtotal) => {
    return subtotal * (0.19 / 1.19);
  };

  /**
   * Calcular total (subtotal + shipping)
   */
  const calculateTotal = (subtotal, shipping) => {
    return subtotal + shipping;
  };

  /**
   * Preparar items del carrito incluyendo dropshipping
   * @param {string} type - Tipo de orden: 'regular' o 'gift'
   */
  const prepareCartItems = (type = 'regular') => {
    const items = cartStore.items.map(item => ({
      woocommerce_product_id: item.product_id || item.id,
      woocommerce_variation_id: item.variation_id || null,
      product_name: item.name,
      quantity: item.quantity,
      unit_price: parseFloat(item.price),
      attributes: item.attributes || null
    }));

    // Agregar producto de dropshipping
    if (dropshippingProduct.value) {
      items.push({
        woocommerce_product_id: dropshippingProduct.value.id,
        woocommerce_variation_id: null,
        product_name: dropshippingProduct.value.name,
        quantity: 1,
        unit_price: parseFloat(dropshippingProduct.value.price),
        attributes: null
      });
      
      const logPrefix = type === 'gift' ? '🎁 [GIFT]' : '📦 [REGULAR]';
      console.log(`${logPrefix} [DROPSHIPPING] Producto agregado a items:`, {
        id: dropshippingProduct.value.id,
        name: dropshippingProduct.value.name,
        price: dropshippingProduct.value.price
      });
    }

    return items;
  };

  /**
   * Preparar datos de orden regular
   */
  const prepareRegularOrderData = (shippingForm, countryName, subtotal, city) => {
    const items = prepareCartItems('regular');
    const baseShipping = calculateBaseShipping(city);
    const shipping = calculateShipping(city);
    const total = calculateTotal(subtotal, shipping);

    const orderData = {
      items: items,
      customer_email: shippingForm.email,
      customer_name: shippingForm.fullName,
      shipping_address: shippingForm.address1,
      shipping_city: shippingForm.city,
      shipping_state: shippingForm.state,
      shipping_postal_code: shippingForm.zipCode,
      shipping_country: countryName,
      phone_number: `${shippingForm.phoneCode} ${shippingForm.phone}`,
      notes: shippingForm.additionalDetails || '',
      shipping: baseShipping, // ⭐ Shipping base (sin recargo)
      total: total // ⭐ Total calculado
    };

    console.log('📤 [REGULAR] Datos de orden:', orderData);
    console.log('💰 [REGULAR] Desglose:', {
      subtotal: subtotal,
      shipping: baseShipping,
      dropshipping: dropshippingProduct.value?.price || 0,
      total: total
    });

    return orderData;
  };

  /**
   * Preparar datos de regalo
   * @param {Object} shippingForm - Formulario de envío
   * @param {string} senderUsername - Username del remitente
   * @param {number} subtotal - Subtotal de productos
   * @param {number} userShippingCost - Costo de envío del destinatario (desde API)
   */
  const prepareGiftOrderData = (shippingForm, senderUsername, subtotal, userShippingCost = 15000) => {
    const items = prepareCartItems('gift');
    
    // Usar el shipping cost del usuario seleccionado + dropshipping
    const baseShipping = userShippingCost;
    const dropshippingCost = dropshippingProduct.value ? parseFloat(dropshippingProduct.value.price) : 0;
    const totalShipping = baseShipping + dropshippingCost;
    const total = calculateTotal(subtotal, totalShipping);

    const giftData = {
      customer_email: shippingForm.email,
      sender_username: senderUsername,
      receiver_username: shippingForm.username.replace('@', ''),
      items: items,
      gift_message: shippingForm.note || '',
      total: total // ⭐ Total calculado con shipping real del destinatario
    };

    console.log('🎁 [GIFT] Datos de regalo:', giftData);
    console.log('💰 [GIFT] Desglose:', {
      subtotal: subtotal,
      userShipping: baseShipping,
      dropshipping: dropshippingCost,
      totalShipping: totalShipping,
      total: total
    });

    return giftData;
  };

  return {
    // State
    dropshippingProduct,
    isLoadingDropshipping,
    DROPSHIPPING_PRODUCT_ID,
    
    // Methods
    loadDropshippingProduct,
    calculateBaseShipping,
    calculateShipping,
    calculateTax,
    calculateTotal,
    prepareCartItems,
    prepareRegularOrderData,
    prepareGiftOrderData
  };
}
