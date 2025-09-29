"""
Authentication views for CrushMe e-commerce application
Based on signin_signon_feature repository implementation
Handles user registration, login, password management, and profile updates
"""
import secrets
import random
from rest_framework import status
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import update_last_login
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User, PasswordCode
from ..utils import generate_auth_tokens
from ..serializers.user_serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    EmailVerificationSerializer, SendPasscodeSerializer, PasswordResetSerializer, 
    PasswordChangeSerializer, GuestCheckoutSerializer, UserProfileSerializer
)


@api_view(['POST'])
def signup(request):
    """
    Handle user registration - Step 1: Create user and send verification email.

    This view processes POST requests to register a new user with email, username, 
    and password. The user is created but inactive until email verification.
    A 4-digit verification code is sent to their email.

    Args:
        request (Request): The HTTP request object containing user data.

    Returns:
        Response: A Response object with success message if registration is successful,
                  or an error message if the registration fails.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Create the new user (inactive until email verification)
        user = serializer.save()
        
        # Generate 4-digit verification code
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # Save verification code to database
        PasswordCode.objects.create(
            user=user,
            code=verification_code,
            code_type='email_verification'
        )
        
        # Send verification email
        try:
            send_mail(
                subject='Verify your email - CrushMe',
                message=f'Your verification code is: {verification_code}\n\nThis code will expire in 5 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Registration successful. Please check your email for verification code.',
                'email': user.email,
                'requires_verification': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If email fails, delete the user and return error
            user.delete()
            return Response({
                'error': 'Failed to send verification email. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_email(request):
    """
    Handle email verification - Step 2: Verify code and activate user account.

    This view processes POST requests to verify the 4-digit code sent to user's email.
    If valid, the user account is activated and JWT tokens are returned.

    Args:
        request (Request): The HTTP request object containing email and verification code.

    Returns:
        Response: A Response object with JWT tokens if verification is successful,
                  or an error message if verification fails.
    """
    serializer = EmailVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        verification_code_obj = serializer.validated_data['verification_code_obj']
        
        # Mark verification code as used
        verification_code_obj.used = True
        verification_code_obj.save()
        
        # Activate user account
        user.is_active = True
        user.email_verified = True
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Return user profile data with tokens
        user_data = UserProfileSerializer(user, context={'request': request}).data
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
            'message': 'Email verified successfully. Account activated.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resend_verification_code(request):
    """
    Resend verification code to user's email.

    Args:
        request (Request): The HTTP request object containing user's email.

    Returns:
        Response: A Response object with success message if code is sent,
                  or an error message if user not found or already verified.
    """
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if user.email_verified:
        return Response({'error': 'Email is already verified'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark previous verification codes as used
    PasswordCode.objects.filter(
        user=user, 
        code_type='email_verification', 
        used=False
    ).update(used=True)
    
    # Generate new 4-digit verification code
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    
    # Save new verification code
    PasswordCode.objects.create(
        user=user,
        code=verification_code,
        code_type='email_verification'
    )
    
    # Send verification email
    try:
        send_mail(
            subject='Verify your email - CrushMe',
            message=f'Your new verification code is: {verification_code}\n\nThis code will expire in 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'New verification code sent to your email.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to send verification email. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login(request):
    """
    Handle user login with email and password.

    This view processes POST requests to authenticate a user using email and password.
    The user must have verified their email to login successfully.

    Args:
        request (Request): The HTTP request object containing user credentials.

    Returns:
        Response: A Response object with JWT tokens if authentication is successful,
                  or an error message if authentication fails.
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        update_last_login(None, user)
        
        # Return user profile data with tokens
        user_data = UserProfileSerializer(user, context={'request': request}).data
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data,
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def google_login(request):
    """
    Handle user login via Google data.

    This view processes POST requests containing user information from Google,
    and uses it to authenticate the user. If the user does not exist, it creates a new one
    with the provided information, then returns a JWT token.

    Args:
        request (Request): The HTTP request object containing user data from Google.

    Returns:
        JsonResponse: A JsonResponse object with JWT tokens if authentication is successful,
                      or an error message if authentication fails.
    """
    if request.method == 'POST':
        # Extract user data from the request body
        email = request.data.get('email')
        given_name = request.data.get('given_name')
        family_name = request.data.get('family_name')

        # Validate that all required data is present
        if not email or not given_name or not family_name:
            return JsonResponse({'status': 'error', 'error_message': 'Required fields are missing'}, status=400)
        
        try:
            # Get or create the user based on the email
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'first_name': given_name, 'last_name': family_name}
            )
            
            # Generate authentication token
            tokens = generate_auth_tokens(user)

            # Return the generated authentication tokens
            return JsonResponse(tokens, status=200)

        except Exception as e:
            # Handle unexpected exceptions
            return JsonResponse({'status': 'error', 'error_message': str(e)}, status=500)
    else:
        # Handle invalid request methods
        return JsonResponse({'status': 'error', 'error_message': 'Invalid request method'}, status=405)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Handle updating the authenticated user's profile.

    This view processes POST requests to update the profile of the authenticated user.
    It uses the UserSerializer to validate and save the updated user data.

    Args:
        request (Request): The HTTP request object containing user data.

    Returns:
        Response: A Response object with a success message if the update is successful,
                  or an error message if the update fails.
    """
    # Serialize the request data with the current user instance
    serializer = UserSerializer(instance=request.user, data=request.data, partial=True)
    
    # Validate the serialized data
    if serializer.is_valid():
        # Save the updated user data
        serializer.save()
        
        # Update the last login timestamp for the user
        update_last_login(None, request.user)
        
        # Return a success message
        return Response({'message': 'Profile updated successfully'}, status=status.HTTP_200_OK)
    
    # Return validation errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    """
    Handle updating the authenticated user's password.

    This view processes POST requests to update the password of the authenticated user.
    It checks if the current password is correct before updating to the new password.

    Args:
        request (Request): The HTTP request object containing the current and new passwords.

    Returns:
        Response: A Response object with a success message if the update is successful,
                  or an error message if the current password is incorrect.
    """
    # Get the authenticated user
    user = request.user
    
    # Get the current and new passwords from the request data
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    # Ensure both passwords are provided
    if not current_password or not new_password:
        return Response({'error': 'Both current and new passwords are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the current password is correct
    if not user.check_password(current_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the user's password
    user.password = make_password(new_password)
    user.save()
    
    # Return a success message
    return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def forgot_password(request):
    """
    Handle password recovery by sending a 4-digit reset code to user's email.

    This view processes POST requests to generate a 4-digit reset code and send it to the 
    user's email for password reset purposes.

    Args:
        request (Request): The HTTP request object containing the user's email.

    Returns:
        Response: A Response object with a success message if the code is sent successfully,
                  or an error message if the user is not found.
    """
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Mark previous password reset codes as used
    PasswordCode.objects.filter(
        user=user, 
        code_type='password_reset', 
        used=False
    ).update(used=True)

    # Generate a 4-digit reset code
    reset_code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    
    # Save the reset code to the database
    PasswordCode.objects.create(
        user=user, 
        code=reset_code,
        code_type='password_reset'
    )

    # Send email with the reset code
    try:
        send_mail(
            subject='Password Reset - CrushMe',
            message=f'Your password reset code is: {reset_code}\n\nThis code will expire in 5 minutes.\n\nIf you did not request this, please ignore this email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Password reset code sent to your email.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to send reset email. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def reset_password(request):
    """
    Verify the 4-digit reset code and set new password.

    This view processes POST requests to verify the provided reset code. If the code is valid,
    it resets the user's password to the new password provided in the request.

    Args:
        request (Request): The HTTP request object containing email, reset code and new password.

    Returns:
        Response: A Response object with a success message if the password reset is successful,
                  or an error message if the code is invalid or expired.
    """
    serializer = PasswordResetSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        password_code = serializer.validated_data['password_code']
        new_password = serializer.validated_data['new_password']
        
        # Update user's password
        user.set_password(new_password)
        user.save()
        
        # Mark the reset code as used
        password_code.used = True
        password_code.save()
        
        return Response({
            'message': 'Password reset successful. You can now login with your new password.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def guest_checkout(request):
    """
    Handle guest checkout by creating a guest user and address.
    
    This allows users to make purchases without registering a full account.
    The data is stored so they can later register and have their purchase history.
    
    Args:
        request (Request): The HTTP request object containing guest data and address.
    
    Returns:
        Response: A Response object with guest user data if successful,
                  or an error message if the creation fails.
    """
    serializer = GuestCheckoutSerializer(data=request.data)
    
    if serializer.is_valid():
        guest_user = serializer.save()
        
        return Response({
            'guest_user': {
                'id': guest_user.id,
                'email': guest_user.email,
                'first_name': guest_user.first_name,
                'last_name': guest_user.last_name,
                'full_name': guest_user.get_full_name(),
                'phone': guest_user.phone,
                'total_orders': guest_user.total_orders,
                'total_spent': str(guest_user.total_spent)
            },
            'message': 'Guest checkout information saved successfully.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get complete user profile including addresses, gallery, and links.
    
    Args:
        request (Request): The HTTP request object.
    
    Returns:
        Response: A Response object with complete user profile data.
    """
    user = request.user
    serializer = UserProfileSerializer(user, context={'request': request})
    
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_username_availability(request):
    """
    Check if a username is available for registration.
    
    Args:
        request (Request): The HTTP request object containing username.
    
    Returns:
        Response: A Response object indicating if username is available.
    """
    username = request.data.get('username', '').strip()
    
    if not username:
        return Response({
            'available': False,
            'message': 'Username is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if username already exists (case-insensitive)
    exists = User.objects.filter(username__iexact=username).exists()
    
    return Response({
        'available': not exists,
        'username': username,
        'message': 'Username is available.' if not exists else 'Username is already taken.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def check_guest_user(request):
    """
    Check if there's a guest user with the provided email for registration conversion.
    
    Args:
        request (Request): The HTTP request object containing email.
    
    Returns:
        Response: A Response object with guest user data if found.
    """
    email = request.data.get('email', '').strip()
    
    if not email:
        return Response({
            'message': 'Email is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        guest_user = GuestUser.objects.get(email=email, has_been_converted=False)
        return Response({
            'has_guest_profile': True,
            'guest_data': {
                'first_name': guest_user.first_name,
                'last_name': guest_user.last_name,
                'phone': guest_user.phone,
                'total_orders': guest_user.total_orders,
                'total_spent': str(guest_user.total_spent)
            },
            'message': f'Found guest profile with {guest_user.total_orders} orders and ${guest_user.total_spent} spent.'
        }, status=status.HTTP_200_OK)
    
    except GuestUser.DoesNotExist:
        return Response({
            'has_guest_profile': False,
            'message': 'No guest profile found with this email.'
        }, status=status.HTTP_200_OK)