"""
Authentication URLs for CrushMe e-commerce application
Based on signin_signon_feature pattern
Handles user registration, login, password management, and profile updates
"""
from django.urls import path
from ..views.auth_views import (
    sign_on, send_verification_code, sign_in, google_login,
    update_profile, update_password, send_passcode, 
    verify_passcode_and_reset_password
)

urlpatterns = [
    # User registration and authentication (following signin_signon_feature pattern)
    path('sign_on/', sign_on, name='sign_on'),
    path('sign_on/send_verification_code/', send_verification_code, name='send_verification_code'),
    path('sign_in/', sign_in, name='sign_in'),
    
    # Profile management
    path('update_profile/', update_profile, name='update_profile'),
    path('update_password/', update_password, name='update_password'),
    
    # Password reset
    path('send_passcode/', send_passcode, name='send_passcode'),
    path('verify_passcode_and_reset_password/', verify_passcode_and_reset_password, name='verify_passcode_and_reset_password'),
    
    # OAuth2 login
    path('google_login/', google_login, name='google_login'),
]
