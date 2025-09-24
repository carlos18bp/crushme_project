"""
Wishlist URLs for CrushMe e-commerce application
Handles wishlist CRUD operations, sharing, and favorites functionality
"""
from django.urls import path
from ..views.wishlist_views import (
    get_wishlists, create_wishlist, get_wishlist, update_wishlist,
    delete_wishlist, add_product_to_wishlist, remove_product_from_wishlist,
    get_public_wishlist, search_public_wishlists, favorite_wishlist,
    unfavorite_wishlist, get_favorite_wishlists, update_wishlist_shipping,
    update_wishlist_item
)

urlpatterns = [
    # Wishlist management
    path('', get_wishlists, name='get_wishlists'),
    path('create/', create_wishlist, name='create_wishlist'),
    path('<int:wishlist_id>/', get_wishlist, name='get_wishlist'),
    path('<int:wishlist_id>/update/', update_wishlist, name='update_wishlist'),
    path('<int:wishlist_id>/delete/', delete_wishlist, name='delete_wishlist'),
    
    # Wishlist items
    path('<int:wishlist_id>/add-product/', add_product_to_wishlist, name='add_product_to_wishlist'),
    path('<int:wishlist_id>/remove-product/<int:product_id>/', remove_product_from_wishlist, name='remove_product_from_wishlist'),
    path('<int:wishlist_id>/items/<int:item_id>/update/', update_wishlist_item, name='update_wishlist_item'),
    
    # Public access and sharing
    path('public/<uuid:unique_link>/', get_public_wishlist, name='get_public_wishlist'),
    path('public/', search_public_wishlists, name='search_public_wishlists'),
    
    # Favorites system
    path('<int:wishlist_id>/favorite/', favorite_wishlist, name='favorite_wishlist'),
    path('<int:wishlist_id>/unfavorite/', unfavorite_wishlist, name='unfavorite_wishlist'),
    path('favorites/', get_favorite_wishlists, name='get_favorite_wishlists'),
    
    # Shipping information
    path('<int:wishlist_id>/shipping/', update_wishlist_shipping, name='update_wishlist_shipping'),
]
