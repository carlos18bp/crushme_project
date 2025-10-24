"""
Feed serializers for CrushMe application
Handles serialization of user feed posts
"""
from rest_framework import serializers
from ..models import Feed, User


class FeedSerializer(serializers.ModelSerializer):
    """
    Serializer for Feed model (Read-only).
    Returns feed entries with all information.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Feed
        fields = [
            'id', 'user', 'user_email', 'user_username', 'user_full_name',
            'text', 'action', 'style', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'text', 'action', 'style', 'created_at', 'updated_at']

