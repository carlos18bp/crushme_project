"""
Authentication URLs for CrushMe e-commerce application
Based on signin_signon_feature pattern
Handles user registration, login, password management, and profile updates
"""
from django.urls import path
from ..views.auth_views import (
    signup, verify_email, resend_verification_code, login, 
    forgot_password, reset_password, google_login,
    update_profile, update_password, guest_checkout,
    get_user_profile, check_username_availability, check_guest_user,
    request_crush_verification, cancel_crush_request,
    get_crush_public_profile, get_random_crush, search_users, list_crushes,
    get_random_crushes
)

urlpatterns = [
    # User registration flow
    path('signup/', signup, name='signup'),
    path('verify-email/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification_code, name='resend_verification_code'),
    
    # User authentication
    path('login/', login, name='login'),
    
    # Password recovery
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    
    # Profile management
    path('profile/', get_user_profile, name='get_user_profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('update_password/', update_password, name='update_password'),
    
    # Guest checkout and pre-registration
    path('guest_checkout/', guest_checkout, name='guest_checkout'),
    path('check_username/', check_username_availability, name='check_username_availability'),
    path('check_guest/', check_guest_user, name='check_guest_user'),
    
    # Crush (Webcammer) verification
    path('crush/request-verification/', request_crush_verification, name='request_crush_verification'),
    path('crush/cancel-request/', cancel_crush_request, name='cancel_crush_request'),
    
    # Public profiles (no authentication required)
    path('public/@<str:username>/', get_crush_public_profile, name='get_public_profile'),
    path('crush/random/', get_random_crush, name='get_random_crush'),
    path('crush/random-7/', get_random_crushes, name='get_random_crushes'),
    path('crush/list/', list_crushes, name='list_crushes'),
    path('search/', search_users, name='search_users'),
    
    # OAuth2 login
    path('google_login/', google_login, name='google_login'),
]
