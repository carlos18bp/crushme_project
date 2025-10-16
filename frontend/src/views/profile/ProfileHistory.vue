<template>
  <div class="profile-history">
    <div class="px-4 md:px-6 py-6 md:py-8 lg:px-8 max-w-7xl mx-auto">
      <!-- Header -->
      <h1 class="text-2xl md:text-3xl font-medium text-gray-900 font-comfortaa mb-6 md:mb-8">
        Purchase History
      </h1>

      <!-- Filters -->
      <div class="filters-section mb-4 md:mb-6">
        <h2 class="text-base md:text-lg font-medium text-gray-900 font-comfortaa mb-3 md:mb-4">
          Filter by
        </h2>
        <div class="filters-row flex flex-col sm:flex-row gap-3 md:gap-4 items-stretch sm:items-center">
          <!-- Search Input -->
          <div class="search-input relative flex-1 sm:max-w-xs">
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input 
              type="text" 
              placeholder="Search"
              v-model="searchQuery"
              class="w-full pl-9 md:pl-10 pr-4 py-2 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-pink focus:border-transparent font-comfortaa"
            />
          </div>

          <!-- Date Filter -->
          <div class="date-filter relative w-full sm:w-auto">
            <select 
              v-model="dateFilter"
              class="appearance-none w-full px-4 py-2 pr-10 text-sm md:text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-pink focus:border-transparent font-comfortaa cursor-pointer bg-white"
            >
              <option value="">Date</option>
              <option value="last-week">Last Week</option>
              <option value="last-month">Last Month</option>
              <option value="last-3-months">Last 3 Months</option>
              <option value="last-year">Last Year</option>
            </select>
            <span class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </span>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state flex justify-center items-center py-12">
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
      <div v-else class="orders-list space-y-4 md:space-y-6">
        <!-- Order Card -->
        <div 
          v-for="order in filteredOrders" 
          :key="order.id"
          class="order-card rounded-2xl md:rounded-3xl p-4 md:p-6 border border-gray-200"
          style="background-color: rgba(255, 63, 213, 0.2);"
        >
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
            <!-- Left Section: Order Details -->
            <div class="lg:col-span-2 space-y-3 md:space-y-4">
              <!-- Order ID -->
              <div class="order-id mb-3 md:mb-4 flex flex-wrap items-center gap-2 md:gap-3">
                <p class="text-xs md:text-sm text-gray-600 font-comfortaa">
                  Order ID #{{ order.orderNumber }}
                </p>
                <span 
                  v-if="order.isGift" 
                  class="gift-badge px-2.5 md:px-3 py-0.5 md:py-1 bg-gradient-to-r from-pink-500 to-purple-500 text-white text-xs font-semibold rounded-full font-poppins flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 md:h-3 md:w-3" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                  </svg>
                  GIFT
                </span>
              </div>

              <!-- Order Summary -->
              <div class="order-summary">
                <h3 class="text-sm md:text-base font-semibold text-gray-900 font-comfortaa mb-2">
                  Order Summary
                </h3>
                <ul class="space-y-1 text-xs md:text-sm text-gray-600 font-comfortaa">
                  <li>• Product: {{ order.product.name }}</li>
                  <li>• Quantity: {{ order.quantity }}</li>
                  <li>• Price: ${{ order.price }}</li>
                  <li>• Shipping: {{ order.shippingMethod }}</li>
                  <li>• Total: ${{ order.total }}</li>
                </ul>
              </div>

              <!-- Shipping Information -->
              <div class="shipping-info">
                <h3 class="text-sm md:text-base font-semibold text-gray-900 font-comfortaa mb-2">
                  Shipping information
                </h3>
                <ul class="space-y-1 text-xs md:text-sm text-gray-600 font-comfortaa">
                  <li>• Name: {{ order.shippingName }}</li>
                  <li>• Address: {{ order.shippingAddress }}</li>
                  <li>• Phone: {{ order.shippingPhone }}</li>
                </ul>
              </div>

              <!-- Gift Message (if it's a gift) -->
              <div v-if="order.isGift && order.giftMessage" class="gift-message mt-3 md:mt-4 p-3 md:p-4 bg-pink-50 rounded-lg md:rounded-xl border border-pink-200">
                <h3 class="text-sm md:text-base font-semibold text-brand-pink font-comfortaa mb-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 mr-1.5 md:mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                  </svg>
                  Gift Message
                </h3>
                <p class="text-xs md:text-sm text-gray-700 font-comfortaa italic">
                  "{{ order.giftMessage }}"
                </p>
              </div>
            </div>

            <!-- Right Section: Product Card -->
            <div class="lg:col-span-1">
              <ProductCard 
                :product="order.product"
                :is-in-favorites="order.isFavorited"
                @navigate-to-product="handleNavigateToProduct"
              />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredOrders.length === 0" class="empty-state text-center py-8 md:py-12">
          <div class="flex flex-col items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 md:h-20 md:w-20 lg:h-24 lg:w-24 text-gray-300 mb-3 md:mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <h3 class="text-lg md:text-xl font-medium text-gray-900 font-comfortaa mb-2">
              No orders found
            </h3>
            <p class="text-sm md:text-base text-gray-500 font-comfortaa mb-4 md:mb-6">
              {{ searchQuery || dateFilter ? 'Try adjusting your filters' : "You haven't made any purchases yet" }}
            </p>
            <button 
              v-if="!searchQuery && !dateFilter"
              @click="router.push({ name: `Products-${i18nStore.locale}` })"
              class="btn-shop px-5 md:px-6 py-2.5 md:py-3 rounded-full text-white font-semibold font-poppins text-sm md:text-base transition-all duration-200 hover:opacity-90"
              style="background-color: #DA9DFF;">
              Start Shopping
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ProductCard from '@/components/products/ProductCard.vue'
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useOrderStore } from '@/stores/modules/orderStore'
import { useProfileStore } from '@/stores/modules/profileStore'

// Router and stores
const router = useRouter()
const i18nStore = useI18nStore()
const orderStore = useOrderStore()
const profileStore = useProfileStore()

// Local state
const searchQuery = ref('')
const dateFilter = ref('')

// Computed: Filtered orders from store
const filteredOrders = computed(() => {
  let filtered = [...orderStore.orders]
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(order => 
      order.order_number?.toLowerCase().includes(query) ||
      order.items?.some(item => 
        item.product_name?.toLowerCase().includes(query)
      )
    )
  }
  
  // Filter by date
  if (dateFilter.value) {
    const now = new Date()
    const filterDate = new Date()
    
    switch (dateFilter.value) {
      case 'last-week':
        filterDate.setDate(now.getDate() - 7)
        break
      case 'last-month':
        filterDate.setMonth(now.getMonth() - 1)
        break
      case 'last-3-months':
        filterDate.setMonth(now.getMonth() - 3)
        break
      case 'last-year':
        filterDate.setFullYear(now.getFullYear() - 1)
        break
    }
    
    filtered = filtered.filter(order => {
      const orderDate = new Date(order.created_at)
      return orderDate >= filterDate
    })
  }
  
  // Transform orders to component structure
  return filtered.map(order => {
    const firstItem = order.items?.[0] || {}
    
    // Check if it's a gift order
    const isGift = order.is_gift === true
    
    // Parse prices as integers (Colombian pesos don't use decimals)
    const itemPrice = Math.floor(parseFloat(firstItem.unit_price || firstItem.price || 0))
    const orderTotal = Math.floor(parseFloat(order.total || 0))
    const shipCost = Math.floor(parseFloat(order.shipping_cost || 0))
    
    return {
      id: order.id,
      orderNumber: order.order_number || order.id,
      quantity: firstItem.quantity || 1,
      price: itemPrice,
      shippingMethod: order.shipping_method || 'Standard (5-7 business days)',
      shippingCost: shipCost,
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
      giftMessage: order.gift_message || null,
      isFavorited: isProductInFavorites(firstItem.woocommerce_product_id || firstItem.product_id),
      product: {
        id: firstItem.woocommerce_product_id || firstItem.product_id,
        name: firstItem.product_name || firstItem.name || 'Product',
        short_description: `<p>${firstItem.product_description || firstItem.description || ''}</p><p class="price">$${itemPrice}</p>`,
        stock_status: firstItem.stock_status || 'instock',
        // Use image_url from backend
        images: firstItem.image_url ? [{ src: firstItem.image_url }] : (firstItem.product_image ? [{ src: firstItem.product_image }] : [])
      }
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
  router.push({ name: `ProductDetails-${i18nStore.locale}`, params: { id: productId } })
}

const loadPurchaseHistory = async () => {
  const result = await orderStore.fetchOrders()
  
  if (result.success) {
    console.log('✅ Purchase history loaded:', orderStore.orders.length, 'orders')
    
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

// Watch for filter changes (local filtering, no need to refetch)
watch([searchQuery, dateFilter], () => {
  // Filters are applied through computed property
})

// Lifecycle hooks
onMounted(async () => {
  // Load purchase history on component mount
  await loadPurchaseHistory()
  
  // Load user favorites if not already loaded
  if (profileStore.favoriteProducts.length === 0) {
    await profileStore.fetchFavoriteProducts()
  }
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

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
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
