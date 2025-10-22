<template>
  <div class="public-profile">
    <!-- Header with cover image or gradient background -->
    <div class="profile-header">
      <div 
        class="header-gradient"
        :class="{ 'has-cover': profile.coverImage }"
        :style="profile.coverImage ? { backgroundImage: `url(${profile.coverImage})` } : {}"
      ></div>
      
      <!-- Share Button -->
      <button 
        class="share-button" 
        @click="copyProfileLink"
        :class="{ 'copied': showCopiedMessage }"
      >
        <svg v-if="!showCopiedMessage" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="18" cy="5" r="3"></circle>
          <circle cx="6" cy="12" r="3"></circle>
          <circle cx="18" cy="19" r="3"></circle>
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span class="share-text">{{ showCopiedMessage ? $t('diaries.publicProfile.linkCopied') : $t('diaries.publicProfile.share') }}</span>
      </button>
      
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
              <!-- Header con título, botones y flecha en la misma línea -->
              <div class="flex items-center justify-between gap-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900 flex-shrink-0">{{ wishlist.name }}</h3>
                
                <div class="flex items-center gap-2 ml-auto">
                  <!-- Wishlist Actions -->
                  <button 
                    @click="copyWishlistLink(wishlist)"
                    class="wishlist-action-btn copy-btn"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                    </svg>
                    Copy wishlist link
                  </button>
                  <button 
                    @click="buyWishlist(wishlist)"
                    class="wishlist-action-btn buy-btn"
                  >
                    Buy my wishlist
                  </button>
                  
                  <!-- Toggle button -->
                  <button 
                    @click="toggleWishlist(wishlist.id)" 
                    class="p-2 hover:bg-gray-100 rounded-full transition-colors flex-shrink-0"
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
              
              <!-- Description y detalles -->
              <div>
                <p class="text-sm text-gray-600 mb-2">{{ wishlist.description || $t('diaries.publicProfile.noDescription') }}</p>
                <p class="text-xs text-gray-500">
                  {{ wishlist.total_items }} {{ $t('diaries.publicProfile.wishlistItems') }} · ${{ formatPrice(wishlist.total_value) }}
                </p>
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
                    :gift-mode="true"
                    @navigate-to-product="navigateToProduct"
                    @add-to-cart="handleAddToCart"
                  />
                  
                  <!-- Notes -->
                  <div v-if="item.notes" class="mt-2">
                    <p class="text-xs text-gray-600 italic">💭 {{ item.notes }}</p>
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
import { useRouter, useRoute } from 'vue-router'
import { useI18nStore } from '@/stores/modules/i18nStore'
import ProductCard from '@/components/products/ProductCard.vue'

const router = useRouter()
const route = useRoute()
const i18nStore = useI18nStore()

// State
const expandedWishlists = ref([])
const showCopiedMessage = ref(false)

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

// Copy profile link to clipboard
const copyProfileLink = async () => {
  try {
    // Obtener la URL completa actual
    const fullUrl = window.location.href
    
    // Copiar al portapapeles
    await navigator.clipboard.writeText(fullUrl)
    
    // Mostrar mensaje de éxito
    showCopiedMessage.value = true
    console.log('✅ Link copiado al portapapeles:', fullUrl)
    
    // Ocultar mensaje después de 2 segundos
    setTimeout(() => {
      showCopiedMessage.value = false
    }, 2000)
  } catch (error) {
    console.error('❌ Error copiando link:', error)
    // Fallback para navegadores antiguos
    try {
      const textArea = document.createElement('textarea')
      textArea.value = window.location.href
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      
      showCopiedMessage.value = true
      setTimeout(() => {
        showCopiedMessage.value = false
      }, 2000)
    } catch (fallbackError) {
      console.error('❌ Fallback también falló:', fallbackError)
    }
  }
}

// Buy entire wishlist - Navigate to checkout with wishlist data
const buyWishlist = (wishlist) => {
  const username = profile.value.username?.replace('@', '') || route.params.username
  
  router.push({
    name: `Checkout-${i18nStore.locale}`,
    query: {
      giftMode: 'true',
      username: username,
      wishlistId: wishlist.id,
      wishlistName: wishlist.name
    }
  })
  
  console.log('🎁 Navigating to checkout for wishlist:', wishlist.name)
}

// Copy wishlist link to clipboard
const copyWishlistLink = async (wishlist) => {
  try {
    // Use public_url from backend if available, otherwise construct it
    const wishlistUrl = wishlist.public_url || `${window.location.origin}${wishlist.shareable_path}`
    
    await navigator.clipboard.writeText(wishlistUrl)
    console.log('✅ Wishlist link copied:', wishlistUrl)
    
    // Optional: Show toast notification
    alert('Wishlist link copied to clipboard!')
  } catch (error) {
    console.error('❌ Error copying wishlist link:', error)
  }
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

/* Header Section - Mobile First */
.profile-header {
  position: relative;
  width: 100%;
  height: 150px;
}

@media (min-width: 640px) {
  .profile-header {
    height: 180px;
  }
}

@media (min-width: 1024px) {
  .profile-header {
    height: 200px;
  }
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

/* Avatar - Mobile First */
.avatar-container {
  position: absolute;
  bottom: -30px;
  left: 16px;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 3px solid white;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@media (min-width: 640px) {
  .avatar-container {
    bottom: -35px;
    left: 24px;
    width: 85px;
    height: 85px;
  }
}

@media (min-width: 1024px) {
  .avatar-container {
    bottom: -40px;
    left: 32px;
    width: 100px;
    height: 100px;
    border: 4px solid white;
  }
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Share Button */
.share-button {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  color: #11181E;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.share-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.share-button:active {
  transform: translateY(0);
}

.share-button.copied {
  background: rgba(218, 157, 255, 0.95);
  color: white;
  border-color: rgba(218, 157, 255, 0.3);
}

.share-button svg {
  flex-shrink: 0;
}

.share-text {
  white-space: nowrap;
}

/* Profile Content - Mobile First */
.profile-content {
  padding: 44px 16px 20px 16px;
}

@media (min-width: 640px) {
  .profile-content {
    padding: 50px 24px 24px 24px;
  }
}

@media (min-width: 1024px) {
  .profile-content {
    padding: 56px 32px 32px 32px;
  }
}

/* Profile Info - Mobile First */
.profile-info {
  margin-bottom: 16px;
}

@media (min-width: 640px) {
  .profile-info {
    margin-bottom: 20px;
  }
}

@media (min-width: 1024px) {
  .profile-info {
    margin-bottom: 24px;
  }
}

.profile-username {
  font-family: 'Comfortaa', cursive;
  font-size: 1.125rem;
  font-weight: 700;
  color: #11181E;
  margin: 0;
}

@media (min-width: 640px) {
  .profile-username {
    font-size: 1.25rem;
  }
}

@media (min-width: 1024px) {
  .profile-username {
    font-size: 1.5rem;
  }
}

/* Section Titles - Mobile First */
.section-title {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: #11181E;
  margin: 0 0 10px 0;
}

@media (min-width: 640px) {
  .section-title {
    font-size: 0.9375rem;
    margin: 0 0 12px 0;
  }
}

@media (min-width: 1024px) {
  .section-title {
    font-size: 1rem;
  }
}

/* Biography Section - Mobile First */
.biography-section {
  margin-bottom: 16px;
}

@media (min-width: 640px) {
  .biography-section {
    margin-bottom: 20px;
  }
}

@media (min-width: 1024px) {
  .biography-section {
    margin-bottom: 24px;
  }
}

.biography-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: #475569;
  white-space: pre-line;
}

@media (min-width: 640px) {
  .biography-text {
    font-size: 0.875rem;
    line-height: 1.6;
  }
}

/* Three Column Grid - Mobile First */
.three-column-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

@media (min-width: 768px) {
  .three-column-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    margin-bottom: 20px;
  }
}

@media (min-width: 1024px) {
  .three-column-grid {
    margin-bottom: 24px;
  }
}

/* Links Section */
.links-section {
  display: flex;
  flex-direction: column;
}

.links-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

@media (min-width: 640px) {
  .links-buttons {
    gap: 12px;
  }
}

.link-button {
  width: 100%;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (min-width: 640px) {
  .link-button {
    padding: 12px 24px;
    border-radius: 24px;
    font-size: 0.875rem;
  }
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
  font-size: 0.8125rem;
  line-height: 1.5;
  color: #475569;
  margin: 0;
}

@media (min-width: 640px) {
  .info-text {
    font-size: 0.875rem;
    line-height: 1.6;
  }
}

/* Gallery Section - Mobile First */
.gallery-section {
  margin-bottom: 0;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

@media (min-width: 640px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 768px) {
  .gallery-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1024px) {
  .gallery-grid {
    grid-template-columns: repeat(5, 1fr);
  }
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

/* Wishlists Section - Mobile First */
.wishlists-section {
  margin-top: 16px;
}

@media (min-width: 640px) {
  .wishlists-section {
    margin-top: 20px;
  }
}

@media (min-width: 1024px) {
  .wishlists-section {
    margin-top: 24px;
  }
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.wishlist-card {
  background: rgba(255, 63, 213, 0.2);
}

/* Wishlist Action Buttons */
.wishlist-action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.wishlist-action-btn.copy-btn {
  background: rgba(199, 125, 255, 0.2);
  color: #9333ea;
  border: 1px solid rgba(199, 125, 255, 0.3);
}

.wishlist-action-btn.copy-btn:hover {
  background: rgba(199, 125, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(199, 125, 255, 0.3);
}

.wishlist-action-btn.buy-btn {
  background: #C77DFF;
  color: white;
  border: 1px solid #C77DFF;
}

.wishlist-action-btn.buy-btn:hover {
  background: #a855f7;
  border-color: #a855f7;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(199, 125, 255, 0.4);
}

.wishlist-action-btn:active {
  transform: translateY(0);
}

.wishlist-action-btn svg {
  flex-shrink: 0;
}

/* Share Button Responsive */
@media (max-width: 480px) {
  .share-button .share-text {
    display: none;
  }
  
  .share-button {
    padding: 10px;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    justify-content: center;
  }
  
  .wishlist-action-btn {
    font-size: 0.8125rem;
    padding: 8px 16px;
  }
}
</style>

