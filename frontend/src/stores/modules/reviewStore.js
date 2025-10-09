/**
 * Review Store for CrushMe e-commerce application
 * Handles product reviews functionality
 * Based on backend API documentation v1.0
 */
import { defineStore } from 'pinia'
import { get_request, create_request, patch_request, delete_request } from '@/services/request_http'

export const useReviewStore = defineStore('review', {
  state: () => ({
    // Product Reviews Data
    productReviews: [], // Reviews for current product
    currentProductId: null, // Current product being viewed
    totalReviews: 0,
    
    // Review Statistics
    reviewStats: {
      total_reviews: 0,
      average_rating: 0,
      rating_distribution: {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0
      }
    },
    
    // Current Review Details
    currentReview: null,
    
    // User Reviews
    myReviews: [],
    totalMyReviews: 0,
    
    // User Review Check
    hasReviewedProduct: false,
    userProductReview: null,
    
    // Loading States
    isLoadingReviews: false,
    isLoadingStats: false,
    isLoadingReviewDetail: false,
    isLoadingMyReviews: false,
    isCreatingReview: false,
    isUpdatingReview: false,
    isDeletingReview: false,
    isCheckingReview: false,
    
    // Error States
    reviewsError: null,
    statsError: null,
    reviewDetailError: null,
    myReviewsError: null,
    createError: null,
    updateError: null,
    deleteError: null,
    checkError: null,
  }),

  getters: {
    /**
     * Get reviews for current product
     */
    getProductReviews: (state) => state.productReviews,

    /**
     * Get total number of reviews for current product
     */
    getTotalReviews: (state) => state.totalReviews,

    /**
     * Get review statistics
     */
    getReviewStats: (state) => state.reviewStats,

    /**
     * Get average rating
     */
    getAverageRating: (state) => state.reviewStats.average_rating,

    /**
     * Get rating distribution
     */
    getRatingDistribution: (state) => state.reviewStats.rating_distribution,

    /**
     * Get current review detail
     */
    getCurrentReview: (state) => state.currentReview,

    /**
     * Get user's reviews
     */
    getMyReviews: (state) => state.myReviews,

    /**
     * Check if user has reviewed current product
     */
    hasUserReviewed: (state) => state.hasReviewedProduct,

    /**
     * Get user's review for current product
     */
    getUserProductReview: (state) => state.userProductReview,

    /**
     * Check if any loading state is active
     */
    isLoading: (state) => {
      return state.isLoadingReviews || 
             state.isLoadingStats || 
             state.isLoadingReviewDetail || 
             state.isLoadingMyReviews ||
             state.isCreatingReview ||
             state.isUpdatingReview ||
             state.isDeletingReview ||
             state.isCheckingReview
    },

    /**
     * Check if there are any errors
     */
    hasError: (state) => {
      return state.reviewsError || 
             state.statsError || 
             state.reviewDetailError || 
             state.myReviewsError ||
             state.createError ||
             state.updateError ||
             state.deleteError ||
             state.checkError
    }
  },

  actions: {
    /**
     * 1. Fetch reviews for a specific product
     * @param {number} productId - WooCommerce product ID
     * @param {boolean} activeOnly - Only show active/approved reviews (default: true)
     * @returns {Promise<Object>} - Result with success status and data
     */
    async fetchProductReviews(productId, activeOnly = true) {
      this.isLoadingReviews = true
      this.reviewsError = null
      this.currentProductId = productId

      try {
        console.log(`🔍 Fetching reviews for product ${productId}...`)
        
        const url = `reviews/product/${productId}/?active_only=${activeOnly}`
        const response = await get_request(url)

        if (response.data.success) {
          this.productReviews = response.data.reviews || []
          this.totalReviews = response.data.total_reviews || 0
          
          console.log(`✅ Loaded ${this.totalReviews} reviews for product ${productId}`)
          
          return {
            success: true,
            data: response.data
          }
        } else {
          throw new Error('Failed to fetch reviews')
        }
      } catch (error) {
        console.error('❌ Error fetching product reviews:', error)
        this.reviewsError = error.response?.data?.error || error.message || 'Error al cargar reseñas'
        this.productReviews = []
        this.totalReviews = 0
        
        return {
          success: false,
          error: this.reviewsError
        }
      } finally {
        this.isLoadingReviews = false
      }
    },

    /**
     * 2. Fetch review statistics for a product
     * @param {number} productId - WooCommerce product ID
     * @returns {Promise<Object>} - Result with success status and stats data
     */
    async fetchReviewStats(productId) {
      this.isLoadingStats = true
      this.statsError = null

      try {
        console.log(`📊 Fetching review stats for product ${productId}...`)
        
        const url = `reviews/product/${productId}/stats/`
        const response = await get_request(url)

        if (response.data.success) {
          this.reviewStats = response.data.stats || {
            total_reviews: 0,
            average_rating: 0,
            rating_distribution: { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0 }
          }
          
          console.log(`✅ Loaded stats: ${this.reviewStats.average_rating} avg rating, ${this.reviewStats.total_reviews} reviews`)
          
          return {
            success: true,
            data: response.data
          }
        } else {
          throw new Error('Failed to fetch review stats')
        }
      } catch (error) {
        console.error('❌ Error fetching review stats:', error)
        this.statsError = error.response?.data?.error || error.message || 'Error al cargar estadísticas'
        
        return {
          success: false,
          error: this.statsError
        }
      } finally {
        this.isLoadingStats = false
      }
    },

    /**
     * 3. Fetch detail of a specific review
     * @param {number} reviewId - Review ID
     * @returns {Promise<Object>} - Result with success status and review data
     */
    async fetchReviewDetail(reviewId) {
      this.isLoadingReviewDetail = true
      this.reviewDetailError = null

      try {
        console.log(`🔍 Fetching review detail ${reviewId}...`)
        
        const url = `reviews/${reviewId}/`
        const response = await get_request(url)

        if (response.data.success) {
          this.currentReview = response.data.review
          
          console.log(`✅ Loaded review detail for review ${reviewId}`)
          
          return {
            success: true,
            data: response.data
          }
        } else {
          throw new Error('Failed to fetch review detail')
        }
      } catch (error) {
        console.error('❌ Error fetching review detail:', error)
        this.reviewDetailError = error.response?.data?.error || error.message || 'Error al cargar detalle de reseña'
        this.currentReview = null
        
        return {
          success: false,
          error: this.reviewDetailError
        }
      } finally {
        this.isLoadingReviewDetail = false
      }
    },

    /**
     * 4. Check if user has reviewed a product
     * @param {number} productId - WooCommerce product ID
     * @returns {Promise<Object>} - Result with has_reviewed status and review data
     */
    async checkUserReview(productId) {
      this.isCheckingReview = true
      this.checkError = null

      try {
        console.log(`🔍 Checking if user has reviewed product ${productId}...`)
        
        const url = `reviews/product/${productId}/check/`
        const response = await get_request(url)

        if (response.data.success) {
          this.hasReviewedProduct = response.data.has_reviewed
          this.userProductReview = response.data.review
          
          console.log(`✅ User ${this.hasReviewedProduct ? 'has' : 'has not'} reviewed product ${productId}`)
          
          return {
            success: true,
            has_reviewed: this.hasReviewedProduct,
            review: this.userProductReview
          }
        } else {
          throw new Error('Failed to check user review')
        }
      } catch (error) {
        console.error('❌ Error checking user review:', error)
        this.checkError = error.response?.data?.error || error.message || 'Error al verificar reseña'
        this.hasReviewedProduct = false
        this.userProductReview = null
        
        return {
          success: false,
          error: this.checkError
        }
      } finally {
        this.isCheckingReview = false
      }
    },

    /**
     * 5. Fetch all reviews created by the authenticated user
     * @returns {Promise<Object>} - Result with success status and user's reviews
     */
    async fetchMyReviews() {
      this.isLoadingMyReviews = true
      this.myReviewsError = null

      try {
        console.log('🔍 Fetching user reviews...')
        
        const url = 'reviews/user/my-reviews/'
        const response = await get_request(url)

        if (response.data.success) {
          this.myReviews = response.data.reviews || []
          this.totalMyReviews = response.data.total_reviews || 0
          
          console.log(`✅ Loaded ${this.totalMyReviews} user reviews`)
          
          return {
            success: true,
            data: response.data
          }
        } else {
          throw new Error('Failed to fetch user reviews')
        }
      } catch (error) {
        console.error('❌ Error fetching user reviews:', error)
        this.myReviewsError = error.response?.data?.error || error.message || 'Error al cargar tus reseñas'
        this.myReviews = []
        this.totalMyReviews = 0
        
        return {
          success: false,
          error: this.myReviewsError
        }
      } finally {
        this.isLoadingMyReviews = false
      }
    },

    /**
     * 6. Create a new review
     * @param {Object} reviewData - Review data
     * @param {number} reviewData.woocommerce_product_id - Product ID (required)
     * @param {number} reviewData.rating - Rating 1-5 (required)
     * @param {string} reviewData.comment - Review comment (required)
     * @param {string} reviewData.title - Review title (optional)
     * @param {string} reviewData.anonymous_name - Name for anonymous users (required if not authenticated)
     * @param {string} reviewData.anonymous_email - Email for anonymous users (required if not authenticated)
     * @returns {Promise<Object>} - Result with success status and created review
     */
    async createReview(reviewData) {
      this.isCreatingReview = true
      this.createError = null

      try {
        console.log('📝 Creating new review...', reviewData)
        
        const url = 'reviews/'
        const response = await create_request(url, reviewData)

        if (response.data.success) {
          const createdReview = response.data.review
          
          // Add to product reviews if it's for the current product
          if (createdReview.woocommerce_product_id === this.currentProductId) {
            this.productReviews.unshift(createdReview)
            this.totalReviews++
          }
          
          // Add to my reviews if user is authenticated
          if (createdReview.is_user_review) {
            this.myReviews.unshift(createdReview)
            this.totalMyReviews++
            this.hasReviewedProduct = true
            this.userProductReview = createdReview
          }
          
          console.log('✅ Review created successfully:', createdReview.id)
          
          return {
            success: true,
            data: response.data,
            review: createdReview
          }
        } else {
          throw new Error(response.data.message || 'Failed to create review')
        }
      } catch (error) {
        console.error('❌ Error creating review:', error)
        this.createError = error.response?.data?.errors || error.response?.data?.error || error.message || 'Error al crear reseña'
        
        return {
          success: false,
          error: this.createError,
          errors: error.response?.data?.errors
        }
      } finally {
        this.isCreatingReview = false
      }
    },

    /**
     * 7. Update an existing review
     * @param {number} reviewId - Review ID
     * @param {Object} updateData - Data to update
     * @param {number} updateData.rating - New rating (optional)
     * @param {string} updateData.title - New title (optional)
     * @param {string} updateData.comment - New comment (optional)
     * @returns {Promise<Object>} - Result with success status and updated review
     */
    async updateReview(reviewId, updateData) {
      this.isUpdatingReview = true
      this.updateError = null

      try {
        console.log(`📝 Updating review ${reviewId}...`, updateData)
        
        const url = `reviews/${reviewId}/update/`
        const response = await patch_request(url, updateData)

        if (response.data.success) {
          const updatedReview = response.data.review
          
          // Update in product reviews
          const productReviewIndex = this.productReviews.findIndex(r => r.id === reviewId)
          if (productReviewIndex !== -1) {
            this.productReviews[productReviewIndex] = updatedReview
          }
          
          // Update in my reviews
          const myReviewIndex = this.myReviews.findIndex(r => r.id === reviewId)
          if (myReviewIndex !== -1) {
            this.myReviews[myReviewIndex] = updatedReview
          }
          
          // Update user product review if applicable
          if (this.userProductReview?.id === reviewId) {
            this.userProductReview = updatedReview
          }
          
          // Update current review if viewing detail
          if (this.currentReview?.id === reviewId) {
            this.currentReview = updatedReview
          }
          
          console.log('✅ Review updated successfully:', reviewId)
          
          return {
            success: true,
            data: response.data,
            review: updatedReview
          }
        } else {
          throw new Error(response.data.message || 'Failed to update review')
        }
      } catch (error) {
        console.error('❌ Error updating review:', error)
        this.updateError = error.response?.data?.errors || error.response?.data?.error || error.message || 'Error al actualizar reseña'
        
        return {
          success: false,
          error: this.updateError,
          errors: error.response?.data?.errors
        }
      } finally {
        this.isUpdatingReview = false
      }
    },

    /**
     * 8. Delete a review
     * @param {number} reviewId - Review ID to delete
     * @returns {Promise<Object>} - Result with success status
     */
    async deleteReview(reviewId) {
      this.isDeletingReview = true
      this.deleteError = null

      try {
        console.log(`🗑️ Deleting review ${reviewId}...`)
        
        const url = `reviews/${reviewId}/delete/`
        const response = await delete_request(url)

        if (response.data.success) {
          const productId = response.data.woocommerce_product_id
          
          // Remove from product reviews
          this.productReviews = this.productReviews.filter(r => r.id !== reviewId)
          this.totalReviews = Math.max(0, this.totalReviews - 1)
          
          // Remove from my reviews
          this.myReviews = this.myReviews.filter(r => r.id !== reviewId)
          this.totalMyReviews = Math.max(0, this.totalMyReviews - 1)
          
          // Clear user product review if applicable
          if (this.userProductReview?.id === reviewId) {
            this.userProductReview = null
            this.hasReviewedProduct = false
          }
          
          // Clear current review if viewing detail
          if (this.currentReview?.id === reviewId) {
            this.currentReview = null
          }
          
          console.log('✅ Review deleted successfully:', reviewId)
          
          return {
            success: true,
            data: response.data,
            productId: productId
          }
        } else {
          throw new Error(response.data.message || 'Failed to delete review')
        }
      } catch (error) {
        console.error('❌ Error deleting review:', error)
        this.deleteError = error.response?.data?.error || error.message || 'Error al eliminar reseña'
        
        return {
          success: false,
          error: this.deleteError
        }
      } finally {
        this.isDeletingReview = false
      }
    },

    /**
     * Clear all review-related errors
     */
    clearErrors() {
      this.reviewsError = null
      this.statsError = null
      this.reviewDetailError = null
      this.myReviewsError = null
      this.createError = null
      this.updateError = null
      this.deleteError = null
      this.checkError = null
    },

    /**
     * Clear product reviews data
     */
    clearProductReviews() {
      this.productReviews = []
      this.totalReviews = 0
      this.currentProductId = null
      this.reviewStats = {
        total_reviews: 0,
        average_rating: 0,
        rating_distribution: { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0 }
      }
      this.hasReviewedProduct = false
      this.userProductReview = null
    },

    /**
     * Clear current review detail
     */
    clearCurrentReview() {
      this.currentReview = null
    },

    /**
     * Clear user reviews
     */
    clearMyReviews() {
      this.myReviews = []
      this.totalMyReviews = 0
    },

    /**
     * Reset entire review store to initial state
     */
    resetStore() {
      this.clearProductReviews()
      this.clearCurrentReview()
      this.clearMyReviews()
      this.clearErrors()
    }
  }
})

