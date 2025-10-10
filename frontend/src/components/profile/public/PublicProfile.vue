<template>
  <div class="public-profile">
    <!-- Header with cover image or gradient background -->
    <div class="profile-header">
      <div 
        class="header-gradient"
        :class="{ 'has-cover': profile.coverImage }"
        :style="profile.coverImage ? { backgroundImage: `url(${profile.coverImage})` } : {}"
      ></div>
      
      <!-- Avatar -->
      <div class="avatar-container">
        <img 
          :src="profile.avatar" 
          :alt="profile.name"
          class="avatar-image"
        />
      </div>
    </div>

    <!-- Profile Content -->
    <div class="profile-content">
      <!-- Username -->
      <div class="profile-info">
        <h1 class="profile-username">{{ profile.username }}</h1>
      </div>

      <!-- Biography -->
      <div class="biography-section">
        <h3 class="section-title">{{ $t('diaries.publicProfile.biography') }}</h3>
        <div class="biography-text">
          {{ profile.biography }}
        </div>
      </div>

      <!-- Three Column Grid: Links, State, Notes -->
      <div class="three-column-grid">
        <!-- My Links -->
        <div class="links-section">
          <h3 class="section-title">{{ $t('diaries.publicProfile.myLinks') }}</h3>
          <div class="links-buttons">
            <button 
              v-for="(link, index) in profile.links" 
              :key="index"
              class="link-button"
              :style="{ backgroundColor: link.color }"
              @click="link.url && window.open(link.url, '_blank')"
            >
              {{ link.label }}
            </button>
          </div>
        </div>

        <!-- My State -->
        <div class="info-card">
          <h3 class="section-title">{{ $t('diaries.publicProfile.myState') }}</h3>
          <p class="info-text">{{ profile.state }}</p>
        </div>

        <!-- Notes -->
        <div class="info-card">
          <h3 class="section-title">{{ $t('diaries.publicProfile.notes') }}</h3>
          <p class="info-text">{{ profile.notes }}</p>
        </div>
      </div>

      <!-- Gallery -->
      <div class="gallery-section" v-if="profile.gallery && profile.gallery.length > 0">
        <h3 class="section-title">{{ $t('diaries.publicProfile.gallery') }}</h3>
        <div class="gallery-grid">
          <div 
            v-for="(image, index) in profile.gallery" 
            :key="index"
            class="gallery-item"
          >
            <img 
              :src="image" 
              :alt="`${$t('diaries.publicProfile.galleryImageAlt')} ${index + 1}`"
              class="gallery-image"
            />
          </div>
        </div>
      </div>

      <!-- Wishlists -->
      <div class="wishlists-section" v-if="profile.wishlists && profile.wishlists.length > 0">
        <h3 class="section-title">{{ $t('diaries.publicProfile.wishlists') }}</h3>
        <div class="space-y-4">
          <div 
            v-for="wishlist in profile.wishlists" 
            :key="wishlist.id"
            class="wishlist-card border-2 border-gray-900 rounded-2xl overflow-hidden"
          >
            <div class="p-6">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ wishlist.name }}</h3>
                  <p class="text-sm text-gray-600 mb-2">{{ wishlist.description || $t('diaries.publicProfile.noDescription') }}</p>
                  <p class="text-xs text-gray-500">
                    {{ wishlist.total_items }} {{ $t('diaries.publicProfile.wishlistItems') }} · ${{ formatPrice(wishlist.total_value) }}
                  </p>
                </div>
                <div class="flex items-center gap-2 ml-4">
                  <button 
                    @click="toggleWishlist(wishlist.id)" 
                    class="p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    <svg 
                      class="w-5 h-5 text-gray-600 transition-transform" 
                      :class="{ 'rotate-180': expandedWishlists.includes(wishlist.id) }" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Products -->
            <div v-if="expandedWishlists.includes(wishlist.id)" class="px-6 pb-6">
              <!-- Products grid -->
              <div v-if="wishlist.items && wishlist.items.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-for="item in wishlist.items" :key="item.id" class="relative">
                  <!-- Product Card -->
                  <ProductCard
                    v-if="item.product_info"
                    :product="formatProductForCard(item)"
                    @navigate-to-product="navigateToProduct"
                    @add-to-cart="handleAddToCart"
                  />
                  
                  <!-- Notes -->
                  <div v-if="item.notes" class="mt-2">
                    <p class="text-xs text-gray-600 italic">💭 {{ item.notes }}</p>
                  </div>

                  <!-- Priority badge -->
                  <div v-if="item.priority" class="mt-1">
                    <span 
                      class="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full"
                      :class="{
                        'bg-red-100 text-red-800': item.priority === 'high',
                        'bg-yellow-100 text-yellow-800': item.priority === 'medium',
                        'bg-blue-100 text-blue-800': item.priority === 'low'
                      }"
                    >
                      {{ item.priority === 'high' ? '⭐ Alta' : item.priority === 'medium' ? '🔸 Media' : '🔹 Baja' }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Empty state -->
              <div v-else class="text-sm text-gray-500 text-center py-8">
                <svg class="w-16 h-16 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p>{{ $t('diaries.publicProfile.noProductsYet') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import ProductCard from '@/components/products/ProductCard.vue'

const router = useRouter()
const i18nStore = useI18nStore()

// State
const expandedWishlists = ref([])

// Props
const props = defineProps({
  profileData: {
    type: Object,
    default: () => ({
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400',
      coverImage: null, // Cover image URL
      name: 'Mary Jackson',
      username: '@username',
      biography: `Hi! I'm [Your Name], a friendly, upbeat webcam model who loves good conversation, cozy vibes, and a touch of playful energy. On my shows you'll find smiles, laughter, and a welcoming space where we can relax, chat, and enjoy the moment together. I'm into [interests: gaming/fitness/cosplay/music], so don't be shy about asking questions or sharing what you love too.

I value respect and positive energy. Please be polite, keep requests within platform rules, and remember I don't do meetups—everything stays online and between consenting adults (18+). Tips and requests help me create more content and upgrade my setup, and I'm always grateful for your support.

Schedule: [Days/Times] ([Timezone]).
What to expect: friendly chats, playful banter, themed outfits, and interactive goals.
Support: follows, tips, and kind words mean the world—thank you!
Hit follow, turn on notifications, and say hi when you join. Let's make great memories together. 💫`,
      links: [
        { label: 'Instagram', color: '#C77DFF' },
        { label: 'Facebook', color: '#C77DFF' },
        { label: 'Stream', color: '#C77DFF' }
      ],
      state: 'Sweet smiles, playful vibes—come say hi ✨',
      notes: `Welcome to my room! This is a respectful, 18+ space. I don't do meetups or off-platform chats, and I follow site rules. Tips and kind words keep the show going and help upgrade my setup. Custom requests? Ask first and be polite. Schedule: [Days/Times, Timezone]. Thanks for being sweet and supportive! 💫`,
      gallery: [
        'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400',
        'https://images.unsplash.com/photo-1488716820095-cbe80883c496?w=400',
        'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400',
        'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400',
        'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400',
        'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400',
        'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400',
        'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
        'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400'
      ],
      wishlists: [],
      items: []
    })
  }
})

// Computed para asegurar que siempre tengamos datos
const profile = computed(() => props.profileData || {})

// Helper functions
const formatPrice = (value) => {
  if (!value) return '0.00'
  return Number(value).toLocaleString('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

// Toggle wishlist expansion
const toggleWishlist = (id) => {
  const index = expandedWishlists.value.indexOf(id)
  if (index > -1) {
    expandedWishlists.value.splice(index, 1)
  } else {
    expandedWishlists.value.push(id)
  }
}

// Format product data for ProductCard component
const formatProductForCard = (item) => {
  return {
    id: item.woocommerce_product_id,
    name: item.product_name,
    price: item.product_price,
    images: item.product_info?.images || [{ src: item.product_image }],
    stock_status: item.product_info?.stock_status || 'instock',
    ...item.product_info
  }
}

// Navigate to product detail page
const navigateToProduct = (productId) => {
  router.push({ name: `ProductDetail-${i18nStore.locale}`, params: { id: productId } })
}

// Handle add to cart
const handleAddToCart = (product) => {
  console.log('Product added to cart from wishlist:', product)
  // El ProductCard ya maneja esto internamente
}
</script>

<style scoped>
/* Container */
.public-profile {
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  height: fit-content;
}

/* Header Section */
.profile-header {
  position: relative;
  width: 100%;
  height: 200px;
}

.header-gradient {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, 
    #60a5fa 0%,    /* blue-400 */
    #a78bfa 25%,   /* violet-400 */
    #f472b6 50%,   /* pink-400 */
    #fb7185 75%,   /* rose-400 */
    #ef4444 100%   /* red-500 */
  );
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.header-gradient.has-cover {
  /* Si tiene cover image, el background-image se aplicará desde el template */
}

/* Avatar */
.avatar-container {
  position: absolute;
  bottom: -40px;
  left: 32px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 4px solid white;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Profile Content */
.profile-content {
  padding: 56px 32px 32px 32px;
}

/* Profile Info */
.profile-info {
  margin-bottom: 24px;
}

.profile-username {
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 700;
  color: #11181E;
  margin: 0;
}

/* Section Titles */
.section-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #11181E;
  margin: 0 0 12px 0;
}

/* Biography Section */
.biography-section {
  margin-bottom: 24px;
}

.biography-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #475569;
  white-space: pre-line;
}

/* Three Column Grid: Links, State, Notes */
.three-column-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

/* Links Section */
.links-section {
  display: flex;
  flex-direction: column;
}

.links-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-button {
  width: 100%;
  padding: 12px 24px;
  border: none;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.link-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.link-button:active {
  transform: translateY(0);
}

/* Info Card */
.info-card {
  display: flex;
  flex-direction: column;
}

.info-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #475569;
  margin: 0;
}

/* Gallery Section */
.gallery-section {
  margin-bottom: 0;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.gallery-item {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  background: #f1f5f9;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover .gallery-image {
  transform: scale(1.05);
}

/* Wishlists Section */
.wishlists-section {
  margin-top: 24px;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.wishlist-card {
  background: rgba(255, 63, 213, 0.2);
}

/* Responsive adjustments */
@media (max-width: 1024px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .profile-content {
    padding: 56px 20px 20px 20px;
  }

  .avatar-container {
    left: 20px;
    width: 80px;
    height: 80px;
  }

  .three-column-grid {
    grid-template-columns: 1fr;
  }

  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>

