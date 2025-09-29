"""
User authentication models based on the signin_signon_feature and gym_project repositories
Extends Django's AbstractUser for custom authentication with JWT support
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import random
import string


class UserManager(BaseUserManager):
    """
    Custom user manager to handle user creation with email as the unique identifier.
    Based on signin_signon_feature and gym_project pattern
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a regular user with the given email and password.

        Args:
            email (str): The email of the user.
            password (str, optional): The password for the user. Defaults to None.
            **extra_fields: Additional fields for the user model.

        Raises:
            ValueError: If the email is not provided.

        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError('The email must be defined')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with the given email and password.

        Args:
            email (str): The email of the superuser.
            password (str, optional): The password for the superuser. Defaults to None.
            **extra_fields: Additional fields for the superuser model.

        Raises:
            ValueError: If is_staff or is_superuser is not set to True.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model extending AbstractUser. Uses email as the unique identifier for authentication.
    Includes username for display purposes and additional profile fields.
    Based on signin_signon_feature and gym_project implementation
    
    Attributes:
        email (EmailField): The unique email of the user (used for authentication).
        username (CharField): Unique username for display purposes.
        first_name (CharField): The first name of the user.
        last_name (CharField): The last name of the user.
        phone (CharField): Phone number of the user.
        about (TextField): About yourself section.
        is_guest_converted (BooleanField): Flag to track if user was converted from guest checkout.
    """
    # Override the default username to make it unique but not for authentication
    username = models.CharField(
        max_length=30, 
        unique=True, 
        verbose_name="Username",
        help_text="Unique username for display purposes. Can be changed later.",
        null=True,
        blank=True
    )
    groups = None
    user_permissions = None
    
    # Use email as the unique identifier for authentication
    email = models.EmailField(unique=True, verbose_name="Email Address")
    first_name = models.CharField(max_length=60, verbose_name="First Name")
    last_name = models.CharField(max_length=60, verbose_name="Last Name")
    
    # Additional profile fields
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Phone Number",
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    about = models.TextField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name="About Yourself",
        help_text="Tell others about yourself (max 500 characters)"
    )
    
    # Track if user was converted from guest checkout
    is_guest_converted = models.BooleanField(
        default=False,
        verbose_name="Converted from Guest",
        help_text="True if this user was created from a guest checkout"
    )
    
    # Track email verification status
    email_verified = models.BooleanField(
        default=False,
        verbose_name="Email Verified",
        help_text="True if user has verified their email address"
    )

    # Set email as the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Use the custom user manager
    objects = UserManager()

    def __str__(self):
        """
        String representation of the User instance.
        
        Returns:
            str: The email of the user.
        """
        return self.email
    
    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class PasswordCode(models.Model):
    """
    Model to store verification codes associated with a user.
    Used for password reset and email verification.
    
    Attributes:
        user (ForeignKey): A foreign key linking the code to a user.
        code (CharField): A 4-digit code used for verification.
        code_type (CharField): Type of code (password_reset, email_verification).
        created_at (DateTimeField): Timestamp of when the code was created.
        used (BooleanField): Flag to indicate if the code has been used.
    """
    CODE_TYPES = [
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
    ]
    
    # Link each password code to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_codes')
    
    # The verification code, restricted to a maximum length of 4 digits
    code = models.CharField(
        max_length=4,
        validators=[RegexValidator(regex='^\d{4}$', message='Code must be 4 digits', code='invalid_code')]
    )
    
    # Type of verification code
    code_type = models.CharField(
        max_length=20,
        choices=CODE_TYPES,
        default='password_reset',
        verbose_name="Code Type"
    )
    
    # Timestamp of when the password code was created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Flag to indicate whether the code has been used
    used = models.BooleanField(default=False)

    def is_expired(self):
        """
        Check if the verification code has expired (5 minutes).
        
        Returns:
            bool: True if the code has expired, False otherwise.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        expiration_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expiration_time
    
    def is_valid(self):
        """
        Check if the verification code is valid (not used and not expired).
        
        Returns:
            bool: True if the code is valid, False otherwise.
        """
        return not self.used and not self.is_expired()

    def __str__(self):
        """
        String representation of the PasswordCode instance.
        
        Returns:
            str: The user's email, code type and the verification code.
        """
        return f'{self.user.email} - {self.get_code_type_display()} - {self.code}'

    class Meta:
        """
        Meta options for the PasswordCode model.
        
        Attributes:
            ordering (list): Default ordering for querysets.
            verbose_name (str): Human-readable singular name for the model.
            verbose_name_plural (str): Human-readable plural name for the model.
        """
        ordering = ['-created_at']
        verbose_name = 'Verification Code'
        verbose_name_plural = 'Verification Codes'


class UserAddress(models.Model):
    """
    Model to store user address information for shipping and billing.
    Can be used for both registered users and guest checkouts.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses',
        null=True,
        blank=True,
        help_text="User who owns this address. Null for guest checkouts."
    )
    
    # Address fields
    country = models.CharField(max_length=100, verbose_name="Country")
    state = models.CharField(max_length=100, verbose_name="State/Province")
    city = models.CharField(max_length=100, verbose_name="City")
    zip_code = models.CharField(max_length=20, verbose_name="ZIP/Postal Code")
    address_line_1 = models.CharField(max_length=255, verbose_name="Address Line 1")
    address_line_2 = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Address Line 2"
    )
    
    # Address type and default flags
    is_default_shipping = models.BooleanField(
        default=False,
        verbose_name="Default Shipping Address"
    )
    is_default_billing = models.BooleanField(
        default=False,
        verbose_name="Default Billing Address"
    )
    
    # For guest checkouts, store contact info
    guest_email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Guest Email",
        help_text="Email for guest checkouts"
    )
    guest_first_name = models.CharField(
        max_length=60, 
        blank=True, 
        null=True,
        verbose_name="Guest First Name"
    )
    guest_last_name = models.CharField(
        max_length=60, 
        blank=True, 
        null=True,
        verbose_name="Guest Last Name"
    )
    guest_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Guest Phone"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.address_line_1}, {self.city}"
        else:
            return f"Guest ({self.guest_email}) - {self.address_line_1}, {self.city}"

    class Meta:
        verbose_name = "User Address"
        verbose_name_plural = "User Addresses"
        ordering = ['-created_at']


class UserGallery(models.Model):
    """
    Model to store user gallery photos.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='gallery_photos'
    )
    image = models.ImageField(
        upload_to='user_gallery/%Y/%m/%d/',
        verbose_name="Gallery Image"
    )
    caption = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Image Caption"
    )
    is_profile_picture = models.BooleanField(
        default=False,
        verbose_name="Profile Picture",
        help_text="Set as profile picture"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username or self.user.email} - Gallery Photo"

    class Meta:
        verbose_name = "User Gallery Photo"
        verbose_name_plural = "User Gallery Photos"
        ordering = ['-uploaded_at']


class UserLink(models.Model):
    """
    Model for user links (linktree-style functionality).
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='links'
    )
    title = models.CharField(
        max_length=100,
        verbose_name="Link Title",
        help_text="Display name for the link"
    )
    url = models.URLField(
        verbose_name="URL",
        help_text="The actual link URL"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order in which links are displayed"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Whether this link is visible"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username or self.user.email} - {self.title}"

    class Meta:
        verbose_name = "User Link"
        verbose_name_plural = "User Links"
        ordering = ['order', 'created_at']


class GuestUser(models.Model):
    """
    Model to store guest user information from checkouts.
    This allows for pre-registration when they decide to create an account.
    """
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address"
    )
    first_name = models.CharField(max_length=60, verbose_name="First Name")
    last_name = models.CharField(max_length=60, verbose_name="Last Name")
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Phone Number"
    )
    
    # Track guest checkout activity
    total_orders = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Orders",
        help_text="Number of orders placed as guest"
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Total Spent",
        help_text="Total amount spent as guest"
    )
    
    # Registration tracking
    has_been_converted = models.BooleanField(
        default=False,
        verbose_name="Converted to User",
        help_text="True if guest has registered as full user"
    )
    converted_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guest_profile',
        verbose_name="Converted User Account"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Guest: {self.email} ({self.total_orders} orders)"

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        verbose_name = "Guest User"
        verbose_name_plural = "Guest Users"
        ordering = ['-created_at']
