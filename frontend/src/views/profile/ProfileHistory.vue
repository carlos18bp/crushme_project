<template>
  <div class="profile-history">
    <div class="px-4 md:px-6 py-6 md:py-8 lg:px-8 max-w-7xl mx-auto">
      <!-- Header -->
      <h1 class="text-2xl md:text-3xl font-medium text-gray-900 font-comfortaa mb-6 md:mb-8">
        Purchase History
      </h1>

      <!-- Loading State -->
      <div v-if="orderStore.isLoading" class="loading-state flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-pink"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="orderStore.error" class="error-state text-center py-12">
        <div class="flex flex-col items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-red-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-xl font-medium text-gray-900 font-comfortaa mb-2">
            Error loading orders
          </h3>
          <p class="text-gray-500 font-comfortaa mb-6">
            {{ orderStore.error }}
          </p>
          <button 
            @click="loadPurchaseHistory"
            class="btn-retry px-6 py-3 rounded-full text-white font-semibold font-poppins transition-all duration-200 hover:opacity-90"
            style="background-color: #DA9DFF;">
            Try Again
          </button>
        </div>
      </div>

      <!-- Orders List -->
      <div v-else class="orders-list space-y-3 md:space-y-4">
        <!-- Order Card -->
        <div 
          v-for="order in displayOrders" 
          :key="order.id"
          class="order-card rounded-xl md:rounded-2xl border border-gray-200 overflow-hidden"
          style="background-color: rgba(255, 63, 213, 0.2);"
        >
          <!-- Order Header (Always Visible) -->
          <div 
            @click="toggleOrderExpansion(order.id)"
            class="order-header p-3 md:p-4 cursor-pointer hover:bg-white/30 transition-colors"
          >
            <div class="flex items-center justify-between gap-3">
              <!-- Left: Order Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <p class="text-xs md:text-sm font-semibold text-gray-900 font-comfortaa">
                    Order #{{ order.orderNumber }}
                  </p>
                  <span 
                    v-if="order.isGift" 
                    class="gift-badge px-2 py-0.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white text-xs font-semibold rounded-full font-poppins flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                    </svg>
                    GIFT
                  </span>
                </div>
                <p class="text-xs md:text-sm text-gray-600 font-poppins">
                  {{ order.itemCount }} {{ order.itemCount === 1 ? 'item' : 'items' }} • Total: ${{ order.total }}
                </p>
              </div>
              
              <!-- Right: Expand Icon -->
              <div class="flex-shrink-0">
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  class="h-5 w-5 md:h-6 md:w-6 text-gray-600 transition-transform duration-200"
                  :class="{ 'rotate-180': isOrderExpanded(order.id) }"
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Order Details (Expandable) -->
          <div 
            v-show="isOrderExpanded(order.id)"
            class="order-details bg-white/50 border-t border-gray-200"
          >
            <div class="p-3 md:p-4 space-y-3 md:space-y-4">
              <!-- Products Table -->
              <div class="products-section">
                <h3 class="text-sm md:text-base font-semibold text-gray-900 font-comfortaa mb-2">
                  Products
                </h3>
                <div class="overflow-x-auto">
                  <table class="w-full">
                    <thead>
                      <tr class="border-b border-gray-200">
                        <th class="text-left py-2 px-2 text-xs md:text-sm font-semibold text-gray-700 font-poppins">Product</th>
                        <th class="text-center py-2 px-2 text-xs md:text-sm font-semibold text-gray-700 font-poppins">Qty</th>
                        <th class="text-right py-2 px-2 text-xs md:text-sm font-semibold text-gray-700 font-poppins">Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr 
                        v-for="item in order.items" 
                        :key="item.id"
                        class="border-b border-gray-100 hover:bg-white/50 transition-colors"
                      >
                        <td class="py-2 px-2">
                          <div class="flex items-center gap-2 md:gap-3">
                            <img 
                              :src="item.image" 
                              :alt="item.name"
                              class="w-10 h-10 md:w-12 md:h-12 object-cover rounded-lg flex-shrink-0"
                              @click="handleNavigateToProduct(item.productId)"
                              style="cursor: pointer;"
                            />
                            <span 
                              class="text-xs md:text-sm text-gray-900 font-poppins line-clamp-2 cursor-pointer hover:text-brand-pink"
                              @click="handleNavigateToProduct(item.productId)"
                            >
                              {{ item.name }}
                            </span>
                          </div>
                        </td>
                        <td class="py-2 px-2 text-center text-xs md:text-sm text-gray-700 font-poppins">
                          {{ item.quantity }}
                        </td>
                        <td class="py-2 px-2 text-right text-xs md:text-sm font-semibold text-gray-900 font-poppins">
                          ${{ item.price }}
                        </td>
                      </tr>
                      <!-- Subtotal Row -->
                      <tr class="border-t-2 border-gray-300">
                        <td colspan="2" class="py-2 px-2 text-right text-xs md:text-sm font-semibold text-gray-700 font-poppins">
                          Subtotal:
                        </td>
                        <td class="py-2 px-2 text-right text-xs md:text-sm font-bold text-gray-900 font-poppins">
                          ${{ order.subtotal }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Shipping Information -->
              <div class="shipping-info">
                <h3 class="text-sm md:text-base font-semibold text-gray-900 font-comfortaa mb-2">
                  Shipping information
                </h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs md:text-sm text-gray-600 font-poppins">
                  <div><span class="font-semibold">Name:</span> {{ order.shippingName }}</div>
                  <div><span class="font-semibold">Phone:</span> {{ order.shippingPhone }}</div>
                  <div class="sm:col-span-2"><span class="font-semibold">Address:</span> {{ order.shippingAddress }}</div>
                  <div class="sm:col-span-2"><span class="font-semibold">Shipping Method:</span> {{ order.shippingMethod }}</div>
                </div>
                
                <!-- Order Summary -->
                <div class="mt-3 pt-3 border-t border-gray-200">
                  <div class="space-y-1 text-xs md:text-sm font-poppins">
                    <div class="flex justify-between text-gray-600">
                      <span>Subtotal:</span>
                      <span class="font-semibold">${{ order.subtotal }}</span>
                    </div>
                    <div class="flex justify-between text-gray-600">
                      <span>Shipping:</span>
                      <span class="font-semibold">${{ order.shippingCost }}</span>
                    </div>
                    <div class="flex justify-between text-base md:text-lg font-bold text-brand-pink pt-1 border-t border-gray-200">
                      <span>Total:</span>
                      <span>${{ order.total }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Gift Message (if it's a gift) -->
              <div v-if="order.isGift && order.giftMessage" class="gift-message p-3 bg-pink-50 rounded-lg border border-pink-200">
                <h3 class="text-sm md:text-base font-semibold text-brand-pink font-comfortaa mb-1 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1.5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                  </svg>
                  Gift Message
                </h3>
                <p class="text-xs md:text-sm text-gray-700 font-poppins italic">
                  "{{ order.giftMessage }}"
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="displayOrders.length === 0" class="empty-state text-center py-8 md:py-12">
          <div class="flex flex-col items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 md:h-20 md:w-20 lg:h-24 lg:w-24 text-gray-300 mb-3 md:mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <h3 class="text-lg md:text-xl font-medium text-gray-900 font-comfortaa mb-2">
              No orders found
            </h3>
            <p class="text-sm md:text-base text-gray-500 font-comfortaa mb-4 md:mb-6">
              You haven't made any purchases yet
            </p>
            <button 
              @click="router.push({ name: `Products-${i18nStore.locale}` })"
              class="btn-shop px-5 md:px-6 py-2.5 md:py-3 rounded-full text-white font-semibold font-poppins text-sm md:text-base transition-all duration-200 hover:opacity-90"
              style="background-color: #DA9DFF;">
              Start Shopping
            </button>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pagination.totalPages > 1" class="pagination-container mt-6 md:mt-8 flex justify-center items-center gap-2">
          <!-- Previous Button -->
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="!pagination.hasPrevious"
            class="pagination-btn px-3 py-2 rounded-lg font-poppins text-sm transition-all duration-200"
            :class="pagination.hasPrevious ? 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700' : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Page Numbers -->
          <div class="flex gap-2">
            <template v-for="page in visiblePages" :key="page">
              <span
                v-if="page === '...'"
                class="w-10 h-10 flex items-center justify-center text-gray-400 font-poppins text-sm"
              >
                ...
              </span>
              <button
                v-else
                @click="goToPage(page)"
                class="pagination-btn w-10 h-10 rounded-lg font-poppins text-sm font-medium transition-all duration-200"
                :class="page === currentPage 
                  ? 'text-white' 
                  : 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700'"
                :style="page === currentPage ? 'background-color: #DA9DFF;' : ''"
              >
                {{ page }}
              </button>
            </template>
          </div>

          <!-- Next Button -->
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="!pagination.hasNext"
            class="pagination-btn px-3 py-2 rounded-lg font-poppins text-sm transition-all duration-200"
            :class="pagination.hasNext ? 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700' : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useOrderStore } from '@/stores/modules/orderStore'
import { useProfileStore } from '@/stores/modules/profileStore'

// Router and stores
const router = useRouter()
const route = useRoute()
const i18nStore = useI18nStore()
const orderStore = useOrderStore()
const profileStore = useProfileStore()

// Local state
const expandedOrders = ref(new Set()) // Track which orders are expanded
const currentPage = ref(1)
const pagination = ref({
  currentPage: 1,
  totalPages: 1,
  totalCount: 0,
  hasNext: false,
  hasPrevious: false
})

// Computed: Display orders (no local filtering, just transform)
const displayOrders = computed(() => {
  // Transform orders to component structure
  return orderStore.orders.map(order => {
    // Check if it's a gift order
    const isGift = order.is_gift === true
    
    // Parse prices
    const orderTotal = Math.floor(parseFloat(order.total || 0))
    
    // Transform all items
    const items = (order.items || []).map(item => {
      const itemPrice = Math.floor(parseFloat(item.unit_price || item.price || 0))
      return {
        id: item.id,
        productId: item.woocommerce_product_id || item.product_id,
        name: item.product_name || item.name || 'Product',
        quantity: item.quantity || 1,
        price: itemPrice,
        image: item.image_url || item.product_image || '/placeholder-product.png'
      }
    })
    
    // Calculate subtotal (sum of all item prices)
    const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    
    // Calculate shipping as difference between total and subtotal
    const shippingCost = Math.max(0, orderTotal - subtotal)
    
    return {
      id: order.id,
      orderNumber: order.order_number || order.id,
      itemCount: items.length,
      items: items,
      subtotal: subtotal,
      shippingMethod: order.shipping_method || 'Standard (5-7 business days)',
      shippingCost: shippingCost,
      total: orderTotal,
      // For gifts, shipping info might be hidden
      shippingName: isGift 
        ? (order.gift_summary?.sender || order.sender_username || 'Gift Order') 
        : (order.shipping_address || order.billing_address?.first_name || ''),
      shippingAddress: isGift 
        ? (order.gift_summary?.privacy_note || 'Gift - Shipping details hidden for privacy')
        : formatAddress(order.shipping_address, order.shipping_city, order.shipping_state, order.shipping_postal_code),
      shippingPhone: isGift 
        ? 'Hidden for privacy' 
        : (order.phone_number || 'N/A'),
      date: order.created_at,
      isGift: isGift,
      giftMessage: order.gift_message || null
    }
  })
})

// Computed: Loading state
const isLoading = computed(() => orderStore.isLoading)

// Methods
const formatAddress = (address, city, state, postalCode) => {
  // If address is an object (old format)
  if (typeof address === 'object' && address !== null) {
    const parts = [
      address.address_1 || address.address,
      address.city,
      address.state,
      address.postcode || address.postal_code
    ].filter(Boolean)
    return parts.join(', ')
  }
  
  // If address is a string (new format from backend)
  const parts = [
    address,
    city,
    state,
    postalCode
  ].filter(Boolean)
  return parts.join(', ') || 'N/A'
}

const isProductInFavorites = (productId) => {
  if (!productId) return false
  return profileStore.favoriteProducts.some(p => p.id === productId)
}

const handleNavigateToProduct = (productId) => {
  router.push({ name: `ProductDetail-${i18nStore.locale}`, params: { id: productId } })
}

const toggleOrderExpansion = (orderId) => {
  if (expandedOrders.value.has(orderId)) {
    expandedOrders.value.delete(orderId)
  } else {
    expandedOrders.value.add(orderId)
  }
  // Force reactivity
  expandedOrders.value = new Set(expandedOrders.value)
}

const isOrderExpanded = (orderId) => {
  return expandedOrders.value.has(orderId)
}

// Computed: Visible page numbers for pagination
const visiblePages = computed(() => {
  const total = pagination.value.totalPages
  const current = currentPage.value
  const pages = []
  
  if (total <= 7) {
    // Show all pages if 7 or less
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    // Always show first page
    pages.push(1)
    
    if (current > 3) {
      pages.push('...')
    }
    
    // Show pages around current
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      pages.push(i)
    }
    
    if (current < total - 2) {
      pages.push('...')
    }
    
    // Always show last page
    pages.push(total)
  }
  
  return pages
})

// Computed: Loading state (use orderStore.isLoading directly in template)

// Methods
const updateURL = () => {
  const query = {}
  
  if (currentPage.value > 1) {
    query.page = currentPage.value
  }
  
  router.replace({ query })
}

const restoreFromURL = () => {
  const page = parseInt(route.query.page) || 1
  currentPage.value = page
  console.log('🔍 Página restaurada desde URL:', page)
}

const goToPage = async (page) => {
  if (page < 1 || page > pagination.value.totalPages || page === currentPage.value) {
    return
  }
  
  currentPage.value = page
  updateURL()
  await loadPurchaseHistory()
  
  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const loadPurchaseHistory = async () => {
  const result = await orderStore.fetchOrders(currentPage.value)
  
  if (result.success) {
    console.log('✅ Purchase history loaded:', orderStore.orders.length, 'orders')
    console.log('📊 Pagination data:', result.pagination)
    
    // Update pagination data
    if (result.pagination) {
      pagination.value = result.pagination
      console.log('📄 Current page:', pagination.value.currentPage, '/', pagination.value.totalPages)
    }
    
    // Load details for each order to get items if not already loaded
    for (const order of orderStore.orders) {
      if (!order.items || order.items.length === 0) {
        await orderStore.fetchOrder(order.id)
      }
    }
  } else {
    console.error('❌ Error loading purchase history:', result.error)
  }
}


// Lifecycle hooks
onMounted(async () => {
  // Restore state from URL
  restoreFromURL()
  
  // Load purchase history on component mount
  await loadPurchaseHistory()
  
  // Load user favorites if not already loaded
  if (profileStore.favoriteProducts.length === 0) {
    await profileStore.fetchFavoriteProducts()
  }
})

onBeforeUnmount(() => {
  // Clean up if needed
})
</script>

<style scoped>
.font-comfortaa {
  font-family: 'Comfortaa', cursive;
}

.font-poppins {
  font-family: 'Poppins', sans-serif;
}

.order-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.order-header:hover {
  background-color: rgba(255, 255, 255, 0.4);
}

.order-details {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

/* Table styles */
table {
  border-collapse: separate;
  border-spacing: 0;
}

tbody tr:last-child {
  border-bottom: none;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Brand pink color */
.text-brand-pink {
  color: #FF3FD5;
}

/* Pagination styles */
.pagination-container {
  user-select: none;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.pagination-btn:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(218, 157, 255, 0.3);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:active:not(:disabled) {
  transform: translateY(0);
}

/* Custom select arrow */
select {
  background-image: none;
}

/* Gift badge */
.gift-badge {
  animation: pulse-gift 2s ease-in-out infinite;
}

@keyframes pulse-gift {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

/* Gift message box */
.gift-message {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Action buttons */
.btn-shop,
.btn-retry {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-shop:hover,
.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(192, 132, 252, 0.5);
}

.btn-shop:active,
.btn-retry:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .order-card .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: 100%;
  }
  
  .date-filter select {
    width: 100%;
  }
}
</style>
