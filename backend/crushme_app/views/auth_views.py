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
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User, PasswordCode
from ..utils import generate_auth_tokens
from ..serializers.user_serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    EmailVerificationSerializer, SendPasscodeSerializer, PasswordResetSerializer, 
    PasswordChangeSerializer, GuestCheckoutSerializer, UserProfileSerializer,
    CrushPublicProfileSerializer, UserSearchSerializer, CrushCardSerializer
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
            import traceback
            print(f"Email sending error: {str(e)}")
            print(traceback.format_exc())
            user.delete()
            return Response({
                'error': f'Failed to send verification email: {str(e)}'
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


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Handle updating the authenticated user's profile.

    This view processes POST, PUT, and PATCH requests to update the profile of the authenticated user.
    It uses the UserProfileSerializer to validate and save the updated user data including nested
    relationships (addresses, links, gallery_photos).
    
    Supports both application/json and multipart/form-data for image uploads.
    Handles profile_picture, cover_image, and gallery_photos.

    Args:
        request (Request): The HTTP request object containing user data.

    Returns:
        Response: A Response object with the updated profile data if the update is successful,
                  or an error message if the update fails.
    """
    # Process multipart/form-data if present (for image uploads)
    data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
    
    # Extract gallery images from multipart/form-data
    # Format: gallery_image_1, gallery_caption_1, gallery_is_profile_1, etc.
    gallery_photos = []
    i = 1
    while f'gallery_image_{i}' in request.FILES or f'gallery_caption_{i}' in data or f'gallery_is_profile_{i}' in data:
        photo_data = {}
        
        # Get image file
        if f'gallery_image_{i}' in request.FILES:
            photo_data['image'] = request.FILES[f'gallery_image_{i}']
        
        # Get caption (handle both string and list)
        if f'gallery_caption_{i}' in data:
            caption = data.pop(f'gallery_caption_{i}')
            # If caption is a list, get the first element
            photo_data['caption'] = caption[0] if isinstance(caption, list) else caption
        
        # Get is_profile_picture (handle both string and list)
        if f'gallery_is_profile_{i}' in data:
            is_profile = data.pop(f'gallery_is_profile_{i}')
            # If is_profile is a list, get the first element
            if isinstance(is_profile, list):
                is_profile = is_profile[0]
            photo_data['is_profile_picture'] = is_profile in ['true', 'True', '1', True]
        
        if photo_data:
            gallery_photos.append(photo_data)
        
        i += 1
    
    # Store gallery_photos separately (handled after serializer validation)
    gallery_photos_to_process = None
    if gallery_photos:
        gallery_photos_to_process = gallery_photos
    
    # Remove gallery_photos from data if present (will be handled manually)
    data.pop('gallery_photos', None)
    
    # Serialize the request data with the current user instance
    serializer = UserProfileSerializer(instance=request.user, data=data, partial=True, context={'request': request})
    
    # Validate the serialized data
    if serializer.is_valid():
        # Save the updated user data
        user = serializer.save()
        
        # Handle gallery_photos manually after successful validation
        if gallery_photos_to_process:
            from ..models import UserGallery
            
            for photo_data in gallery_photos_to_process:
                try:
                    # If setting as profile picture, unset others first
                    if photo_data.get('is_profile_picture'):
                        UserGallery.objects.filter(user=user, is_profile_picture=True).update(is_profile_picture=False)
                    
                    # Create new photo
                    UserGallery.objects.create(
                        user=user,
                        image=photo_data.get('image'),
                        caption=photo_data.get('caption', ''),
                        is_profile_picture=photo_data.get('is_profile_picture', False)
                    )
                except Exception:
                    # Silent fail - could add proper error logging here if needed
                    pass
        
        # Update the last login timestamp for the user
        update_last_login(None, user)
        
        # Get fresh serializer with updated gallery_photos
        result_serializer = UserProfileSerializer(user, context={'request': request})
        
        # Return the updated profile data
        return Response(result_serializer.data, status=status.HTTP_200_OK)
    
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_crush_verification(request):
    """
    Request Crush (Webcammer) verification for authenticated user.
    
    This endpoint allows users to request verification as a Crush/Webcammer.
    The request will be pending until an admin approves or rejects it.
    
    Args:
        request (Request): The HTTP request object.
    
    Returns:
        Response: Success message if request is created, or error if already exists.
    """
    user = request.user
    
    # Check if user already has a verified Crush status
    if user.is_crush:
        return Response({
            'success': False,
            'error': 'You are already a verified Crush.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already has a pending request
    if user.crush_verification_status == 'pending':
        return Response({
            'success': False,
            'error': 'You already have a pending Crush verification request.',
            'requested_at': user.crush_requested_at
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create the verification request
    user.crush_verification_status = 'pending'
    user.crush_requested_at = timezone.now()
    user.crush_verified_at = None
    user.crush_rejection_reason = None
    user.save()
    
    return Response({
        'success': True,
        'message': 'Crush verification request submitted successfully. An admin will review your request.',
        'crush_verification_status': user.crush_verification_status,
        'crush_requested_at': user.crush_requested_at
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_crush_request(request):
    """
    Cancel a pending Crush verification request.
    
    This endpoint allows users to cancel their pending Crush verification request.
    Only works if the request is in 'pending' status.
    
    Args:
        request (Request): The HTTP request object.
    
    Returns:
        Response: Success message if request is cancelled, or error if not possible.
    """
    user = request.user
    
    # Check if user has a pending request
    if user.crush_verification_status != 'pending':
        return Response({
            'success': False,
            'error': 'You do not have a pending Crush verification request to cancel.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Cancel the request
    user.crush_verification_status = 'none'
    user.crush_requested_at = None
    user.save()
    
    return Response({
        'success': True,
        'message': 'Crush verification request cancelled successfully.',
        'crush_verification_status': user.crush_verification_status
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_crush_public_profile(request, username):
    """
    Get public profile information for any user by username.
    
    This is a public endpoint (no authentication required) that returns
    public information about a user.
    
    Returns:
        - username
        - profile_picture_url and cover_image_url
        - about (biography)
        - links (social media, etc.)
        - current_status
        - note
        - gallery_photos
        - public_wishlists (only wishlists marked as public)
        - is_crush (whether they are a verified Crush/webcammer)
    
    Args:
        request (Request): The HTTP request object
        username (str): The username of the user to retrieve
    
    Returns:
        Response: Public profile data or error if user not found
    """
    try:
        # Get user by username (no is_crush filter)
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize and return the public profile
    serializer = CrushPublicProfileSerializer(user, context={'request': request})
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_random_crush(request):
    """
    Get a random verified Crush user profile.
    
    This is a public endpoint (no authentication required) that returns
    a random Crush (webcammer) from all verified Crushes.
    
    Perfect for discovery features like "Random Crush" or "Surprise Me".
    
    Returns:
        - Random Crush's public profile information
        - Same fields as get_crush_public_profile
    
    Args:
        request (Request): The HTTP request object
    
    Returns:
        Response: Random Crush profile data or error if no Crushes exist
    """
    # Get a random verified Crush
    random_crush = User.objects.filter(is_crush=True).order_by('?').first()
    
    if not random_crush:
        return Response({
            'success': False,
            'error': 'No verified Crushes found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize and return the public profile
    serializer = CrushPublicProfileSerializer(random_crush, context={'request': request})
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def search_users(request):
    """
    Search for users by username.
    
    This is a public endpoint (no authentication required) that allows
    searching for users by partial username match.
    
    Query Parameters:
        q (str): Search query for username (case-insensitive)
        limit (int, optional): Maximum number of results to return (default: 20, max: 50)
    
    Returns:
        List of users with:
        - id
        - username
        - profile_picture_url
        - is_crush
    
    Example:
        GET /api/auth/search/?q=cerro
        GET /api/auth/search/?q=john&limit=10
    
    Args:
        request (Request): The HTTP request object
    
    Returns:
        Response: List of matching users or empty list if no matches
    """
    # Get search query
    search_query = request.GET.get('q', '').strip()
    
    if not search_query:
        return Response({
            'success': False,
            'error': 'Search query parameter "q" is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get limit parameter (default 20, max 50)
    try:
        limit = int(request.GET.get('limit', 20))
        limit = min(limit, 50)  # Cap at 50 results
    except ValueError:
        limit = 20
    
    # Search for users by username (case-insensitive partial match)
    users = User.objects.filter(
        username__icontains=search_query
    ).order_by('-is_crush', 'username')[:limit]
    
    # Serialize results
    serializer = UserSearchSerializer(users, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_crushes(request):
    """
    Get list of all verified Crushes.
    
    This is a public endpoint (no authentication required) that returns
    a list of all verified Crush (webcammer) users.
    
    Perfect for displaying a directory or catalog of available Crushes.
    
    Query Parameters:
        limit (int, optional): Maximum number of results to return (default: 50, max: 100)
        offset (int, optional): Number of results to skip for pagination (default: 0)
    
    Returns:
        List of verified Crushes with:
        - id
        - username
        - profile_picture_url
        - is_crush (always true)
    
    Example:
        GET /api/auth/crush/list/
        GET /api/auth/crush/list/?limit=20&offset=0
        GET /api/auth/crush/list/?limit=20&offset=20
    
    Args:
        request (Request): The HTTP request object
    
    Returns:
        Response: List of verified Crushes with pagination info
    """
    # Get pagination parameters
    try:
        limit = int(request.GET.get('limit', 50))
        limit = min(limit, 100)  # Cap at 100 results
    except ValueError:
        limit = 50
    
    try:
        offset = int(request.GET.get('offset', 0))
        offset = max(offset, 0)  # Ensure non-negative
    except ValueError:
        offset = 0
    
    # Get total count of Crushes
    total_count = User.objects.filter(is_crush=True).count()
    
    # Get paginated Crushes
    crushes = User.objects.filter(
        is_crush=True
    ).order_by('username')[offset:offset + limit]
    
    # Serialize results
    serializer = UserSearchSerializer(crushes, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'total': total_count,
        'offset': offset,
        'limit': limit,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_random_crushes(request):
    """
    Get 7 random verified Crushes for discovery/carousel display.
    
    This is a public endpoint (no authentication required) that returns
    exactly 7 random Crushes with card information.
    
    Perfect for homepage carousels, discovery sections, or "Explore Crushes".
    
    Returns:
        List of 7 random Crushes with:
        - id
        - username
        - profile_picture_url
        - current_status
        - note
        - is_crush (always true)
    
    Example:
        GET /api/auth/crush/random-7/
    
    Args:
        request (Request): The HTTP request object
    
    Returns:
        Response: List of 7 random Crushes or fewer if not enough Crushes exist
    """
    # Get 7 random verified Crushes
    random_crushes = User.objects.filter(is_crush=True).order_by('?')[:7]
    
    if not random_crushes:
        return Response({
            'success': False,
            'error': 'No verified Crushes found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize results
    serializer = CrushCardSerializer(random_crushes, many=True, context={'request': request})
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'results': serializer.data
    }, status=status.HTTP_200_OK)