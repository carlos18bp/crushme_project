"""
User authentication serializers for CrushMe e-commerce application
Based on signin_signon_feature repository implementation
Handles user registration, authentication, and password management
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..models import User, PasswordCode


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    Used for displaying user information and profile updates
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined']
    
    def update(self, instance, validated_data):
        """Update user profile information"""
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    Validates email uniqueness and password requirements
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
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate_email(self, value):
        """Check if email is already registered"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create new user with hashed password"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=validated_data['email'],  # Django requirement, but we use email
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    Supports both email/password and email/passcode authentication
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        required=False,
        style={'input_type': 'password'}
    )
    passcode = serializers.CharField(
        required=False,
        max_length=6,
        min_length=6
    )
    
    def validate(self, attrs):
        """Validate login credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        passcode = attrs.get('passcode')
        
        if not password and not passcode:
            raise serializers.ValidationError("Either password or passcode is required.")
        
        if password and passcode:
            raise serializers.ValidationError("Provide either password or passcode, not both.")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        if password:
            # Authenticate with password
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
        
        elif passcode:
            # Authenticate with passcode
            try:
                password_code = PasswordCode.objects.get(
                    user=user,
                    code=passcode,
                    used=False
                )
                if password_code.is_expired():
                    raise serializers.ValidationError("Passcode has expired.")
                
                # Mark passcode as used
                password_code.used = True
                password_code.save()
                
            except PasswordCode.DoesNotExist:
                raise serializers.ValidationError("Invalid or expired passcode.")
        
        attrs['user'] = user
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
    Serializer for password reset with passcode
    """
    email = serializers.EmailField()
    passcode = serializers.CharField(max_length=6, min_length=6)
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
        passcode = attrs['passcode']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        try:
            password_code = PasswordCode.objects.get(
                user=user,
                code=passcode,
                used=False
            )
            if password_code.is_expired():
                raise serializers.ValidationError("Passcode has expired.")
            
            attrs['user'] = user
            attrs['password_code'] = password_code
            
        except PasswordCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired passcode.")
        
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
