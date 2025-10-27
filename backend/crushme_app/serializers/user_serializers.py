
"""
User authentication serializers for CrushMe e-commerce application
Based on signin_signon_feature repository implementation
Handles user registration, authentication, and password management
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..models import User, PasswordCode, UserAddress, UserGallery, UserLink, GuestUser
from ..services.translation_service import create_translator_from_request


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    Used for displaying user information and profile updates
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'phone', 'about', 'profile_picture', 'cover_image', 'current_status', 'note',
            'date_joined', 'is_active', 'is_guest_converted',
            'is_crush', 'crush_verification_status', 'crush_requested_at', 'crush_verified_at'
        ]
        read_only_fields = [
            'id', 'date_joined', 'is_guest_converted', 
            'is_crush', 'crush_verification_status', 'crush_requested_at', 'crush_verified_at'
        ]
    
    def validate_username(self, value):
        """Check if username is unique (case-insensitive)"""
        if value:
            # Check if username exists (excluding current instance if updating)
            queryset = User.objects.filter(username__iexact=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def update(self, instance, validated_data):
        """Update user profile information"""
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.about = validated_data.get('about', instance.about)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.cover_image = validated_data.get('cover_image', instance.cover_image)
        instance.current_status = validated_data.get('current_status', instance.current_status)
        instance.note = validated_data.get('note', instance.note)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration - Step 1
    Creates user but requires email verification to activate account.
    Validates email uniqueness, username uniqueness, and password requirements.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm'
        ]
    
    def validate_email(self, value):
        """
        Check if email is already registered AND verified.
        Note: The view handles the case of unverified users (email_verified=False)
        by updating their data instead of creating a new user.
        """
        user = User.objects.filter(email=value).first()
        if user and user.email_verified:
            raise serializers.ValidationError("A user with this email is already registered and verified.")
        return value
    
    def validate_username(self, value):
        """
        Check if username is unique (case-insensitive).
        Note: The view handles username updates for unverified users.
        """
        if value:
            # Check if username exists for a verified user
            existing = User.objects.filter(username__iexact=value).first()
            if existing and existing.email_verified:
                raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation and username requirement"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        if not attrs.get('username'):
            raise serializers.ValidationError("Username is required for registration.")
        
        return attrs
    
    def create(self, validated_data):
        """
        Create new user with hashed password but inactive until email verification.
        If a guest user exists with the same email, convert it to full user.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        email = validated_data['email']
        
        # Check if there's a guest user with this email
        guest_user = None
        try:
            guest_user = GuestUser.objects.get(email=email, has_been_converted=False)
        except GuestUser.DoesNotExist:
            pass
        
        # Create the user (inactive until email verification)
        user = User.objects.create_user(
            email=email,
            username=validated_data['username'],
            first_name=guest_user.first_name if guest_user else '',
            last_name=guest_user.last_name if guest_user else '',
            phone=guest_user.phone if guest_user else '',
            password=password,
            is_active=False,  # Inactive until email verification
            email_verified=False
        )
        
        # If guest user exists, convert it
        if guest_user:
            user.is_guest_converted = True
            user.save()
            
            # Mark guest as converted
            guest_user.has_been_converted = True
            guest_user.converted_user = user
            guest_user.save()
        
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification with 4-digit code
    """
    email = serializers.EmailField()
    verification_code = serializers.CharField(
        max_length=4,
        min_length=4,
        help_text="4-digit verification code sent to your email"
    )
    
    def validate(self, attrs):
        """Validate verification code"""
        email = attrs['email']
        code = attrs['verification_code']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        # Find valid verification code
        try:
            verification_code = PasswordCode.objects.get(
                user=user,
                code=code,
                code_type='email_verification',
                used=False
            )
            
            if verification_code.is_expired():
                raise serializers.ValidationError("Verification code has expired.")
            
            attrs['user'] = user
            attrs['verification_code_obj'] = verification_code
            
        except PasswordCode.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code.")
        
        return attrs


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login with username and password
    """
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is not activated. Please verify your email.")
        
        if not user.email_verified:
            raise serializers.ValidationError("Email not verified. Please check your email for verification code.")
        
        # Authenticate with password
        authenticated_user = authenticate(username=user.username, password=password)
        if not authenticated_user:
            raise serializers.ValidationError("Invalid username or password.")
        
        attrs['user'] = authenticated_user
        return attrs


class PasswordCodeSerializer(serializers.ModelSerializer):
    """
    Serializer for password reset codes
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_expired = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = PasswordCode
        fields = ['id', 'user_email', 'code', 'created_at', 'used', 'is_expired', 'is_valid']
        read_only_fields = ['id', 'code', 'created_at']
    
    def get_is_expired(self, obj):
        """Check if code is expired"""
        return obj.is_expired()
    
    def get_is_valid(self, obj):
        """Check if code is valid"""
        return obj.is_valid()


class SendPasscodeSerializer(serializers.Serializer):
    """
    Serializer for sending password reset passcode
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Check if user with email exists"""
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset with 4-digit code
    """
    email = serializers.EmailField()
    reset_code = serializers.CharField(
        max_length=4, 
        min_length=4,
        help_text="4-digit reset code sent to your email"
    )
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password reset data"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        email = attrs['email']
        reset_code = attrs['reset_code']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        try:
            password_code = PasswordCode.objects.get(
                user=user,
                code=reset_code,
                code_type='password_reset',
                used=False
            )
            if password_code.is_expired():
                raise serializers.ValidationError("Reset code has expired.")
            
            attrs['user'] = user
            attrs['password_code'] = password_code
            
        except PasswordCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired reset code.")
        
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password (authenticated users)
    """
    current_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate password change data"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth2 login
    """
    google_token = serializers.CharField(
        help_text="Google ID token from frontend authentication"
    )
    
    def validate_google_token(self, value):
        """Validate Google token (implementation depends on Google auth library)"""
        # Note: This would require implementing Google token verification
        # using google-auth library as shown in the signin_signon_feature repo
        if not value:
            raise serializers.ValidationError("Google token is required.")
        return value


class UserAddressSerializer(serializers.ModelSerializer):
    """
    Serializer for UserAddress model
    Used for both registered users and guest checkout addresses
    """
    guest_full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserAddress
        fields = [
            'id', 'user', 'country', 'state', 'city', 'zip_code',
            'address_line_1', 'address_line_2', 'additional_details',
            'is_default_shipping', 'is_default_billing', 'guest_email', 
            'guest_first_name', 'guest_last_name', 'guest_phone', 
            'guest_full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'guest_full_name']
    
    def get_guest_full_name(self, obj):
        """Get full name for guest checkout"""
        if obj.guest_first_name or obj.guest_last_name:
            return f"{obj.guest_first_name or ''} {obj.guest_last_name or ''}".strip()
        return None


class GuestCheckoutSerializer(serializers.ModelSerializer):
    """
    Serializer for guest checkout - creates GuestUser and UserAddress
    """
    # Address fields
    country = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    zip_code = serializers.CharField(max_length=20)
    address_line_1 = serializers.CharField(max_length=255)
    address_line_2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    class Meta:
        model = GuestUser
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'country', 'state', 'city', 'zip_code', 
            'address_line_1', 'address_line_2'
        ]
    
    def create(self, validated_data):
        """
        Create or update guest user and create address
        """
        # Extract address data
        address_data = {
            'country': validated_data.pop('country'),
            'state': validated_data.pop('state'),
            'city': validated_data.pop('city'),
            'zip_code': validated_data.pop('zip_code'),
            'address_line_1': validated_data.pop('address_line_1'),
            'address_line_2': validated_data.pop('address_line_2', ''),
        }
        
        # Create or update guest user
        email = validated_data['email']
        guest_user, created = GuestUser.objects.get_or_create(
            email=email,
            defaults=validated_data
        )
        
        if not created:
            # Update existing guest user
            for key, value in validated_data.items():
                if value:  # Only update if value is provided
                    setattr(guest_user, key, value)
            guest_user.save()
        
        # Create address for guest checkout
        UserAddress.objects.create(
            user=None,  # No user for guest checkout
            guest_email=guest_user.email,
            guest_first_name=guest_user.first_name,
            guest_last_name=guest_user.last_name,
            guest_phone=guest_user.phone,
            **address_data
        )
        
        return guest_user


class UserGallerySerializer(serializers.ModelSerializer):
    """
    Serializer for UserGallery model
    Supports both file uploads and URL references
    """
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = UserGallery
        fields = [
            'id', 'user', 'image', 'caption', 'is_profile_picture', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def validate(self, attrs):
        """Ensure only one profile picture per user"""
        if attrs.get('is_profile_picture'):
            user = attrs.get('user') or (self.instance.user if self.instance else None)
            if user:
                # Check if user already has a profile picture
                existing_profile = UserGallery.objects.filter(
                    user=user, 
                    is_profile_picture=True
                )
                if self.instance:
                    existing_profile = existing_profile.exclude(pk=self.instance.pk)
                
                if existing_profile.exists():
                    raise serializers.ValidationError(
                        "User already has a profile picture. Please remove the current one first."
                    )
        return attrs
    
    def to_representation(self, instance):
        """Translate caption field for public endpoints"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if request:
            translator = create_translator_from_request(request)
            # Translate user-generated caption (auto-detect source language)
            if representation.get('caption'):
                representation['caption'] = translator.translate_user_content(representation['caption'])
        
        return representation


class UserLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for UserLink model
    """
    class Meta:
        model = UserLink
        fields = [
            'id', 'user', 'title', 'url', 'order', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_url(self, value):
        """Validate URL format"""
        if not value.startswith(('http://', 'https://')):
            value = f"https://{value}"
        return value


class GuestUserSerializer(serializers.ModelSerializer):
    """
    Serializer for GuestUser model - read only for admin purposes
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = GuestUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone',
            'total_orders', 'total_spent', 'has_been_converted', 
            'converted_user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Complete user profile serializer including related data
    Supports both read and write operations for nested relationships
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    addresses = UserAddressSerializer(many=True, required=False, allow_null=True)
    # gallery_photos is handled manually in update() to support file uploads
    links = UserLinkSerializer(many=True, required=False, allow_null=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    cover_image_url = serializers.SerializerMethodField(read_only=True)
    guest_profile = GuestUserSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'about', 'profile_picture', 'profile_picture_url', 'cover_image', 'cover_image_url',
            'current_status', 'note', 'date_joined', 'is_active', 'is_guest_converted', 
            'is_crush', 'crush_verification_status', 'crush_requested_at', 'crush_verified_at',
            'addresses', 'gallery_photos', 'links', 'guest_profile'
        ]
        read_only_fields = [
            'id', 'date_joined', 'is_guest_converted', 'full_name', 'profile_picture_url', 'cover_image_url', 
            'guest_profile', 'is_crush', 'crush_verification_status', 'crush_requested_at', 'crush_verified_at'
        ]
    
    def get_profile_picture_url(self, obj):
        """Get user's profile picture URL"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        # Fallback to gallery profile picture if direct profile_picture is not set
        profile_pic = obj.gallery_photos.filter(is_profile_picture=True).first()
        if profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_pic.image.url)
            return profile_pic.image.url
        return None
    
    def get_cover_image_url(self, obj):
        """Get user's cover image URL"""
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None
    
    def to_representation(self, instance):
        """Override to properly serialize gallery_photos when reading"""
        representation = super().to_representation(instance)
        # Use UserGallerySerializer for reading gallery_photos
        representation['gallery_photos'] = UserGallerySerializer(
            instance.gallery_photos.all(), 
            many=True, 
            context=self.context
        ).data
        return representation
    
    def update(self, instance, validated_data):
        """Update user profile including nested relationships"""
        # Extract nested data
        addresses_data = validated_data.pop('addresses', None)
        links_data = validated_data.pop('links', None)
        # gallery_photos is handled in the view, not here
        
        # Update basic user fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.about = validated_data.get('about', instance.about)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.cover_image = validated_data.get('cover_image', instance.cover_image)
        instance.current_status = validated_data.get('current_status', instance.current_status)
        instance.note = validated_data.get('note', instance.note)
        instance.save()
        
        # Update addresses if provided
        if addresses_data is not None:
            self._update_addresses(instance, addresses_data)
        
        # Update links if provided
        if links_data is not None:
            self._update_links(instance, links_data)
        
        return instance
    
    def _update_addresses(self, user, addresses_data):
        """Update or create user addresses"""
        # Get existing address IDs from the request
        incoming_ids = [addr.get('id') for addr in addresses_data if addr.get('id')]
        
        # Delete addresses not in the incoming data
        UserAddress.objects.filter(user=user).exclude(id__in=incoming_ids).delete()
        
        # Update or create addresses
        for address_data in addresses_data:
            address_id = address_data.get('id')
            address_data.pop('user', None)  # Remove user field if present
            
            if address_id:
                # Update existing address
                UserAddress.objects.filter(id=address_id, user=user).update(**address_data)
            else:
                # Create new address
                UserAddress.objects.create(user=user, **address_data)
    
    def _update_links(self, user, links_data):
        """Update or create user links"""
        # Get existing link IDs from the request
        incoming_ids = [link.get('id') for link in links_data if link.get('id')]
        
        # Delete links not in the incoming data
        UserLink.objects.filter(user=user).exclude(id__in=incoming_ids).delete()
        
        # Update or create links
        for link_data in links_data:
            link_id = link_data.get('id')
            link_data.pop('user', None)  # Remove user field if present
            
            if link_id:
                # Update existing link
                UserLink.objects.filter(id=link_id, user=user).update(**link_data)
            else:
                # Create new link
                UserLink.objects.create(user=user, **link_data)


class CrushPublicProfileSerializer(serializers.ModelSerializer):
    """
    Public profile serializer for verified Crush users
    Only shows public information (no private data like email, phone, addresses)
    Includes gallery photos and public wishlists
    """
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    cover_image_url = serializers.SerializerMethodField(read_only=True)
    gallery_photos = UserGallerySerializer(many=True, read_only=True)
    links = UserLinkSerializer(many=True, read_only=True)
    public_wishlists = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'about',
            'profile_picture_url', 'cover_image_url',
            'current_status', 'note',
            'gallery_photos', 'links', 'public_wishlists',
            'is_crush', 'crush_verified_at'
        ]
    
    def get_profile_picture_url(self, obj):
        """Get user's profile picture URL"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        # Fallback to gallery profile picture
        profile_pic = obj.gallery_photos.filter(is_profile_picture=True).first()
        if profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_pic.image.url)
            return profile_pic.image.url
        return None
    
    def get_cover_image_url(self, obj):
        """Get user's cover image URL"""
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None
    
    def get_public_wishlists(self, obj):
        """Get only public wishlists for this user with full details including items"""
        from .wishlist_serializers import WishListDetailSerializer
        public_wishlists = obj.wishlists.filter(is_public=True, is_active=True)
        return WishListDetailSerializer(public_wishlists, many=True, context=self.context).data
    
    def to_representation(self, instance):
        """Translate user-generated content fields"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if request:
            translator = create_translator_from_request(request)
            # Translate user-generated fields (auto-detect source language)
            if representation.get('about'):
                representation['about'] = translator.translate_user_content(representation['about'])
            if representation.get('note'):
                representation['note'] = translator.translate_user_content(representation['note'])
        
        return representation


class UserSearchSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for user search results
    Returns only essential information: username, profile picture, and crush status
    """
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture_url', 'is_crush']
    
    def get_profile_picture_url(self, obj):
        """Get user's profile picture URL"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        # Fallback to gallery profile picture
        profile_pic = obj.gallery_photos.filter(is_profile_picture=True).first()
        if profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_pic.image.url)
            return profile_pic.image.url
        return None


class CrushCardSerializer(serializers.ModelSerializer):
    """
    Serializer for Crush card display
    Returns username, profile picture, status, and note
    Perfect for displaying Crush cards in grids or carousels
    """
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture_url', 'current_status', 'note', 'is_crush']
    
    def get_profile_picture_url(self, obj):
        """Get user's profile picture URL"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        # Fallback to gallery profile picture
        profile_pic = obj.gallery_photos.filter(is_profile_picture=True).first()
        if profile_pic:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_pic.image.url)
            return profile_pic.image.url
        return None
    
    def to_representation(self, instance):
        """Translate user-generated content fields"""
        representation = super().to_representation(instance)
        request = self.context.get('request')
        
        if request:
            translator = create_translator_from_request(request)
            # Translate user-generated note (auto-detect source language)
            if representation.get('note'):
                representation['note'] = translator.translate_user_content(representation['note'])
        
        return representation
    
