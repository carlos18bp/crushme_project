"""
URL routing for Feed endpoints
"""
from django.urls import path
from ..views import feed_views

urlpatterns = [
    # List all feeds (read-only, feeds are created automatically by actions)
    path('', feed_views.feed_list, name='feed-list'),
    
    # Get authenticated user's feeds
    path('my-feeds/', feed_views.my_feeds, name='my-feeds'),
    
    # Get specific user's feeds
    path('user/<int:user_id>/', feed_views.user_feeds, name='user-feeds'),
]



