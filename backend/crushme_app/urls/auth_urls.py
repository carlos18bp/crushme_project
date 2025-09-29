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
    get_user_profile, check_username_availability, check_guest_user
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
    
    # OAuth2 login
    path('google_login/', google_login, name='google_login'),
]
