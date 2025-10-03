"""
Review URLs for WooCommerce products
Handles review CRUD operations and statistics
"""
from django.urls import path
from ..views.review_views import (
    get_product_reviews, get_product_review_stats, get_review_detail,
    create_review, update_review, delete_review,
    get_user_reviews, check_user_review
)

urlpatterns = [
    # Get reviews for a WooCommerce product
    path('product/<int:woocommerce_product_id>/', get_product_reviews, name='get_product_reviews'),
    
    # Get review statistics for a WooCommerce product
    path('product/<int:woocommerce_product_id>/stats/', get_product_review_stats, name='get_product_review_stats'),
    
    # Check if user has reviewed a product
    path('product/<int:woocommerce_product_id>/check/', check_user_review, name='check_user_review'),
    
    # Get specific review details
    path('<int:review_id>/', get_review_detail, name='get_review_detail'),
    
    # Create a new review
    path('', create_review, name='create_review'),
    
    # Update a review
    path('<int:review_id>/update/', update_review, name='update_review'),
    
    # Delete a review
    path('<int:review_id>/delete/', delete_review, name='delete_review'),
    
    # Get all reviews by authenticated user
    path('user/my-reviews/', get_user_reviews, name='get_user_reviews'),
]



