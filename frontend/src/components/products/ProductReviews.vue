<template>
  <section class="product-reviews-section">
    <div class="reviews-container">
      
      <!-- Rating & Reviews Section -->
          
          <!-- Reviews Header -->
          <div class="reviews-header">
            <h2 class="reviews-title">
              {{ $t('productReviews.title') }} <span class="reviews-count">({{ reviewStore.getTotalReviews }})</span>
            </h2>
            
            <div class="reviews-actions">
              <!-- Latest Dropdown -->
              <button class="latest-button">
                {{ $t('productReviews.latest') }}
                <svg class="dropdown-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              <!-- Write a Review Button -->
              <button class="write-review-button">
                {{ $t('productReviews.writeReview') }}
              </button>
            </div>
          </div>
          
          <!-- Loading State -->
          <div v-if="reviewStore.isLoadingReviews" class="loading-state">
            <div class="loading-spinner"></div>
            <p class="loading-text">{{ $t('productReviews.loading') }}</p>
          </div>
          
          <!-- Error State -->
          <div v-else-if="reviewStore.reviewsError" class="error-state">
            <p class="error-text">{{ reviewStore.reviewsError }}</p>
            <button @click="loadReviews" class="retry-button">{{ $t('productReviews.retry') }}</button>
          </div>
          
          <!-- No Reviews State -->
          <div v-else-if="reviewStore.getTotalReviews === 0" class="empty-state">
            <p class="empty-text">{{ $t('productReviews.noReviews') }}</p>
          </div>
          
          <!-- Reviews Grid -->
          <div v-else class="reviews-grid">
            
            <!-- Dynamic Review Cards -->
            <div 
              v-for="review in reviewStore.getProductReviews" 
              :key="review.id"
              class="review-card"
              :class="{ 'highlighted': review.is_user_review }"
            >
              <div class="review-header">
                <div class="review-stars">
                  <span 
                    v-for="star in 5" 
                    :key="star"
                    class="star"
                    :class="{ 'filled': star <= review.rating }"
                  >
                    ★
                  </span>
                </div>
                <button 
                  v-if="review.is_user_review"
                  class="review-menu-button"
                  @click="handleReviewMenu(review.id)"
                >
                  <span>⋯</span>
                </button>
              </div>
              
              <div class="review-author">
                <span class="author-name">{{ review.reviewer_name }}</span>
                <svg 
                  v-if="review.is_verified_purchase"
                  class="verified-icon" 
                  xmlns="http://www.w3.org/2000/svg" 
                  viewBox="0 0 24 24" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clip-rule="evenodd" />
                </svg>
              </div>
              
              <h4 v-if="review.title" class="review-title">{{ review.title }}</h4>
              
              <p class="review-text">{{ review.comment }}</p>
              
              <p class="review-date">{{ $t('productReviews.postedOn') }} {{ formatDate(review.created_at) }}</p>
            </div>
            
          </div>
          
          <!-- Load More Button (only show if there are reviews) -->
          <div v-if="reviewStore.getTotalReviews > 0" class="load-more-container">
            <button class="load-more-button">
              {{ $t('productReviews.loadMore') }}
            </button>
          </div>
      
    </div>
  </section>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useReviewStore } from '@/stores/modules/reviewStore'

// Props
const props = defineProps({
  productId: {
    type: [Number, String],
    required: true
  }
})

// Store
const reviewStore = useReviewStore()

// Methods
const loadReviews = async () => {
  if (!props.productId) return
  
  console.log(`🔄 Loading reviews for product ${props.productId}...`)
  
  // Load reviews and stats
  await Promise.all([
    reviewStore.fetchProductReviews(props.productId, true),
    reviewStore.fetchReviewStats(props.productId)
  ])
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return date.toLocaleDateString('es-ES', options)
}

const handleReviewMenu = (reviewId) => {
  console.log('Review menu clicked:', reviewId)
  // TODO: Implementar menú de editar/eliminar review
}

// Lifecycle
onMounted(() => {
  loadReviews()
})

// Watch for product changes
watch(() => props.productId, (newId) => {
  if (newId) {
    loadReviews()
  }
})
</script>

<style scoped>
/* Section Container */
.product-reviews-section {
  width: 100%;
  padding: 3rem 0;
  background: #fdf2f8;
}

.reviews-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* Reviews Header */
.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.reviews-title {
  font-family: 'Comfortaa', cursive;
  font-size: 1.5rem;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.reviews-count {
  font-weight: 400;
  color: #6b7280;
}

.reviews-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Loading, Error, Empty States */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(218, 157, 255, 0.2);
  border-top-color: #DA9DFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #6b7280;
}

.error-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  color: #dc2626;
  text-align: center;
}

.retry-button {
  padding: 0.75rem 1.5rem;
  background: #DA9DFF;
  border: none;
  border-radius: 20px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.retry-button:hover {
  background: #c084fc;
  transform: translateY(-2px);
}

.empty-text {
  font-family: 'Poppins', sans-serif;
  font-size: 1.125rem;
  color: #6b7280;
  text-align: center;
  max-width: 400px;
}

/* Latest Dropdown */
.latest-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #f3f4f6;
  border: none;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.latest-button:hover {
  background: #e5e7eb;
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  color: #374151;
}

/* Write Review Button */
.write-review-button {
  padding: 0.875rem 2rem;
  background: #DA9DFF;
  border: none;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(218, 157, 255, 0.3);
}

.write-review-button:hover {
  background: #c084fc;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(218, 157, 255, 0.4);
}

/* Reviews Grid */
.reviews-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Review Card */
.review-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.review-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.review-card.highlighted {
  border: 2px solid #60a5fa;
  background: #eff6ff;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.review-stars {
  display: flex;
  gap: 0.25rem;
}

.star {
  font-size: 1.25rem;
  color: #e5e7eb;
}

.star.filled {
  color: #fbbf24;
}

.star.half {
  background: linear-gradient(90deg, #fbbf24 50%, #e5e7eb 50%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.review-menu-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  color: #9ca3af;
  transition: all 0.2s ease;
  border-radius: 8px;
}

.review-menu-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.review-author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.author-name {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #000000;
}

.verified-icon {
  width: 20px;
  height: 20px;
  color: #10b981;
}

.review-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0.5rem 0;
}

.review-text {
  font-family: 'Poppins', sans-serif;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #6b7280;
  margin-bottom: 0.75rem;
}

.review-date {
  font-family: 'Poppins', sans-serif;
  font-size: 0.875rem;
  color: #9ca3af;
  font-weight: 500;
}

/* Load More Container */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 2rem 0;
}

.load-more-button {
  padding: 0.875rem 3rem;
  background: transparent;
  border: 2px solid #e5e7eb;
  border-radius: 24px;
  font-family: 'Poppins', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-button:hover {
  background: #f9fafb;
  border-color: #d1d5db;
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .reviews-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .reviews-container {
    padding: 0 1rem;
  }
  
  .reviews-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .reviews-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .write-review-button {
    padding: 0.75rem 1.5rem;
    font-size: 0.875rem;
  }
  
  .review-card {
    padding: 1.25rem;
  }
}

@media (max-width: 480px) {
  .reviews-title {
    font-size: 1.25rem;
  }
  
  .latest-button {
    padding: 0.625rem 1rem;
    font-size: 0.875rem;
  }
  
  .write-review-button {
    width: 100%;
    text-align: center;
  }
  
  .reviews-actions {
    flex-wrap: wrap;
  }
  
  .load-more-button {
    width: 100%;
  }
}
</style>

