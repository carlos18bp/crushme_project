<template>
  <div class="min-h-screen bg-brand-pink-lighter flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
      <!-- Loading State -->
      <div v-if="isLoading" data-testid="wishlist-redirect-loading">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-brand-pink mx-auto mb-4"></div>
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Loading wishlist...</h2>
        <p class="text-gray-600">Preparing your gift checkout</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" role="alert" data-testid="wishlist-redirect-error">
        <div class="text-red-500 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Oops! Something went wrong</h2>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button 
          @click="goHome"
          class="px-6 py-2 bg-brand-pink text-white rounded-full hover:opacity-90 transition-all"
        >
          Go to Home
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWishlistStore } from '@/stores'
import { useCartStore } from '@/stores'
import { useI18nStore } from '@/stores/modules/i18nStore'

const route = useRoute()
const router = useRouter()
const wishlistStore = useWishlistStore()
const cartStore = useCartStore()
const i18nStore = useI18nStore()

const isLoading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    // Extraer username y wishlistId de la ruta
    const username = route.params.username
    const wishlistId = route.params.wishlistId

    console.log('🎁 [WISHLIST REDIRECT] Loading wishlist:', { username, wishlistId })

    if (!username || !wishlistId) {
      throw new Error('Invalid wishlist link')
    }

    // Consultar la wishlist pública
    const result = await wishlistStore.fetchPublicWishlistByUsername(username, wishlistId)

    if (!result.success || !result.data) {
      throw new Error(result.error || 'Wishlist not found')
    }

    const wishlist = result.data

    console.log('✅ [WISHLIST REDIRECT] Wishlist loaded:', wishlist)

    // Verificar que tenga items
    if (!wishlist.items || wishlist.items.length === 0) {
      throw new Error('This wishlist is empty')
    }

    // Limpiar el carrito antes de agregar los nuevos productos
    const clearResult = cartStore.clearCart()
    if (!clearResult.success) {
      throw new Error(clearResult.error || 'Unable to prepare the gift cart')
    }

    // Agregar cada producto de la wishlist al carrito con los precios del backend
    let addedItems = 0
    for (const item of wishlist.items) {
      if (item.is_available) {
        // Asegurar que el precio sea un número válido
        const itemPrice = parseFloat(item.product_price)
        
        if (isNaN(itemPrice) || itemPrice === 0) {
          console.error('❌ [WISHLIST REDIRECT] Invalid price for item:', item.product_name, 'Price:', item.product_price)
        }
        
        // Usar el precio que viene del backend (ya convertido a la moneda correcta)
        const productData = {
          name: item.product_name,
          price: itemPrice, // ⭐ Precio del backend como número
          image: item.product_image,
          variation_id: item.woocommerce_variation_id || null,
          attributes: item.attributes || null,
          stock_status: 'instock'
        }

        console.log('➕ [WISHLIST REDIRECT] Adding to cart:', {
          productId: item.woocommerce_product_id,
          quantity: 1,
          productData: productData,
          priceType: typeof itemPrice,
          priceValue: itemPrice,
          currency: item.currency || wishlist.currency
        })
        
        const addResult = cartStore.addToCart(item.woocommerce_product_id, 1, productData)
        if (!addResult.success) {
          throw new Error(addResult.error || `Unable to add ${item.product_name} to the gift cart`)
        }
        addedItems += 1
        console.log('✅ [WISHLIST REDIRECT] Add to cart result:', addResult)
      } else {
        console.warn('⚠️ [WISHLIST REDIRECT] Skipping unavailable item:', item.product_name)
      }
    }

    if (addedItems === 0) {
      throw new Error('This wishlist has no available items')
    }

    console.log('🛒 [WISHLIST REDIRECT] Cart updated with', cartStore.items.length, 'items')
    console.log('💰 [WISHLIST REDIRECT] Total value:', wishlist.total_value, wishlist.currency)

    // Redirigir al checkout con modo gift y username prellenado
    console.log('🔄 [WISHLIST REDIRECT] Redirecting to checkout...')
    
    router.push({
      name: `Checkout-${i18nStore.locale}`,
      query: {
        giftMode: 'true',
        username: wishlist.user_username,
        wishlistId: wishlist.id,
        wishlistName: wishlist.name
      }
    })

  } catch (err) {
    console.error('❌ [WISHLIST REDIRECT] Error:', err)
    error.value = err.message || 'Failed to load wishlist'
    isLoading.value = false
  }
})

const goHome = () => {
  router.push({ name: `Home-${i18nStore.locale}` })
}
</script>

<style scoped>
/* Animación de spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
