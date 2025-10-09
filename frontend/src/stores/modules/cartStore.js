/**
 * Cart Store para CrushMe - Solo con LocalStorage
 * Gestiona el carrito de compras de forma simple sin backend
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const CART_STORAGE_KEY = 'crushme_cart';

export const useCartStore = defineStore('cart', () => {
  // State
  const items = ref([]);
  const isUpdating = ref(false);

  // Getters
  const totalItems = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0);
  });

  const totalPrice = computed(() => {
    return items.value.reduce((total, item) => total + (item.quantity * item.price), 0);
  });

  const itemsCount = computed(() => items.value.length);

  const isEmpty = computed(() => items.value.length === 0);

  const hasItems = computed(() => items.value.length > 0);

  // Funciones auxiliares de localStorage

  /**
   * Cargar carrito desde localStorage
   */
  function loadCart() {
    try {
      const savedCart = localStorage.getItem(CART_STORAGE_KEY);
      if (savedCart) {
        items.value = JSON.parse(savedCart);
      }
    } catch (err) {
      items.value = [];
    }
  }

  /**
   * Guardar carrito en localStorage
   */
  function saveCart() {
    try {
      localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items.value));
    } catch (err) {
      // Silent error handling
    }
  }

  // Acciones principales

  /**
   * Inicializar carrito
   */
  function initializeCart() {
    loadCart();
    return { success: true, data: { items: items.value } };
  }

  /**
   * Agregar producto al carrito
   * @param {number} productId - ID del producto
   * @param {number} quantity - Cantidad a agregar (por defecto 1)
   * @param {object} productData - Datos del producto (name, price, image, stock_status, color, size, attributes)
   */
  function addToCart(productId, quantity = 1, productData = {}) {
    isUpdating.value = true;

    try {
      // Crear una clave única para el producto basada en sus atributos
      const attributesKey = JSON.stringify({
        color: productData.color || null,
        size: productData.size || null,
        attributes: productData.attributes || null
      });

      const existingItem = items.value.find(item => {
        const itemAttributesKey = JSON.stringify({
          color: item.color || null,
          size: item.size || null,
          attributes: item.attributes || null
        });
        return item.product_id === productId && itemAttributesKey === attributesKey;
      });
      
      if (existingItem) {
        // Si el producto ya existe con los mismos atributos, aumentar la cantidad
        existingItem.quantity = existingItem.quantity + quantity;
        // Actualizar la información del producto por si cambió
        existingItem.name = productData.name || existingItem.name;
        existingItem.price = parseFloat(productData.price) || existingItem.price;
        existingItem.image = productData.image || existingItem.image;
        existingItem.stock_status = productData.stock_status || existingItem.stock_status;
      } else {
        // Agregar nuevo producto con la cantidad especificada
        const newItem = {
          id: Date.now(), // ID temporal único
          product_id: productId,
          name: productData.name || `Producto ${productId}`,
          price: parseFloat(productData.price) || 0,
          image: productData.image || null,
          stock_status: productData.stock_status || 'instock',
          color: productData.color || null,
          size: productData.size || null,
          attributes: productData.attributes || null,
          quantity: quantity,
          added_at: new Date().toISOString()
        };
        
        items.value.push(newItem);
      }
      
      saveCart();
      return { success: true, data: { items: items.value } };
    } catch (err) {
      return { success: false, error: 'Error al agregar al carrito' };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Actualizar cantidad de un item
   * @param {number} itemId - ID del item en el carrito
   * @param {number} quantity - Nueva cantidad
   */
  function updateCartItem(itemId, quantity) {
    isUpdating.value = true;

    try {
      const item = items.value.find(item => item.id === itemId);
      
      if (item) {
        if (quantity <= 0) {
          // Si la cantidad es 0 o menos, eliminar el item
          removeFromCart(itemId);
        } else {
          item.quantity = quantity;
          saveCart();
        }
      }
      
      return { success: true, data: { items: items.value } };
    } catch (err) {
      return { success: false, error: 'Error al actualizar item' };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Eliminar producto del carrito
   * @param {number} itemId - ID del item en el carrito
   */
  function removeFromCart(itemId) {
    isUpdating.value = true;

    try {
      const index = items.value.findIndex(item => item.id === itemId);
      
      if (index !== -1) {
        items.value.splice(index, 1);
        saveCart();
      }
      
      return { success: true, data: { items: items.value } };
    } catch (err) {
      return { success: false, error: 'Error al eliminar del carrito' };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Vaciar todo el carrito
   */
  function clearCart() {
    isUpdating.value = true;

    try {
      items.value = [];
      localStorage.removeItem(CART_STORAGE_KEY);
      
      return { success: true, data: { items: [] } };
    } catch (err) {
      return { success: false, error: 'Error al vaciar el carrito' };
    } finally {
      isUpdating.value = false;
    }
  }

  /**
   * Verificar si un producto está en el carrito
   * @param {number} productId - ID del producto
   */
  function isProductInCart(productId) {
    return items.value.some(item => item.product_id === productId);
  }

  /**
   * Obtener cantidad de un producto en el carrito
   * @param {number} productId - ID del producto
   */
  function getProductQuantityInCart(productId) {
    const item = items.value.find(item => item.product_id === productId);
    return item ? item.quantity : 0;
  }

  /**
   * Obtener un item del carrito por su ID
   * @param {number} itemId - ID del item
   */
  function getCartItemById(itemId) {
    return items.value.find(item => item.id === itemId);
  }

  // Inicializar el carrito al crear el store
  loadCart();

  return {
    // State
    items,
    isUpdating,
    
    // Getters
    totalItems,
    totalPrice,
    itemsCount,
    isEmpty,
    hasItems,
    
    // Actions
    initializeCart,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    isProductInCart,
    getProductQuantityInCart,
    getCartItemById,
    
    // Helpers
    loadCart,
    saveCart
  };
});
