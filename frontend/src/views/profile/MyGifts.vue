<template>
  <div class="my-gifts">
    <div class="px-4 md:px-6 py-6 md:py-8 lg:px-8 max-w-7xl mx-auto">
      <!-- Header -->
      <h1 class="text-2xl md:text-3xl font-medium text-brand-dark font-comfortaa mb-6 md:mb-8">
        My Gifts
      </h1>

      <!-- Tabs for Sent/Received -->
      <div class="tabs-container mb-6 md:mb-8">
        <div class="flex gap-1 md:gap-2 border-b border-brand-pink-light overflow-x-auto">
          <button
            @click="activeTab = 'received'"
            :class="[
              'tab-btn px-4 md:px-6 py-2.5 md:py-3 font-semibold font-poppins text-xs md:text-sm transition-all duration-200 relative whitespace-nowrap',
              activeTab === 'received' 
                ? 'text-brand-pink' 
                : 'text-brand-blue-medium hover:text-brand-pink-dark'
            ]"
          >
            <span class="flex items-center gap-1.5 md:gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
              </svg>
              <span class="hidden sm:inline">Gifts Received</span>
              <span class="sm:hidden">Received</span>
            </span>
            <span 
              v-if="activeTab === 'received'" 
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-pink"
            ></span>
          </button>
          
          <button
            @click="activeTab = 'sent'"
            :class="[
              'tab-btn px-4 md:px-6 py-2.5 md:py-3 font-semibold font-poppins text-xs md:text-sm transition-all duration-200 relative whitespace-nowrap',
              activeTab === 'sent' 
                ? 'text-brand-pink' 
                : 'text-brand-blue-medium hover:text-brand-pink-dark'
            ]"
          >
            <span class="flex items-center gap-1.5 md:gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
              </svg>
              <span class="hidden sm:inline">Gifts Sent</span>
              <span class="sm:hidden">Sent</span>
            </span>
            <span 
              v-if="activeTab === 'sent'" 
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-pink"
            ></span>
          </button>
        </div>
      </div>

      <!-- Filter Section -->
      <div class="filters-section mb-4 md:mb-6">
        <h2 class="text-base md:text-lg font-medium text-brand-dark font-comfortaa mb-3 md:mb-4">
          Filter by
        </h2>
        <div class="filters-row flex flex-col sm:flex-row gap-3 md:gap-4 items-stretch sm:items-center">
          <!-- Search Input -->
          <div class="search-input relative flex-1 sm:max-w-xs">
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-brand-pink-medium">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input 
              type="text" 
              placeholder="Search"
              v-model="searchQuery"
              class="w-full pl-9 md:pl-10 pr-4 py-2 text-sm md:text-base border border-brand-pink-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-pink focus:border-transparent font-comfortaa text-brand-dark"
            />
          </div>

          <!-- Date Filter -->
          <div class="date-filter relative w-full sm:w-auto">
            <select 
              v-model="dateFilter"
              class="appearance-none w-full px-4 py-2 pr-10 text-sm md:text-base border border-brand-pink-light rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-pink focus:border-transparent font-comfortaa cursor-pointer bg-white text-brand-dark"
            >
              <option value="">Date</option>
              <option value="last-week">Last Week</option>
              <option value="last-month">Last Month</option>
              <option value="last-3-months">Last 3 Months</option>
              <option value="last-year">Last Year</option>
            </select>
            <span class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none text-brand-pink-medium">
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

      <!-- Gifts List -->
      <div v-else class="gifts-list space-y-4 md:space-y-6">
        <!-- Gift Card -->
        <div
          v-for="gift in transformedGifts"
          :key="gift.id"
          class="gift-card rounded-2xl md:rounded-3xl p-4 md:p-6 border border-brand-pink-light bg-brand-pink-lighter"
        >
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
            <!-- Left Section: Gift Details -->
            <div class="lg:col-span-2 space-y-3 md:space-y-4">
              <!-- Order ID with Gift Badge -->
              <div class="order-id mb-3 md:mb-4 flex flex-wrap items-center gap-2 md:gap-3">
                <p class="text-xs md:text-sm text-brand-blue-medium font-comfortaa">
                  Order ID #{{ gift.orderNumber }}
                </p>
                <span
                  class="gift-badge px-2.5 md:px-3 py-0.5 md:py-1 bg-gradient-to-r from-brand-pink to-brand-purple-light text-white text-xs font-semibold rounded-full font-poppins flex items-center gap-1">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 md:h-3 md:w-3" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" />
                  </svg>
                  GIFT
                </span>
              </div>

              <!-- Gift Info -->
              <div class="gift-info">
                <h3 class="text-sm md:text-base font-semibold text-brand-dark font-comfortaa mb-2">
                  Gift Information
                </h3>
                <ul class="space-y-1 text-xs md:text-sm text-brand-blue-medium font-comfortaa">
                  <li v-if="activeTab === 'received'">• From: <span class="font-semibold text-brand-pink">{{ gift.sender }}</span></li>
                  <li v-if="activeTab === 'sent'">• To: <span class="font-semibold text-brand-pink">{{ gift.receiver }}</span></li>
                  <li>• Product: {{ gift.product.name }}</li>
                  <li>• Quantity: {{ gift.quantity }}</li>
                  <li>• Value: ${{ gift.value }}</li>
                  <li>• Status: <span class="capitalize">{{ gift.status }}</span></li>
                </ul>
              </div>

              <!-- Gift Message -->
              <div v-if="gift.message" class="gift-message p-3 md:p-4 bg-brand-pink-lighter rounded-lg md:rounded-xl border border-brand-pink-light">
                <h3 class="text-sm md:text-base font-semibold text-brand-pink font-comfortaa mb-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 mr-1.5 md:mr-2" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clip-rule="evenodd" />
                  </svg>
                  Message
                </h3>
                <p class="text-xs md:text-sm text-brand-dark font-comfortaa italic">
                  "{{ gift.message }}"
                </p>
              </div>

              <!-- Shipping Information (only for sent gifts) -->
              <div v-if="activeTab === 'sent'" class="shipping-info">
                <h3 class="text-sm md:text-base font-semibold text-brand-dark font-comfortaa mb-2">
                  Shipping information
                </h3>
                <ul class="space-y-1 text-xs md:text-sm text-brand-blue-medium font-comfortaa">
                  <li>• Address: {{ gift.shippingAddress }}</li>
                  <li>• City: {{ gift.shippingCity }}</li>
                  <li>• Date: {{ formatDate(gift.createdAt) }}</li>
                </ul>
              </div>

              <!-- Privacy Note (for received gifts) -->
              <div v-if="activeTab === 'received'" class="privacy-note p-3 bg-brand-pink-lighter rounded-lg border border-brand-purple-light">
                <p class="text-xs text-brand-purple-light font-comfortaa flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                  Shipping details hidden for privacy
                </p>
              </div>
            </div>

            <!-- Right Section: Product Card -->
            <div class="lg:col-span-1">
              <ProductCard
                :product="gift.product"
                :is-in-favorites="false"
                @navigate-to-product="handleNavigateToProduct"
              />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="transformedGifts.length === 0 && !isLoading" class="empty-state text-center py-12">
          <div class="flex flex-col items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-brand-pink-light mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7" />
            </svg>
            <h3 class="text-xl font-medium text-brand-dark font-comfortaa mb-2">
              No gifts {{ activeTab === 'received' ? 'received' : 'sent' }} yet
            </h3>
            <p class="text-brand-blue-medium font-comfortaa mb-6">
              {{ activeTab === 'received'
                ? 'When someone sends you a gift, it will appear here'
                : 'Send your first gift to someone special'
              }}
            </p>
            <button
              v-if="activeTab === 'sent'"
              @click="router.push({ name: `Products-${i18nStore.locale}` })"
              class="btn-shop px-6 py-3 rounded-full text-white font-semibold font-poppins transition-all duration-200 hover:opacity-90 bg-brand-purple-light">
              Send a Gift
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
import { useI18nStore } from '@/stores/modules/i18nStore'
import { useOrderStore } from '@/stores/modules/orderStore'
import { useAuthStore } from '@/stores/modules/authStore'
import { get_request } from '@/services/request_http.js'
import ProductCard from '@/components/products/ProductCard.vue'

// Router and stores
const router = useRouter()
const i18nStore = useI18nStore()
const orderStore = useOrderStore()
const authStore = useAuthStore()

// Local state
const activeTab = ref('received') // 'received' or 'sent'
const searchQuery = ref('')
const dateFilter = ref('')

// Gifts data from API
const gifts = ref([])

// Loading state
const isLoading = ref(false)

// Computed: Filter gifts based on active tab and search
const filteredGifts = computed(() => {
  let filtered = [...gifts.value]

  // Filter by tab (received/sent)
  filtered = filtered.filter(gift => {
    if (activeTab.value === 'received') {
      return gift.receiver_username === authStore.username
    } else {
      return gift.sender_username === authStore.username
    }
  })

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(gift =>
      gift.orderNumber?.toLowerCase().includes(query) ||
      gift.product?.name?.toLowerCase().includes(query) ||
      gift.message?.toLowerCase().includes(query)
    )
  }

  // Filter by date (implement date filtering logic here)
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

    filtered = filtered.filter(gift => {
      const giftDate = new Date(gift.createdAt)
      return giftDate >= filterDate
    })
  }

  return filtered
})

// Computed: Transform gifts data for display
const transformedGifts = computed(() => {
  return filteredGifts.value.map(gift => {
    const firstItem = gift.items?.[0] || {}

    // Check if it's a gift order
    const isGift = gift.is_gift === true

    return {
      id: gift.id,
      orderNumber: gift.order_number || gift.id,
      quantity: firstItem.quantity || 1,
      value: Math.floor(parseFloat(firstItem.unit_price || firstItem.price || 0)),
      status: gift.status,
      // For gifts, sender/receiver info might be hidden
      sender: gift.sender_username || 'Anonymous',
      receiver: gift.receiver_username || 'Anonymous',
      // Gift information
      message: gift.gift_message || null,
      shippingAddress: isGift ? 'Dirección de envío privada (regalo)' : (gift.shipping_address || 'N/A'),
      shippingCity: gift.shipping_city || 'N/A',
      createdAt: gift.created_at,
      // Product information
      product: {
        id: firstItem.woocommerce_product_id || firstItem.product_id,
        name: firstItem.product_name || firstItem.name || 'Product',
        short_description: `<p>${firstItem.product_description || firstItem.description || ''}</p><p class="price">$${Math.floor(parseFloat(firstItem.unit_price || firstItem.price || 0))}</p>`,
        stock_status: firstItem.stock_status || 'instock',
        images: firstItem.image_url ? [{ src: firstItem.image_url }] : (firstItem.product_image ? [{ src: firstItem.product_image }] : [])
      }
    }
  })
})

// Methods
const handleNavigateToProduct = (productId) => {
  router.push({ name: `ProductDetails-${i18nStore.locale}`, params: { id: productId } })
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadGifts = async () => {
  isLoading.value = true

  try {
    console.log('🎁 [MyGifts] Loading gifts for tab:', activeTab.value)
    console.log('🎁 [MyGifts] User authenticated:', authStore.isLoggedIn)
    console.log('🎁 [MyGifts] Access token exists:', !!localStorage.getItem('access_token'))

    // Check authentication before making request
    if (!authStore.isLoggedIn) {
      console.log('🎁 [MyGifts] User not authenticated, redirecting to login')
      router.push({ name: `Login-${i18nStore.locale}` })
      return
    }

    // Use the authenticated request service
    const response = await get_request(`orders/gifts/?type=${activeTab.value}`)

    if (response.data) {
      // API returns array directly, not wrapped in 'orders' property
      gifts.value = Array.isArray(response.data) ? response.data : (response.data.orders || [])
      console.log('🎁 [MyGifts] Gifts loaded:', gifts.value.length, 'gifts')
      console.log('🎁 [MyGifts] Gifts data sample:', gifts.value[0] || 'No gifts')
    } else {
      console.error('🎁 [MyGifts] No data in response')
      gifts.value = []
    }
  } catch (error) {
    console.error('🎁 [MyGifts] Error loading gifts:', error)
    console.error('🎁 [MyGifts] Error details:', error.response?.data || error.message)

    // If unauthorized, redirect to login
    if (error.response?.status === 401) {
      console.log('🎁 [MyGifts] Unauthorized - token may be invalid or expired')
      // Clear invalid tokens
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push({ name: `Login-${i18nStore.locale}` })
      return
    }

    gifts.value = []
  } finally {
    isLoading.value = false
  }
}

// Watch for tab changes to reload data
watch(activeTab, () => {
  console.log('🎁 [MyGifts] Tab changed to:', activeTab.value)

  if (authStore.isLoggedIn) {
    loadGifts()
  } else {
    console.log('🎁 [MyGifts] User not authenticated, redirecting to login')
    router.push({ name: `Login-${i18nStore.locale}` })
  }
})

// Debug function to check authentication status
const debugAuthStatus = () => {
  console.log('🔍 [MyGifts] Authentication Debug Info:')
  console.log('  - isLoggedIn:', authStore.isLoggedIn)
  console.log('  - hasToken:', !!localStorage.getItem('access_token'))
  console.log('  - hasRefreshToken:', !!localStorage.getItem('refresh_token'))
  console.log('  - user:', authStore.user)
  console.log('  - token value:', localStorage.getItem('access_token') ? '[TOKEN EXISTS]' : '[NO TOKEN]')
  console.log('  - Current route:', router.currentRoute.value.name)
  console.log('  - Current tab:', activeTab.value)
}

// Lifecycle hooks
onMounted(async () => {
  // Initialize auth state first
  authStore.initializeAuth()

  console.log('🎁 [MyGifts] Component mounted')

  // Debug authentication status
  debugAuthStatus()

  // Check if user is authenticated before loading gifts
  if (authStore.isLoggedIn) {
    console.log('🎁 [MyGifts] User authenticated, loading gifts...')
    await loadGifts()
  } else {
    console.log('🎁 [MyGifts] User not authenticated, redirecting to login')
    router.push({ name: `Login-${i18nStore.locale}` })
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

.gift-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.gift-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

/* Custom select arrow */
select {
  background-image: none;
}

/* Gift badge animation */
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

/* Tab button */
.tab-btn {
  position: relative;
}

.tab-btn:hover {
  background-color: rgba(250, 243, 243, 0.5); /* brand-pink-lighter with opacity */
}

/* Action buttons */
.btn-shop {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-shop:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(218, 157, 255, 0.5); /* brand-purple-light */
}

.btn-shop:active {
  transform: translateY(0);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .gift-card .grid {
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

  .tabs-container .flex {
    overflow-x: auto;
  }
}
</style>

