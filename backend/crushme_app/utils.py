"""
Utility functions for CrushMe application
Based on signin_signon_feature implementation
"""
from .serializers.user_serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)


def calculate_shipping_cost(city):
    """
    Calculate shipping cost based on city
    
    Args:
        city: City name (string)
    
    Returns:
        int: Shipping cost in COP
    
    Rules:
        - Medellín: 10,500 COP
        - San Andrés Isla, Santa Catalina, Providencia: 45,000 COP
        - Other cities: 15,000 COP
    """
    if not city:
        logger.warning("⚠️ No city provided for shipping calculation, using default")
        return 15000
    
    # Normalize city name (lowercase and trim)
    city_normalized = city.lower().strip()
    
    # Remove accents for comparison
    city_normalized = city_normalized.replace('é', 'e').replace('í', 'i').replace('á', 'a')
    
    # Calculate shipping based on city
    if city_normalized == 'medellin':
        shipping_cost = 10500
        logger.info(f"📦 Shipping for Medellín: {shipping_cost}")
    elif city_normalized in ['san andres isla', 'santa catalina', 'providencia', 'san andres', 'san andrés']:
        shipping_cost = 45000
        logger.info(f"📦 Shipping for island ({city}): {shipping_cost}")
    else:
        shipping_cost = 15000
        logger.info(f"📦 Shipping for {city}: {shipping_cost} (default)")
    
    return shipping_cost


def generate_auth_tokens(user):
    """
    Generate JWT authentication tokens for the given user.

    This function creates a new refresh token and access token for the specified user
    and serializes the user's data for inclusion in the response.

    Args:
        user (User): The user instance for which to generate tokens.

    Returns:
        dict: A dictionary containing the refresh token, access token, and serialized user data.
    """
    # Generate a new refresh token for the user
    refresh = RefreshToken.for_user(user)
    
    # Serialize the user's data
    user_data = UserSerializer(user).data
    
    # Return the tokens and user data in a dictionary
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user_data
    }
