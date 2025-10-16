"""
User search URLs for gift sending
"""
from django.urls import path
from ..views.user_search_views import search_users_for_gift

urlpatterns = [
    # Search users for gift sending
    path('search/', search_users_for_gift, name='search_users_for_gift'),
]
