"""
URL routing for Feed endpoints
"""
from django.urls import path
from ..views import feed_views

urlpatterns = [
    # List all feeds and create new feed
    path('', feed_views.feed_list_create, name='feed-list-create'),
    
    # Get authenticated user's feeds
    path('my-feeds/', feed_views.my_feeds, name='my-feeds'),
    
    # Get specific user's feeds
    path('user/<int:user_id>/', feed_views.user_feeds, name='user-feeds'),
    
    # Feed detail (get, update, delete)
    path('<int:feed_id>/', feed_views.feed_detail, name='feed-detail'),
]



